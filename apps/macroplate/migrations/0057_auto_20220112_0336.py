# Generated by Django 2.2.4 on 2022-01-12 11:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('macroplate', '0056_customer_updated_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='preferences_notes',
            field=models.TextField(blank=True, verbose_name='Preferences Notes'),
        ),
    ]
