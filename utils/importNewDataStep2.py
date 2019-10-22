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
import re
from pprint import pprint

def importWassenaarML(ekn):
  if(ekn == ""):
    raise(ValueError("empty ekn not possible"))
    
  eknFormatted = ekn
  for char in ['.', ',', ':', ')', '(']:
    eknFormatted = eknFormatted.replace(char, '')

  tmp=eknFormatted
  parts = []
  letters = True
  while(len(tmp)!=0):
    if(letters):
      regex = '[a-zA-Z]+'
    else:
      regex = '[0-9]+'
    part = re.search(regex, tmp)
    if(part):
      part=part.group()
      part.lstrip('0') # UNTESTED: Should remove preceding 0s
      parts.append(part)
      tmp = tmp[part.end():]
      letters = not letters
    else:
      raise(ValueError(ekn + ' is not parseable'))
  
  parts[0] = parts[0].upper()
  if(parts[0] not in ['ML', 'KM']):
    raise(ValueError(ekn + ' must begin with ML or KM'))
  
  if(len(parts)<2):
    raise(ValueError(ekn + " is too short to be valid"))
  
  if(parts[0] == "KM"):
    gueterArt="Kriegsmaterial"
  else:
    gueterArt="Besondere militärische Güter"
  
  kontrollregime = Kontrollregimes.objects.get(gueterArt__name__de=gueterArt)
  toAdd = [parts[0]]
  while(toAdd != parts):
    toAdd.append(parts[len(toAdd)])
    number = ""
    for part in toAdd:
      number += part
    try:
      Exportkontrollnummern.objects.get(kontrollregime=kontrollregime, nummer=number)
      #print(number + " already exists, skipped")
    except Exportkontrollnummern.DoesNotExist:
      Exportkontrollnummern(kontrollregime=kontrollregime, nummer=number).save()
      #print(number + " added to database")
    except Exportkontrollnummern.MultipleObjectsReturned:
      print(number + " exists multiple times in DB")
  
  return(eknFormatted)

def importAll():
  einzelbewilligung=Bewilligungstypen.objects.get(name=Uebersetzungen.objects.get(de="Einzelbewilligung"))
  ausfuhr=Geschaeftsrichtungen.objects.get(name=Uebersetzungen.objects.get(de="Ausfuhr"))
  for g in GeschaefteCSVImport.objects.filter(importiert=False):
    if(g.bewilligungstyp != 'Einzelbewilligung'):
      # no support for this type of entry
      continue
    if(g.richtung != 'Ausfuhr'):
      # no support for this type of entry
      continue
      
    # correct previously encountered mistakes in country names
    corrections = [
      [['Mazedonien (ehemalige jugoslawische Republik)', 'Nordmazedonien, Republik'], 'Republik Nordmazedonien'],
      [['Korea, Republik (Südkorea)', 'Korea (Süd)'], 'Republik Korea'],
      [['China', 'China, Volksrepublik'], 'Volksrepublik China'],
      [['China, Taiwan'], 'Republik China (Taiwan)'],
      [['Bosnien-Herzegowina', 'Bosnien und Herzeg.'], 'Bosnien und Herzegowina'],
      [['Rwanda'], 'Republik Ruanda'],
      [['Elfenbeinküste'], 'Republik Côte d’Ivoire'],
      [['Ekuador'], 'Republik Ecuador'],
      [['Moldova'], 'Republik Moldova'],
      [['Fidschi'], 'Republik Fidschi'],
      [['Vatikan'], 'Staat Vatikanstadt'],
      [['Albanien'], 'Republik Albanien'],
      [['Kongo, Republik'], 'Republik Kongo'],
      [['Somalia'], 'Bundesrepublik Somalia'],
      [['Georgien, Republik'], 'Georgien'],
      [['Trinidad und Tobago'], 'Republik Trinidad und Tobago'],
      [['Djibouti'], 'Republik Dschibuti'],
      [['Myanmar (Union)'], 'Republik der Union Myanmar'],
      [['Macau', 'Macao'], 'Sonderverwaltungszone Macau der Volksrepublik China'],
      [['Arabische Emirate'], 'Vereinigte Arabische Emirate'],
      [['U.S.A'], 'Vereinigte Staaten von Amerika'],
      [['Dominikanische Rep'], 'Dominikanische Republik'],
      [['Tschechische Rep.'], 'Tschechische Republik'],
      [['Slowakei'], 'Slowakische Republik'],
      [['Katar', 'Qatar'], 'Staat Katar'],
      [['Bangladesh', 'Bangladesch'], 'Volksrepublik Bangladesch'],
    ]
    for c in corrections:
      if(g.endempfaengerstaat in c[0]):
        g.endempfaengerstaat=c[1]
        break
    
    try:
      land = Laender.objects.get(name__de=g.endempfaengerstaat)
    except Laender.DoesNotExist:
      print(g.endempfaengerstaat + " misspelled or missing")
      continue
    
    if(g.gueterArt in ['Kriegsmaterial', 'Besondere militärische Güter']):
      try:
        eknFormatted = importWassenaarML(g.ekn)
      except ValueError:
        print("skipping " + g.ekn)
        continue
      
      # in principle this must succeed, but no reason to remove extra checks
      try:
        ekn=Exportkontrollnummern.objects.get(nummer=eknFormatted)
      except Exportkontrollnummern.DoesNotExist:
        print(g.ekn + " missing or wrong")
        continue
      except Exportkontrollnummern.MultipleObjectsReturned:
        print(g.ekn + "multiple exist")
        continue
    else:
      continue

    g.umfang = g.umfang.replace('CHF', '')
    g.umfang = g.umfang.replace(',', '')
    g.umfang = g.umfang.strip()
    
    try:
      Geschaefte(endempfaengerstaat=land, bewilligungstyp=einzelbewilligung, richtung=ausfuhr, exportkontrollnummer=ekn, umfang=g.umfang, beginn=g.beginn, ende=g.ende).save()
      g.importiert = True
      g.save()
    except:
      raise
