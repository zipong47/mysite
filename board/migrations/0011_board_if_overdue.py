# Generated by Django 5.0.3 on 2024-07-24 15:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('board', '0010_alter_errorrecord_fail_picture'),
    ]

    operations = [
        migrations.AddField(
            model_name='board',
            name='if_overdue',
            field=models.BooleanField(default=False),
        ),
    ]
