# Generated by Django 5.1.1 on 2025-04-14 10:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0066_participant_job_title'),
    ]

    operations = [
        migrations.AlterField(
            model_name='participant',
            name='job_title',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='Должность'),
        ),
        migrations.AlterField(
            model_name='participant',
            name='organization',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='Организация'),
        ),
    ]
