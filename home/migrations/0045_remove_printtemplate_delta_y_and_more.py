# Generated by Django 5.1.1 on 2024-12-30 07:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0044_userimage_height_userimage_width'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='printtemplate',
            name='delta_y',
        ),
        migrations.AddField(
            model_name='printtemplate',
            name='font_color',
            field=models.CharField(max_length=25, null=True),
        ),
    ]