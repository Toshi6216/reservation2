# Generated by Django 3.2.16 on 2023-05-08 11:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0008_auto_20230508_1949'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='customuser',
            name='admin',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='customuser',
            name='staff',
            field=models.BooleanField(default=False),
        ),
    ]
