# Generated by Django 5.0 on 2023-12-12 15:40

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('account', '0001_initial'),
        ('lodging', '0003_rename_star_lodgingreview_star_score'),
        ('traffic', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Reservation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_at', models.DateTimeField()),
                ('end_at', models.DateTimeField()),
                ('type', models.CharField(max_length=100)),
                ('bus', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reservations', to='traffic.bus')),
                ('lodging', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reservations', to='lodging.lodging')),
                ('rental_car', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reservations', to='traffic.rentalcar')),
                ('train', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reservations', to='traffic.train')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reservations', to='account.customuser')),
            ],
        ),
    ]
