# Generated by Django 4.0.4 on 2024-04-07 11:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_remove_nominee_month_remove_nominee_vote_count'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='nominee',
            name='poll',
        ),
        migrations.AddField(
            model_name='nominee',
            name='poll',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='core.poll'),
        ),
    ]
