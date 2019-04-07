NICHT AUSFÜHREN - das ist kein fertiges Skript, nur Schnipsel für die interaktive Konsole

from exportkontrollstatistiken.models import *
import json
import csv

# replace 3 letter codes with 2 letter codes
f = open('/home/t4b/persönlich/engagement/gsoa/webseite/django/kriegsmaterialch/exportkontrollstatistiken/static/exportkontrollstatistiken/world_countries.json', 'r')
d = json.loads(f.read())
f.close()
f = open('/home/t4b/persönlich/engagement/gsoa/webseite/django/kriegsmaterialch/iso3166-2019-04-05.csv', 'r', newline='')
iso = csv.reader(f)
iso.__next__()
for countryCodes in iso:
  for country in d["features"]:
    country["id"] = country["id"].replace(countryCodes[3], countryCodes[2])
f.close()
f = open('/home/t4b/persönlich/engagement/gsoa/webseite/django/kriegsmaterialch/world_countries_2.json', 'w')
json.dumps(d, f, separators=(',', ':'))
f.close()

# replace them in the other file
f = open('/home/t4b/persönlich/engagement/gsoa/webseite/django/kriegsmaterialch/exportkontrollstatistiken/static/exportkontrollstatistiken/world_population.tsv', 'r')
d = f.read()
f.close()
f = open('/home/t4b/persönlich/engagement/gsoa/webseite/django/kriegsmaterialch/iso3166-2019-04-05.csv', 'r', newline='')
iso = csv.reader(f)
iso.__next__()
for countryCodes in iso:
  d = d.replace(countryCodes[3], countryCodes[2])

f.close()
f = open('/home/t4b/persönlich/engagement/gsoa/webseite/django/kriegsmaterialch/exportkontrollstatistiken/static/exportkontrollstatistiken/world_population.tsv', 'w')
f.write(d)
f.close()
