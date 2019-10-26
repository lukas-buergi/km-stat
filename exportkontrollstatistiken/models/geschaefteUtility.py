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

from .utility import *
from .geschaefte import Laender
from .geschaefte import GueterArten
from .geschaefte import Geschaefte

class Geschaeftslaendersummen(models.Model):
  """Hilfsmodell, das Teilsummen pro Land, Jahr und Güterart enthält. TODO: Neues Feld für nur die Summe von dem Jahr."""
  endempfaengerstaat = models.ForeignKey(Laender, on_delete=models.PROTECT)
  """ Wie bei einzelnen Geschäften. """
  gueterArt = models.ForeignKey(GueterArten, on_delete=models.PROTECT)
  """ Wie bei einzelnen Geschäften. """
  umfang = models.PositiveIntegerField()
  """Summe aller Exporte bis zu dem Jahr inklusive."""
  umfangJahr = models.PositiveIntegerField()
  """ Summe aller Exporte in dem Jahr. """
  jahr = models.PositiveIntegerField()

  @staticmethod
  def recalculate():
    """Delete all entries and calculate new entries from Geschaefte entries.
    This needs to be run after any relevant changes to the Geschaefte entries.
    So it's not performance-relevant, allowed to run for tens of seconds or longer."""
    Geschaeftslaendersummen.objects.all().delete()
    geschaefte = Geschaefte.objects.all().order_by("endempfaengerstaat", "exportkontrollnummer__kontrollregime__gueterArt", "beginn")

    # get the first separately
    firstG = next(geschaefte.__iter__())
    curSum = Geschaeftslaendersummen(
      endempfaengerstaat=firstG.endempfaengerstaat,
      gueterArt=firstG.exportkontrollnummer.kontrollregime.gueterArt,
      umfang=firstG.umfang,
      umfangJahr=firstG.umfang,
      jahr=firstG.beginn.year)
    curSum.save()
    # then iterate over the rest
    for g in geschaefte:
      if(g.beginn.year!=curSum.jahr):
        if(g.endempfaengerstaat!=curSum.endempfaengerstaat or g.exportkontrollnummer.kontrollregime.gueterArt!=curSum.gueterArt):
          # start calculating partial sums for new country+type combination
          curSum = Geschaeftslaendersummen(
            endempfaengerstaat=g.endempfaengerstaat,
            gueterArt=g.exportkontrollnummer.kontrollregime.gueterArt,
            umfang=g.umfang,
            umfangJahr=g.umfang,
            jahr=g.beginn.year)
          curSum.save()
        else:
          # new year, but same row of partial sums
          curSum = Geschaeftslaendersummen(
            endempfaengerstaat=g.endempfaengerstaat,
            gueterArt=g.exportkontrollnummer.kontrollregime.gueterArt,
            umfang=curSum.umfang+g.umfang,
            umfangJahr=curSum.umfang,
            jahr=g.beginn.year)
          curSum.save()
      else:
        # same year+country+type, add
        curSum.umfang += g.umfang
        curSum.umfangJahr += g.umfang
        curSum.save()
    # now all the entries that change are here, but zero entries and
    # entries that have zero difference to the previous year are still missing
    for country in Laender.objects.all():
      for gueterArt in GueterArten.objects.all():
        cur=None
        for jahr in range(Geschaefte.getFirstYear()-1,
                          Geschaefte.getLastYear()+1):
          try:
            cur=Geschaeftslaendersummen.objects.filter(jahr=jahr, gueterArt=gueterArt, endempfaengerstaat=country).get()
          except Geschaeftslaendersummen.DoesNotExist:
            if(cur==None):
              cur=Geschaeftslaendersummen(endempfaengerstaat=country, gueterArt=gueterArt, jahr=jahr, umfang=0, umfangJahr=0)
              cur.save()
            else:
              # copy cur with new year
              cur.pk=None
              cur.jahr=jahr
              cur.umfangJahr=0
              cur.save()

  @staticmethod
  def getJSONSummed(p):
    """Sum transactions per country.

    Begin and end are both inclusive.

    Algorithm:
        * Get entries for year2 sorted by country
        * Get entries for (year1-1) sorted by country
        * Slice both of them correctly
        * Iterate through both sets in parallel
            * subtract the latter from the former in each entry
            * add up the selected types
        * Sort according to p.sortBy
    """
    # TODO BUG: This returns empty for du exports
    # TODO: I think I fixed this
    queryset2 = Geschaeftslaendersummen.objects.filter(jahr=p.year2)
    queryset2 = queryset2.filter(p.getTypes("gueterArt__name"))
    queryset2 = queryset2.filter(p.countries)
    queryset2 = queryset2.order_by("endempfaengerstaat")

    queryset1 = Geschaeftslaendersummen.objects.filter(jahr=(p.year1-1))
    queryset1 = queryset1.filter(p.getTypes("gueterArt__name"))
    queryset1 = queryset1.filter(p.countries)
    queryset1 = queryset1.order_by("endempfaengerstaat")
    # TODO: Should I make a method for the above duplicate code?

    # TODO: This can be done more elegantly with the new apiData class
    sums = dict()
    for country in zip(queryset1, queryset2):
        if(country[0].endempfaengerstaat.code in sums):
            sums[country[0].endempfaengerstaat.code][1] += country[1].umfang - country[0].umfang
        else:
            sums[country[0].endempfaengerstaat.code]=[country[0].endempfaengerstaat, (country[1].umfang-country[0].umfang)]

    
    if(p.sortBy=="-umfang"):
        reverse=True
    else:
        reverse=False

    order = sorted(sums, key=lambda key : sums.get(key)[1], reverse=reverse)

    result = apiData(True, ["", "Name", "Exporte"], ['country code', 'country name', 'money'])
    result.setTotal(len(order))
    for country in p.getPage(order):
        result.addRow([country, sums[country][0].name.de, sums[country][1]])
    return(result.getJSON())

  @staticmethod
  def getJSONSummedPerYear(p):
    """Return transactions summed per year, sort according to p.sortBy (even if some combinations might not make much sense, they are available too for free). """

    result = apiData(False, ["", "Name", "Jahr", "Exporte"], ['country code', 'country name', 'untreated', 'money'])

    queryset = Geschaeftslaendersummen.objects
    queryset = queryset.filter(jahr__gte=p.year1)
    queryset = queryset.filter(jahr__lte=p.year2)
    queryset = queryset.filter(p.getTypes("gueterArt__name"))
    queryset = queryset.filter(p.countries)

    # TODO p class should probably be updated instead of translating the values here
    sortTrans = {
      'beginn' : 'jahr',
      '-beginn' : '-jahr',
      'umfang' : 'umfangJahr',
      '-umfang' : '-umfangJahr',
    }

    sort = sortTrans[p.sortBy]
    
    queryset = queryset.order_by(sort)
    
    result.setTotal(queryset.count())
    
    for ysum in p.getPage(queryset):
      result.addRow([ysum.endempfaengerstaat.code, ysum.endempfaengerstaat.name.de, ysum.jahr, ysum.umfangJahr])
    return(result.getJSON())

