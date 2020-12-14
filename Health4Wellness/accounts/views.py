from django.contrib.auth.models import User, Permission, Group
from django.contrib.auth import login, logout
from django.contrib.sessions.models import Session
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required, permission_required
from django.template.defaulttags import register
from .models import Dietlog
from food.models import Meal

import datetime
import re

@register.filter(name='lookup')
def lookup(value, arg):
    return value[arg]

def keep_session_active(request):
    request.session['last_activity'] = datetime.datetime.strftime(datetime.datetime.now(), "%d/%m/%Y %H:%M:%S")

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

@login_required
def show_profile(request, user_id):
    keep_session_active(request)
    return render(request, 'accounts/profile.html')

#TODO: fix this
@login_required
def update_profile(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    user.email = request.POST.get('Email', '')
    user.first_name = request.POST.get('FName', '')
    user.last_name = request.POST.get('LName', '')

    user.save()
    #print(request.POST) #debug
    user.profile.bio = request.POST.get('Bio', '')
    user.profile.location = request.POST.get('Location', '')
    try:
        user.profile.birth_date = datetime.datetime.strptime(str(request.POST.get('Birthdate'))[:10], '%Y-%m-%d')
    except ValueError:
        user.profile.birth_date = datetime.datetime.now()
    user.profile.goals = request.POST.get('Goals', '')
    user.profile.weight = float(request.POST.get('Weight', '-1.0'))
    user.profile.gender = request.POST.get('Gender', '')
    #user.profile.coach = request.POST['Coach']
    user.profile.save()

    if request.POST.get('create', False):
        log = Dietlog.create(user=user, name='blank_dietlog')
        log.save()
        return HttpResponseRedirect(reverse('accounts:log', args=(user.id, log.id)))

    keep_session_active(request)
    return HttpResponseRedirect(reverse('accounts:profile', args=(user.id,)))

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
            keep_session_active(request)
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
            keep_session_active(request)
            return HttpResponseRedirect(reverse('accounts:profile', args=(user.id,)))
    else:
        keep_session_active(request)
        return render(request, 'accounts/register.html')

@login_required
def dietlog(request, user_id, log_id):
    dietlog = get_object_or_404(Dietlog, pk=log_id)
    user = get_object_or_404(Dietlog, pk=log_id)

    active_meals = {}
    add_meals = []
    for meal_id in request.session.get('meal_set', []):
        meal_id = int(meal_id)
        for meal in dietlog.meal_set.all():
            if meal.id == int(meal_id):
                active_meals[meal_id] = 1
                break
        if active_meals.get(meal_id, None) == None:
            add_meals.append(Meal.objects.get(id=meal_id))

    #print(active_meals)
    #print(add_meals)

    keep_session_active(request)
    #idk why this is here lol
    if request.method == "POST":
        
        return render(request, 'accounts/dietlog.html', {'log':dietlog, 'active_meals':active_meals, 'add_meals':add_meals})
    else:
        #probably a get method
        return render(request, 'accounts/dietlog.html', {'log':dietlog, 'active_meals':active_meals, 'add_meals':add_meals})

@login_required
def update_dietlog(request, user_id, log_id):
    user = get_object_or_404(User, pk=user_id)
    log = get_object_or_404(Dietlog, pk=log_id)

    meal_set = request.session.get('meal_set', [])

    if bool(request.POST.get('delete', False)): #Dietlog was designated to be deleted
            Dietlog.objects.filter(id=log_id).delete()
            return HttpResponseRedirect(reverse('accounts:profile', args=(user.id,)))

    #activate/deactivate those already a part of the dietlog
    for meal in log.meal_set.all():
        if request.POST.get("m{}".format(meal.id), False) and not meal.id in meal_set:
            session_set = request.session.get('meal_set', [])
            if len(session_set) == 0:
                request.session['meal_set'] = [meal.id]
            else:
                request.session['meal_set'].append(meal.id)
        elif request.POST.get("m{}".format(meal.id), False):
            pass
        else:
            try:
                request.session['meal_set'].remove(meal.id)
                meal.active = False
            except ValueError:
                pass
        if request.POST.get("r{}".format(meal.id), False):
            log.meal_set.remove(meal)

    request.session.modified = True

    for meal_id in meal_set:
        if request.POST.get("a{}".format(meal_id), False):
            m = Meal.objects.get(id=meal_id)
            log.meal_set.add(m)
            m.save()
            log.save()

    log.name = request.POST.get('Logname')
    log.save()

    keep_session_active(request)
    return HttpResponseRedirect(reverse('accounts:log', args=(user.id, log_id)))

class SessionExpiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        now = datetime.datetime.now()
        last_activity = datetime.datetime.strptime(request.session.get('last_activity', datetime.datetime.strftime(now, "%d/%m/%Y %H:%M:%S")), "%d/%m/%Y %H:%M:%S")
        
        if (now - last_activity).total_seconds() > 600:
            try:
                logout(request.user)
            except:
                pass
            for meal_id in request.session.get('meal_set', []):
                meal = Meal.objects.get(id=meal_id)
                meal.active = False
                if meal.dietlog == None:
                    Meal.objects.filter(id=meal_id).delete()
        for sess in Session.objects.all():
            data = sess.get_decoded()
            last_activity = datetime.datetime.strptime(data.get('last_activity', datetime.datetime.strftime(now, "%d/%m/%Y %H:%M:%S")), "%d/%m/%Y %H:%M:%S")
            print(sess.session_key)
            print(last_activity)
            print(now)
            if (now - last_activity).total_seconds() > 600 and sess.session_key != request.session.session_key:
                for meal_id in data.get('meal_set', []):
                    meal = Meal.objects.get(id=meal_id)
                    meal.active = False
                    if meal.dietlog == None:
                        Meal.objects.filter(id=meal_id).delete()
                Session.objects.filter(session_key=sess.session_key).delete()

        response = self.get_response(request)
        return response

    