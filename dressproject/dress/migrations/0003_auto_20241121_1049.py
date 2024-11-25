# Generated by Django 3.2 on 2024-11-21 01:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dress', '0002_auto_20241120_0932'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='question',
            name='choice_a',
        ),
        migrations.RemoveField(
            model_name='question',
            name='choice_b',
        ),
        migrations.RemoveField(
            model_name='question',
            name='choice_c',
        ),
        migrations.RemoveField(
            model_name='question',
            name='choice_d',
        ),
        migrations.AddField(
            model_name='question',
            name='choice_a_image',
            field=models.ImageField(blank=True, null=True, upload_to='choices_images/'),
        ),
        migrations.AddField(
            model_name='question',
            name='choice_a_text',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='question',
            name='choice_b_image',
            field=models.ImageField(blank=True, null=True, upload_to='choices_images/'),
        ),
        migrations.AddField(
            model_name='question',
            name='choice_b_text',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='question',
            name='choice_c_image',
            field=models.ImageField(blank=True, null=True, upload_to='choices_images/'),
        ),
        migrations.AddField(
            model_name='question',
            name='choice_c_text',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='question',
            name='choice_d_image',
            field=models.ImageField(blank=True, null=True, upload_to='choices_images/'),
        ),
        migrations.AddField(
            model_name='question',
            name='choice_d_text',
            field=models.TextField(blank=True, null=True),
        ),
    ]
