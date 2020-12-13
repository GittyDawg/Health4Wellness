from django.db import models
from accounts.models import Dietlog

# Create your models here.
class Meal(models.Model):
    name = models.TextField(max_length=100)
    dietlog = models.ManyToManyField(Dietlog)
    date_eaten = models.DateField(null=True)

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

