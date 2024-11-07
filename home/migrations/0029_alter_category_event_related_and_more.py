# Generated by Django 5.1.1 on 2024-11-07 16:31

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0028_category_event_related_competency_event_related_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='event_related',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_event_related', to='home.event'),
        ),
        migrations.AlterField(
            model_name='competency',
            name='event_related',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_event_related', to='home.event'),
        ),
        migrations.AlterField(
            model_name='participant',
            name='event_related',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_event_related', to='home.event'),
        ),
    ]
