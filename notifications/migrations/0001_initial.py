from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('message', 'New Message'), ('mention', 'Mention'), ('follow', 'Follow')], default='message', max_length=20)),
                ('content', models.TextField()),
                ('sender_avatar', models.URLField(blank=True)),
                ('sender_name', models.CharField(blank=True, max_length=255)),
                ('conversation_id', models.IntegerField(blank=True, null=True)),
                ('message_id', models.IntegerField(blank=True, null=True)),
                ('is_read', models.BooleanField(db_index=True, default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('sender', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sent_notifications', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='notification',
            index=models.Index(fields=['user', '-created_at'], name='notifications_notifi_user_id_7f8a9b_idx'),
        ),
        migrations.AddIndex(
            model_name='notification',
            index=models.Index(fields=['user', 'is_read', '-created_at'], name='notifications_notifi_user_id_is_read_8c9d2e_idx'),
        ),
        migrations.AddIndex(
            model_name='notification',
            index=models.Index(fields=['user'], name='notifications_notifi_user_id_db_index'),
        ),
    ]
