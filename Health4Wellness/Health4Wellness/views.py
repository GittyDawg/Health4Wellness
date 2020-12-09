from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.db.models import Q

# Create your views here.


def index(request):
    return render(request, 'Health4Wellness/index.html')
