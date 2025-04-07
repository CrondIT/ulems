# Generated by Django 5.1.1 on 2025-04-07 16:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0064_printtemplate_user_font_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='printtemplate',
            name='after_print_text',
            field=models.TextField(blank=True, null=True, verbose_name='Текст после'),
        ),
        migrations.AddField(
            model_name='printtemplate',
            name='before_print_text',
            field=models.TextField(blank=True, null=True, verbose_name='Текст до'),
        ),
    ]
