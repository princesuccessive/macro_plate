# Generated by Django 2.2.4 on 2019-11-26 09:38

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('macroplate', '0029_merge_20191126_0907'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customer',
            old_name='cold_brew',
            new_name='coffee_count',
        ),
        migrations.RenameField(
            model_name='customer',
            old_name='cold_pressed_juice',
            new_name='juice_count',
        ),
        migrations.RenameField(
            model_name='customer',
            old_name='protein_snacks',
            new_name='snacks_count',
        ),
        migrations.RenameField(
            model_name='customer',
            old_name='notes',
            new_name='snacks_notes',
        ),

    ]
