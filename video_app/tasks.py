import os
import django_rq
from django.conf import settings
from video_app.models import Video
from video_app.utils import convert_to_hls, generate_thumbnail, generate_preview_clip, PREVIEW_MAX_COUNT


@django_rq.job('videos')
def process_video(video_id: int):
    """Background task: convert an uploaded video to HLS, generate a thumbnail and preview clip.

    Converts to 480p, 720p, and 1080p HLS variants, extracts a thumbnail at 3 s,
    generates a 15 s silent 720p preview clip, enforces a max of PREVIEW_MAX_COUNT
    preview clips on disk, and sets processing_done=True on the Video model.
    """
    video = Video.objects.get(pk=video_id)
    video_path = video.video_file.path

    # HLS output directory: media/videos/hls/<video_id>/
    hls_dir = os.path.join(settings.MEDIA_ROOT, 'videos', 'hls', str(video_id))
    master_path = convert_to_hls(video_path, hls_dir)
    video.hls_path = os.path.relpath(master_path, settings.MEDIA_ROOT)

    # Thumbnail
    thumbnail_path = os.path.join(settings.MEDIA_ROOT, 'videos', 'thumbnails', f'{video_id}.jpg')
    generate_thumbnail(video_path, thumbnail_path)
    video.thumbnail = os.path.relpath(thumbnail_path, settings.MEDIA_ROOT)

    # Preview clip (skip if a custom one was already uploaded)
    if not video.preview_clip:
        preview_path = os.path.join(settings.MEDIA_ROOT, 'videos', 'previews', f'{video_id}.mp4')
        generate_preview_clip(video_path, preview_path)
        video.preview_clip = os.path.relpath(preview_path, settings.MEDIA_ROOT)

    video.processing_done = True
    video.save()

    # Keep only the PREVIEW_MAX_COUNT newest preview clips on disk
    videos_with_preview = (
        Video.objects
        .filter(processing_done=True, preview_clip__isnull=False)
        .exclude(preview_clip='')
        .order_by('created_at')
    )
    overflow = videos_with_preview.count() - PREVIEW_MAX_COUNT
    if overflow > 0:
        for old_video in videos_with_preview[:overflow]:
            old_video.preview_clip.delete(save=False)
            old_video.preview_clip = None
            old_video.save(update_fields=['preview_clip'])
