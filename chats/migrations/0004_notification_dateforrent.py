# Generated by Django 4.2.4 on 2023-08-07 17:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chats', '0003_remove_chat_users'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='dateForRent',
            field=models.CharField(max_length=50, null=True),
        ),
    ]
