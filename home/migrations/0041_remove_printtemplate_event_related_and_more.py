# Generated by Django 5.1.1 on 2024-12-16 13:02

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0040_printtemplate_event_related'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='printtemplate',
            name='event_related',
        ),
        migrations.AddField(
            model_name='printtemplate',
            name='user_image_related',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_user_image_related', to='home.userimage'),
        ),
    ]
