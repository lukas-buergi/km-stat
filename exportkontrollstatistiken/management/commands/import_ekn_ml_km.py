#!/usr/bin/env python3
#######################################################################
# Copyright Lukas Bürgi 2022
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
import re

from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help="""
    Warning: Makes a mess if run multiple times without deleting all export control codes in between each run.

    Imports the Wassenaar munitions list(s) into the database. It saves them into the export control regime "Wassenaar Arrangement" - while this can be directly used for exports, long term we should verify how and when Switzerland accepts changes to the upstream lists and make a Swiss version of the upstream lists.
    Right now it only imports the 2018 list and gives it validity over the whole period.
    
    Also KM."""
    def handle(self, **options):

        for mlv in [
            ["/code/export-control-code-lists/wassenaar-lists/2018-12-06 18 1/03 - WA-LIST (18) 1 - Cat 1.manual.txt", "Wassenaar Arrangement 18 1", "Dual-Use Goods",  datetime.date(1900, 1, 1), datetime.date(2200, 12, 31), "en"],
            ["/code/export-control-code-lists/wassenaar-lists/2018-12-06 18 1/04 - WA-LIST (18) 1 - Cat 2.manual.txt", "Wassenaar Arrangement 18 1", "Dual-Use Goods",  datetime.date(1900, 1, 1), datetime.date(2200, 12, 31), "en"],
            ["/code/export-control-code-lists/wassenaar-lists/2018-12-06 18 1/05 - WA-LIST (18) 1 - Cat 3.manual.txt", "Wassenaar Arrangement 18 1", "Dual-Use Goods",  datetime.date(1900, 1, 1), datetime.date(2200, 12, 31), "en"],
            ["/code/export-control-code-lists/wassenaar-lists/2018-12-06 18 1/06 - WA-LIST (18) 1 - Cat 4.manual.txt", "Wassenaar Arrangement 18 1", "Dual-Use Goods",  datetime.date(1900, 1, 1), datetime.date(2200, 12, 31), "en"],
            ["/code/export-control-code-lists/wassenaar-lists/2018-12-06 18 1/07 - WA-LIST (18) 1 - Cat 5P1.manual.txt", "Wassenaar Arrangement 18 1", "Dual-Use Goods",  datetime.date(1900, 1, 1), datetime.date(2200, 12, 31), "en"],
            ["/code/export-control-code-lists/wassenaar-lists/2018-12-06 18 1/08 - WA-LIST (18) 1 - Cat 5P2.manual.txt", "Wassenaar Arrangement 18 1", "Dual-Use Goods",  datetime.date(1900, 1, 1), datetime.date(2200, 12, 31), "en"],
            ["/code/export-control-code-lists/wassenaar-lists/2018-12-06 18 1/09 - WA-LIST (18) 1 - Cat 6.manual.txt", "Wassenaar Arrangement 18 1", "Dual-Use Goods",  datetime.date(1900, 1, 1), datetime.date(2200, 12, 31), "en"],
            ["/code/export-control-code-lists/wassenaar-lists/2018-12-06 18 1/10 - WA-LIST (18) 1 - Cat 7.manual.txt", "Wassenaar Arrangement 18 1", "Dual-Use Goods",  datetime.date(1900, 1, 1), datetime.date(2200, 12, 31), "en"],
            ["/code/export-control-code-lists/wassenaar-lists/2018-12-06 18 1/11 - WA-LIST (18) 1 - Cat 8.manual.txt", "Wassenaar Arrangement 18 1", "Dual-Use Goods",  datetime.date(1900, 1, 1), datetime.date(2200, 12, 31), "en"],
            ["/code/export-control-code-lists/wassenaar-lists/2018-12-06 18 1/12 - WA-LIST (18) 1 - Cat 9.manual.txt", "Wassenaar Arrangement 18 1", "Dual-Use Goods",  datetime.date(1900, 1, 1), datetime.date(2200, 12, 31), "en"],
            ["/code/export-control-code-lists/wassenaar-lists/2018-12-06 18 1/15 - WA-LIST (18) 1 - ML.manual.txt", "Wassenaar Arrangement 18 1", "Special Military Goods",  datetime.date(1900, 1, 1), datetime.date(2200, 12, 31), "en"],
            ["/code/export-control-code-lists/km-swiss/2022-01-01.manual.txt", "SR 514.511 Anhang 1 (KMV) 2022-01-01", "Kriegsmaterial",  datetime.date(2022, 1, 1), datetime.date(2200, 12, 31), "de"]
        ]:
            # find/create the right export control regime 
            kontrollregimeName = mlv[1]
            try:
                kontrollregime=Kontrollregimes.objects.get(**{"name__" + mlv[5] : kontrollregimeName, "gueterArt__name__" + mlv[5] : mlv[2]})
            except geschaefte.Kontrollregimes.DoesNotExist:
                print("Added Kontrollregime " + kontrollregimeName)
                name=Uebersetzungen(**{mlv[5] : kontrollregimeName})
                name.save()
                kontrollregime=Kontrollregimes(name=name, gueterArt=GueterArten.objects.get(**{"name__" + mlv[5] : mlv[2]}), inkrafttreten=mlv[3], aufgehobenwerden=mlv[4])
                kontrollregime.save()

            # import the export control codes
            # step 1 put them into list
            codesSet=set()
            descList=[]
            with open(mlv[0], newline='') as f:
                reader = csv.reader(f, delimiter='\t')
                for row in reader:
                    try:
                        assert(len(row) in [0,2])
                    except AssertionError:
                        print(row)
                        continue # needs to be raise when the lists are correct
                    if(len(row) == 2):
                        descList.append(row)
                        codesSet.add(row[0])
            
            # step 2 put them into dict
            codesDict = {}
            for code in codesSet:
                codesDict[code] = ""
                for line in descList:
                    if(code.startswith(line[0]) or line[0].startswith(code) or code.startswith(re.sub("[^.]*Note.*$", "" ,line[0]))):
                        codesDict[code] += line[0] + "  " + line[1] + "\n"
            
            # step 3 put dict into db
            for code, desc in codesDict.items():
                descO = Uebersetzungen(**{mlv[5] : desc})
                descO.save()
                ekn=Exportkontrollnummern(kontrollregime=kontrollregime, nummer=code, beschreibung=descO)
                ekn.save()
            print(str(len(codesDict)) + " export control codes added to " + mlv[1])
            