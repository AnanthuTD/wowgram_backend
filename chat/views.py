import json
from django.http import HttpRequest, JsonResponse
from .models import Chat, Conversation
from django.db.models import Q, Max
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist


def conversations(request: HttpRequest):
    user = request.user
    conversations = Conversation.objects.filter(Q(sender=user) | Q(
        receiver=user)).select_related('sender', 'receiver')

    if not conversations:
        return JsonResponse({'status': True, 'message': 'no conversations', 'conversations': []})

    response = {'status': True,
                'message': 'conversation retrieval successful', 'conversations': []}
    for conversation in conversations:
        # determine the other user in the conversation
        if conversation.sender == user:
            other_user = conversation.receiver
        else:
            other_user = conversation.sender

        conversation_dict = {
            'username': other_user.username,
            'profile_img': settings.MEDIA_URL + str(other_user.profile.profile_img) if other_user.profile.profile_img else None,
            'last_message': conversation.last_message,
            'updated_at': conversation.updated_at
            # 'unread_count': conversation.messages.filter(read=False, conversation__sender=user).count(),
        }
        for con_dict in response['conversations']:
            if con_dict['username'] == conversation_dict['username']:
                if con_dict['updated_at'] > conversation_dict['updated_at']:
                    response['conversations'].remove(con_dict)

        response['conversations'].append(conversation_dict)

    return JsonResponse(response)


def load_messages(request: HttpRequest, username):
    try:
        current_username = request.user.get_username()

        conversations = Conversation.objects.filter(
            (Q(receiver__username=username) & Q(sender__username=current_username)) |
            (Q(receiver__username=current_username) & Q(sender__username=username))
        ).prefetch_related('messages', 'sender')

        chats = []
    
        for conversation in conversations:
            messages = (
                list(conversation.messages.all().order_by('timestamp')))
            chats.extend(messages)

        sorted_chats = sorted(chats, key=lambda chat: chat.timestamp)

        message_list = []

        for message in sorted_chats:
            message_list.append({
                'message': message.message,
                'timestamp': message.timestamp,
                'sender_username': message.conversation.sender.username,
                'id': message.id
            })

        return JsonResponse({'status': True, 'message_list': message_list})
    except ObjectDoesNotExist:
        return JsonResponse({'status': False, 'message': 'Conversation not found'})
    
def unsend(request:HttpRequest):
    data =json.loads(request.body)
    id = data['id']
    try:
        Chat.objects.get(id=id, conversation__sender=request.user).delete()
        return JsonResponse({'status':True, 'message': 'Chat was deleted successfully'}) 
    except ObjectDoesNotExist:
        return JsonResponse({'status': False, 'message':'chat not found or not the sender'})