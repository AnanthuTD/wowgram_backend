# Generated by Django 4.2 on 2023-05-15 06:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='usercommunication',
            options={'ordering': ['updated_at']},
        ),
    ]
