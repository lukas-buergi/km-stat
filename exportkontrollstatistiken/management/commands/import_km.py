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
import re
from exportkontrollstatistiken.models import *
import csv

from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help="""Warning: Can make a mess in the DB. Have backups.
    
    Imports the km export statistics from the csv files."""

    def handle(self, **options):
        prefix='/code/export-control-statistics-original-data/sorted-for-automated-handling/km-nach-kategorie-pro-endempf-staat/'
        files=[
            '2002-01-01-2002-12-31.csv',
            '2004-01-01-2004-12-31.csv',
            '2005-01-01-2005-12-31.csv',
            '2006-01-01-2006-12-31.csv',
            '2007-01-01-2007-12-31.csv',
            '2008-01-01-2008-12-31.csv',
            '2009-01-01-2009-12-31.csv',
            '2010-01-01-2010-12-31.csv',
            '2011-01-01-2011-12-31.csv',
            '2012-01-01-2012-12-31.csv',
            '2013-01-01-2013-12-31.csv',
            '2014-01-01-2014-12-31.csv',
            '2015-01-01-2015-12-31.csv',
            '2016-01-01-2016-12-31.csv',
            '2017-01-01-2017-12-31.csv',
            '2018-01-01-2018-12-31.csv',
            '2019-01-01-2019-12-31.csv',
#            '2020-01-01-2020-03-31.csv',
#            '2020-01-01-2020-06-30.csv',
#            '2020-01-01-2020-09-30.csv',
            '2020-01-01-2020-12-31.csv',
#            '2021-01-01-2021-03-31.csv',
#            '2021-01-01-2021-06-30.csv',
            '2021-01-01-2021-09-30.csv',
        ]

        header = ["Land", "Pays", "KM1", "KM2", "KM3", "KM4", "KM5", "KM6", "KM7", "KM8", "KM9", "KM10", "KM11", "KM12", "KM13", "KM14", "KM15", "KM16", "KM17", "KM18", "KM19", "K20", "KM21", "KM22"]

        prevQuarterEnd = {
            (12,31) : (9,30),
            (9,30) : (6,30),
            (6,30) : (3,31)
        }

        krname = "SR 514.511 Anhang 1 (KMV) 2022-01-01"
        kontrollregime = Kontrollregimes.objects.get(name__de=krname)
        Geschaefte.objects.filter(exportkontrollnummer__kontrollregime=kontrollregime).delete()

        lastYear = 0
        for f in files:
            r = re.findall(r"[0-9]+", f)
            s = [int(x) for x in r]
            b=datetime.date(s[0], s[1], s[2])
            e=datetime.date(s[3], s[4], s[5])
            
            path = prefix + f
            with open(path, newline='') as of:
                reader = csv.DictReader(of, restval=0)
                for row in reader:
                    try:
                        Land=Laender.fuzzyGet(row["Land"], "de")
                    except Laender.DoesNotExist:
                        print(path)
                        print("Country does not exist: " + str(row))

                    for key, value in row.items():
                        if(key in ["Land", "Pays"]):
                            continue

                        if(value == ""):
                            value = 0
                        else:
                            value = value.replace("'", "")
                            value = float(value)
                        
                        key = re.sub(r"^[^0-9]*([0-9]+)[^0-9]*$", r"KM\1.", key)

                        try:
                            ekn = Exportkontrollnummern.objects.get(kontrollregime=kontrollregime, nummer=key)
                        except Exportkontrollnummern.DoesNotExist:
                            if(value != 0):
                                print("EKN does not exist: " + str(key))
                            continue
                        
                        if(b.year > lastYear):
                            g = Geschaefte(
                                endempfaengerstaat = Land,
                                exportkontrollnummer = ekn,
                                umfang = value,
                                beginn = b,
                                ende = e
                            )
                            g.save()
                        elif(b.year == lastYear):
                            lastGP = {
                                "endempfaengerstaat" : Land,
                                "exportkontrollnummer" : ekn,
                                "beginn" : b,
                                "ende" : datetime.date(e.year, *prevQuarterEnd[(e.month, e.day)])
                                }
                            try:
                                lastG = Geschaefte.objects.get(**lastGP)
                            except Geschaefte.DoesNotExist:
                                #print("Previous transaction not found: " + str(lastGP))
                                #print("Assumg it was 0.")
                                lastG = type('X', (), dict(umfang=0, beginn=b, ende=lastGP["ende"]))
                            except Geschaefte.MultipleObjectsReturned:
                                print("Multple transactions returned - choosing first one.")
                                print(Geschaefte.objects.filter(**lastGP))

                            g = Geschaefte(
                                endempfaengerstaat = Land,
                                exportkontrollnummer = ekn,
                                umfang = value - lastG.umfang,
                                beginn = lastG.ende + datetime.timedelta(days=1),
                                ende = e
                            )
                            g.save()
                        else:
                            print("Must go through exports by increasing date.")
                            assert(False)
            lastYear = b.year
