# Generated by Django 3.0.3 on 2020-02-14 12:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('exportkontrollstatistiken', '0021_auto_20200212_1718'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='geschaeftekriegsmaterialnachkategorieendempfaengerstaat',
            options={'verbose_name': 'Geschäft: Kriegsmaterial, tatsächliche Ausfuhren, Format ähnlich Seco', 'verbose_name_plural': 'Geschäfte: Kriegsmaterial, tatsächliche Ausfuhren, Format ähnlich Seco'},
        ),
        migrations.AddField(
            model_name='laendergruppen',
            name='seco_km_order',
            field=models.PositiveIntegerField(default=0),
            preserve_default=False,
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
