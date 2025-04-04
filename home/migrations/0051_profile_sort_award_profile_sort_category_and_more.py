# Generated by Django 5.1.1 on 2025-01-14 05:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0050_alter_participant_first_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='sort_award',
            field=models.CharField(default='created_date', max_length=25),
        ),
        migrations.AddField(
            model_name='profile',
            name='sort_category',
            field=models.CharField(default='created_date', max_length=25),
        ),
        migrations.AddField(
            model_name='profile',
            name='sort_competency',
            field=models.CharField(default='created_date', max_length=25),
        ),
        migrations.AddField(
            model_name='profile',
            name='sort_event',
            field=models.CharField(default='created_date', max_length=25),
        ),
        migrations.AddField(
            model_name='profile',
            name='sort_image',
            field=models.CharField(default='created_date', max_length=25),
        ),
        migrations.AddField(
            model_name='profile',
            name='sort_participant',
            field=models.CharField(default='created_date', max_length=25),
        ),
        migrations.AddField(
            model_name='profile',
            name='sort_template',
            field=models.CharField(default='created_date', max_length=25),
        ),
    ]
