# Generated by Django 5.0.7 on 2024-07-27 09:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pubs', '0005_pub_local_authority2'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pub',
            name='local_authority',
        ),
    ]
