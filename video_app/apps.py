from django.apps import AppConfig


class VideoAppConfig(AppConfig):
    name = 'video_app'
    verbose_name = 'Video Library'

    def ready(self):
        import video_app.signals  # noqa: F401

