# Generated by Django 5.0.6 on 2025-04-12 09:17

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('diagnosis', '0004_alter_user_wallet_balance'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointment',
            name='time_sent',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
