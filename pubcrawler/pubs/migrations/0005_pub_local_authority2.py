# Generated by Django 5.0.7 on 2024-07-27 09:32

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pubs', '0004_localauthority'),
    ]

    operations = [
        migrations.AddField(
            model_name='pub',
            name='local_authority2',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='pubs', to='pubs.localauthority'),
        ),
    ]
