# Generated by Django 3.1.4 on 2021-01-20 10:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('deliveryApp', '0006_auto_20210120_1354'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='client',
            name='Name',
        ),
    ]
