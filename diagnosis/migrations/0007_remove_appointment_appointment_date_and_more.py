# Generated by Django 5.0.6 on 2025-04-13 08:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('diagnosis', '0006_certifiedvet'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='appointment',
            name='appointment_date',
        ),
        migrations.RemoveField(
            model_name='appointment',
            name='date_requested',
        ),
        migrations.RemoveField(
            model_name='appointment',
            name='location_lat',
        ),
        migrations.RemoveField(
            model_name='appointment',
            name='location_lng',
        ),
        migrations.RemoveField(
            model_name='appointment',
            name='updated_at',
        ),
        migrations.RemoveField(
            model_name='appointment',
            name='vet_status_updated_at',
        ),
        migrations.DeleteModel(
            name='Rating',
        ),
    ]
