# Generated by Django 2.1.7 on 2019-03-29 14:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exportkontrollstatistiken', '0006_auto_20190329_1425'),
    ]

    operations = [
        migrations.CreateModel(
            name='GeschaefteImport',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=2)),
                ('art', models.CharField(max_length=40)),
                ('system', models.CharField(max_length=10)),
                ('kategorie', models.CharField(max_length=15)),
                ('datum', models.DateField()),
                ('betrag', models.PositiveIntegerField()),
            ],
        ),
    ]