class Geschaeftssummen(models.Model):
  """Hilfsmodell, das Teilsummen pro Jahr und Güterart enthält."""
  gueterArt = models.ForeignKey(GueterArten, on_delete=models.PROTECT)
  umfang = models.PositiveIntegerField()
  """Summe aller Exporte bis zu dem Jahr inklusive."""
  jahr = models.PositiveIntegerField()

  def recalculate():
    """Delete all entries and calculate new entries Geschaeftssummen."""
    pass # TODO

class GeschaefteImport(models.Model):
  """Hilfsmodell zum Import der alten Daten, hat gleiche Struktur wie "export" Tabelle dort."""
  code = models.CharField(max_length=2)
  art = models.CharField(max_length=40)
  system = models.CharField(max_length=10)
  kategorie = models.CharField(max_length=15)
  datum = models.DateField()
  betrag = models.PositiveIntegerField()
  

class GeschaefteCSVImport(models.Model):
  """ Hilfsmodell zum Import von BMG, DU, etc. aus den Tabellendateien."""
  nummer = models.CharField(max_length=20)
  endempfaengerstaat = models.CharField(max_length=100)
  gueterArt = models.CharField(max_length=100)
  bewilligungstyp = models.CharField(max_length=100)
  richtung = models.CharField(max_length=100)
  ekn = models.CharField(max_length=100)
  umfang = models.CharField(max_length=100)
  importiert = models.BooleanField()
  beginn = models.DateField()
  ende = models.DateField()
