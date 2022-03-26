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

from django.db import models
from django.conf import settings
import json

# does this belong here?
class apiData():
  """The data that is returned by an API query. Methods to add data and return json of accumulated data. Does some sanity checks on the data.
  The JSON contains exactly the following dict:
    {
    'total' : amount of results on all pages
    'cnames' : [column title 1, ..., column title n,],
    'ctypes' :   [ country code, country name, date, money, untreated ],
    'countries' :
      {
        'country code 1' : 0,
        'country code 2' : 1,
        ...
        'country code m' : m-1,
      }
    'data' :
      [
        [data country 1 column 1, ..., data country 1 column n],
        ...
        [data country m column 1, ..., data country m column n],
      ]
    }
  The 'ctypes' entry has the types of the columns in order.
  The 'countries' entry exists only if we know the countries are unique in all data rows and need to index the data by country. """
  
  """This attribute is the one that is converted to json and sent."""
  def __init__(self, uniqueCountry, columnNames, columnTypes):
    self.data = dict()
    assert(len(columnNames) == len(columnTypes))
    if(uniqueCountry):
      self.data['countries'] = dict()
      self.uniqueCountry = True
    else:
      self.uniqueCountry = False
    self.data['total'] = None
    self.data['cnames'] = columnNames
    self.data['ctypes'] = columnTypes
    self.countryCodeColumn = None
    for (index, t) in enumerate(columnTypes):
      if(t=='country code'):
        if(self.countryCodeColumn == None):
          self.countryCodeColumn = index
        else:
          # doesn't make sense to have multiple
          raise(ValueError)
    if(self.countryCodeColumn == None):
      raise(ValueError)
      
    self.data['data'] = []

  def addRow(self, row):
    if(self.uniqueCountry):
      self.data['countries'][row[self.countryCodeColumn]] = len(self.data['data'])
    self.data['data'].append(row)

  def addRows(self, rows):
    for row in rows:
      self.addRow(row)

  def setTotal(self, total):
    self.data['total'] = total
  
  def getJSON(self):
    """ Returns a string that is the JSON representation of self.data. """
    if(self.data['total'] == None):
      raise(RuntimeError("Need to know a total."))
    if(settings.DEBUG):
      return(json.dumps(self.data, indent=2))
    else:
      return(json.dumps(self.data, separators=(',', ':')))

class Uebersetzungen(models.Model):
  """ Enthält alles, was übersetzt werden muss. """

  de = models.TextField(blank=True)
  fr = models.TextField(blank=True)
  it = models.TextField(blank=True)
  en = models.TextField(blank=True)

  def __str__(self):
    """ Sollte je nach Spracheinstellung die richtige Sprache zurückgeben und dann auf andere Sprachen zurückfallen wenn es diese nicht gibt. TODO. """
    if(self.de!=""):
      return(self.de)
    else:
      return(self.en)

  class Meta:
    verbose_name = 'Übersetzung'
    verbose_name_plural = 'Übersetzungen'

class Laendergruppen(models.Model):
  """ Groups of countries for easy selection, say "Africa", "European Union" or "Middle East". """
  
  name = models.ForeignKey(Uebersetzungen, on_delete=models.PROTECT)
  """ Name of the group. """
  
  code = models.CharField(max_length=2)
  """ Two character made up id. It's ok if they collide with country codes."""
  
  seco_km_order = models.PositiveIntegerField()
  """ The Seco doesn't order continents alphabetically, so we order by this field to mirror Seco's ordering. """

  def __str__(self):
    return(self.code)
  
  class Meta:
    verbose_name = 'Ländergruppe'
    verbose_name_plural = 'Ländergruppen'

