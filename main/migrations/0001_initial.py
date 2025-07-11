# Generated by Django 5.2.1 on 2025-05-29 03:28

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Schedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Song',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('key', models.CharField(max_length=3)),
                ('frequency', models.PositiveIntegerField()),
                ('hymn', models.BooleanField()),
                ('schedule', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.schedule')),
            ],
        ),
    ]
