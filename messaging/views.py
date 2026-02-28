import json
import logging

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.exceptions import ValidationError as DRFValidationError

from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin

from PIL import Image as PilImage

from .models import Conversation, Message, MessageReaction, MessageAttachment
from .serializers import ConversationSerializer, MessageSerializer, MessageReactionSerializer, UserSimpleSerializer, MessageAttachmentSerializer

User = get_user_model()
logger = logging.getLogger(__name__)

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
ALLOWED_VIDEO_TYPES = {"video/mp4", "video/webm", "video/quicktime"}
ALLOWED_AUDIO_TYPES = {"audio/ogg", "audio/webm", "audio/mpeg", "audio/wav", "audio/aac", "audio/mp4"}

MAX_IMAGE_SIZE = 15 * 1024 * 1024   # 15MB
MAX_VIDEO_SIZE = 250 * 1024 * 1024  # 250MB
MAX_AUDIO_SIZE = 25 * 1024 * 1024   # 25MB


def _rewind(f):
    try:
        f.seek(0)
    except Exception:
        pass


def _validate_uploaded_file(f, kind: str):
    if not f:
        return

    ct = (getattr(f, "content_type", "") or "").lower().strip()
    _rewind(f)

    if kind == "image":
        if f.size > MAX_IMAGE_SIZE:
            raise DRFValidationError({"file": f"{f.name}: image is too large."})
        if not ct.startswith("image/") or ct not in ALLOWED_IMAGE_TYPES:
            raise DRFValidationError({"file": f"{f.name}: Unsupported image type ({ct})."})
        try:
            img = PilImage.open(f)
            img.verify()
        except Exception:
            raise DRFValidationError({"file": f"{f.name}: Invalid image file."})
        finally:
            _rewind(f)
        return

    if kind == "video":
        if f.size > MAX_VIDEO_SIZE:
            raise DRFValidationError({"file": f"{f.name}: video is too large."})
        if not ct.startswith("video/") or ct not in ALLOWED_VIDEO_TYPES:
            raise DRFValidationError({"file": f"{f.name}: Unsupported video type ({ct})."})
        _rewind(f)
        return

    if kind in {"voice", "audio"}:
        if f.size > MAX_AUDIO_SIZE:
            raise DRFValidationError({"file": f"{f.name}: audio is too large."})
        if not ct.startswith("audio/") or ct not in ALLOWED_AUDIO_TYPES:
            raise DRFValidationError({"file": f"{f.name}: Unsupported audio type ({ct})."})
        _rewind(f)
        return

    raise DRFValidationError({"file": f"{f.name}: Unsupported file type ({ct})."})


class MessengerView(LoginRequiredMixin, TemplateView):
    template_name = "messenger/messenger.html"
    login_url = "users:login"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from .serializers import avatar_data_uri

        try:
            if self.request.user.avatar and self.request.user.avatar.name:
                avatar_url = self.request.user.avatar.url
            else:
                avatar_url = avatar_data_uri(self.request.user.username, size=80)
        except (AttributeError, FileNotFoundError, ValueError):
            avatar_url = avatar_data_uri(self.request.user.username, size=80)

        context["user_data"] = json.dumps(
            {
                "id": self.request.user.id,
                "username": self.request.user.username,
                "display_name": self.request.user.display_name,
                "avatar": avatar_url,
            }
        )
        return context


class IsParticipantOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user in obj.participants.all()


