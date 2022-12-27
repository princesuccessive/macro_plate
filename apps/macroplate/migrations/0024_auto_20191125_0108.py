# Generated by Django 2.2.4 on 2019-11-25 01:08

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('macroplate', '0023_auto_20191122_0603'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='meal',
            name='best_buy',
        ),
        migrations.AlterField(
            model_name='customer',
            name='cold_brew',
            field=models.SmallIntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(30)], verbose_name='Cold Brew?'),
        ),
        migrations.AlterField(
            model_name='customer',
            name='cold_pressed_juice',
            field=models.PositiveSmallIntegerField(choices=[(0, 'No juice'), (4, '4/week'), (5, '5/week'), (6, '6/week'), (7, '7/week'), (8, '8/week'), (9, '9/week')], default=0, verbose_name='Cold Pressed Juice?'),
        ),
        migrations.AlterField(
            model_name='customer',
            name='protein_snacks',
            field=models.PositiveSmallIntegerField(choices=[(0, 'No snacks'), (1, '1/day'), (2, '2/day'), (3, '3/day')], default=0, verbose_name='Protein snacks'),
        ),
    ]