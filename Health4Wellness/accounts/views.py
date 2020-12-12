from django.contrib.auth.models import User, Permission, Group
from django.contrib.auth import login
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required, permission_required
from .models import Dietlog

import datetime
import re

def check_user(string): 
    regex = re.compile('[@_!#$%^&*()<>?/\|}{~:.,; ]')      
    if (regex.search(string) == None and len(string) > 0): 
        return True 
    else: 
        return False

def check_password(string):
    regex = re.compile('[@_#$%^&*()<>?/\|}{~ ]')      
    if (regex.search(string) == None and len(string) > 7): 
        return True 
    else: 
        return False

def show_profile(request, user_id):
    return render(request, 'accounts/profile.html')

#TODO: fix this
def update_profile(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    user.email = request.POST.get('Email', '')
    user.first_name = request.POST.get('FName', '')
    user.last_name = request.POST.get('LName', '')

    user.save()
    #print(request.POST) #debug
    user.profile.bio = request.POST.get('Bio', '')
    user.profile.location = request.POST.get('Location', '')
    user.profile.birth_date = datetime.datetime.strptime(str(request.POST.get('Birthdate', timezone.now()))[:10], '%Y-%m-%d')
    user.profile.goals = request.POST.get('Goals', '')
    user.profile.weight = float(request.POST.get('Weight', '-1.0'))
    user.profile.gender = request.POST.get('Gender', '')
    #user.profile.coach = request.POST['Coach']
    user.profile.save()

    return show_profile(request, user)

def register(request):
    if request.method == "POST":
        username = request.POST.get('Username', '').strip()
        first = request.POST.get('FName', '').strip()
        last = request.POST.get('LName', '').strip()
        email = request.POST.get('Email', '')
        password1 = request.POST.get('Password1', '')
        password2 = request.POST.get('Password2', '')
        error_message = []

        if not check_user(username):
            username = ''
            error_message.append('Username invalid. Make sure it contains no special characters.')
        elif User.objects.filter(username=username):
            username = ''
            error_message.append('Username invalid. Not unique.')
        
        if not check_password(password1) or not check_password(password2):
            password1 = ''
            password2 = ''
            error_message.append('Password invalid. Make sure it contains no special characters and is at least 8 characters long.')
        elif password1 != password2:
            password1 = ''
            password2 = ''
            error_message.append('Passwords do not match!')

        #Right now, no checking on email or first and last name, only thing we may want is email to be unique. But even then...

        if len(error_message) > 0:
            #Failure
            return render(request, 'accounts/register.html', {
                'error_message': error_message,
                'username': username,
                'fname': first,
                'lname': last,
                'email': email,
                'password1': password1,
                'password2': password2,
                })
        else:
            #Success
            user = User.objects.create_user(username, email, password1)
            user.first_name = first
            user.last_name = last
            user.save()
            registered_group = Group.objects.get(name='Registered User') 
            registered_group.user_set.add(user)
            registered_group.save()
            login(request, user)
            return HttpResponseRedirect(reverse('accounts:profile', args=(user.id,)))
    else:
        return render(request, 'accounts/register.html')

@login_required
def dietlog(request, user_id, log_id):
    dietlog = get_object_or_404(Dietlog, pk=log_id)
    user = get_object_or_404(Dietlog, pk=log_id)
    if request.method == "POST":
        
        return render(request, 'accounts/dietlog.html', {'log':dietlog})
    else:
        #probably a get method
        return render(request, 'accounts/dietlog.html', {'log':dietlog})

    