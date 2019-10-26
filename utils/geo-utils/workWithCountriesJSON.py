#######################################################################
# Copyright Lukas Bürgi 2019
#
# This file is part of km-stat.
#
# km-stat is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# km-stat is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public
# License for more details.
#
# You should have received a copy of the GNU Affero General Public
# License along with km-stat.  If not, see
# <https://www.gnu.org/licenses/>.
########################################################################

DONT EXECUTE - NOT A SCRIPT, JUST SNIPPETS TO COPY AND PASTE

from exportkontrollstatistiken.models import *
import json
import csv

# add characteristic coordinates to each country
f = open('/home/t4b/persönlich/engagement/gsoa/webseite/django/kriegsmaterialch/exportkontrollstatistiken/static/exportkontrollstatistiken/world_countries.json', 'r')
d = json.loads(f.read())
f.close()

for country in d["features"]:
  try:
    countryDBObject = Laender.objects.get(code=country['id'])
  except Laender.DoesNotExist:
    print(country['id'])
    continue
  country['latitude'] = countryDBObject.laengengrad
  country['longitude'] = countryDBObject.breitengrad

f = open('/home/t4b/tmp/world_countries.json', 'w')
json.dump(d, f, separators=(',', ':'))
f.close()

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

# replace names with codes
filename='/home/t4b/persönlich/engagement/gsoa/webseite/django/kriegsmaterialch/exportkontrollstatistiken/static/exportkontrollstatistiken/worldmap.js'
with open(filename, "r") as f:
    d = f.read()
with open(filename, "w") as f:
  with open('/home/t4b/persönlich/engagement/gsoa/webseite/django/kriegsmaterialch/iso3166-2019-04-05.csv', 'r', newline='') as isof:
    iso = csv.reader(isof)
    iso.__next__()
    for countryCodes in iso:
      d = d.replace("(d.properties.name === '" + countryCodes[0] + "')", "(d.id === '" + countryCodes[2] + "')")
    f.write(d)
