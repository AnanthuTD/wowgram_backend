from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/post/comment/(?P<room_name>[0-9a-f-]+)/$', consumers.CommentConsumer.as_asgi()),
]
