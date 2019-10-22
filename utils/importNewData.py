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
from pprint import pprint
from datetime import date
import calendar

# Zuerst .xlsx zu csv konvertieren, z.B. mit xlsx2csv (pip install ..., Konsolenanwendung)

# ML importieren (also Geschäfte Zeilenweise)
def MLImport():
  for year in []:
    for quarter in []:
      with open('/home/t4b/persönlich/engagement/gsoa/webseite/django/kriegsmaterialch/utils/original-statistiken/Dual Use und besondere militärische Güter/csv-konvertiert/' + str(year) + '-' + str(quarter) + ' Erteilte Ausfuhrbewilligungen.csv', newline='') as f:
        reader = csv.reader(f)
        rows = iter(reader)
        next(rows)
        for row in rows:
          pprint(row)
          GeschaefteCSVImport(None, # pk
                              *(row[:7]),
                              False,
                              date(year, (quarter-1)*3+1, 1),
                              date(year, quarter*3, calendar.monthrange(year, quarter*3)[1])
                              ).save()
# KM importieren (jedes Feld ist ein "Geschäft"), erste Zeile enthält ein leeres Feld gefolgt von den ekn der spalten, die nächsten Zeilen haben das Land auf Deutsch gefolgt von Exporten in Franken für die ekn der Spalte, leere Zellen bedeuten 0.
def KMImport():
  for year in []:
    with open('/home/t4b/km-stat/kriegsmaterialch/utils/original-statistiken/Kriegsmaterial/csv-konvertiert/' + str(year) + '.csv', newline='') as f:
      reader = csv.reader(f)
      rows = iter(reader)
      header = next(rows)
      pprint(header)
      for row in rows:
        for i in range(1, len(row)):
          volume = row[i]
          if(volume!=""):
            GeschaefteCSVImport(None, # pk
                                "", # number
                                row[0], # state
                                "Kriegsmaterial",
                                "Einzelbewilligung",
                                "Ausfuhr",
                                header[i], # ekn
                                volume,
                                False, # already imported
                                date(year, 1, 1), # begin
                                date(year, 12, 31) # end
                                ).save()
          else:
            print("empty")
  for year in []:
    for quarter in []:
      with open('/home/t4b/km-stat/kriegsmaterialch/utils/original-statistiken/Kriegsmaterial/csv-konvertiert/' + str(year) + '-' + str(quarter) +  '.csv', newline='') as f:
        reader = csv.reader(f)
        rows = iter(reader)
        header = next(rows)
        pprint(header)
        for row in rows:
          for i in range(1, len(row)):
            volume = row[i]
            if(volume!=""):
              GeschaefteCSVImport(None, # pk
                                  "", # number
                                  row[0], # state
                                  "Kriegsmaterial",
                                  "Einzelbewilligung",
                                  "Ausfuhr",
                                  header[i], # ekn
                                  volume,
                                  False, # already imported
                                  date(year, (quarter-1)*3+1, 1), # begin
                                  date(year, quarter*3, calendar.monthrange(year, quarter*3)[1]) # end
                                  ).save()
            else:
              print("empty")
