# Generated by Django 5.0.3 on 2024-07-22 14:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('board', '0007_rename_subprotject_name_board_subproject_name'),
    ]

    operations = [
        migrations.RenameField(
            model_name='board',
            old_name='configration',
            new_name='configuration',
        ),
    ]