class ConversationViewSet(viewsets.ModelViewSet):
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (JSONParser, MultiPartParser, FormParser)

    def get_queryset(self):
        return (
            Conversation.objects.filter(participants=self.request.user)
            .prefetch_related("participants", "messages")
        )

    def perform_create(self, serializer):
        conversation = serializer.save()
        conversation.participants.add(self.request.user)
        participant_ids = self.request.data.getlist("participants")
        for user_id in participant_ids:
            try:
                user = User.objects.get(id=user_id)
                conversation.participants.add(user)
            except User.DoesNotExist:
                pass

    @action(detail=False, methods=["get"])
    def search_users(self, request):
        query = request.query_params.get("q", "").strip()
        if not query or len(query) < 2:
            return Response([], status=status.HTTP_200_OK)

        from django.db.models import Q

        users = (
            User.objects.filter(Q(username__icontains=query) | Q(display_name__icontains=query))
            .exclude(id=request.user.id)[:10]
        )
        serializer = UserSimpleSerializer(users, many=True, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"])
    def create_or_get(self, request):
        user_id = request.data.get("user_id")
        username = request.data.get("username")

        if not user_id and not username:
            return Response({"error": "user_id or username is required"}, status=400)

        try:
            if user_id:
                other_user = User.objects.get(id=user_id)
            else:
                other_user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        conversation = (
            Conversation.objects.filter(is_group=False, participants=request.user)
            .filter(participants=other_user)
            .distinct()
            .first()
        )

        if not conversation:
            conversation = Conversation.objects.create(is_group=False)
            conversation.participants.add(request.user, other_user)

        serializer = ConversationSerializer(conversation, context={"request": request})
        return Response(serializer.data, status=200)
    
    @action(detail=True, methods=["get"])
    def messages(self, request, pk=None):
        conversation = self.get_object()

        qs = (
            Message.objects
            .filter(conversation=conversation)
            .select_related("sender")
            .order_by("-created_at")
        )

        offset = int(request.query_params.get("offset", 0))
        limit = int(request.query_params.get("limit", 30))

        total = qs.count()
        qs = qs[offset: offset + limit]

        serializer = MessageSerializer(qs, many=True, context={"request": request})

        return Response({
            "count": total,
            "results": serializer.data
        })


class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (JSONParser, MultiPartParser, FormParser)

    def get_queryset(self):
        return (
            Message.objects.filter(conversation__participants=self.request.user)
            .select_related("sender")
            .prefetch_related("read_by_users", "reactions")
        )

    def perform_create(self, serializer):
        conversation = serializer.validated_data.get("conversation")
        if not conversation:
            conversation_id = self.request.data.get("conversation")
            conversation = get_object_or_404(Conversation, id=conversation_id)

        if self.request.user not in conversation.participants.all():
            raise permissions.PermissionDenied("You are not a participant in this conversation")

        message_type = (self.request.data.get("message_type") or "text").strip()

        uploaded = self.request.FILES.get("file")

        if message_type in {"image", "video", "voice", "audio"}:
            if not uploaded:
                raise DRFValidationError({"file": "file is required for this message_type"})
            _validate_uploaded_file(uploaded, kind=message_type)
            _rewind(uploaded)

        # create base message
        message = serializer.save(
            sender=self.request.user,
            message_type=message_type,
            conversation=conversation,
        )

        # attach file safely
        if uploaded and message_type in {"image", "video", "voice"}:
            try:
                if message_type == "image":
                    message.image = uploaded
                    message.save()

                elif message_type == "video":
                    message.video = uploaded
                    message.save()

                elif message_type in {"voice", "audio"}:
                    message.voice = uploaded
                    message.save()
                    
                    # Handle additional photo/video attachments with voice messages
                    attachments_files = self.request.FILES.getlist("attachments")
                    attachment_types = self.request.POST.getlist("attachment_types")
                    
                    if attachments_files and attachment_types:
                        for idx, attachment_file in enumerate(attachments_files):
                            if idx < len(attachment_types):
                                att_type = attachment_types[idx]
                                if att_type in {"image", "video"}:
                                    try:
                                        _validate_uploaded_file(attachment_file, kind=att_type)
                                        _rewind(attachment_file)
                                        
                                        attachment = MessageAttachment.objects.create(
                                            message=message,
                                            attachment_type=att_type,
                                            file=attachment_file
                                        )
                                    except DRFValidationError:
                                        logger.error(f"Attachment validation failed for {attachment_file.name}", exc_info=True)
                                        raise
                                    except Exception as e:
                                        logger.error(f"Failed to create attachment: {e}", exc_info=True)
                                        raise DRFValidationError({"attachments": f"Failed to upload attachment: {attachment_file.name}"})


            except DRFValidationError:
                message.delete()
                raise
            except Exception:
                # storage/cloudinary errors -> 400, not 500
                message.delete()
                raise DRFValidationError({"file": f"{uploaded.name}: upload failed (invalid/unsupported file)."})

        message.read_by_users.add(self.request.user)

    @action(detail=True, methods=["post"])
    def mark_as_read(self, request, pk=None):
        message = self.get_object()
        message.mark_as_read(request.user)
        return Response({"status": "message marked as read"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def react(self, request, pk=None):
        message = self.get_object()
        reaction_type = request.data.get("reaction_type")
        if not reaction_type:
            return Response({"error": "reaction_type is required"}, status=400)

        reaction, created = MessageReaction.objects.get_or_create(
            message=message, user=request.user, defaults={"reaction_type": reaction_type}
        )
        if not created:
            reaction.reaction_type = reaction_type
            reaction.save()

        serializer = MessageReactionSerializer(reaction)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def remove_reaction(self, request, pk=None):
        message = self.get_object()
        MessageReaction.objects.filter(message=message, user=request.user).delete()
        return Response({"status": "reaction removed"}, status=status.HTTP_204_NO_CONTENT)