# Generated by Django 5.1.2 on 2024-10-11 21:18

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0004_rename_is_temp_locked_seat_is_locked_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='seat',
            name='event',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='manager.event'),
            preserve_default=False,
        ),
    ]
