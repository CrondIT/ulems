# Generated by Django 5.1.1 on 2024-11-08 04:48

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0030_remove_participant_event'),
    ]

    operations = [
       
        migrations.AlterField(
            model_name='profile',
            name='current_event',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='home.event'),
        ),
    ]
