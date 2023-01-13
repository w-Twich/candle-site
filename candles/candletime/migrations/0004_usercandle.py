# Generated by Django 4.1.5 on 2023-01-13 10:59

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('candletime', '0003_alter_candle_detail_extinguish_time'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserCandle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('candle', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='candletime.candle')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]