# Generated by Django 5.0.3 on 2024-07-24 13:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('board', '0009_errorrecord_fail_picture'),
    ]

    operations = [
        migrations.AlterField(
            model_name='errorrecord',
            name='fail_picture',
            field=models.ImageField(blank=True, null=True, upload_to='failures/%Y/%m/%d/%H%M%S/'),
        ),
    ]
