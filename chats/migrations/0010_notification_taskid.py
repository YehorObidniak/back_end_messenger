# Generated by Django 4.2.4 on 2023-08-15 21:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chats', '0009_notification_previousid'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='taskId',
            field=models.IntegerField(null=True),
        ),
    ]
