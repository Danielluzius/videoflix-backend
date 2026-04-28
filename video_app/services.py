from video_app.models import Video


def get_all_videos():
    """Return all fully processed videos ordered by creation date descending."""
    return Video.objects.filter(processing_done=True).order_by('-created_at')


def get_video_by_id(video_id: int):
    """Return a single fully processed video by ID, or None if not found."""
    return Video.objects.filter(pk=video_id, processing_done=True).first()
