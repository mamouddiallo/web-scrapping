from django.urls import path
from . import views

app_name = 'house'

urlpatterns = [
    path('', views.house_index, name='house_index'),
    # path('scrape/', views.scrape_books, name='scrape_books'),
    # path('start/', views.start, name='start_scrape'), 
    # path('books/<int:pk>/', views.book_detail, name='book_detail'),
]
