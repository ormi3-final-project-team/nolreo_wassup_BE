# Generated by Django 5.0 on 2023-12-14 17:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lodging', '0005_remove_lodging_price_roomtype_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lodgingimage',
            name='image',
            field=models.ImageField(upload_to=''),
        ),
    ]