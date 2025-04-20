from django.urls import path
from .import views

app_name = 'ecommerce'

urlpatterns = [
    path('', views.index, name='ecom_index'),
    path('index', views.index, name='index'),
    path('product/<int:pk>/', views.ecommerce_detail, name='ecommerce_detail'),
    path('start-job/', views.start_ecommerce_job, name='start_job'),    

]
