from django.db import models

# Create your models here.


class food(models.Model):
    carbohydrates = models.IntegerField(default=0)
    fat = models.IntegerField(default=0)
    protein = models.IntegerField(default=0)
    calories = models.IntegerField(default=0)
    ingredients = models.CharField(max_length=200)
