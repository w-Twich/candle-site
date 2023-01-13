from django.urls import include, path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'candletime'
urlpatterns = [
    path('', views.index, name='index'),
    path('<int:pk>/', views.candle, name='candle'),
    path('<int:pk>/new-candle/', views.new_candle, name='new_candle'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='candletime/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='candletime/logout.html'), name='logout'),
]