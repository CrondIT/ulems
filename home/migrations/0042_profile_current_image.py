# Generated by Django 5.1.1 on 2024-12-17 11:11

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0041_remove_printtemplate_event_related_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='current_image',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='home.userimage'),
        ),
    ]