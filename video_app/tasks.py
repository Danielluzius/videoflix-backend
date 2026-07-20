import os
import django_rq
from django.conf import settings
from video_app.models import Video
from video_app.utils import convert_to_hls, generate_thumbnail, generate_preview_clip, PREVIEW_MAX_COUNT


def _build_hls(video_id: int, video_path: str) -> str:
    """Convert to HLS variants; return the relative path to master.m3u8."""
    hls_dir = os.path.join(settings.MEDIA_ROOT, 'videos', 'hls', str(video_id))
    master_path = convert_to_hls(video_path, hls_dir)
    return os.path.relpath(master_path, settings.MEDIA_ROOT)


def _build_thumbnail(video_id: int, video_path: str) -> str:
    """Extract a thumbnail frame; return the relative path."""
    out = os.path.join(settings.MEDIA_ROOT, 'videos', 'thumbnails', f'{video_id}.jpg')
    generate_thumbnail(video_path, out)
    return os.path.relpath(out, settings.MEDIA_ROOT)


def _build_preview_clip(video_id: int, video_path: str) -> str:
    """Generate a short preview clip; return the relative path."""
    out = os.path.join(settings.MEDIA_ROOT, 'videos', 'previews', f'{video_id}.mp4')
    generate_preview_clip(video_path, out)
    return os.path.relpath(out, settings.MEDIA_ROOT)


def _prune_old_previews() -> None:
    """Delete the oldest preview clips when the total exceeds PREVIEW_MAX_COUNT."""
    qs = (
        Video.objects
        .filter(processing_done=True, preview_clip__isnull=False)
        .exclude(preview_clip='')
        .order_by('created_at')
    )
    for old in qs[:max(qs.count() - PREVIEW_MAX_COUNT, 0)]:
        old.preview_clip.delete(save=False)
        old.preview_clip = None
        old.save(update_fields=['preview_clip'])


@django_rq.job('videos')
def process_video(video_id: int) -> None:
    """Background task: convert an uploaded video to HLS, generate thumbnail and preview clip."""
    video = Video.objects.get(pk=video_id)
    video.hls_path = _build_hls(video_id, video.video_file.path)
    video.thumbnail = _build_thumbnail(video_id, video.video_file.path)
    if not video.preview_clip:
        video.preview_clip = _build_preview_clip(video_id, video.video_file.path)
    video.processing_done = True
    video.save()
    _prune_old_previews()
