from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from .models import food
from django.db.models import Q
import requests
# Create your views here.


def index(request):
    food_list = food.objects.order_by('calories')[:15]
    output = ', '.join([q.name for q in food_list])
    return render(request, 'food/index.html', {'food_list': food_list})


def detail(request, name):
    queryset = food.objects.filter(name__startswith=name)
    this_food = get_object_or_404(queryset)
    return render(request, 'food/details.html', {'food': this_food})


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


def search_fda(request):
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
