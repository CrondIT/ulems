# Generated by Django 5.1.1 on 2024-10-09 05:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0005_alter_category_print_title'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='print_title',
            field=models.TextField(verbose_name='Название для печати'),
        ),
    ]
