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
from video_app.tasks import process_video


class VideoListView(APIView):
    def get(self, request):
        videos = services.get_all_videos()
        serializer = VideoSerializer(videos, many=True, context={'request': request})
        return Response(serializer.data)


class VideoUploadView(APIView):
    permission_classes = [IsAdminUser]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        serializer = VideoUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        video = serializer.save()
        process_video.delay(video.id)
        return Response(
            {'id': video.id, 'detail': 'Upload successful. Video is being processed.'},
            status=status.HTTP_201_CREATED,
        )


class HLSPlaylistView(APIView):
    def get(self, request, video_id, resolution):
        playlist_path = os.path.join(
            settings.MEDIA_ROOT, 'videos', 'hls', str(video_id), resolution, 'index.m3u8'
        )
        if not os.path.exists(playlist_path):
            raise Http404
        return FileResponse(open(playlist_path, 'rb'), content_type='application/vnd.apple.mpegurl')


class HLSSegmentView(APIView):
    def get(self, request, video_id, resolution, segment):
        segment_path = os.path.join(
            settings.MEDIA_ROOT, 'videos', 'hls', str(video_id), resolution, segment
        )
        if not os.path.exists(segment_path):
            raise Http404
        return FileResponse(open(segment_path, 'rb'), content_type='video/MP2T')
