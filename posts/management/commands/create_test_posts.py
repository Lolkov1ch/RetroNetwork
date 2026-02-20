from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from posts.models import Post
from attachments.models import Media
from django.contrib.contenttypes.models import ContentType
from django.core.files.base import ContentFile
from PIL import Image
import io
import random

User = get_user_model()


class Command(BaseCommand):
    help = 'Create test posts for development'

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=40, help='Number of posts to create')

    def handle(self, *args, **options):
        count = options['count']
    
        users = []
        for i in range(5):
            user, created = User.objects.get_or_create(
                username=f'testuser{i}',
                defaults={
                    'email': f'testuser{i}@test.com',
                    'handle': f'test_user_{i}'
                }
            )
            users.append(user)
        
        if not users:
            self.stdout.write(self.style.ERROR('No users available'))
            return

        titles = [
            'Beautiful Sunset at the Beach',
            'Morning Coffee and Views',
            'Mountain Adventure',
            'Urban Photography',
            'Nature Walk',
            'Street Art Discovery',
            'Local Food Delights',
            'Travel Memories',
            'Architecture Appreciation',
            'Wildlife Encounter',
            'Moments Captured',
            'Exploring Hidden Gems',
            'Weekend Getaway',
            'Creative Inspiration',
            'Sunset Colors',
            'Urban Exploration',
            'Nature Photography',
            'Food Photography',
            'Travel Journal',
            'Photography Tips',
        ]
        
        descriptions = [
            'Amazing view today!',
            'Just captured this incredible moment.',
            'Nature never ceases to amaze me.',
            'Love exploring new places.',
            'Beautiful day for photography.',
            'Found this gem while traveling.',
            'The colors are incredible!',
            'Can\'t believe how perfect this was.',
            'Worth the trip.',
            'Pure magic.',
            'Simply breathtaking.',
            'My happy place.',
            'Always worth it.',
            'Visual poetry.',
            'Dreams do come true.',
            'This view hits different.',
            'Chasing beauty.',
            'Captured in a moment.',
            'Timeless memories.',
            'Absolutely stunning.',
        ]
        
        for i in range(count):
            user = random.choice(users)

            title = f"{random.choice(titles)} #{i+1}"
            description = random.choice(descriptions)
            
            post = Post.objects.create(
                title=title,
                description=description,
                author=user
            )

            num_images = random.randint(1, 3)
            for j in range(num_images):
                img = Image.new(
                    'RGB',
                    (800, 600),
                    color=(
                        random.randint(50, 255),
                        random.randint(50, 255),
                        random.randint(50, 255)
                    )
                )
                
                img_io = io.BytesIO()
                img.save(img_io, format='JPEG', quality=85)
                img_io.seek(0)
            
                Media.objects.create(
                    user=user,
                    file=ContentFile(img_io.read(), name=f'test_post_{post.id}_image_{j}.jpg'),
                    content_type=ContentType.objects.get_for_model(Post),
                    object_id=post.id
                )
            
            self.stdout.write(
                self.style.SUCCESS(f'Created post {i+1}/{count}: {title}')
            )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {count} test posts')
        )
