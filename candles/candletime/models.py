from django.db import models

# Create your models here.

class Candle(models.Model):
    candle_name = models.CharField(max_length=20)
    status = models.BooleanField()
    total_time_lit = models.IntegerField(null=True)

    def __str__(self):
        return self.candle_name

class Candle_detail(models.Model):
    candle = models.ForeignKey(Candle, on_delete=models.CASCADE)
    light_time = models.DateTimeField()
    extinguish_time = models.DateTimeField(null=True)

    def __str__(self):
        return str(self.candle)