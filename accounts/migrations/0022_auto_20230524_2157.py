# Generated by Django 3.2.16 on 2023-05-24 12:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0021_rename_admin_customuser_is_admin'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customuser',
            old_name='is_active',
            new_name='active',
        ),
        migrations.RenameField(
            model_name='customuser',
            old_name='is_admin',
            new_name='admin',
        ),
        migrations.RenameField(
            model_name='customuser',
            old_name='is_staff',
            new_name='staff',
        ),
    ]
