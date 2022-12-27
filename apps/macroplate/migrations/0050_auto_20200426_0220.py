# Generated by Django 2.2.4 on 2020-04-26 02:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('macroplate', '0049_auto_20200426_0217'),
    ]

    operations = [
        migrations.AlterField(
            model_name='weeklyschedule',
            name='customer',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='weekly_schedule', to='macroplate.Customer', verbose_name='Customer'),
        ),
    ]