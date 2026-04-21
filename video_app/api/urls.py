from django.urls import path
from video_app.api.views import VideoListView, VideoUploadView, HLSManifestView, HLSSegmentView

urlpatterns = [
    path('videos/', VideoListView.as_view(), name='video-list'),
    path('videos/upload/', VideoUploadView.as_view(), name='video-upload'),
    path('videos/<int:video_id>/hls/', HLSManifestView.as_view(), name='hls-manifest'),
    path('videos/<int:video_id>/hls/<str:quality>/<str:filename>', HLSSegmentView.as_view(), name='hls-segment'),
]
