from django.urls import path, re_path

from . import views


urlpatterns = [
    path('/<int:user>/', views.index, name="index"),
    re_path(r'^(?P<user>\d+)/(?P<chat>-?\d+)/$', views.index_chat, name="index_chat"),
    path('/enter_chat/', views.enter_chat, name='enter_chat'),
    path('/get_update/', views.get_update, name='get_update'),
    path('/send_message/', views.send_message, name='send_message'),
    path('/get_old/', views.get_old, name='get_old'),
    path('/get_unrecieved/', views.get_urecieved_messages, name='get_unrecieved')
]