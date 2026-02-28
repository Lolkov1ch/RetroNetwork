import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import Conversation, Message
from .serializers import MessageSerializer

User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.conversation_id = self.scope["url_route"]["kwargs"]["conversation_id"]
        self.conversation_group_name = f"chat_{self.conversation_id}"
        self.user = self.scope["user"]

        print(f"ChatConsumer.connect user={self.user} conversation={self.conversation_id}")

        await self.channel_layer.group_add(self.conversation_group_name, self.channel_name)
        await self.accept()

        if self.user.is_authenticated:
            await self.set_user_status("online")
            await self.mark_conversation_read()
            await self._broadcast_status("online")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.conversation_group_name, self.channel_name)

        if getattr(self, "user", None) and self.user.is_authenticated:
            await self.set_user_status("offline")
            await self._broadcast_status("offline")

        print(f"ChatConsumer.disconnect user={self.user} conversation={self.conversation_id} code={close_code}")

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message_type = data.get("type")

            if message_type == "chat_message":
                message = await self.save_message(data)
                if message:
                    await self.channel_layer.group_send(
                        self.conversation_group_name,
                        {"type": "chat_message", "message": MessageSerializer(message).data},
                    )

            elif message_type == "typing":
                await self.channel_layer.group_send(
                    self.conversation_group_name,
                    {
                        "type": "typing_indicator",
                        "user_id": self.user.id,
                        "username": self.user.display_name,
                        "is_typing": data.get("is_typing", True),
                    },
                )

            elif message_type == "message_read":
                message_id = data.get("message_id")
                await self.mark_message_read(message_id)
                await self.channel_layer.group_send(
                    self.conversation_group_name,
                    {"type": "message_read_indicator", "message_id": message_id, "user_id": self.user.id},
                )

            elif message_type == "message_edited":
                message_id = data.get("message_id")
                message = await self.get_message(message_id)
                if message and message.sender == self.user:
                    await self.channel_layer.group_send(
                        self.conversation_group_name,
                        {"type": "message_edited", "message": MessageSerializer(message).data},
                    )

            elif message_type == "message_deleted":
                message_id = data.get("message_id")
                message = await self.get_message(message_id)
                if message and message.sender == self.user:
                    await self.channel_layer.group_send(
                        self.conversation_group_name,
                        {"type": "message_deleted", "message_id": message_id},
                    )

            elif message_type == "status_change":
                new_status = data.get("status", "online")
                if new_status in ["online", "dnd", "inactive", "offline"]:
                    await self.set_user_status(new_status)
                    await self._broadcast_status(new_status)

        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({"type": "error", "message": "Invalid JSON"}))

    async def _broadcast_status(self, status: str):
        """Шлём статус и в группу чата, и в глобальную presence-группу."""
        event = {
            "type": "user_status_changed",
            "user_id": self.user.id,
            "username": self.user.username,
            "status": status,
        }

        # 1) в конкретный чат
        await self.channel_layer.group_send(self.conversation_group_name, event)

        # 2) глобально всем, кто подписан на presence
        await self.channel_layer.group_send("presence", event)

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({"type": "chat_message", "message": event["message"]}))

    async def typing_indicator(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "typing_indicator",
                    "user_id": event["user_id"],
                    "username": event["username"],
                    "is_typing": event["is_typing"],
                }
            )
        )

    async def message_read_indicator(self, event):
        await self.send(
            text_data=json.dumps(
                {"type": "message_read_indicator", "message_id": event["message_id"], "user_id": event["user_id"]}
            )
        )

    async def message_edited(self, event):
        await self.send(text_data=json.dumps({"type": "message_edited", "message": event["message"]}))

    async def message_deleted(self, event):
        await self.send(text_data=json.dumps({"type": "message_deleted", "message_id": event["message_id"]}))

    async def user_status_changed(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "user_status_changed",
                    "user_id": event["user_id"],
                    "username": event["username"],
                    "status": event["status"],
                }
            )
        )

    @database_sync_to_async
    def save_message(self, data):
        try:
            conversation = Conversation.objects.get(id=self.conversation_id)
            if self.user not in conversation.participants.all():
                return None

            message_type = data.get("message_type", "text")
            message = Message.objects.create(
                conversation=conversation,
                sender=self.user,
                message_type=message_type,
                content=data.get("content", ""),
            )
            message.read_by_users.add(self.user)
            return message
        except Conversation.DoesNotExist:
            return None

    @database_sync_to_async
    def mark_message_read(self, message_id):
        try:
            message = Message.objects.get(id=message_id)
            if self.user not in message.read_by_users.all():
                message.read_by_users.add(self.user)
        except Message.DoesNotExist:
            pass

    @database_sync_to_async
    def mark_conversation_read(self):
        try:
            conversation = Conversation.objects.get(id=self.conversation_id)
            conversation.mark_as_read(self.user)
        except Conversation.DoesNotExist:
            pass

    @database_sync_to_async
    def get_message(self, message_id):
        try:
            return Message.objects.get(id=message_id)
        except Message.DoesNotExist:
            return None

    @database_sync_to_async
    def set_user_status(self, status):
        try:
            user = User.objects.get(id=self.user.id)
            user.status = status
            user.save(update_fields=["status"])
            return True
        except User.DoesNotExist:
            return False


class PresenceConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope.get("user")
        await self.channel_layer.group_add("presence", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("presence", self.channel_name)

    async def user_status_changed(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "user_status_changed",
                    "user_id": event.get("user_id"),
                    "username": event.get("username"),
                    "status": event.get("status"),
                }
            )
        )