# Generated by Django 3.2.16 on 2023-05-23 03:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0018_auto_20230509_1138'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customuser',
            old_name='active',
            new_name='is_active',
        ),
        migrations.RenameField(
            model_name='customuser',
            old_name='admin',
            new_name='is_admin',
        ),
        migrations.RenameField(
            model_name='customuser',
            old_name='staff',
            new_name='is_staff',
        ),
    ]