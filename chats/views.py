from django.http import JsonResponse
from .models import Chat, Message, Users, UnrecievedMessages
from django.core import serializers
from time import time
import asyncio
from django.shortcuts import redirect
from .db_manager import DBManager
from . import bot_documents, bot_sales, bot_trucks
from .bots import BOTS
import re
from django.db.models import Case, When, Value
import pymongo
from django.views.decorators.csrf import csrf_exempt
from .bitrix_methods import get_user_id_by_auth, tg_id_by_contact_id
import json
from .sql_queries import get_messages

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


    return JsonResponse(data={"chats_rel":unrecieved_messages, 'count_of_chats':count_of_chats, 'me':user})

def enter_chat(request):
    chat = request.GET.get('id')
    user = request.GET.get('user')

    messages = get_messages(chat)

    recieve = UnrecievedMessages.objects.get(chat=chat, user=user)
    recieve.unrecieved = 0
    recieve.taged = 0
    recieve.save()

    chat = Chat.objects.get(id=chat)
    users_in_chat = UnrecievedMessages.objects.filter(chat=chat).count()
    chat_name = chat.chat_name

    departments = UnrecievedMessages.objects.filter(chat=chat).values("user__department__name").distinct()
    department_names = [department['user__department__name'] for department in departments]
    dep_name = Users.objects.get(id=user).department.name

    return JsonResponse(data={'messages':messages, 'users_in_chat':users_in_chat, 'chat_name':chat_name, 'departments':department_names, 'department':dep_name})

def get_update(request):
    chat = int(request.GET.get('id'))
    old_time = int(request.GET.get('old'))
    cur_time = int(time())

    if Message.objects.filter(chat=chat).filter(time__gte=old_time).filter(time__lt=cur_time).exists():
        messages = Message.objects.filter(chat=chat).filter(time__gte=old_time).filter(time__lt=cur_time).order_by('id').all()
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

    myclient = pymongo.MongoClient("mongodb+srv://test_mongodb:123@cluster0.ev4zkwl.mongodb.net/?retryWrites=true&w=majority")
    mydb = myclient["test"]
    mycol = mydb["buffered-messages"]
    query = {str(chat): {"$exists": True}}
    result = mycol.find_one(query)
    if result:
        messages = result[str(chat)]
        messages.append(message)
        # Update the document in MongoDB to add the text to the array
        mycol.update_one({"_id": result["_id"]}, {"$set": {str(chat): messages}})
    else:
        # If chat_id does not exist, create a new document with the chat_id and text array
        mycol.insert_one({str(chat): [message]})
    myclient.close()
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
    print(-30*(count+1), -30*count)

    all_messages = Message.objects.filter(chat=request.GET.get('id')).order_by('-id').all()
    all = all_messages.count()
    print(all)

    messages = list(all_messages)[count*30:(count+1)*30]

    print(messages)

    return JsonResponse(data={'messages':serializers.serialize('json', messages)})

def get_urecieved_messages(request):
    user = request.GET.get('user')

    count_of_chats = Chat.objects.filter(users=Users.objects.get(id=user)).count()
    unrec = UnrecievedMessages.objects.filter(user=Users.objects.get(id=user)).order_by('chat__chat_name').all()
    return JsonResponse(data={'unrec':serializers.serialize('json', unrec), 'number_chats':count_of_chats})

@csrf_exempt
def bitrix(request):
    if(request.method == "POST"):
        print(request.POST)
        print(tg_id_by_contact_id(json.loads(request.POST['PLACEMENT_OPTIONS'])['ID']))
        return redirect('https://messengerwebapp.netlify.app/'+get_user_id_by_auth(request.POST['AUTH_ID']) + '/'+ tg_id_by_contact_id(json.loads(request.POST['PLACEMENT_OPTIONS'])['ID'])+'/')

