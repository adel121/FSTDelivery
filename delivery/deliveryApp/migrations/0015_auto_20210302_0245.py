# Generated by Django 3.1.4 on 2021-03-02 00:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('deliveryApp', '0014_reportlog'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bill',
            name='Delivery_cost',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='bill',
            name='Product_cost',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
