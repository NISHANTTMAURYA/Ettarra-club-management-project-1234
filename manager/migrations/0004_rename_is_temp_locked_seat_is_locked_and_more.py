# Generated by Django 5.1.2 on 2024-10-11 20:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0003_rename_is_temp_disabled_seat_is_temp_locked'),
    ]

    operations = [
        migrations.RenameField(
            model_name='seat',
            old_name='is_temp_locked',
            new_name='is_locked',
        ),
        migrations.AddField(
            model_name='seat',
            name='locked_until',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
