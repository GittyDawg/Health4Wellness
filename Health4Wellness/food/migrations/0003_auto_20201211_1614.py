# Generated by Django 3.1.4 on 2020-12-11 21:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_auto_20201211_1614'),
        ('food', '0002_food_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Meal',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(max_length=100)),
                ('date_eaten', models.DateField(null=True)),
                ('dietlog', models.ManyToManyField(to='accounts.Dietlog')),
            ],
        ),
        migrations.AddField(
            model_name='food',
            name='meals',
            field=models.ManyToManyField(to='food.Meal'),
        ),
    ]
