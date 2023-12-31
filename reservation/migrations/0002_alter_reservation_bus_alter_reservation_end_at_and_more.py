# Generated by Django 5.0 on 2023-12-12 15:47

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lodging', '0003_rename_star_lodgingreview_star_score'),
        ('reservation', '0001_initial'),
        ('traffic', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reservation',
            name='bus',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='reservations', to='traffic.bus'),
        ),
        migrations.AlterField(
            model_name='reservation',
            name='end_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='reservation',
            name='lodging',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='reservations', to='lodging.lodging'),
        ),
        migrations.AlterField(
            model_name='reservation',
            name='rental_car',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='reservations', to='traffic.rentalcar'),
        ),
        migrations.AlterField(
            model_name='reservation',
            name='start_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='reservation',
            name='train',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='reservations', to='traffic.train'),
        ),
    ]
