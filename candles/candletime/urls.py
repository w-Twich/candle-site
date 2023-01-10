from django.urls import include, path
from . import views

app_name = 'candletime'
urlpatterns = [
    path('<int:pk>/', views.candle, name='candle'),
    path('<int:pk>/new-candle/', views.new_candle, name='new_candle' )
]