#!/usr/bin/env python3
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
from exportkontrollstatistiken.models import *
import csv

from django.core.management.base import BaseCommand

class Command(BaseCommand):
    def handle(self, **options):
        for year in range(2006,2019):
            blankLine = ["","","","","","","","","","","","","","","","","","","","","","","",""]
            country=""
            curLine = ["Land", "Pays", "KM1", "KM2", "KM3", "KM4", "KM5", "KM6", "KM7", "KM8", "KM9", "KM10", "KM11", "KM12", "KM13", "KM14", "KM15", "KM16", "KM17", "KM18", "KM19", "K20", "KM21", "KM22"]

            with open("/code/utils/original-statistiken/Kriegsmaterial/nach-kategorie-pro-endempf-staat/" + str(year) + "-01-01-" + str(year) + "-12-31.csv", mode='w') as f:
                out = csv.writer(f)

                for g in Geschaefte.objects.filter(exportkontrollnummer__kontrollregime__gueterArt__name__de="Kriegsmaterial", beginn=datetime.date(year, 1, 1)).order_by('endempfaengerstaat__name__de'):
                    if(g.endempfaengerstaat.name.de == country):
                        curLine[int(g.exportkontrollnummer.nummer[2:])+1] = g.umfang
                    else:
                        country=g.endempfaengerstaat.name.de
                        out.writerow(curLine)
                        curLine=blankLine.copy()
                        curLine[0]=country
                        curLine[1]=g.endempfaengerstaat.name.fr
                        curLine[int(g.exportkontrollnummer.nummer[2:])+1] = g.umfang
