from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.urls import reverse
from django.shortcuts import get_object_or_404, render, redirect
from .models import food, Meal, Entry
from django.db.models import Q
from accounts.views import keep_session_active
import requests
import datetime
# Create your views here.

def check_meal_owner(request, meal_id):
    owner = False
    for i in request.session.get('meal_set'):
        if i == int(meal_id):
            owner = True
    return owner

def index(request):
    food_list = food.objects.order_by('calories')[:15]
    output = ', '.join([q.name for q in food_list])
    keep_session_active(request)
    return render(request, 'food/index.html', {'food_list': food_list})
    # return render(request, 'food/index.html')


def detail(request, name):
    queryset = food.objects.filter(name__startswith=name)
    this_food = get_object_or_404(queryset)

    meal_set = request.session.get('meal_set', [])
    for i in range(len(meal_set)):
        meal_set[i] = Meal.objects.get(id=meal_set[i])
    keep_session_active(request)
    return render(request, 'food/details.html', {'food': this_food, 'meal_set': meal_set})


def compare(request):
    # try:
    #     this_food1 = food.objects.get(name=request.GET.get(
    #         'q'))
    #     this_food2 = food.objects.get(name=request.GET.get(
    #         'q2'))
    # except food.DoesNotExist:
    #     this_food1 = None
    #     this_food2 = None

    if request.GET.get('q'):
        food1x = request.GET.get('q')
        list_food1 = searchFDA(food1x)
        food1 = list_food1[0]
        # print(food1)
    else:
        food1 = None   

    if request.GET.get('q2'):
        food2x = request.GET.get('q2')
        list_food2 = searchFDA(food2x)
        food2 = list_food2[0]
    else:
        food2 = None   

    context = {'food1': food1, 'food2': food2}
    return render(request, 'food/compare.html', context)


def compare_search(request):
    keep_session_active(request)
    return render(request, 'food/compare_search.html')


def search(request):
    query = request.GET.get('q')
    object_list = food.objects.filter(
        Q(name__icontains=query) | Q(ingredients__icontains=query)
    )
    keep_session_active(request)
    return render(request, 'food/search.html', {'foods': object_list})

def update_meal(request, meal_id):
    if check_meal_owner(request, meal_id): #make sure the person making changes is in the session that owns the meal
        if bool(request.POST.get('delete', False)): #Meal was designated to be deleted
            Meal.objects.filter(id=meal_id).delete()
            request.session['meal_set'].remove(meal_id)
            request.session.modified=True
            return HttpResponseRedirect(reverse('index'))
        
        meal = Meal.objects.get(id=meal_id)
        meal.name = request.POST.get('Mealname')

        try:
            meal.date_eaten = datetime.datetime.strptime(str(request.POST.get('Eatdate'))[:10], '%Y-%m-%d')
        except ValueError:
            meal.date_eaten = datetime.datetime.now()

        for entry in meal.entry_set.all():
            quantity = int(request.POST.get("e{}".format(entry.id)))
            #print(entry)
            #print(entry.id)
            #print(quantity)
            if quantity == 0:
                Entry.objects.filter(id=entry.id).delete()
            else:
                entry.quantity = quantity
                entry.save()
        meal.save()
        keep_session_active(request)
        return HttpResponseRedirect(reverse('view_meal', args=(meal_id,)))
    else:
        #Yell at them for being hackers lol
        print("blocked {}".format(request.session.get('meal_set')))
        keep_session_active(request)
        return Http404()

def add_food_to_meal(request, food_id):
    if request.POST.get("yes") == None:
        keep_session_active(request)
        return HttpResponseRedirect(reverse('detail', args=(food.objects.get(id=food_id).name,)))

    meal_id = int(request.POST.get("yes"))
    
    meal_set = request.session.get('meal_set', [])
    f = food.objects.get(id=food_id)
    
    if len(meal_set) == 0 or meal_id == 0:
        this_meal = Meal.create("blank_meal")
        this_meal.save()

        #must create new entry for blank meal to be populated
        entry = Entry.create(f, this_meal)
        entry.save()
        if len(meal_set) == 0:
            request.session['meal_set'] = [this_meal.id]
        else:
            request.session['meal_set'].append(this_meal.id)
    else:
        if check_meal_owner(request, meal_id):
            this_meal = Meal.objects.get(id=meal_id)
            
            entry = this_meal.entry_set.filter(food=f)

            if not entry: #this food is not yet a part of the meal
                entry = Entry.create(f, this_meal)
                entry.save()
            else: #this food already has an entry in the meal
                entry.quantity += 1
                entry.save() 
        else:
            #yell at them, for being hackers lol
            print("blocked {}".format(request.session.get('meal_set')))
            keep_session_active(request)
            return Http404()
    request.session.modified = True
    
    context = {'meal': this_meal}
    keep_session_active(request)
    return HttpResponseRedirect(reverse('view_meal', args=(this_meal.id,)))

def view_meal(request, meal_id):
    keep_session_active(request)
    return render(request, 'food/meal.html', {'meal': Meal.objects.get(id=meal_id)})

