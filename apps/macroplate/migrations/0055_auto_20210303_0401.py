# Generated by Django 2.2.4 on 2021-03-03 04:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('macroplate', '0054_auto_20201013_0501'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='plan_priority',
            field=models.CharField(choices=[('primary', 'Primary'), ('secondary', 'Secondary')], default='primary', max_length=20, verbose_name='Plan Priority'),
        ),
        migrations.AlterField(
            model_name='customer',
            name='dishes_per_day',
            field=models.PositiveSmallIntegerField(default=2, verbose_name='Plan Frequency'),
        ),
    ]