class Laender(models.Model):
  """ Liste der Länder, in die exportiert wird. """
  
  code = models.CharField(max_length=2)
  """ The ISO 3166-1 alpha-2 code for the country. The current data might or might not be standards-compliant."""
  
  name = models.ForeignKey(Uebersetzungen, on_delete=models.PROTECT)
  """ Voller Name des Landes. """
  
  gruppen = models.ManyToManyField(Laendergruppen)
  """ Groups that this country is a member of. """
  
  breitengradMin = models.FloatField()
  """ Der minimale Breitengrad, der dieses Land schneidet. """
  
  breitengradMax = models.FloatField()
  """ Der maximale Breitengrad, der dieses Land schneidet. """
  
  laengengradMin = models.FloatField()
  """ Der minimale Längengrad, der dieses Land schneidet. """
  
  laengengradMax = models.FloatField()
  """ Der maximale Längengrad, der dieses Land schneidet. """
  
  latitude = models.FloatField()
  """ Latitude of a characteristic point of the country. """
  
  longitude = models.FloatField()
  """ Longitude of a characteristic point of the country. """


  def __str__(self):
    return(self.code)
  
  @staticmethod
  def fuzzyGet(name, language):
    if(language=='de'):
      corrections = [
        [['Mazedonien (ehemalige jugoslawische Republik)', 'Nordmazedonien, Republik', 'Nordmazedonien', 'Mazedonien, die ehemalige jugoslawische Republik'], 'Republik Nordmazedonien'],
        [['Korea, Republik (Südkorea)', 'Korea (Süd)', 'Korea, Republik'], 'Republik Korea'],
        [['Korea, Demokratische Volksrepublik'], 'Demokratische Volksrepublik Korea'],
        [['China', 'China, Volksrepublik'], 'Volksrepublik China'],
        [['China, Taiwan', 'Taiwan, Provinz von China'], 'Republik China (Taiwan)'],
        [['Bosnien-Herzegowina', 'Bosnien und Herzeg.', 'Bosnien', 'Bosnien-Herzeg.'], 'Bosnien und Herzegowina'], ## AAAaaah, Bosnien is not the same as B und H, but...
        [['Rwanda'], 'Republik Ruanda'],
        [['Elfenbeinküste'], 'Republik Côte d’Ivoire'],
        [['Ekuador'], 'Republik Ecuador'],
        [['Moldova', 'Moldau, Republik', 'Moldau'], 'Republik Moldova'],
        [['Fidschi'], 'Republik Fidschi'],
        [['Vatikan', 'Vatikanstadt'], 'Staat Vatikanstadt'],
        [['Albanien'], 'Republik Albanien'],
        [['Kongo, Republik', 'Zaïre'], 'Republik Kongo'],
        [['Somalia'], 'Bundesrepublik Somalia'],
        [['Georgien, Republik'], 'Georgien'],
        [['Trinidad und Tobago'], 'Republik Trinidad und Tobago'],
        [['Djibouti'], 'Republik Dschibuti'],
        [['Myanmar (Union)'], 'Republik der Union Myanmar'],
        [['Macau', 'Macao'], 'Sonderverwaltungszone Macau der Volksrepublik China'],
        [['Arabische Emirate', 'Arab. Emirate', 'VAE'], 'Vereinigte Arabische Emirate'],
        [['USA', 'U.S.A', 'Vereinigte Staaten'], 'Vereinigte Staaten von Amerika'],
        [['Dominikanische Rep', 'Dom. Rep.'], 'Dominikanische Republik'],
        [['Tschechische Rep.', 'Tschechien'], 'Tschechische Republik'],
        [['Slowakei', 'Slowakei, Slowakische Republik', 'Slowakai', 'Slowakische Rep.'], 'Slowakische Republik'],
        [['Katar', 'Qatar'], 'Staat Katar'],
        [['Bangladesh', 'Bangladesch'], 'Volksrepublik Bangladesch'],
        [['Neukaledonien', 'Frankreich (inkl. Monaco)', 'Frankreich (mit Monaco)', 'Neukaledonien', 'Frankreich mit Monaco'], 'Frankreich'], # Neukaledonien hier zu Frankreich ist nehmen ist... na ja.
        [['Großbritannien (Vereinigtes Königreich)', 'Gr. Britannien'], 'Grossbritannien'],
        [['Brunei Darussalam'], 'Brunei'],
        [['Ecuador'], 'Republik Ecuador'],
        [['Tansania, Vereinigte Republik', 'Tansania'], 'Vereinigte Republik Tansania'],
        [['Serbia'], 'Serbien'],
        [['Saudi Arabien'], 'Saudi-Arabien'],
        [['Bhutan', 'Buthan'], 'Königreich Bhutan'],
        [['Finnnland'], 'Finnland'],
        [['Burkina Fasso'], 'Burkina Faso'],
        [['Bahrein', 'Bahrain'], 'Königreich Bahrain'],
        [['Aegypten'], 'Ägypten'],
        [['Kirgistan'], 'Kirgisische Republik'],
        [['Kap Verde'], 'Republik Cabo Verde'],
        [['Russland'], 'Russische Föderation'],
        [['Iran', 'Iran, Islamische Republik'], 'Islamische Republik Iran'],
        [['Kroatien', 'Kroatien (Hrvatska)'], 'Republik Kroatien'],
        [['Syrien', 'Syrien, Arabische Republik'], 'Syrische Arabische Republik'],
        [['Hong Kong'], 'Hongkong'],
        [['Mauritius'], 'Republik Mauritius'],
        [['Eritrea'], 'Staat Eritrea'],
        [['Burundi'], 'Republik Burundi'],
        [['Norfolk-Inseln', 'Norfolkinsel'], 'Australien'],
        [['Mosambik'], 'Republik Mosambik'],
        [['Grönland'], 'Dänemark'], # na jaaaa...
        [['Zimbabwe'], 'Republik Simbabwe'],
        [['Libysch-Arabische Dschamahirija', 'Libyen'], 'Staat Libyen'] # same borders, but where did the weapons go in the transition?
      ]

      name = name.strip()

      for c in corrections:
        if(name in c[0]):
          name=c[1]
          break
  
    return(Laender.objects.get(**{"name__" + language : name}))
      
  class Meta:
    verbose_name = 'Land'
    verbose_name_plural = 'Länder'