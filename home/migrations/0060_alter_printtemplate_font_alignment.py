# Generated by Django 5.1.1 on 2025-03-17 04:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0059_printtemplate_delta_x_printtemplate_delta_y_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='printtemplate',
            name='font_alignment',
            field=models.PositiveSmallIntegerField(choices=[(0, 'Лево'), (1, 'По центр'), (2, 'Право'), (4, 'По ширине')], default=0),
        ),
    ]
