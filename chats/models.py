from django.db import models
from time import time

class Department(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=64, unique=True)
    botName = models.CharField(max_length=65, null=True)

class Users(models.Model):
    id = models.CharField(max_length=64, primary_key=True)
    tgid = models.CharField(max_length=64, null=True)
    name = models.CharField(max_length=64)
    password = models.CharField(max_length=64)
    email = models.EmailField(max_length=64)
    isManager = models.BooleanField(default=False)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True)

class Chat(models.Model):
    id = models.BigIntegerField(primary_key=True)
    chat_name = models.CharField(max_length=128, null=True)
    lastTimeInteracted = models.IntegerField(null=True)
    img = models.TextField(null=True)
    tgMembers = models.JSONField(null=True)

class UnrecievedMessages(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, default=942368094)
    unrecieved = models.IntegerField(default=0)
    taged = models.BooleanField(default=False)
    folder = models.CharField(max_length=100, null=True)

    class Meta:
        unique_together = ('user', 'chat',)

class Message(models.Model):
    PHOTO = "photo"
    TEXT = "text"
    AUDIO = "audio"
    VIDEO = "video"
    DOCUMENT = "document"
    TAG = "tag"
    TYPE_OF_MESSAGE_CHOICES=[
        (PHOTO, "photo"),
        (TEXT, "text"),
        (AUDIO, "audio"),
        (VIDEO, "video"),
        (DOCUMENT,"document"),
        (TAG, "tag"),
    ]

    id = models.AutoField(primary_key=True)
    tgid = models.IntegerField(null=True)
    from_user = models.CharField(max_length=64)
    departmentName = models.CharField(max_length=64, null=True)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    text = models.TextField(null=True, db_collation='utf8mb4_bin')
    typeOfMessage = models.CharField(max_length=25, choices=TYPE_OF_MESSAGE_CHOICES, default=TEXT)
    time =models.CharField(max_length=100)

class Transcription(models.Model):
    id = models.AutoField(primary_key=True)
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    transcriptiontText = models.TextField()

class Issue(models.Model):
    id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=64)
    description = models.TextField()
    priority = models.IntegerField()
    responsiblePerson = models.ForeignKey(Users, on_delete=models.PROTECT, null=True)
    status = models.CharField(max_length=64)
    department = models.CharField(max_length=64)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, null=True)
    active = models.BooleanField(default=True)

class NotificationTypes(models.Model):
    name = models.CharField(max_length=100, unique=True)

class Notification(models.Model):
    timeToSendNext = models.IntegerField()
    text = models.TextField()
    bitrixId = models.IntegerField()
    typeId = models.IntegerField(default=1)
    notificatedCount = models.IntegerField(default=0)
    sendInterval = models.IntegerField(default=0)
    active = models.BooleanField(default=False)
    section = models.CharField(null=True, max_length=128)
    letter = models.CharField(max_length=1024, null=True)
    dateForRent = models.CharField(max_length=50, null=True)
    previousId = models.CharField(max_length=64, null=True)
    taskId = models.IntegerField(null=True)