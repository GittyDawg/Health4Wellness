from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from .models import food, Meal
from django.db.models import Q
# Create your views here.


def index(request):
    food_list = food.objects.order_by('calories')[:15]
    output = ', '.join([q.name for q in food_list])
    return render(request, 'food/index.html', {'food_list': food_list})


def detail(request, name):
    queryset = food.objects.filter(name__startswith=name)
    this_food = get_object_or_404(queryset)

    meal = Meal()

    return render(request, 'food/details.html', {'food': this_food, 'meal': meal})


def compare(request):
    try:
        this_food1 = food.objects.get(name=request.GET.get(
            'q'))
        this_food2 = food.objects.get(name=request.GET.get(
            'q2'))
    except food.DoesNotExist:
        this_food1 = None
        this_food2 = None
    context = {'food1': this_food1, 'food2': this_food2}
    return render(request, 'food/compare.html', context)


def compare_search(request):
    return render(request, 'food/compare_search.html')


def search(request):
    query = request.GET.get('q')
    object_list = food.objects.filter(
        Q(name__icontains=query) | Q(ingredients__icontains=query)
    )
    return render(request, 'food/search.html', {'foods': object_list})


def added_food(request, meal, name):
    # queryset = Meal.objects.filter(name__startswith=meal)
    # this_meal = get_object_or_404(queryset) #
    this_meal = Meal.get_meal()
    this_meal.add(name)

    template = 'food/added_food.html'
    context = {'meal': this_meal}
    return render(request, template, context)