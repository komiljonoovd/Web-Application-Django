# Generated by Django 5.1.1 on 2024-12-23 06:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schoolapp', '0005_parentpupil_createdby_parentpupil_createdon_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='classes',
            name='createdby',
            field=models.CharField(blank=True, max_length=128),
        ),
        migrations.AlterField(
            model_name='gender',
            name='createdby',
            field=models.CharField(blank=True, max_length=128),
        ),
        migrations.AlterField(
            model_name='parentpupil',
            name='createdby',
            field=models.CharField(blank=True, max_length=128),
        ),
        migrations.AlterField(
            model_name='parents',
            name='createdby',
            field=models.CharField(blank=True, max_length=128),
        ),
        migrations.AlterField(
            model_name='payment',
            name='createdby',
            field=models.CharField(blank=True, max_length=128),
        ),
        migrations.AlterField(
            model_name='pupils',
            name='createdby',
            field=models.CharField(blank=True, max_length=128),
        ),
    ]
