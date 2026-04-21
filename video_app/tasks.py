import os
import django_rq
from django.conf import settings
from video_app.models import Video
from video_app.utils import convert_to_hls, generate_thumbnail


@django_rq.job
def process_video(video_id: int):
    video = Video.objects.get(pk=video_id)
    video_path = video.video_file.path

    # HLS output directory: media/videos/hls/<video_id>/
    hls_dir = os.path.join(settings.MEDIA_ROOT, 'videos', 'hls', str(video_id))
    master_path = convert_to_hls(video_path, hls_dir)

    # Store relative path from MEDIA_ROOT
    video.hls_path = os.path.relpath(master_path, settings.MEDIA_ROOT)

    # Thumbnail: media/videos/thumbnails/<video_id>.jpg
    thumbnail_path = os.path.join(settings.MEDIA_ROOT, 'videos', 'thumbnails', f'{video_id}.jpg')
    generate_thumbnail(video_path, thumbnail_path)
    video.thumbnail = os.path.relpath(thumbnail_path, settings.MEDIA_ROOT)

    video.processing_done = True
    video.save()
