# Generated by Django 5.1.1 on 2024-10-29 05:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0015_remove_category_author_remove_competency_author_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='author',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='competency',
            name='author',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='event',
            name='author',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='participant',
            name='author',
            field=models.CharField(max_length=200, null=True),
        ),
    ]