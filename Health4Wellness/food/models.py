from django.db import models

# Create your models here.


class food(models.Model):
    name = models.CharField(max_length=200, default='food')
    carbohydrates = models.IntegerField(default=0)
    fat = models.IntegerField(default=0)
    protein = models.IntegerField(default=0)
    calories = models.IntegerField(default=0)
    ingredients = models.CharField(max_length=200)

    #allows a many-to-one relationship for food to meal
    # meal = models.ForeignKey(Meal, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Meal(models.Model):
    name = "My Meal!"
    contains = []

    def __init__(self):
        Meal.current_meal = self

    @staticmethod
    def get_meal():
        return Meal.current_meal

    def __str__(self):
        return self.name
    
    def add(self, food):
        self.contains.append(food)
        return True

    # name = models.CharField(max_length=200, default="meal")
    # carbohydrates = #sum of carbs
    # fat = 
    # protein = 
    # calories = 
    # ingredients = 
