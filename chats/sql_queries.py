from django.db import connection

def get_messages(chat):
    query = """
    SELECT messenger.chats_message.*, messenger.chats_transcription.transcriptiontText 
    FROM messenger.chats_message
    LEFT JOIN messenger.chats_transcription ON messenger.chats_message.id = messenger.chats_transcription.message_id
    WHERE messenger.chats_message.chat_id = %s
    ORDER BY messenger.chats_message.id DESC
    LIMIT 30;
    """

    params = (chat,)
    with connection.cursor() as cursor:
        cursor.execute(query, params)
        columns = [col[0] for col in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    return results