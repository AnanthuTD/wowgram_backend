# Generated by Django 4.2 on 2023-05-15 09:59

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0004_chats_conversations_delete_chat_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='conversations',
            name='room_id',
        ),
        migrations.AddField(
            model_name='conversations',
            name='converdation_id',
            field=models.UUIDField(default=uuid.UUID('b1d01b14-94b8-4ab3-ae3b-7868c48c0f6e'), primary_key=True, serialize=False),
        ),
    ]
