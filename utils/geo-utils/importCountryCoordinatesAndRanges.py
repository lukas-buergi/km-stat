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
  country.laengengradMin = data[country.code]['minlongitude']
  country.laengengradMax = data[country.code]['maxlongitude']
  country.breitengradMin = data[country.code]['minlatitude']
  country.breitengradMax = data[country.code]['maxlatitude']
  country.laengengrad = data[country.code]['latitude']
  country.breitengrad = data[country.code]['longitude']
  print(country)
