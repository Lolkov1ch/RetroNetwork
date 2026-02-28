# Generated migration for adding friends_visibility field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_block_follow_friend'),
    ]

    operations = [
        migrations.AddField(
            model_name='privacysettings',
            name='friends_visibility',
            field=models.CharField(
                choices=[('all', 'Everyone'), ('friends', 'Friends only'), ('none', 'Only me')],
                default='all',
                help_text='Who can see your friends list',
                max_length=10
            ),
        ),
    ]
