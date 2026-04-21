from django.urls import path
from video_app.api.views import VideoListView, VideoUploadView, HLSPlaylistView, HLSSegmentView

urlpatterns = [
    path('video/', VideoListView.as_view(), name='video-list'),
    path('video/upload/', VideoUploadView.as_view(), name='video-upload'),
    path('video/<int:video_id>/<str:resolution>/index.m3u8', HLSPlaylistView.as_view(), name='hls-playlist'),
    path('video/<int:video_id>/<str:resolution>/<str:segment>/', HLSSegmentView.as_view(), name='hls-segment'),
]
