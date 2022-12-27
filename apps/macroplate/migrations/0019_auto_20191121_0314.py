# Generated by Django 2.2.4 on 2019-11-21 03:14

import django.db.models.deletion
from django.db import migrations, models


def create_default_plan(apps, schema_editor):
    PlanType = apps.get_model('macroplate', 'PlanType')
    PlanType.objects.get_or_create(
        id='default',
        name='default',
    )


class Migration(migrations.Migration):
    dependencies = [
        ('macroplate', '0018_auto_20191120_0910'),
    ]

    operations = [
        migrations.RunPython(
            create_default_plan,
            reverse_code=migrations.RunPython.noop,
        ),
        migrations.CreateModel(
            name='MealIngredient',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('quantity',
                 models.DecimalField(decimal_places=4, max_digits=19,
                                     max_length=500, verbose_name='Quantity')),
                ('ingredient',
                 models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                   to='macroplate.Ingredient',
                                   verbose_name='Ingredient')),
            ],
            options={
                'verbose_name': 'Meal Ingredient',
                'verbose_name_plural': 'Meal Ingredients',
            },
        ),
        migrations.CreateModel(
            name='MealModifier',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('mod_type', models.PositiveSmallIntegerField(
                    choices=[(0, 'NO'), (1, 'SUB'), (2, 'EXTRA')], default=0,
                    verbose_name='Modifier type')),
                ('ingredient_from',
                 models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                   related_name='mods_from',
                                   to='macroplate.Ingredient',
                                   verbose_name='Ingredient from')),
                ('ingredient_to',
                 models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                   related_name='mods_to',
                                   to='macroplate.Ingredient',
                                   verbose_name='Ingredient to')),
            ],
            options={
                'verbose_name': 'Meal Modifier',
                'verbose_name_plural': 'Meal Modifiers',
            },
        ),
        migrations.RemoveField(
            model_name='submealingredient',
            name='ingredient',
        ),
        migrations.RemoveField(
            model_name='submealingredient',
            name='sub_meal',
        ),
        migrations.AlterUniqueTogether(
            name='submealmodifier',
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name='submealmodifier',
            name='ingredient_from',
        ),
        migrations.RemoveField(
            model_name='submealmodifier',
            name='ingredient_to',
        ),
        migrations.RemoveField(
            model_name='submealmodifier',
            name='sub_meal',
        ),
        migrations.RemoveField(
            model_name='dailymenu',
            name='unique_meals',
        ),
        migrations.AddField(
            model_name='meal',
            name='best_buy',
            field=models.DateField(blank=True, null=True,
                                   verbose_name='Best buy'),
        ),
        migrations.AddField(
            model_name='meal',
            name='plan_type',
            field=models.ForeignKey(default='default',
                                    on_delete=django.db.models.deletion.CASCADE,
                                    related_name='meals',
                                    to='macroplate.PlanType'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='meal',
            name='prep_instructions',
            field=models.TextField(blank=True, max_length=500,
                                   verbose_name='Prep Instructions'),
        ),
        migrations.AlterUniqueTogether(
            name='meal',
            unique_together={('name', 'plan_type')},
        ),
        migrations.DeleteModel(
            name='SubMeal',
        ),
        migrations.DeleteModel(
            name='SubMealIngredient',
        ),
        migrations.DeleteModel(
            name='SubMealModifier',
        ),
        migrations.AddField(
            model_name='mealmodifier',
            name='meal',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='mods', to='macroplate.Meal',
                verbose_name='Meal'),
        ),
        migrations.AddField(
            model_name='mealingredient',
            name='meal',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='ingredients', to='macroplate.Meal'),
        ),
        migrations.AlterUniqueTogether(
            name='mealmodifier',
            unique_together={('meal', 'ingredient_from')},
        ),
    ]
