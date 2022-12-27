# Generated by Django 2.2.4 on 2019-12-04 03:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('macroplate', '0035_auto_20191128_0341'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredient',
            name='conversion_raw',
            field=models.DecimalField(decimal_places=4, default=1, help_text='Used only for protein', max_digits=19, max_length=500, verbose_name='Conversion Raw'),
        ),
        migrations.AlterField(
            model_name='ingredient',
            name='count',
            field=models.BooleanField(default=False, help_text='Used only for protein', verbose_name='Count?'),
        ),
    ]
