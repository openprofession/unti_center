# Generated by Django 2.2.2 on 2019-07-16 21:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('center', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='dashboard',
            name='admin',
            field=models.BooleanField(default=False),
        ),
    ]
