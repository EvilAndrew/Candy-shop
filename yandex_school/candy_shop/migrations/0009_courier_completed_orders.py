# Generated by Django 3.1.7 on 2021-03-22 03:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('candy_shop', '0008_auto_20210320_1553'),
    ]

    operations = [
        migrations.AddField(
            model_name='courier',
            name='completed_orders',
            field=models.TextField(blank=True, default=''),
        ),
    ]
