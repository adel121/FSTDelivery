# Generated by Django 3.1.4 on 2021-01-01 08:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('deliveryApp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='bill',
            name='Date_In',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Date'),
        ),
    ]
