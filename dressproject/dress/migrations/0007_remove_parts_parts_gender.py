# Generated by Django 3.2 on 2024-11-29 01:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dress', '0006_parts_parts_gender'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='parts',
            name='parts_gender',
        ),
    ]
