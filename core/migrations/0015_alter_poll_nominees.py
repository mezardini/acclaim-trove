# Generated by Django 4.0.4 on 2024-04-07 12:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_poll_nominees'),
    ]

    operations = [
        migrations.AlterField(
            model_name='poll',
            name='nominees',
            field=models.JSONField(default=list, null=True),
        ),
    ]
