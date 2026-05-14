from rest_framework import serializers
from video_app.models import Video


class VideoSerializer(serializers.ModelSerializer):
    """Read serializer for Video: exposes public fields and absolute media URLs."""

    thumbnail_url = serializers.SerializerMethodField()
    preview_clip_url = serializers.SerializerMethodField()

    class Meta:
        model = Video
        fields = ['id', 'title', 'description', 'category', 'thumbnail_url', 'preview_clip_url', 'created_at']

    def get_thumbnail_url(self, obj):
        """Return the absolute URL of the thumbnail, or None if unavailable."""
        request = self.context.get('request')
        if obj.thumbnail and request:
            return request.build_absolute_uri(obj.thumbnail.url)
        return None

    def get_preview_clip_url(self, obj):
        """Return the absolute URL of the preview clip, or None if not yet generated."""
        request = self.context.get('request')
        if obj.preview_clip and request:
            return request.build_absolute_uri(obj.preview_clip.url)
        return None


class VideoUploadSerializer(serializers.ModelSerializer):
    """Write serializer for Video: accepts file upload fields for admin use."""

    class Meta:
        model = Video
        fields = ['id', 'title', 'description', 'category', 'video_file', 'preview_clip']
