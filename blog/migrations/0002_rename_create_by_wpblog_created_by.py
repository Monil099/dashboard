# Generated by Django 4.2.16 on 2024-09-22 06:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='wpblog',
            old_name='create_by',
            new_name='created_by',
        ),
    ]
