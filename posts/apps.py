from django.apps import AppConfig


class PostsConfig(AppConfig):
    name = 'posts'

    def ready(self):
        try:
            import posts.signals
        except ImportError:
            pass
