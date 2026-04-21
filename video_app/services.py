from video_app.models import Video


def get_all_videos():
    return Video.objects.filter(processing_done=True).order_by('-created_at')


def get_video_by_id(video_id: int):
    return Video.objects.filter(pk=video_id, processing_done=True).first()
