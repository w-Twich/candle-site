from django.shortcuts import render, redirect
from .models import Candle, Candle_detail, UserCandle
from django.contrib.auth.models import User
from .forms import NewCandleForm, CandleForm, RegisterForm
from django.urls import reverse
from django.utils import timezone
from django.db.models import F, Sum, Func
from django.contrib import messages


# Create your views here.

def index(request):
    if request.user.id is not None:
        user_candles = UserCandle.objects.filter(user=request.user)
        candles = Candle.objects.filter(id__in=user_candles)
        context = {'candles':candles}
    else:
        context = {}
    
    return render(request, 'candletime/index.html', context)

def candle(request, pk):
    # Get the current candle status
    try:
        candle = Candle.objects.get(pk=pk)
    except Candle.DoesNotExist:
        response = redirect('new-candle/')
        return response
    candle_detail = Candle_detail.objects.filter(candle=pk).annotate(
        time_lit = Func(
            F('extinguish_time') - F('light_time'),
            function="ROUND"
        )
    )

    total_burn_time = candle_detail.aggregate(Sum('time_lit'))['time_lit__sum']

    context = {'candle': candle,
               'pk':pk,
               'candle_detail':candle_detail,
               'burn_time':total_burn_time,
               }

    # Toggle the candle status
    if request.method == 'POST':
        form = CandleForm(request.POST)
        if form.is_valid():
            if candle.status == False:
                candle.candle_detail_set.create(
                    candle = candle.pk,
                    light_time = timezone.now()
                )
            else:
                t = candle.candle_detail_set.latest('light_time')
                t.extinguish_time = timezone.now()
                t.save()

            candle.status = not candle.status
            candle.save()
            return redirect(reverse('candletime:candle', kwargs={'pk':pk}), context=context)
    else:
        return render(request, 'candletime/update_candle.html', context=context)

def new_candle(request, pk):
    if request.method == 'POST':
        form = NewCandleForm(request.POST)
        if form.is_valid():
            candle = Candle(
                pk = pk,
                candle_name=form.cleaned_data['candle_name'],
                status=False,
            )
            candle.save()
            return redirect(reverse('candletime:candle', kwargs={'pk':pk}))
    else:
        form = NewCandleForm()
    return render(request, 'candletime/new_candle.html', {'form': form, 'pk': pk})

# New User Registration
def register(request):
    if request.method == 'GET':
        form  = RegisterForm()
        context = {'form': form}
        return render(request, 'candletime/register.html', context)
    
    if request.method == 'POST':
        form  = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            user = form.cleaned_data.get('username')
            messages.success(request, 'Account was created for ' + user)
            return redirect('candletime:index')
        else:
            print('Form is not valid')
            messages.error(request, 'Error Processing Your Request')
            context = {'form': form}
            return render(request, 'candletime/register.html', context)

    return render(request, 'candletime/register.html', {})