NICHT AUSFÜHREN - das ist kein fertiges Skript, nur Schnipsel für die interaktive Konsole

from exportkontrollstatistiken.models import *
import csv

f = open('utils/iso3166-2019-04-05.csv', 'r', newline='')
iso = csv.reader(f)

iso.__next__()

regions = {
    "AF":"Africa",
    "NA":"North America",
    "OC":"Oceania",
    "AS":"Asia",
    "EE":"Europe",
    "SA":"South America",
}

for code, english in regions.items():
    name = Uebersetzungen(de='', fr='', it='', en=english)
    name.save()
    region = Laendergruppen(code=code, name=name)
    region.save()
