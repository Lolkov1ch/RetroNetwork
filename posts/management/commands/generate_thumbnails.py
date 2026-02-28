from django.core.management.base import BaseCommand
from posts.models import Post
from posts.thumbnail_utils import generate_post_thumbnail


class Command(BaseCommand):
    help = 'Generate thumbnails and collages for all posts'

    def handle(self, *args, **options):
        posts = Post.objects.all()
        total = posts.count()
        
        for idx, post in enumerate(posts, 1):
            try:
                generate_post_thumbnail(post)
                self.stdout.write(
                    self.style.SUCCESS(f'[{idx}/{total}] Generated thumbnail for post {post.id}: {post.title}')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'[{idx}/{total}] Error generating thumbnail for post {post.id}: {str(e)}')
                )
        
        self.stdout.write(self.style.SUCCESS('Successfully completed thumbnail generation'))
