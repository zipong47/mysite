# Generated by Django 5.0.3 on 2024-07-08 15:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('board', '0002_remove_testschedule_build_name_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='NoteQueryBoard',
        ),
        migrations.DeleteModel(
            name='NotPassBoard',
        ),
        migrations.AddField(
            model_name='board',
            name='product_code',
            field=models.CharField(default='', max_length=20),
        ),
        migrations.AddField(
            model_name='testrecord',
            name='operator',
            field=models.CharField(default='', max_length=50),
        ),
        migrations.AddField(
            model_name='testrecord',
            name='remark',
            field=models.CharField(default='', max_length=500),
        ),
        migrations.AddField(
            model_name='testrecord',
            name='site',
            field=models.CharField(default='FXLH', max_length=20),
        ),
        migrations.DeleteModel(
            name='TestResult',
        ),
    ]
