# Generated by Django 4.2 on 2023-05-09 20:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0032_vendornotification'),
    ]

    operations = [
        migrations.AddField(
            model_name='vendor',
            name='avr_rating',
            field=models.FloatField(null=True),
        ),
    ]
