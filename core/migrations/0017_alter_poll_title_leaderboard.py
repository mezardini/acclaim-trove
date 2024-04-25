# Generated by Django 4.0.4 on 2024-04-13 18:44

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0016_poll_title'),
    ]

    operations = [
        migrations.AlterField(
            model_name='poll',
            name='title',
            field=models.CharField(max_length=250, null=True, unique=True),
        ),
        migrations.CreateModel(
            name='Leaderboard',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('month', models.CharField(max_length=20, null=True)),
                ('nominees', models.JSONField(default=list, null=True)),
                ('organizer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
