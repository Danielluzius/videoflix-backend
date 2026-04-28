import os
from django.http import FileResponse, Http404
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.parsers import MultiPartParser, FormParser
from video_app import services
from video_app.api.serializers import VideoSerializer, VideoUploadSerializer


class VideoListView(APIView):
    """Return all fully processed videos."""

    def get(self, request):
        """Retrieve the list of available videos ordered by creation date."""
        videos = services.get_all_videos()
        serializer = VideoSerializer(videos, many=True, context={'request': request})
        return Response(serializer.data)


class VideoUploadView(APIView):
    """Accept a video file upload from admin users and queue background processing."""

    permission_classes = [IsAdminUser]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        """Save the uploaded video; HLS conversion is triggered automatically via signal."""
        serializer = VideoUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        video = serializer.save()
        return Response(
            {'id': video.id, 'detail': 'Upload successful. Video is being processed.'},
            status=status.HTTP_201_CREATED,
        )


class HLSPlaylistView(APIView):
    """Serve the HLS index playlist for a given video and resolution."""

    def get(self, request, video_id, resolution):
        """Return the index.m3u8 file for the requested resolution (480p/720p/1080p)."""
        playlist_path = os.path.join(
            settings.MEDIA_ROOT, 'videos', 'hls', str(video_id), resolution, 'index.m3u8'
        )
        if not os.path.exists(playlist_path):
            raise Http404
        return FileResponse(open(playlist_path, 'rb'), content_type='application/vnd.apple.mpegurl')


class HLSSegmentView(APIView):
    """Serve individual .ts HLS segments for video playback."""

    def get(self, request, video_id, resolution, segment):
        """Return a single .ts segment binary for the requested video and resolution."""
        segment_path = os.path.join(
            settings.MEDIA_ROOT, 'videos', 'hls', str(video_id), resolution, segment
        )
        if not os.path.exists(segment_path):
            raise Http404
        return FileResponse(open(segment_path, 'rb'), content_type='video/MP2T')
