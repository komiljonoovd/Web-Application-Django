# Generated by Django 5.1.1 on 2024-12-23 06:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schoolapp', '0003_alter_classes_createdby_alter_classes_modifiedby'),
    ]

    operations = [
        migrations.AlterField(
            model_name='classes',
            name='createdby',
            field=models.CharField(max_length=128),
        ),
        migrations.AlterField(
            model_name='classes',
            name='modifiedby',
            field=models.CharField(blank=True, max_length=128),
        ),
    ]