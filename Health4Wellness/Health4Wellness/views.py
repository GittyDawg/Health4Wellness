from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.db.models import Q
from accounts.views import keep_session_active

# Create your views here.


def index(request):
    keep_session_active(request)
    return render(request, 'Health4Wellness/index.html')
