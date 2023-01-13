from django.contrib import admin
from .models import Candle, Candle_detail, UserCandle

# Register your models here.
admin.site.register(Candle)
admin.site.register(Candle_detail)
admin.site.register(UserCandle)