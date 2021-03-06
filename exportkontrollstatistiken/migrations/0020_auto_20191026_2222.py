# Generated by Django 2.2.6 on 2019-10-26 20:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exportkontrollstatistiken', '0019_auto_20190722_1427'),
    ]

    operations = [
        migrations.AddField(
            model_name='laender',
            name='breitengrad',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='laender',
            name='laengengrad',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='laender',
            name='gruppen',
            field=models.ManyToManyField(to='exportkontrollstatistiken.Laendergruppen'),
        ),
    ]
