# Generated by Django 3.0.7 on 2020-12-11 15:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dba', '0002_user_is_gf'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='objid',
            field=models.CharField(default=False, max_length=100),
        ),
    ]