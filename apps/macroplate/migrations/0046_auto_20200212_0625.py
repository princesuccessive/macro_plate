# Generated by Django 2.2.4 on 2020-02-12 06:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('macroplate', '0045_weeklyschedule_manually_confirmed'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='plantype',
            name='name_unique',
        ),
        migrations.AlterField(
            model_name='customer',
            name='juice_count',
            field=models.PositiveSmallIntegerField(choices=[(0, 'No juice'), (1, '1/week'), (2, '2/week'), (3, '3/week'), (4, '4/week'), (5, '5/week'), (6, '6/week'), (7, '7/week'), (8, '8/week'), (9, '9/week')], default=0, verbose_name='Juice Count'),
        ),
        migrations.AlterField(
            model_name='customer',
            name='snacks_count',
            field=models.PositiveSmallIntegerField(choices=[(0, 'No snacks'), (1, '1/day'), (2, '2/day'), (3, '3/day'), (4, '4/day'), (5, '5/day'), (6, '6/day'), (7, '7/day'), (8, '8/day'), (9, '9/day')], default=0, verbose_name='Snacks Count'),
        ),
    ]
