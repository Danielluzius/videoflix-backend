import os
from django.http import FileResponse, Http404
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
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


class HLSManifestView(APIView):
    def get(self, request, video_id):
        video = services.get_video_by_id(video_id)
        if not video or not video.hls_path:
            raise Http404
        manifest_path = os.path.join(settings.MEDIA_ROOT, video.hls_path)
        if not os.path.exists(manifest_path):
            raise Http404
        return FileResponse(open(manifest_path, 'rb'), content_type='application/vnd.apple.mpegurl')


class HLSSegmentView(APIView):
    def get(self, request, video_id, quality, filename):
        segment_path = os.path.join(
            settings.MEDIA_ROOT, 'videos', 'hls', str(video_id), quality, filename
        )
        if not os.path.exists(segment_path):
            raise Http404
        if filename.endswith('.m3u8'):
            content_type = 'application/vnd.apple.mpegurl'
        else:
            content_type = 'video/MP2T'
        return FileResponse(open(segment_path, 'rb'), content_type=content_type)
