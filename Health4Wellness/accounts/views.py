from django.contrib.auth.models import User, Permission
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
import datetime

# Create your views here.
def show_profile(request, user_id):
    return render(request, 'accounts/profile.html')

#TODO: fix this
def update_profile(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    user.email = request.POST.get('Email', '') #couldn't get this one to work
    user.save()
    #print(request.POST) #debug
    user.profile.bio = request.POST.get('Bio', '')
    user.profile.location = request.POST.get('Location', '')
    #user.profile.birth_date = request.POST.get('BirthDate', timezone.now()) #need better method for this
    user.profile.goals = request.POST.get('Goals', '')
    user.profile.weight = float(request.POST.get('Weight', '-1.0'))
    user.profile.gender = request.POST.get('Gender', '')
    #user.profile.coach = request.POST['Coach']
    user.profile.save()

    return show_profile(request, user)

def register(request):
    #Not implemented

    return render(request, 'accounts/register.html')