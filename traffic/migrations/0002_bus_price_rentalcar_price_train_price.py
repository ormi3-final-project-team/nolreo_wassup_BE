# Generated by Django 5.0 on 2023-12-13 14:00

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("traffic", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="bus",
            name="price",
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="rentalcar",
            name="price",
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="train",
            name="price",
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
