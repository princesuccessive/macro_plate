# Generated by Django 2.2.4 on 2019-11-15 09:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('macroplate', '0015_auto_20191115_0128'),
    ]

    operations = [
        migrations.CreateModel(
            name='AssignedMenu',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('has_issues', models.BooleanField(default=False, verbose_name='Has issues')),
                ('is_approved', models.BooleanField(default=False, verbose_name='Is Approved')),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='macroplate.Customer', verbose_name='Customer')),
                ('daily_menu', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='macroplate.DailyMenu', verbose_name='Daily Menu')),
            ],
            options={
                'verbose_name': 'Assigned Menu',
                'verbose_name_plural': 'Assigned Menus',
                'unique_together': {('customer', 'daily_menu')},
            },
        ),
        migrations.CreateModel(
            name='AssignedMeal',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mods', models.CharField(blank=True, max_length=255, verbose_name='Mods')),
                ('assigned_menu', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='macroplate.AssignedMenu', verbose_name='Assigned menu')),
                ('meal', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='macroplate.Meal', verbose_name='Meal')),
            ],
            options={
                'verbose_name': 'Assigned Meal',
                'verbose_name_plural': 'Assigned Meals',
            },
        ),
    ]
