# Generated by Django 2.2.4 on 2020-07-03 06:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('macroplate', '0050_auto_20200426_0220'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='carbs',
            field=models.TextField(blank=True, max_length=255, verbose_name='Carbs'),
        ),
        migrations.AddField(
            model_name='customer',
            name='fat',
            field=models.TextField(blank=True, max_length=255, verbose_name='Fat'),
        ),
        migrations.AddField(
            model_name='customer',
            name='protein',
            field=models.TextField(blank=True, max_length=255, verbose_name='Protein'),
        ),
    ]
