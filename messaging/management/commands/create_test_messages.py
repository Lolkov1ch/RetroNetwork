from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from messaging.models import Conversation, Message

User = get_user_model()

class Command(BaseCommand):
    help = 'Create test conversations with messages for demo'

    def handle(self, *args, **options):

        users = list(User.objects.all()[:3])
        
        if len(users) < 2:
            self.stdout.write(self.style.ERROR('Need at least 2 users'))
            return
        
        user1 = users[0]
        user2 = users[1] if len(users) > 1 else User.objects.create_user(
            handle='testuser2',
            email='test2@example.com',
            password='testpass123',
            display_name='Test User 2'
        )
        
        conversation, created = Conversation.objects.get_or_create(is_group=False)
        if created:
            conversation.participants.add(user1, user2)
            self.stdout.write(self.style.SUCCESS('Created conversation'))
        else:

            conversation = Conversation.objects.filter(is_group=False).first()
            if not conversation:
                conversation = Conversation.objects.create(is_group=False)
                conversation.participants.add(user1, user2)
        
        messages = [
            'Hey! How are you?',
            'I\'m doing well, thanks for asking!',
            'Want to chat sometime?',
            'Sure, let\'s catch up soon 😄',
            'Great! Talk to you later.',
        ]
        
        if conversation.messages.count() == 0:
            for i, msg_text in enumerate(messages):
                sender = user1 if i % 2 == 0 else user2
                message = Message.objects.create(
                    conversation=conversation,
                    sender=sender,
                    message_type='text',
                    content=msg_text
                )

                if i % 2 == 1:
                    message.read_by_users.add(user1, user2)
                else:
                    message.read_by_users.add(sender)
            
            self.stdout.write(self.style.SUCCESS('Created test messages'))
        
        self.stdout.write(self.style.SUCCESS(f'Test data ready: {user1.display_name} ↔ {user2.display_name}'))
