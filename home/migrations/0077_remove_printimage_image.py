# Generated by Django 5.1.1 on 2025-05-20 06:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0076_printimage_print_image'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='printimage',
            name='image',
        ),
    ]
