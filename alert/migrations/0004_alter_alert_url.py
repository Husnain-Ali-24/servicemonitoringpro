# Generated by Django 5.1.6 on 2025-02-25 03:08

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("alert", "0003_alert_url"),
    ]

    operations = [
        migrations.AlterField(
            model_name="alert",
            name="url",
            field=models.URLField(null=True),
        ),
    ]
