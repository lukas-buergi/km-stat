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
    Warning: Overwrites important database entries without prompting. Make sure to backup any important changes before running this.

    TODO: Makes a mess because it doesn't thoroughly delete entries not used anymore and creates duplicate entries.

    Imports the Wassenaar munitions list(s) into the database. It saves them into the export control regime "Wassenaar Arrangement" - while this can be directly used for exports, long term we should verify how and when Switzerland accepts changes to the upstream lists and make a Swiss version of the upstream lists.
    Right now it only imports the 2018 list and gives it validity over the whole period.
    
    Also KM."""
    def handle(self, **options):
        # once the km and bmg exports can be re-imported from the files, delete all of them from the db and uncomment the following lines to get rid of bad old data:
        #Exportkontrollnummern.objects.all().delete()
        #Kontrollregimes.objects.all().delete()
        for mlv in [
            ["/code/export-control-code-lists/wassenaar-lists/2018-12-06 18 1/15 - WA-LIST (18) 1 - ML.manual.txt", "Wassenaar Arrangement 18 1", "Special Military Goods",  datetime.date(1900, 1, 1), datetime.date(2200, 12, 31), "en"],
            ["/code/export-control-code-lists/km-swiss/2022-01-01.manual.txt", "SR 514.511 Anhang 1 (KMV) 2022-01-01", "Kriegsmaterial",  datetime.date(2022, 1, 1), datetime.date(2200, 12, 31), "de"]
        ]:
            # find/create the right export control regime 
            kontrollregimeName = mlv[1]
            try:
                kontrollregime=Kontrollregimes.objects.get(**{"name__" + mlv[5] : kontrollregimeName})
            except geschaefte.Kontrollregimes.DoesNotExist:
                print("Added Kontrollregime " + kontrollregimeName)
                name=Uebersetzungen(**{mlv[5] : kontrollregimeName})
                name.save()
                kontrollregime=Kontrollregimes(name=name, gueterArt=GueterArten.objects.get(**{"name__" + mlv[5] : mlv[2]}), inkrafttreten=mlv[3], aufgehobenwerden=mlv[4])
                kontrollregime.save()
            
            # delete all existing entries in this export contol regime because we are reimporting them
            Exportkontrollnummern.objects.filter(kontrollregime=kontrollregime).delete()

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
                        raise
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
            