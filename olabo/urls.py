from django.urls import path
from . import views

app_name = 'olabo'

urlpatterns = [
    path('', views.index, name='olabo_index'),
    path('product/<int:pk>/', views.olabo_detail, name='olabo_detail'),
    path('start-job/', views.start_olabo_job, name='start_job'),    

]
