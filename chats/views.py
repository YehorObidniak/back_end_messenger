from django.http import JsonResponse
from .models import Chat, Message, Users, UnrecievedMessages
from django.core import serializers
from time import time
import asyncio
from django.shortcuts import render
from .db_manager import DBManager
from . import bot_documents, bot_sales, bot_trucks
from .bots import BOTS
import re
from django.db.models import F, Case, When, Value
from django.db import connection

# Create your views here.
def index(request, user):
    custom_order = {
        'accident': 1,
        'landing': 2,
        'change': 3,
        'return': 4,
        'problems' : 5
    }

    count_of_chats = UnrecievedMessages.objects.filter(user=Users.objects.get(id=user)).count()
    unrecieved_messages = list(UnrecievedMessages.objects.select_related('chat').filter(user_id=user).order_by(
        Case(
        *[When(folder=folder, then=Value(rank)) for folder, rank in custom_order.items()],
        default=Value(6)
    ), "chat__chat_name").values('chat', 'user', 'unrecieved', 'taged', 'folder', 'chat__chat_name', 'chat__img'))


    return JsonResponse(data={"chats_rel":unrecieved_messages, 'count_of_chats':count_of_chats, 'me':user, 'department':Users.objects.get(id=user).department.name})

def enter_chat(request):
    messages = list(Message.objects.filter(chat=request.GET.get('id')).all())[-30:]

    recieve = UnrecievedMessages.objects.get(chat=request.GET.get('id'), user=request.GET.get('user'))
    recieve.unrecieved = 0
    recieve.taged = 0
    recieve.save()

    chat = Chat.objects.get(id=request.GET.get('id'))
    users_in_chat = chat.users.count()
    chat_name = chat.chat_name

    departments = chat.users.values("department__name").distinct()
    department_names = [department['department__name'] for department in departments]

    return JsonResponse(data={'messages':serializers.serialize('json', messages), 'users_in_chat':users_in_chat, 'chat_name':chat_name, 'departments':department_names})

def get_update(request):
    chat = int(request.GET.get('id'))
    old_time = int(request.GET.get('old'))
    cur_time = int(time())

    if Message.objects.filter(chat=chat).filter(time__gte=old_time).filter(time__lt=cur_time).exists():
        messages = Message.objects.filter(chat=chat).filter(time__gte=old_time).filter(time__lt=cur_time).all()
        recieve = UnrecievedMessages.objects.get(chat=request.GET.get('id'), user=request.GET.get('user'))
        recieve.unrecieved = 0
        recieve.taged = 0
        recieve.save()

        return JsonResponse(data={'old':cur_time, 'messages':serializers.serialize('json', messages)})
    return JsonResponse(data={'old':cur_time, 'messages':serializers.serialize('json', [])})

def send_message(request):
    chat=int(request.GET.get('chat'))
    user=int(request.GET.get('user'))
    message=request.GET.get('message')
    department=request.GET.get('department')
    typeOfMessage=request.GET.get('typeOfMessage')

    try:
        tgid = asyncio.run(BOTS["truck_rental_bot"].send_message(chat, message))
        db = DBManager()
        mentions = re.findall(r'@(\w+)', message)
        if mentions != 0:
            db.add_tagged(chat, mentions)
        db.insert_message(tgid, user, message, chat, department, typeOfMessage)

    except:
        print("can't send message")
        return JsonResponse(data={'response':False})
    return JsonResponse(data={'response':True})



def get_old(request):
    count = int(request.GET.get('count'))
    print(count)
    messages = list(Message.objects.filter(chat=request.GET.get('id')).all())[-30*(count+1):-30*(count)]
    return JsonResponse(data={'messages':serializers.serialize('json', messages)})

def index_chat(request, user, chat):
    return render(request, 'chats/index_chat.html', {'chat':chat, 'me':user, 'chats_ser':serializers.serialize('json', Chat.objects.filter(users=Users.objects.get(id=user)).order_by('chat_name')), 'department':Users.objects.get(id=user).department.name})

def get_urecieved_messages(request):
    user = request.GET.get('user')

    count_of_chats = Chat.objects.filter(users=Users.objects.get(id=user)).count()
    unrec = UnrecievedMessages.objects.filter(user=Users.objects.get(id=user)).order_by('chat__chat_name').all()
    return JsonResponse(data={'unrec':serializers.serialize('json', unrec), 'number_chats':count_of_chats})

def custom_sql_request(user):
    # Write your custom SQL query here
    sql_query = """
        SELECT *
        FROM chats_unrecievedmessages u
        JOIN chats_chat c ON u.chat_id = c.id
        WHERE u.user_id = %s
    """

    # Define any parameters for the SQL query
    params = [user]

    rows = None
    # Execute the custom SQL query
    with connection.cursor() as cursor:
        cursor.execute(sql_query, params)

        rows = cursor.fetchall()
    return rows