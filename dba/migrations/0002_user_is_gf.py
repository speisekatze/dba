# Generated by Django 3.0.7 on 2020-06-22 05:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dba', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_gf',
            field=models.BooleanField(default=False),
        ),
    ]