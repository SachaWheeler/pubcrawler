# Generated by Django 5.0.7 on 2024-08-01 08:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pubs', '0012_remove_pub_location'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Distance',
            new_name='PubDist',
        ),
        migrations.RenameIndex(
            model_name='pubdist',
            new_name='pubs_pubdis_pub1_id_184e7d_idx',
            old_name='pubs_distan_pub1_id_f3522c_idx',
        ),
    ]
