from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from .models import food


# Create your views here.


def index(request):
    food_list = food.objects.order_by('calories')[:5]
    output = ', '.join([q.name for q in food_list])
    return render(request, 'food/index.html', {'food_list': food_list})


def detail(request, name):
    queryset = food.objects.filter(name__startswith=name)
    this_food = get_object_or_404(queryset)
    return render(request, 'food/details.html', {'food': this_food})


def compare(request, name1, name2):
    food1 = get_object_or_404(food, name=name1)
    food2 = get_object_or_404(food, name=name2)
    context = {'food1': food1, 'food2': food2}
    return render(request, 'food/compare.html', context)


def compare_search(request):
    return render(request, 'food/compare_search.html')
