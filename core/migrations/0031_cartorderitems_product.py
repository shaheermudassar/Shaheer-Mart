# Generated by Django 4.2 on 2023-05-08 22:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0030_notification'),
    ]

    operations = [
        migrations.AddField(
            model_name='cartorderitems',
            name='product',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.product'),
        ),
    ]