from exportkontrollstatistiken.models import *

einzelbewilligung=Bewilligungstypen.objects.get(name=Uebersetzungen.objects.get(de="Einzelbewilligung"))
ausfuhr=Geschaeftsrichtungen.objects.get(name=Uebersetzungen.objects.get(de="Ausfuhr"))
for g in GeschaefteCSVImport.objects.filter(importiert=False):
  if(g.bewilligungstyp != 'Einzelbewilligung'):
    continue
  if(g.richtung != 'Ausfuhr'):
    continue
  try:
    land = Laender.objects.get(name__de=g.endempfaengerstaat)
  except Laender.DoesNotExist:
    print(g.endempfaengerstaat + " misspelled or missing")
    continue
  
  if(g.gueterArt != 'Besondere militärische Güter'):
    continue
  # TODO
  try:
    ekn=Exportkontrollnummern.objects.get(nummer=g.ekn)
  except Exportkontrollnummern.DoesNotExist:
    print(g.ekn + " missing or wrong")
    continue
  try:
    Geschaefte(endempfaengerstaat=land, bewilligungstyp=einzelbewilligung, richtung=ausfuhr, exportkontrollnummer=g.ekn, umfang=g.betrag, beginn=g.beginn, ende=g.ende)
    #g.save()
    g.importiert = True
  except:
    continue

for g in GeschaefteCSVImport.objects.filter(importiert=False):
  for char in ['.']:
    if(g.ekn not in ["5.1", "5.2"]):
      g.ekn = g.ekn.replace(char, '')
  g.endempfaengerstaat = g.endempfaengerstaat.replace('Mazedonien (ehemalige jugoslawische Republik)', 'Republik Nordmazedonien')
  g.save()

# get an overview
for g in GeschaefteCSVImport.objects.filter(importiert=False):
  try:
    ekn = Exportkontrollnummern.objects.get(nummer=g.ekn)
  except Exportkontrollnummern.DoesNotExist:
    print(g.ekn)
  except Exportkontrollnummern.MultipleObjectsReturned:
    print(g.ekn + " exists multiple times:")
    for gd in GeschaefteCSVImport.objects.filter(nummer=g.ekn):
      print(gd)

# import ML EKN
ekns = set()
for g in GeschaefteCSVImport.objects.filter(importiert=False):
  if(g.ekn[0:2]=='ML'):
    ekns.add(g.ekn)

eknsLower = set()
for ekn in ekns:
  eknsLower.add('ML' + ekn[2:].lower())

for ekn in eknsLower:
  print(ekn)
