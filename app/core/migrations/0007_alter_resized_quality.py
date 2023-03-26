# Generated by Django 4.1.7 on 2023-03-25 23:13

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_resized_quality'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resized',
            name='quality',
            field=models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(100)]),
        ),
    ]
