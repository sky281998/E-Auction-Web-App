from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from .forms import RegistrationForm, DateForm, MessageForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Message
from itertools import chain
from auction.views import (
    read_messages,
    unread_messages,
    seen_wins,
    unseen_wins,
    get_unread_message_count
)



def register_view(request):
    # a user should not be able to register for a new account while being logged in
    if request.user.is_authenticated:
        return HttpResponse("First logout")

    if request.method == "POST":

        date_form = DateForm(request.POST)
        if not date_form.is_valid():
            messages.info(request, "Please enter a valid date.")
            return render(request, 'user/register.html', context={'user': request.user})

        # checking whether the passwords match
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')
        if password1 != password2:
            messages.info(request, "Your passwords don't match.")
            return render(request, 'user/register.html', context={'user': request.user})

        data = {
            'username':request.POST.get('email', ''),
            'first_name': request.POST.get('name', ''),
            'email': request.POST.get('email', ''),
            'password': password1
        }

        form = RegistrationForm(data)
        if form.is_valid():
            user = form.save()
            user.set_password(request.POST.get('password1', ''))
            user.profile.birthday = date_form.cleaned_data['datepicker']
            print(date_form.cleaned_data['datepicker'])
            user.save()
            print(user.profile.birthday)

            login(request, user)
            return redirect('homepage')
        else:
            messages.info(request, "The email is already registered. Please login or reset password.")
            context = {
                'user': request.user
            }
            render(request, 'user/login.html')

    return render(request, 'user/register.html', context={'user': request.user})


def login_view(request):
    if request.method == "POST":
        email = request.POST.get('email', '')
        password = request.POST.get('password', '')
        user = authenticate(username=email, password=password)
        if user:
            login(request, user)
        else:
            messages.info(request, "The email/password is not correct. Please try again.")

    if request.user.is_authenticated:
        return redirect('homepage')
    return render(request, 'user/login.html', context={'user': request.user})


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


@login_required(login_url='/user/login/')
def message_view(request):
    user = request.user
    context = {
        'seen_wins': seen_wins(user),
        'unseen_wins': unseen_wins(user),
        'unseen_wins_len': len(unseen_wins(user)),
        'unread_messages': unread_messages(user),
        'unread_messages_len': len(unread_messages(user)),
        'read_messages': read_messages(user),
        'message_cnt': get_unread_message_count(request.user)
    }

    return render(request, 'user/read_message.html', context=context)


@login_required(login_url='/user/login/')
def write_to(request, pk):
    sender = request.user
    receiver = get_object_or_404(User, pk=pk)

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            Message(
                message=form.cleaned_data['message'],
                sender=sender,
                receiver=receiver
            ).save()

    messages_to = Message.objects.filter(sender=sender, receiver=receiver)
    messages_from = Message.objects.filter(sender=receiver, receiver=sender)
    for message in unread_messages(sender):
        message.seen = True
        message.save()

    messages = sorted(
        chain(messages_to, messages_from),
        key=lambda instance: instance.sent_at
    )
    context = {
        'user': sender,
        'to_user': receiver,
        'all_messages': messages,
        'message_cnt': get_unread_message_count(sender)
    }

    return render(request, 'user/message_with.html', context=context)