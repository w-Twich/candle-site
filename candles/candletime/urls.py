from django.urls import include, path
from . import views

app_name = 'candletime'
urlpatterns = [
    path('', views.index, name='index'),
    path('<int:pk>/', views.candle, name='candle'),
    path('<int:pk>/new-candle/', views.new_candle, name='new_candle'),
]