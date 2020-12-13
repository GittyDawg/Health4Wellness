# Generated by Django 3.1.4 on 2020-12-13 09:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_auto_20201211_1614'),
        ('food', '0004_auto_20201212_2300'),
    ]

    operations = [
        migrations.AddField(
            model_name='meal',
            name='active',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='meal',
            name='dietlog',
            field=models.ManyToManyField(null=True, to='accounts.Dietlog'),
        ),
    ]
