# Generated by Django 3.1.7 on 2021-03-20 09:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('candy_shop', '0006_courier_assign_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='courier',
            name='assign_type',
            field=models.TextField(blank=True, default=''),
        ),
    ]
