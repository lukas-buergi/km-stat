NICHT AUSFÜHREN - das ist kein fertiges Skript, nur Schnipsel für die interaktive Konsole

from exportkontrollstatistiken.models import *
import csv
from pprint import pprint
from datetime import date
import calendar

# Zuerst .xlsx zu csv konvertieren, z.B. mit xlsx2csv (pip install ..., Konsolenanwendung)

# ML importieren:

GeschaefteCSVImport.objects.all().delete()
for year in [2016, 2017, 2018]:
  for quarter in [1, 2, 3, 4]:
    with open('/home/t4b/persönlich/engagement/gsoa/webseite/django/kriegsmaterialch/utils/original-statistiken/Dual Use und besondere militärische Güter/Erteilte Ausfuhrbewilligungen/' + str(year) + '-' + str(quarter) + ' Erteilte Ausfuhrbewilligungen.csv', newline='') as f:
      reader = csv.reader(f)
      rows = iter(reader)
      next(rows)
      for row in rows:
        pprint(row)
        GeschaefteCSVImport(None,
                            *(row[:7]),
                            False,
                            date(year, (quarter-1)*3+1, 1),
                            date(year, quarter*3, calendar.monthrange(year, quarter*3)[1])
                            ).save()
# fertig, jetzt normalisieren...
