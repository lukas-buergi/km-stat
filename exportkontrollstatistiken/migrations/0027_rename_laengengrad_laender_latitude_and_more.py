# Generated by Django 4.0.2 on 2022-03-22 00:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('exportkontrollstatistiken', '0026_alter_exportkontrollnummern_nummer'),
    ]

    operations = [
        migrations.RenameField(
            model_name='laender',
            old_name='laengengrad',
            new_name='latitude',
        ),
        migrations.RenameField(
            model_name='laender',
            old_name='breitengrad',
            new_name='longitude',
        ),
    ]
