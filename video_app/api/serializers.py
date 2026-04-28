from rest_framework import serializers
from video_app.models import Video


class VideoSerializer(serializers.ModelSerializer):
    """Read serializer for Video: exposes public fields and an absolute thumbnail URL."""

    thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        model = Video
        fields = ['id', 'title', 'description', 'category', 'thumbnail_url', 'created_at']

    def get_thumbnail_url(self, obj):
        """Return the absolute URL of the thumbnail, or None if unavailable."""
        request = self.context.get('request')
        if obj.thumbnail and request:
            return request.build_absolute_uri(obj.thumbnail.url)
        return None


class VideoUploadSerializer(serializers.ModelSerializer):
    """Write serializer for Video: accepts file upload fields for admin use."""

    class Meta:
        model = Video
        fields = ['id', 'title', 'description', 'category', 'video_file']
