# Generated by Django 5.1.1 on 2025-04-05 03:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0061_userfont'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='sort_font',
            field=models.CharField(default='created_date', max_length=25),
        ),
    ]
