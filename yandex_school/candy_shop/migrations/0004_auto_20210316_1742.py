# Generated by Django 3.1.7 on 2021-03-16 11:42

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('candy_shop', '0003_auto_20210316_1348'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='is_completed',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
        migrations.AlterField(
            model_name='courier',
            name='assign_time',
            field=models.DateTimeField(blank=True, default=datetime.datetime(1900, 1, 31, 20, 0)),
        ),
        migrations.AlterField(
            model_name='courier',
            name='complete_times',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='courier',
            name='last_time',
            field=models.DateTimeField(blank=True, default=datetime.datetime(1900, 1, 31, 20, 0)),
        ),
        migrations.AlterField(
            model_name='courier',
            name='orders',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='order',
            name='complete_time',
            field=models.DateTimeField(blank=True, default=datetime.datetime(1900, 1, 31, 20, 0)),
        ),
        migrations.AlterField(
            model_name='order',
            name='last_time',
            field=models.DateTimeField(blank=True, default=datetime.datetime(1900, 1, 31, 20, 0)),
        ),
    ]
