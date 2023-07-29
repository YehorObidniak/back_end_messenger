import mysql.connector
from time import time

class DBManager:
    def __init__(self):
        self.conn = None
        self.cursor = None
        self.bots = {'truck_rental_bot':23}

    def renew_connection(func):
        def inner(self, *args, **kwargs):
            self.conn = mysql.connector.connect(user='yehor', password='4vRes4^9mH', host='adamserver.mysql.database.azure.com', database='messenger')
            self.cursor = self.conn.cursor()
            res = func(self, *args, **kwargs)
            self.cursor.close()
            self.conn.close()
            return res
        return inner

    @renew_connection
    def insert_message(self, tgid, from_user, text, chat_id, departmentName, typeOfMessage):
        insertion = 'INSERT INTO chats_message(tgid, from_user, text, chat_id, departmentName, typeOfMessage, time) VALUES(%s, %s, %s, %s, %s, %s, %s)'
        values = (tgid, from_user, text, chat_id, departmentName, typeOfMessage, time())
        try:
            self.cursor.execute(insertion, values)
            self.conn.commit()
        except:
            print("message was not sended")
            return

        update = 'UPDATE chats_unrecievedmessages SET unrecieved = unrecieved + %s WHERE chat_id = %s'
        values = (1, chat_id)
        try:
            self.cursor.execute(update, values)
            self.conn.commit()
        except:
            print("can't increase unrecieved messages")

    @renew_connection
    def add_tagged(self, chat_id, bot_name):
        try:
            result = tuple(self.bots[key] for key in bot_name)    
        except:
            print("can't find taged user")
            return

        update = None
        values = None

        if len(result) > 1:
            update = "UPDATE chats_unrecievedmessages un JOIN chats_users us ON un.user_id = us.id SET taged = %s WHERE chat_id = %s AND us.department_id IN (%s);"
            values = (1, chat_id, str(result))
        elif len(result) == 1:
            update = "UPDATE chats_unrecievedmessages un JOIN chats_users us ON un.user_id = us.id SET taged = %s WHERE chat_id = %s AND us.department_id = %s;"
            values = (1, chat_id, result[0])
        else:
            return

        try:
            self.cursor.execute(update, values)
            self.conn.commit()
        except:
            print("can't add tag")