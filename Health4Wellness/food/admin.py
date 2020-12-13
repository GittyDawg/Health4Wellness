
# Register your models here.
from django.contrib import admin

from .models import food, Meal

admin.site.register(food)
admin.site.register(Meal)
