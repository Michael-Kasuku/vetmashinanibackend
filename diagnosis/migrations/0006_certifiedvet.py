# Generated by Django 5.0.6 on 2025-04-13 07:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('diagnosis', '0005_appointment_time_sent'),
    ]

    operations = [
        migrations.CreateModel(
            name='CertifiedVet',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('email', models.EmailField(max_length=254, unique=True)),
            ],
        ),
    ]
