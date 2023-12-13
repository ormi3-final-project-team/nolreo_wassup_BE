# Generated by Django 5.0 on 2023-12-13 22:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lodging', '0004_lodging_price'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='lodging',
            name='price',
        ),
        migrations.AddField(
            model_name='roomtype',
            name='price',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]