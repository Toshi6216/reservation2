# Generated by Django 3.2.16 on 2023-05-08 10:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_auto_20230211_0942'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='active',
        ),
        migrations.RemoveField(
            model_name='customuser',
            name='admin',
        ),
        migrations.RemoveField(
            model_name='customuser',
            name='staff',
        ),
    ]
