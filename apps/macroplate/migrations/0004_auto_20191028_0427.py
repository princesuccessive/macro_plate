# Generated by Django 2.2.4 on 2019-10-28 04:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('macroplate', '0003_plantype_submeal_submealingredients'),
    ]

    operations = [
        migrations.CreateModel(
            name='SubMealIngredient',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.DecimalField(blank=True, decimal_places=4, max_digits=19, max_length=500, verbose_name='Quantity')),
                ('ingredient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='macroplate.Ingredient', verbose_name='Ingredient')),
            ],
            options={
                'verbose_name': 'Sub Meal Ingredient',
                'verbose_name_plural': 'Sub Meal Ingredients',
            },
        ),
        migrations.AlterField(
            model_name='submeal',
            name='best_buy',
            field=models.DateField(blank=True, null=True, verbose_name='Best buy'),
        ),
        migrations.AlterField(
            model_name='submeal',
            name='prep_instructions',
            field=models.TextField(blank=True, max_length=500, verbose_name='Prep Instructions'),
        ),
        migrations.DeleteModel(
            name='SubMealIngredients',
        ),
        migrations.AddField(
            model_name='submealingredient',
            name='sub_meal',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='meal_ingredients', to='macroplate.SubMeal'),
        ),
    ]