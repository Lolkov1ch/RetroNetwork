# Generated migration for MessageAttachment model

from django.db import migrations, models
import django.db.models.deletion
import messaging.models


class Migration(migrations.Migration):

    dependencies = [
        ('messaging', '0004_alter_message_options'),
    ]

    operations = [
        migrations.CreateModel(
            name='MessageAttachment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attachment_type', models.CharField(
                    choices=[('image', 'Image'), ('video', 'Video')],
                    db_index=True,
                    max_length=20
                )),
                ('file', models.FileField(upload_to=messaging.models.get_message_upload_path)),
                ('thumbnail', models.ImageField(
                    blank=True,
                    null=True,
                    upload_to=messaging.models.get_message_upload_path
                )),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('message', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='attachments',
                    to='messaging.message',
                    db_index=True
                )),
            ],
            options={
                'ordering': ['created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='messageattachment',
            index=models.Index(fields=['message', '-created_at'], name='messaging_m_message_idx'),
        ),
        migrations.AddIndex(
            model_name='messageattachment',
            index=models.Index(fields=['attachment_type'], name='messaging_m_attach_idx'),
        ),
    ]
