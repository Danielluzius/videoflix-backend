from django.db.models.signals import post_save
from django.dispatch import receiver
from video_app.models import Video


@receiver(post_save, sender=Video)
def trigger_video_processing(sender, instance, created, **kwargs):
    """Enqueue the HLS conversion task whenever a new Video instance is created."""
    if created and instance.video_file and not instance.processing_done:
        from video_app.tasks import process_video
        process_video.delay(instance.id)
