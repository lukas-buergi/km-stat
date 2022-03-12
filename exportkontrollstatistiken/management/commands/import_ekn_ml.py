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
    Imports the Wassenaar munitions list(s) into the database. It saves them into the export control regime "Wassenaar Arrangement" - while this can be directly used for exports, long term we should verify how and when Switzerland accepts changes to the upstream lists and make a Swiss version of the upstream lists.
    Right now it only imports the 2018 list and gives it validity over the whole period."""
    def handle(self, **options):
        for mlv in [["2018-12-06 18 1/15 - WA-LIST (18) 1 - ML.manual.txt", "18 1", datetime.date(1900, 1, 1), datetime.date(2200, 12, 31)]]:
            # find/create the right export control regime 
            kontrollregimeName = "Wassenaar Arrangement " + mlv[1]
            try:
                kontrollregime=Kontrollregimes.objects.get(name__en=kontrollregimeName)
            except geschaefte.Kontrollregimes.DoesNotExist:
                print("Added Kontrollregime " + kontrollregimeName)
                name=Uebersetzungen(en=kontrollregimeName)
                name.save()
                kontrollregime=Kontrollregimes(name=name, gueterArt=GueterArten.objects.get(name__en="Dual-Use Goods"), inkrafttreten=mlv[2], aufgehobenwerden=mlv[3])
                kontrollregime.save()
            
            # delete all existing entries in this export contol regime because we are reimporting them
            Exportkontrollnummern.objects.filter(kontrollregime=kontrollregime).delete()

            # import the export control codes
            # step 1 put them into list
            codesSet=set()
            descList=[]
            with open("/code/utils/wassenaar-lists/" + mlv[0], newline='') as f:
                reader = csv.reader(f, delimiter='\t')
                for row in reader:
                    assert(len(row) in [0,2])
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
                descO = Uebersetzungen(en=desc)
                descO.save()
                Exportkontrollnummern(kontrollregime=kontrollregime, nummer=code, beschreibung=descO).save()