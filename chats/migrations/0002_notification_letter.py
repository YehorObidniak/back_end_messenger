# Generated by Django 4.2.4 on 2023-08-01 18:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chats', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='letter',
            field=models.CharField(max_length=1024, null=True),
        ),
    ]
