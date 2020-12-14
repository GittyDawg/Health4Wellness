from django.db import models
from accounts.models import Dietlog
from django.db.models.signals import pre_delete, m2m_changed
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.contrib.sessions.models import Session
from django.dispatch import receiver

# Create your models here.
class Meal(models.Model):
    name = models.TextField(max_length=100)
    dietlog = models.ManyToManyField(Dietlog, null=True)
    date_eaten = models.DateField(null=True)
    active = models.BooleanField(default=True)

    class meta:
        ordering = ['name']

    @classmethod
    def create(cls, name):
        meal = cls(name=name)
        
        return meal

    def __str__(self):
        return self.name

    #This is all calculatable stuff:
    # name = models.CharField(max_length=200, default="meal")
    # carbohydrates = #sum of carbs
    # fat = 
    # protein = 
    # calories = 
    # ingredients = 

class food(models.Model):
    name = models.CharField(max_length=200, default='food')
    carbohydrates = models.IntegerField(default=0)
    fat = models.IntegerField(default=0)
    protein = models.IntegerField(default=0)
    calories = models.IntegerField(default=0)
    ingredients = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class Entry(models.Model): #an entry in a meal containing food and quantity of the food
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE)
    food = models.ForeignKey(food, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return "Entry of {} {} in meal: {}".format(self.quantity, self.food, self.meal)

    @classmethod
    def create(cls, food_, meal):
        entry = cls(food=food_, meal=meal)
        
        return entry

@receiver(m2m_changed, sender=Dietlog)
def handle_meals(sender, **kwargs):
    for meal in Meal.objects.all():
        if meal.dietlog == None and meal.active == False:
            Meal.objects.filter(id=meal.id).delete()

#def sessionend_handler(sender, **kwargs):
    #print(sender)
    #for meal_id in sender.get('meal_set', []):
        #m = Meal.objects.filter(id=meal_id)
        #m.active = False
        #if m.dietlog == None:
        #    Meal.objects.filter(id=meal_id).delete()

#pre_delete.connect(sessionend_handler, sender=Session)

def delete_meals_on_log(sender, user, request, **kwargs):
    for m_id in request.session.get('meal_set', []):
        meal = Meal.objects.get(id=m_id)
        if meal.dietlog == None:
            Meal.objects.filter(id=m_id).delete()
    request.session['meal_set'] = []

user_logged_in.connect(delete_meals_on_log)
user_logged_out.connect(delete_meals_on_log)