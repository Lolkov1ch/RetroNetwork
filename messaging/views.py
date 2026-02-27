from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.shortcuts import get_object_or_404, render
from django.views.generic import TemplateView
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Conversation, Message, MessageReaction
from .serializers import ConversationSerializer, MessageSerializer, MessageReactionSerializer

User = get_user_model()


class MessengerView(LoginRequiredMixin, TemplateView):
    template_name = 'messenger/messenger.html'
    login_url = 'users:login'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        import json
        from .serializers import avatar_data_uri
        try:
            avatar_url = self.request.user.avatar.url
        except Exception:
            avatar_url = avatar_data_uri(self.request.user.username, size=80)

        context['user_data'] = json.dumps({
            'id': self.request.user.id,
            'username': self.request.user.username,
            'display_name': self.request.user.display_name,
            'avatar': avatar_url,
        })
        return context


class IsParticipantOrReadOnly(permissions.BasePermission):
    
    def has_object_permission(self, request, view, obj):
        return request.user in obj.participants.all()


class ConversationViewSet(viewsets.ModelViewSet):
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (JSONParser, MultiPartParser, FormParser)

    def get_queryset(self):
        return Conversation.objects.filter(
            participants=self.request.user
        ).prefetch_related('participants', 'messages')

    def perform_create(self, serializer):
        conversation = serializer.save()
        conversation.participants.add(self.request.user)
        participant_ids = self.request.data.getlist('participants')
        for user_id in participant_ids:
            try:
                user = User.objects.get(id=user_id)
                conversation.participants.add(user)
            except User.DoesNotExist:
                pass

    @action(detail=False, methods=['get'])
    def search_users(self, request):
        query = request.query_params.get('q', '').strip()
        if not query or len(query) < 2:
            return Response([], status=status.HTTP_200_OK)

        from django.db.models import Q
        users = User.objects.filter(
            Q(username__icontains=query) | Q(display_name__icontains=query)
        ).exclude(id=request.user.id).values('id', 'username', 'display_name', 'avatar')[:10]
        
        return Response(list(users), status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def create_or_get(self, request):
        user_id = request.data.get('user_id')
        username = request.data.get('username')
        
        if not user_id and not username:
            return Response(
                {'error': 'user_id or username is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            if user_id:
                other_user = User.objects.get(id=user_id)
            else:
                other_user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        if other_user == request.user:
            return Response(
                {'error': 'Cannot create conversation with yourself'},
                status=status.HTTP_400_BAD_REQUEST
            )

        conversation = Conversation.objects.filter(
            is_group=False,
            participants=request.user
        ).filter(participants=other_user).first()

        if not conversation:
            conversation = Conversation.objects.create(is_group=False)
            conversation.participants.add(request.user, other_user)

        serializer = self.get_serializer(conversation)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def change_status(self, request):
        new_status = request.data.get('status')
        
        if not new_status:
            return Response(
                {'error': 'status is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        valid_statuses = [choice[0] for choice in User.STATUS_CHOICES]
        if new_status not in valid_statuses:
            return Response(
                {'error': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        request.user.status = new_status
        request.user.save()

        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync
        import json
        
        channel_layer = get_channel_layer()
        conversations = Conversation.objects.filter(participants=request.user)
        for conversation in conversations:
            async_to_sync(channel_layer.group_send)(
                f'chat_{conversation.id}',
                {
                    'type': 'user_status_changed',
                    'user_id': request.user.id,
                    'status': new_status,
                    'display_name': request.user.get_display_name(),
                }
            )
        async_to_sync(channel_layer.group_send)(
            'presence',
            {
                'type': 'user_status_changed',
                'user_id': request.user.id,
                'username': request.user.username,
                'status': new_status,
            }
        )
        
        return Response(
            {
                'status': 'ok',
                'user_id': request.user.id,
                'new_status': new_status,
            },
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        conversation = self.get_object()
        self.check_object_permissions(request, conversation)
        conversation.mark_as_read(request.user)
        
        return Response(
            {'status': 'messages marked as read'},
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        conversation = self.get_object()
        self.check_object_permissions(request, conversation)

        try:
            offset = int(request.query_params.get('offset', 0))
        except Exception:
            offset = 0
        try:
            limit = int(request.query_params.get('limit', 50))
        except Exception:
            limit = 50

        qs = conversation.messages.all().order_by('-created_at')
        total_count = qs.count()
        messages = qs[offset:offset+limit]

        serializer = MessageSerializer(
            messages,
            many=True,
            context={'request': request}
        )
        return Response({
            'count': total_count,
            'results': serializer.data
        })


class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (JSONParser, MultiPartParser, FormParser)

    def get_queryset(self):
        return Message.objects.filter(
            conversation__participants=self.request.user
        ).select_related('sender').prefetch_related('read_by_users', 'reactions')

    def perform_create(self, serializer):
        conversation = serializer.validated_data.get('conversation')
        if not conversation:
            conversation_id = self.request.data.get('conversation')
            conversation = get_object_or_404(Conversation, id=conversation_id)

        if self.request.user not in conversation.participants.all():
            raise permissions.PermissionDenied("You are not a participant in this conversation")
        
        message_type = self.request.data.get('message_type', 'text')

        message = serializer.save(
            sender=self.request.user,
            message_type=message_type
        )

        if 'file' in self.request.FILES and message_type in ['image', 'video', 'voice']:
            file = self.request.FILES['file']
            if message_type == 'image':
                message.image = file
                message.generate_image_thumbnail()
            elif message_type == 'video':
                message.video = file
                message.generate_video_thumbnail()
            elif message_type == 'voice':
                message.voice = file
            message.save()

        message.read_by_users.add(self.request.user)

    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        message = self.get_object()
        message.mark_as_read(request.user)
        
        return Response(
            {'status': 'message marked as read'},
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'])
    def react(self, request, pk=None):
        message = self.get_object()
        reaction_type = request.data.get('reaction_type')
        
        if not reaction_type:
            return Response(
                {'error': 'reaction_type is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reaction, created = MessageReaction.objects.get_or_create(
            message=message,
            user=request.user,
            defaults={'reaction_type': reaction_type}
        )
        
        if not created:
            reaction.reaction_type = reaction_type
            reaction.save()
        
        serializer = MessageReactionSerializer(reaction)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def remove_reaction(self, request, pk=None):
        message = self.get_object()
        
        MessageReaction.objects.filter(
            message=message,
            user=request.user
        ).delete()
        
        return Response(
            {'status': 'reaction removed'},
            status=status.HTTP_204_NO_CONTENT
        )

    @action(detail=True, methods=['patch'])
    def edit(self, request, pk=None):
        message = self.get_object()
        
        if message.sender != request.user:
            return Response(
                {'error': 'You can only edit your own messages'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if message.message_type != 'text':
            return Response(
                {'error': 'Only text messages can be edited'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        message.content = request.data.get('content', message.content)
        message.is_edited = True
        message.save()
        
        serializer = self.get_serializer(message)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def perform_destroy(self, instance):
        if instance.sender != self.request.user:
            raise permissions.PermissionDenied("You can only delete your own messages")
        instance.delete()
