# Generated by Django 2.2.4 on 2019-11-22 03:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('macroplate', '0022_auto_20191121_0635'),
    ]

    operations = [
        migrations.AddField(
            model_name='dailyschedule',
            name='is_modified',
            field=models.BooleanField(default=False, verbose_name='Is Modified'),
        ),
        migrations.AddField(
            model_name='weeklyschedule',
            name='is_modified',
            field=models.BooleanField(default=False, verbose_name='Is Modified'),
        ),
    ]
