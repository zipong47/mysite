# Generated by Django 5.0.3 on 2024-06-06 02:47

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Board',
            fields=[
                ('project_name', models.CharField(max_length=200)),
                ('project_config', models.CharField(default='C', max_length=50)),
                ('subprotject_name', models.CharField(max_length=200)),
                ('serial_number', models.CharField(max_length=200, primary_key=True, serialize=False)),
                ('configration', models.CharField(max_length=200)),
                ('board_number', models.IntegerField()),
                ('test_item_name', models.CharField(max_length=100)),
                ('cp_nums', models.IntegerField(default=0)),
                ('APN', models.CharField(default='', max_length=50)),
                ('HHPN', models.CharField(default='', max_length=50)),
                ('first_GS_sn', models.CharField(default='', max_length=50)),
                ('second_GS_sn', models.CharField(default='', max_length=50)),
                ('env_finished_flag', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='NoteQueryBoard',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('serial_number', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='NotPassBoard',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('project_name', models.CharField(max_length=200)),
                ('subprotject_name', models.CharField(max_length=200)),
                ('serial_number', models.CharField(max_length=200)),
                ('cp_nums', models.IntegerField(default=0)),
                ('last_query_time', models.DateTimeField(verbose_name='last query time')),
            ],
        ),
        migrations.CreateModel(
            name='TestSchedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('project_name', models.CharField(max_length=100)),
                ('config_name', models.CharField(max_length=50)),
                ('build_name', models.CharField(max_length=50)),
                ('cp_nums', models.IntegerField(default=0)),
                ('test_sequence', models.CharField(max_length=300)),
            ],
        ),
        migrations.CreateModel(
            name='TestRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('station_type', models.CharField(max_length=50)),
                ('start_time', models.DateTimeField(verbose_name='start time.')),
                ('cp_nums', models.IntegerField(default=0)),
                ('stop_time', models.DateTimeField(verbose_name='stop time')),
                ('result', models.CharField(choices=[('pass', 'pass'), ('fail', 'fail')], default='fail', max_length=4)),
                ('board', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='board.board')),
            ],
        ),
        migrations.CreateModel(
            name='TestResult',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_name', models.CharField(max_length=200)),
                ('test_station', models.CharField(max_length=200)),
                ('result', models.CharField(max_length=200)),
                ('station_id', models.CharField(max_length=200)),
                ('start_time', models.DateTimeField(verbose_name='started time')),
                ('finish_time', models.DateTimeField(verbose_name='finished time')),
                ('board', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='board.board')),
            ],
        ),
    ]
