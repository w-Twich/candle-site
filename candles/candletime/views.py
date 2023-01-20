from django.shortcuts import render, redirect
from .models import Candle, Candle_detail, UserCandle
from django.contrib.auth.models import User
from .forms import NewCandleForm, CandleForm, RegisterForm, LinkCandleForm, Candle_detailForm
from django.urls import reverse
from django.utils import timezone
from django.db.models import F, Sum, Func, Max
from django.contrib import messages
import qrcode
import qrcode.image.svg
from io import BytesIO


# Create your views here.

# Home page listing all candles connected to the current user
def index(request):
    if request.user.id is not None:
        user_candles = UserCandle.objects.filter(user=request.user)
        candles = user_candles.select_related('candle').annotate(date=Max('candle__candle_detail__light_time')).order_by('-date')
        context = {'candles':candles}
    else:
        context = {}
    
    return render(request, 'candletime/index.html', context)

# About page returning static html template
def about(request):
    return render(request, 'candletime/about.html')

# Contact page returning static html template
def contact(request):
    return render(request, 'candletime/contact.html')

# Main candle page
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
    ).order_by('-light_time')

    # Calculate the total time the candle has been lit by summing the candle_detial burn times
    total_burn_time = candle_detail.aggregate(Sum('time_lit'))['time_lit__sum']

    # Determine whether the logged in user is already linked to the candle
    check_candles = UserCandle.objects.filter(candle=pk, user=request.user.pk)
    if len(check_candles) == 0:
        is_connected = False
    else:
        is_connected = True

    context = {'candle': candle,
               'pk':pk,
               'candle_detail':candle_detail,
               'burn_time':total_burn_time,
               'is_connected':is_connected,
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

# Create a new candle by scanning an unused QR Code
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

# Create a new candle from the homepage (no key from new QR Code)
def new_candle_nokey(request):
    if request.method == 'POST':
        form = NewCandleForm(request.POST)
        if form.is_valid():
            candle = Candle(
                candle_name=form.cleaned_data['candle_name'],
                status=False,
            )
            candle.save()
            user_candle = UserCandle(
                user=request.user,
                candle=candle
            )
            user_candle.save()
            return redirect(reverse('candletime:candle', kwargs={'pk':candle.pk}))
    else:
        form = NewCandleForm()
    return render(request, 'candletime/new_candle_nokey.html', {'form': form})

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

# Link existing candle to logged in user
def link_user_candle(request, pk):
    # Link user to existing candle
    if request.method == 'POST':
        form = LinkCandleForm(request.POST)
        if form.is_valid():
            print("form was valid")
            check_candles = UserCandle.objects.filter(candle=pk, user=request.user.pk)
            if len(check_candles) == 0:
                print("check_candles was None")
                user_candle = UserCandle(
                user=request.user,
                candle=Candle.objects.get(pk=pk)
                )
                user_candle.save()
                return redirect(reverse('candletime:candle', kwargs={'pk':pk}))
            else:
                print("check_candles was not None")
            return redirect(reverse('candletime:candle', kwargs={'pk':pk}))
        else:
            print("form was not valid")
    else:
        return render(request, 'candletime/update_candle.html')

# Generate a QR code
def qr_gen(request, pk):
    text = print(request.build_absolute_uri()[:-7])
    context = {}
    factory = qrcode.image.svg.SvgImage
    img = qrcode.make(request.build_absolute_uri()[:-7], image_factory=factory, box_size=10)
    stream = BytesIO()
    img.save(stream)
    context["svg"] = stream.getvalue().decode()

    return render(request, "candletime/qr_gen.html", context=context)

# Update a specific candle detail
def detail_update(request, candle_pk, detail_pk):
    candle_detail = Candle_detail.objects.get(pk=detail_pk)
    candle = Candle.objects.get(pk = candle_pk)
    form = Candle_detailForm(instance=candle_detail)

    if request.method == 'POST':
        form = Candle_detailForm(request.POST, instance=candle_detail) # Prepopulate the form with an existing candle_detail
        if form.is_valid():
            # update the existing `candle_detail` in the database
            form.save()
            # redirect to the detail page of the `candle` we just updated
            return redirect('candletime:candle', candle_pk)


    return render(request, 'candletime/update_candle_detail.html', {'form':form, 'candle_pk': candle_pk})

def detail_delete(request, candle_pk, detail_pk):
    candle_detail = Candle_detail.objects.get(pk=detail_pk) # Get candle detail
    candle = Candle.objects.get(pk=candle_pk) # Get candle object


    if request.method == 'POST':
        # Delete the selected candle detail
        candle_detail.delete()
        # Redirect to candle page
        return(redirect('candletime:candle', candle_pk))
    
    return render(request, 'candletime/delete_candle_detail.html', {'candle':candle, 'candle_detail':candle_detail})
    
