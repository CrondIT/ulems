# Generated by Django 5.1.1 on 2024-11-07 17:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0029_alter_category_event_related_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='participant',
            name='event',
        ),
    ]
