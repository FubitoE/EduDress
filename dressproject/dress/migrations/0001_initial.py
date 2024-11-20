# Generated by Django 3.2 on 2024-11-15 01:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Question',
            fields=[
                ('questions_id', models.AutoField(primary_key=True, serialize=False)),
                ('questions_number', models.IntegerField(default=0)),
                ('questions_text', models.TextField()),
                ('choice_a', models.TextField()),
                ('choice_b', models.TextField()),
                ('choice_c', models.TextField()),
                ('choice_d', models.TextField()),
                ('correct_answer', models.CharField(blank=True, choices=[('a', 'ア'), ('b', 'イ'), ('c', 'ウ'), ('d', 'エ')], default='a', max_length=10)),
                ('exam_year', models.CharField(max_length=20)),
                ('explanation', models.TextField()),
                ('difficulty', models.CharField(choices=[('IP', 'Iパス'), ('SG', 'セキュマネ'), ('FE', '基本'), ('AP', '応用')], max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Style',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True, verbose_name='スタイル名')),
            ],
            options={
                'verbose_name': 'スタイル',
                'verbose_name_plural': 'スタイル',
            },
        ),
        migrations.CreateModel(
            name='Questionimg',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question_imgA', models.ImageField(blank=True, null=True, upload_to='question_images/')),
                ('question_imgB', models.ImageField(blank=True, null=True, upload_to='question_images/')),
                ('explanation_imgA', models.ImageField(blank=True, null=True, upload_to='explanation_images/')),
                ('explanation_imgB', models.ImageField(blank=True, null=True, upload_to='explanation_images/')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='dress.question')),
            ],
        ),
        migrations.CreateModel(
            name='Parts',
            fields=[
                ('parts_id', models.AutoField(primary_key=True, serialize=False)),
                ('parts_name', models.CharField(max_length=100)),
                ('parts_category', models.CharField(choices=[('hair', '髪'), ('eyes', '目'), ('clothes', '服'), ('accessory', 'アクセサリー'), ('background', '背景')], max_length=10)),
                ('parts_default', models.BooleanField(default=False)),
                ('parts_image', models.ImageField(upload_to='parts/')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='作成日時')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新日時')),
                ('parts_style', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='dress.style', verbose_name='スタイル')),
            ],
            options={
                'verbose_name': 'パーツ',
                'verbose_name_plural': 'パーツ',
                'ordering': ['parts_category', 'parts_name'],
            },
        ),
    ]
