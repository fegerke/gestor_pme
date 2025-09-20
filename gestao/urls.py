from django.urls import path
from . import views

app_name = 'gestao'

urlpatterns = [
    path('api/get-item-price/', views.get_item_price, name='get_item_price'),
]