def search_fda(request):
    keep_session_active(request)
    return render(request, 'food/search_fda.html')


def search_fda_list(request):
    # get request to search the fda db here
    # print top 15 items (maybe do display pages?)
    # show name and couple facts
    # click on it will bring up new full details page
    # have to copy over an html view
    
    query = request.GET.get('q')
    foodz = searchFDA(query)
    #print(foodz)
    context = {
        'foodz': foodz,
        'query': query
    }
    keep_session_active(request)
    return render(request, 'food/search_fda_list.html', context)


def searchFDA(query):
    url = 'https://api.nal.usda.gov/fdc/v1/foods/search?api_key=rpIgP2LfGafdahKmgf3PqLAbtj7fpdQZnzPMtsQg&query=' + query
    response = requests.get(url)
    foodData = response.json()
    #print(foodData['foods'][0]['lowercaseDescription'])
    foodStuffs = {}

    # return first 15 best matching results
    # abbreviated results
    
    def isitinFoods(index, attribute):
        if attribute in foodData['foods'][index]:
            return foodData['foods'][index][attribute]
        else:
            return "None"

    def isitinNutrients(index, jndex, attribute):
        if attribute in foodData['foods'][index]['foodNutrients'][jndex]:
            return foodData['foods'][index]['foodNutrients'][jndex][attribute]
        else:
            return "None"

    def getNutrients(foodItem):
        nutrients = {}
        for i in range(len(foodData['foods'][foodItem]['foodNutrients'])):
            # add nutrient properties to list of singles
            nutrients.update(
                {
                    i: 
                    {
                        "nutrientName": isitinNutrients(foodItem, i, "nutrientName"),
                        "nutrientNumber": isitinNutrients(foodItem, i, "nutrientNumber"),
                        "units": isitinNutrients(foodItem, i, "unitName"),
                        "derivedFrom": isitinNutrients(foodItem, i, "derivationDescription"),
                        "value": isitinNutrients(foodItem, i, "value")
                    }
                }
            )
        return nutrients

    for i in range(15):
        #print(foodData['foods'][i]['fdcId'])
        
        foodStuffs.update(
            {
                i:
                {
                "fdcId": isitinFoods(i, 'fdcId'),
                "name": isitinFoods(i, 'lowercaseDescription'),
                "brandOwner": isitinFoods(i, "brandOwner"),
                "ingredients": isitinFoods(i, "ingredients"),
                #for every nutrient in foodItem
                "nutrients": getNutrients(i)
                }
            } 
        )

    # abbrv. list, / cleaned up one.
    return foodStuffs


# use specific fda id
def search_fda_details(request):
    # returns foodz[i]
    query = request.GET.get('q')
    foodz = searchFDAbyID(query)
    #print(foodz)
    context = {
        'foodz': foodz,
        'query': query
    }
    keep_session_active(request)
    return render(request, 'food/search_fda_details.html', context)


def searchFDAbyID(query):
    # note food/ not foods/
    url = 'https://api.nal.usda.gov/fdc/v1/food/' + query + '?api_key=rpIgP2LfGafdahKmgf3PqLAbtj7fpdQZnzPMtsQg'
    response = requests.get(url)
    foodData = response.json()
    foodStuffs = {}
    
    # double stack down for possible other listings
    def isitinFoods(attribute):
        if attribute in foodData:
            return foodData[attribute]
        else:
            return "None"

    def isitinNutrients(index, attribute):
        if attribute in foodData['foodNutrients'][index]['nutrient']:
            return foodData['foodNutrients'][index]['nutrient'][attribute]
        else:
            return "None"

    def isitinDerived(index, attribute):
        if "foodNutrientDerivation" in foodData['foodNutrients'][index]:
            if attribute in foodData['foodNutrients'][index]["foodNutrientDerivation"]:
                return foodData['foodNutrients'][index]["foodNutrientDerivation"][attribute]
            else:
                return "None"
        else:
            return "None"

    def isitAmount(index, attribute):
        if attribute in foodData['foodNutrients'][index]:
            return foodData['foodNutrients'][index][attribute]
        else:
            return "None"

    def getNutrients():
        nutrients = {}
        
        for i in range(len(foodData["foodNutrients"])):
            # add nutrient properties to list of singles
            nutrients.update(
                {
                    i: 
                    {
                        "nutrientName": isitinNutrients(i, "name"),
                        "nutrientNumber": isitinNutrients(i, "number"),
                        "amount": isitAmount(i, "amount"),
                        "units": isitinNutrients(i, "unitName"),
                        "derivedFrom": isitinDerived(i, "description")
                    }
                }
            )
        return nutrients

    foodStuffs.update(
        {
            '0' :
            {
            "fdcId": isitinFoods('fdcId'),
            "name": str.lower(isitinFoods('description')),
            "brandOwner": isitinFoods("brandOwner"),
            "ingredients": isitinFoods("ingredients"),
            #for every nutrient in foodItem
            "nutrients": getNutrients()
            },
            'nutrientsLength' : len(foodData["foodNutrients"])
        } 
    )
    
    return foodStuffs
