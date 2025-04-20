from django.urls import path
from . import views

app_name = 'quote'

urlpatterns=[
    path('',views.list_quote,name='index'),
    path('detail/<int:id>/',views.detail,name='detail'),
    path('start',views.start_job,name='start')
]