# Generated by Django 3.0.3 on 2020-02-19 08:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('exportkontrollstatistiken', '0023_auto_20200214_2031'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='geschaefte',
            name='quelle',
        ),
        migrations.AddField(
            model_name='geschaefte',
            name='sources',
            field=models.ManyToManyField(to='exportkontrollstatistiken.QuellenGeschaefte'),
        ),
        migrations.AlterField(
            model_name='geschaeftekriegsmaterialnachkategorieendempfaengerstaat',
            name='continent',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='exportkontrollstatistiken.Laendergruppen'),
        ),
        migrations.AlterField(
            model_name='laender',
            name='gruppen',
            field=models.ManyToManyField(to='exportkontrollstatistiken.Laendergruppen'),
        ),
    ]
