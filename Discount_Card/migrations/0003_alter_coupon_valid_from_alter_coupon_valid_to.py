# Generated by Django 5.1.3 on 2024-12-08 03:54

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Discount_Card', '0002_user_email_verified_alter_user_is_active'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coupon',
            name='valid_from',
            field=models.DateField(default=datetime.date(2024, 12, 8)),
        ),
        migrations.AlterField(
            model_name='coupon',
            name='valid_to',
            field=models.DateField(),
        ),
    ]
