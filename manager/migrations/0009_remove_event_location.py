# Generated by Django 5.1.2 on 2024-10-12 04:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0008_event_event_date_event_location'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='location',
        ),
    ]
