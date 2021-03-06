# Generated by Django 3.1.4 on 2021-01-21 12:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('deliveryApp', '0010_auto_20210120_1619'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bill',
            name='Date',
            field=models.DateTimeField(verbose_name='Processing Date'),
        ),
        migrations.AlterField(
            model_name='bill',
            name='Status',
            field=models.CharField(choices=[('paid', 'PAID'), ('pending', 'PENDING'), ('sent', 'SENT'), ('refunded', 'REFUNDED')], default='pending', max_length=99),
        ),
    ]
