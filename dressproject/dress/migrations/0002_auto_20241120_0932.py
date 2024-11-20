# Generated by Django 3.2 on 2024-11-20 00:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dress', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExamYear',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True, verbose_name='試験年度名')),
            ],
            options={
                'verbose_name': '試験年度',
                'verbose_name_plural': '試験年度',
            },
        ),
        migrations.AddField(
            model_name='questionimg',
            name='explanation_imgC',
            field=models.ImageField(blank=True, null=True, upload_to='explanation_images/'),
        ),
        migrations.AddField(
            model_name='questionimg',
            name='explanation_imgD',
            field=models.ImageField(blank=True, null=True, upload_to='explanation_images/'),
        ),
        migrations.AddField(
            model_name='questionimg',
            name='question_imgC',
            field=models.ImageField(blank=True, null=True, upload_to='question_images/'),
        ),
        migrations.AddField(
            model_name='questionimg',
            name='question_imgD',
            field=models.ImageField(blank=True, null=True, upload_to='question_images/'),
        ),
        migrations.AlterField(
            model_name='question',
            name='exam_year',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='dress.examyear', verbose_name='試験年度'),
        ),
    ]