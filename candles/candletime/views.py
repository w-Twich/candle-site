from django.shortcuts import render, redirect
from .models import Candle, Candle_detail
from .forms import NewCandleForm, CandleForm
from django.urls import reverse
from django.utils import timezone
from django.db.models import F, Sum


# Create your views here.
def candle(request, pk):
    # Get the current candle status
    try:
        candle = Candle.objects.get(pk=pk)
    except Candle.DoesNotExist:
        response = redirect('new-candle/')
        return response
    candle_detail = Candle_detail.objects.filter(candle=pk).annotate(time_lit = F('extinguish_time') - F('light_time'))

    total_burn_time = candle_detail.aggregate(Sum('time_lit'))['time_lit__sum']

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
            return redirect(reverse('candletime:candle', kwargs={'pk':pk}), {'candle_detail':candle_detail, 'burn_time':total_burn_time})
    else:
        return render(request, 'candletime/update_candle.html', {'candle': candle, 'pk':pk, 'candle_detail':candle_detail, 'burn_time':total_burn_time})

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

