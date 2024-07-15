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
import csv

f = open('utils/geo-utils/variousCountryDataOnlyData.csv', 'r', encoding='utf-8-sig')
reader = csv.DictReader(f, delimiter=';')
data = dict()
for row in reader:
  data[row['ISO3166A2']] = row

for country in Laender.objects.all():
  try:
    dataRow = data[country.code]
  except KeyError:
    print(country.code)
    continue
  
  country.laengengradMin = dataRow['minlongitude']
  country.laengengradMax = dataRow['maxlongitude']
  country.breitengradMin = dataRow['minlatitude']
  country.breitengradMax = dataRow['maxlatitude']
  country.laengengrad = dataRow['latitude']
  country.breitengrad = dataRow['longitude']
  country.save()
