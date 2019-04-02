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
# pk 21099, 21100, 21104, 21971 in der alten Datenbank haben zwei EKN, die zweite EKN hat im Schema keinen Platz und wurde gelöscht
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
