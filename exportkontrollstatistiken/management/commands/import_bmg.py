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

    Imports data about special military goods exports."""
    def handle(self, **options):
        files = [
            ['2014-01-01-2014-12-31-bmg.csv', 'elic'],
            ['2014-01-01-2014-12-31-du.csv', 'elic'],
            ['2015-01-01-2015-12-31.csv', 'elic'],
            ['2016-01-01-2016-03-31.csv', 'elic'],
            ['2016-04-01-2016-06-30.csv', 'elic'],
            ['2016-07-01-2016-09-30.csv', 'elic'],
            ['2016-10-01-2016-12-31.csv', 'elic'],
            ['2017-01-01-2017-03-31.csv', 'elic'],
            ['2017-04-01-2017-06-30.csv', 'elic'],
            ['2017-07-01-2017-09-30.csv', 'elic'],
            ['2017-10-01-2017-12-31.csv', 'elic'],
            ['2018-01-01-2018-03-31.csv', 'elic'],
            ['2018-04-01-2018-06-30.csv', 'elic'],
            ['2018-07-01-2018-09-30.csv', 'elic'],
            ['2018-10-01-2018-12-31.csv', 'elic'],
            ['2019-01-01-2019-03-31.csv', 'elic'],
            ['2019-04-01-2019-06-30.csv', 'elic'],
            ['2019-07-01-2019-09-30.csv', 'elic'],
            ['2019-10-01-2019-12-31.csv', 'elic'],
            ['2020-01-01-2020-03-31.csv', 'elic'],
            ['2020-04-01-2020-06-30.csv', 'elic'],
            ['2020-07-01-2020-09-30.csv', 'elic'],
            ['2020-10-01-2020-12-31.csv', 'elic'],
            ['2021-01-01-2021-03-31.csv', 'elic'],
            ['2021-04-01-2021-06-30.csv', 'elic'],
            ['2021-07-01-2021-09-30.csv', 'elic'],
            ['2021-10-01-2021-12-31.csv', 'elic'],
            ['1997-01-01-2011-12-31.csv', 'trackerV1'],
#            ['2012-01-01-2014-09-30-bmg.csv', 'trackerV2'],
            ['2012-01-01-2014-09-30-du.csv', 'trackerV2'],
        ]
        kontrollregimeName = "Wassenaar Arrangement 18 1"
        Geschaefte.objects.filter(exportkontrollnummer__kontrollregime__name__en=kontrollregimeName).delete()
        for f in files:
            if(f[1] == "elic"):
                path="/code/export-control-statistics-original-data/sorted-for-automated-handling/du+bmg-elic/" + f[0]
            else:
                path="/code/export-control-statistics-original-data/sorted-for-automated-handling/du+bmg-tracker/" + f[0]
            
            with open(path, newline='') as of:
                r = re.findall(r"[0-9]+", f[0])
                s = [int(x) for x in r]
                b=datetime.date(s[0], s[1], s[2])
                e=datetime.date(s[3], s[4], s[5])
                
                reader = csv.reader(of)
                for line in reader:
                    if(f[1] == "elic"):
                        # line has new elic format, for which this method was written, so requires no transformations
                        # Geschäftsnummer, Bestimmungsland, Güterart, Geschäftstyp, Richtung, Exportkontrollnummer [EKN], Wert [CHF]
                        pass
                    elif(f[1] == "trackerV1"):
                        # line has old "tracker" format and needs to be transformed into new format
                        #Geschäftstyp, Bewilligungsnummer, Richtung, Bewilligungsdatum, Bestimmungsland, Catch-All, AG (GKV), MTCR (GKV), NSGI (GKV), NSGII (GKV), WA (GKV), ML (GKV), Anhang 5.1, Anhang 5.2, Anhang 5.3, ChKV, Wert
                        if(len(line) < 17):
                            print("Line is too short: " + str(line))
                            continue
                        
                        if(line[11] != ""):
                            # it's special military goods

                            d=line[3].split("/")
                            if(len(d) != 3):
                                print("Line (trackerV1) has no date: " + str(line))
                                continue

                            if(int(d[2]) < 95):
                                d[2] = int(d[2]) + 2000
                            b=datetime.date(int(d[2]), int(d[0]), int(d[1]))
                            if(b.year < 1995 or b.year > 2013):
                                print("TrackerV1: " + str(line))
                                assert(False)
                            e=b

                            line = [line[1], line[4], "Besondere militärische Güter", "", "", line[11], line[16]]

                    elif(f[1] == "trackerV2"):
                        # line has old "tracker" format and needs to be transformed into new format
                        #Geschäftsnummer, Bewilligungsdatum, Endverbraucherland, AG (GKV), MTCR (GKV), NSGI (GKV), NSGII (GKV),	WA (GKV), ML (GKV), Anhang 5.1,	Anhang 5.2,	Anhang 5.3, ChKV, Wert
                        if(len(line) < 14):
                            print("Line is too short: " + str(line))
                            continue

                        if(line[8] != ""):
                            # it's special military goods

                            d=line[1].split("-")
                            if(len(d) != 3):
                                print("Line (trackerV2) has no date: " + str(line))
                                continue
                            if(int(d[2]) < 95):
                                d[2] = int(d[2]) + 2000
                            b=datetime.date(int(d[2]), int(d[0]), int(d[1]))
                            if(b.year < 2011 or b.year > 2023):
                                print("TrackerV2: " + str(line))
                                assert(False)
                            e=b

                            line = [line[0], line[2], "Besondere militärische Güter", "", "", "ML" + line[8], line[13]]

                    else:
                        # it's some kind of goods which doesn't interest us now
                        line=["","",""]

                    if(line[2] == "Besondere militärische Güter"):
                        code = line[5]
                        code = code.splitlines()[0] # sometimes there are multiple codes. need to complain about that
                        code = code.lower()
                        code = code.replace("ml", "ML")
                        code = code.replace("0", "")
                        if(code[-1] != "."):
                            code += "."
                        code = re.sub(r"(\.|ML)([0-9]+)([a-z]+)\.", r"\1\2.\3.", code)
                        code = re.sub(r"(\.|ML)([a-z]+)([0-9]+)\.", r"\1\2.\3.", code)
                        code = re.sub(r"(\.|ML)([0-9]+)([a-z]+)([0-9]+)\.", r"\1\2.\3.\4.", code)
                        code = re.sub(r"(\.|ML)([a-z]+)([0-9]+)([a-z]+)\.", r"\1\2.\3.\4.", code)

                        # specific possible typos in the official lists:
                        code = code.replace("ML8.5.b.1.", "ML8.c.5.b.1.")
                        if(code in ["ML1.c.2.", "ML1.g.", "ML1.f."]):
                            continue
                            # no idea what those codes are supposed to mean, skip

                        try:
                            ekn=Exportkontrollnummern.objects.get(nummer=code, kontrollregime__name__en=kontrollregimeName)
                        except geschaefte.Exportkontrollnummern.DoesNotExist:
                            print("Export control code \"" + code + "\" could not be found (original: \"" + line[5] + "\" in file " + path + " for country " + line[1] + ").")
                            continue
                        
                        try:
                            land = Laender.fuzzyGet(line[1], "de")
                        except Laender.DoesNotExist:
                            print("Country does not exist: " + str(line))
                            continue

                        line[0] = line[0].replace("A/", "")
                        
                        g=Geschaefte(
                            nummer=int(line[0]),
                            endempfaengerstaat=land,
                            exportkontrollnummer=ekn,
                            umfang=float(line[6]),
                            beginn=b,
                            ende=e
                        )
                        g.save()
