from django.contrib import admin
from video_app.models import Video


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'category', 'processing_done', 'created_at']
    list_filter = ['category', 'processing_done']
    search_fields = ['title', 'description']
    readonly_fields = ['hls_path', 'thumbnail', 'processing_done', 'created_at']

