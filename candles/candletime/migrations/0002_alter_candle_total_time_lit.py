# Generated by Django 4.1.5 on 2023-01-10 02:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('candletime', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='candle',
            name='total_time_lit',
            field=models.IntegerField(null=True),
        ),
    ]