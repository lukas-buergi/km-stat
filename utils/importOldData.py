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

# kriegsmaterial importieren
for i in [1,2,3,4,5,6,7,8,10,16]:
  ekn=Exportkontrollnummern.objects.get(nummer="KM" + str(i))
  bewTyp=Bewilligungstypen.objects.get(name=Uebersetzungen.objects.get(de="Einzelbewilligung"))
  richtung=Geschaeftsrichtungen.objects.get(name=Uebersetzungen.objects.get(de="Ausfuhr"))
  for g in GeschaefteImport.objects.filter(kategorie="KM" + str(i)):
    land=Laender.objects.get(code=g.code)
    Geschaefte(endempfaengerstaat=land, bewilligungstyp=bewTyp, richtung=richtung, exportkontrollnummer=ekn, umfang=g.betrag, beginn=g.datum, ende=g.datum).save()

# kriegsmaterial aus alter Datenbank löschen
for i in [1,2,3,4,5,6,7,8,10,16]:
  for g in GeschaefteImport.objects.filter(kategorie="KM" + str(i)):
    g.delete()

# datenbank aufräumen, Wert ersetzen Beispiel
for g in GeschaefteImport.objects.filter(kategorie="01a"):
  g.kategorie="1a"
  g.save()
for g in GeschaefteImport.objects.filter(art="Besondere militärische Güter"):
  g.kategorie=g.kategorie.lower().lstrip("0").replace("ML","").replace(".","")
  g.save()


# bes. mil. Güter importieren
# pk 21099, 21100, 21104, 21971 in der alten Datenbank haben zwei EKN, die zweite EKN hat im Schema keinen Platz und wurde gelöscht TODO
mlekn = set()
for g in GeschaefteImport.objects.filter(art="Besondere militärische Güter"):
  mlekn.add(g.kategorie)
for ekn in mlekn:
  Exportkontrollnummern(kontrollregime=Kontrollregimes.objects.get(name=Uebersetzungen.objects.get(de="946.202.1 Anhang 3")), nummer="ML" + ekn).save()

einzelbewilligung=Bewilligungstypen.objects.get(name=Uebersetzungen.objects.get(de="Einzelbewilligung"))
ausfuhr=Geschaeftsrichtungen.objects.get(name=Uebersetzungen.objects.get(de="Ausfuhr"))
for g in GeschaefteImport.objects.filter(art="Besondere militärische Güter"):
  land=Laender.objects.get(code=g.code)
  ekn=Exportkontrollnummern.objects.get(nummer="ML" + g.kategorie)
  Geschaefte(endempfaengerstaat=land, bewilligungstyp=einzelbewilligung, richtung=ausfuhr, exportkontrollnummer=ekn, umfang=g.betrag, beginn=g.datum, ende=g.datum).save()

# dual use importieren
# TODO

for g in GeschaefteImport.objects.filter(kategorie="3B.5, 1C350.2"):
  g.kategorie="3B.5"
  g.save()
for g in GeschaefteImport.objects.filter(kategorie="3B.7, 1C350.38"):
  g.kategorie="3B.7"
  g.save()
for g in GeschaefteImport.objects.filter(kategorie="3B.9, 1C350.30"):
  g.kategorie="3B.9"
  g.save()
for g in GeschaefteImport.objects.filter(art="Dual-Use-Güter"):
  g.kategorie=g.kategorie.replace(".","")
  g.save()
for g in GeschaefteImport.objects.filter(kategorie="51"):
  g.kategorie="5.1"
  g.save()
for g in GeschaefteImport.objects.filter(kategorie="52"):
  g.kategorie="5.2"
  g.save()
for g in GeschaefteImport.objects.filter(kategorie="2b"):
  g.kategorie="2B"
  g.save()
for g in GeschaefteImport.objects.filter(kategorie="3A001A7A"):
  g.kategorie="3A001a7a"
  g.save()
for g in GeschaefteImport.objects.filter(kategorie="6A005B6A"):
  g.kategorie="6A005b6a"
  g.save()
for g in GeschaefteImport.objects.filter(kategorie="3B14, 1C3509"):
  g.kategorie="3B14"
  g.save()
  


# Anhang 5 import
einzelbewilligung=Bewilligungstypen.objects.get(name=Uebersetzungen.objects.get(de="Einzelbewilligung"))
ausfuhr=Geschaeftsrichtungen.objects.get(name=Uebersetzungen.objects.get(de="Ausfuhr"))
for g in GeschaefteImport.objects.filter(system="Anhang 5"):
  land=Laender.objects.get(code=g.code)
  ekn=Exportkontrollnummern.objects.get(nummer=g.kategorie)
  Geschaefte(endempfaengerstaat=land, bewilligungstyp=einzelbewilligung, richtung=ausfuhr, exportkontrollnummer=ekn, umfang=g.betrag, beginn=g.datum, ende=g.datum).save()

# ChKV import
duImport = GeschaefteImport.objects.filter(art="Dual-Use-Güter").filter(system="ChKV")
DUekn = set()
for g in duImport:
  DUekn.add(g.kategorie)

for ekn in DUekn:
  Exportkontrollnummern(kontrollregime=Kontrollregimes.objects.get(name=Uebersetzungen.objects.get(de="946.202.21")), nummer=ekn).save()

einzelbewilligung=Bewilligungstypen.objects.get(name=Uebersetzungen.objects.get(de="Einzelbewilligung"))
ausfuhr=Geschaeftsrichtungen.objects.get(name=Uebersetzungen.objects.get(de="Ausfuhr"))
for g in duImport:
  land=Laender.objects.get(code=g.code)
  ekn=Exportkontrollnummern.objects.get(nummer=g.kategorie)
  Geschaefte(endempfaengerstaat=land, bewilligungstyp=einzelbewilligung, richtung=ausfuhr, exportkontrollnummer=ekn, umfang=g.betrag, beginn=g.datum, ende=g.datum).save()

# NSGI, NSGII, Wassenaar import
duImport = GeschaefteImport.objects.filter(art="Dual-Use-Güter").filter(system__in=["NSGI", "NSGII", "Wassenaar"])
DUekn = set()
for g in duImport:
  DUekn.add(g.kategorie)

for ekn in set(DUekn):
  commaPos = ekn.find(",")
  if(commaPos != -1):
    print("comma removed from " + ekn)
    DUekn.remove(ekn)
    DUekn.add(ekn[0:commaPos])
    print("new: " + ekn)

for ekn in DUekn:
  Exportkontrollnummern(kontrollregime=Kontrollregimes.objects.get(name=Uebersetzungen.objects.get(de="946.202.1 Anhang 2")), nummer=ekn).save()


einzelbewilligung=Bewilligungstypen.objects.get(name=Uebersetzungen.objects.get(de="Einzelbewilligung"))
ausfuhr=Geschaeftsrichtungen.objects.get(name=Uebersetzungen.objects.get(de="Ausfuhr"))
for g in duImport:
  land=Laender.objects.get(code=g.code)
  ekn=Exportkontrollnummern.objects.filter(kontrollregime__name=Uebersetzungen.objects.get(de="946.202.1 Anhang 2")).get(nummer=g.kategorie)
  Geschaefte(endempfaengerstaat=land, bewilligungstyp=einzelbewilligung, richtung=ausfuhr, exportkontrollnummer=ekn, umfang=g.betrag, beginn=g.datum, ende=g.datum).save()
