from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from datetime import datetime, timezone
from .models import Auction, Bid
from .forms import AddAuctionForm, BidForm
from django.core.serializers import serialize
from django.contrib import messages
import pytz


def top_bid(auction):
    return auction.bid_set.all().order_by('-amount').first()


def unseen_wins(user):
    if not user.is_authenticated:
        return None
    return user.buyer.filter(end_time__lt=datetime.now(timezone.utc), sold=False).exclude(seller=user)


def seen_wins(user):
    return user.buyer.filter(end_time__lt=datetime.now(timezone.utc)).filter(sold=True)


def unread_messages(user):
    if not user.is_authenticated:
        return None
    return user.received_message.filter(seen=False).order_by('-sent_at')


def read_messages(user):
    if not user.is_authenticated:
        return None
    result = user.received_message.filter(seen=True) | user.sent_message.all()
    return result.order_by('-sent_at')


def get_unread_message_count(user):
    if not user.is_authenticated:
        return 0
    return len(unread_messages(user)) + len(unseen_wins(user))


def to_datetime(date, time):
    '''
    :param date: data extracted from datepicker input field
    :param time: data extracted from timepicker input field
    :return: python datetime object associated with given input, in UTC
    '''
    time = date + ' ' + time
    time = time.replace('/', ' ').replace(':', ' ')
    month, day, year, hour, minute = [int(item) for item in time.split()]
    return datetime(
        year=year,
        month=month,
        day=day,
        hour=hour,
        minute=minute,
        tzinfo=pytz.timezone('UTC')
    )


@login_required(login_url='/user/login/')
def add(request):
    if request.method == "POST":
        date = request.POST.get('datepicker', 'no date found')
        time = request.POST.get('timepicker', 'no time found')
        form  = AddAuctionForm(request.POST, request.FILES)

        try:
            auction = form.save()
            auction.seller = request.user
            auction.buyer = request.user
            auction.end_time = to_datetime(date, time)
            auction.save()
            messages.info(request, 'Item added.')
            return redirect('homepage')
        except Exception as e:
            messages.info(request, 'Some error occurred. Please try again.')

    context = {
        'message_cnt': get_unread_message_count(request.user)
    }
    return render(request, 'auction/add.html', context=context)


def details(request, pk):
    auction = get_object_or_404(Auction, pk=pk)

    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('login')

        form = BidForm(request.POST)
        if form.is_valid():
            bid = Bid(
                auction=auction,
                bidder=request.user,
                amount=form.cleaned_data['amount']
            )
            if datetime.now(tz=timezone.utc) <= auction.end_time and bid.amount > auction.price:
                bid.save()

                auction.buyer = request.user
                auction.price = bid.amount
                auction.save()
                messages.info(request, 'Your bid was accepted!')
            else:
                messages.info(request, 'You must bid more than the last bid.')


    allow_bidding = (auction.seller != request.user)
    try:
        allow_buying = auction in unseen_wins(request.user)
    except Exception as e:
        allow_buying = False

    context = {
        'auction': auction,
        'bid_going_on': auction.end_time > datetime.now(timezone.utc),
        'allow_bidding': allow_bidding,
        'allow_buying': allow_buying,
        'user': request.user,
        'message_cnt': get_unread_message_count(request.user)
    }

    return render(request, 'auction/details.html', context=context)


def show_upcoming(request):
    auctions = Auction.objects.filter(
        end_time__gt=datetime.now(timezone.utc)
    )
    title = 'Active Listings'

    return show_all(request, title, auctions)


def show_ended(request):
    auctions = Auction.objects.filter(
        end_time__lte=datetime.now(timezone.utc)
    )
    title = 'Ended Listings'

    return show_all(request, title, auctions)


def show_all(request, title, auctions):
    if len(auctions) == 0:
        context = { 'auctions': None }
    else:
        context = { 'auctions': auctions }
    context['title'] = title
    context['message_cnt'] = get_unread_message_count(request.user)

    return render(request, 'auction/showall.html', context=context)


@login_required(login_url='/user/login/')
def buy(request, pk):
    auction = get_object_or_404(Auction, pk=pk)
    if auction in unseen_wins(request.user):
        auction.sold = True
        auction.save()

    return redirect('show_details', pk=pk)


def search_result(request, search_text):
    keywords = [word for word in search_text.split('+') if word]
    queryset = Auction.objects.filter(pk=-1)
    for keyword in keywords:
        queryset = queryset | Auction.objects.filter(title__icontains=keyword) | Auction.objects.filter(description__icontains=keyword)
    queryset = queryset.order_by('-created_at')

    response = serialize('json', queryset)
    return JsonResponse(response, safe=False)