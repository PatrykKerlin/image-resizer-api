# Generated by Django 4.1.7 on 2023-03-26 12:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_rename_resized_resized_resized_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resized',
            name='image',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='core.image'),
        ),
    ]