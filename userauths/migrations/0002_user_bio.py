# Generated by Django 4.2 on 2023-04-14 14:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userauths', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='bio',
            field=models.CharField(default=1, max_length=255),
            preserve_default=False,
        ),
    ]
