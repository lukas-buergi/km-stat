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
