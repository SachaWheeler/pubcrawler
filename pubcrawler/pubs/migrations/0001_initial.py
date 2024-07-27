# Generated by Django 5.0.7 on 2024-07-27 09:09

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Pub',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fas_id', models.CharField(max_length=50)),
                ('name', models.CharField(max_length=255)),
                ('address', models.CharField(max_length=255)),
                ('postcode', models.CharField(max_length=20)),
                ('easting', models.IntegerField()),
                ('northing', models.IntegerField()),
                ('latitude', models.FloatField()),
                ('longitude', models.FloatField()),
                ('local_authority', models.CharField(max_length=255)),
            ],
        ),
    ]
