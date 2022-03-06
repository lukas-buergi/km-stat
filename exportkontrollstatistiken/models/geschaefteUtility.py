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
import django.core.files

from .utility import *
from .geschaefte import Laender
from .geschaefte import GueterArten
from .geschaefte import Geschaefte
from .geschaefte import QuellenGeschaefte

import types
import itertools
import csv
from datetime import date
import calendar
import os

class Geschaeftslaendersummen(models.Model):
  """Utility model which contains partial sums per country, year and export type.
  TODO: Neues Feld für nur die Summe von dem Jahr.
  TODO: Did I do this?"""
  
  endempfaengerstaat = models.ForeignKey(Laender, on_delete=models.PROTECT)
  """ As for individual Geschaefte. """
  
  jahr = models.PositiveIntegerField()
  """ The year of the given partial sum. """

  gueterArt = models.ForeignKey(GueterArten, on_delete=models.PROTECT)
  """ As for individual Geschaefte. """
  
  umfang = models.PositiveIntegerField()
  """ Partial sum of exports up to and including that year."""

  umfangJahr = models.PositiveIntegerField()
  """ Sum of exports only in the year of this entry. """
  

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
            umfangJahr=g.umfang,
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
      print(ysum.endempfaengerstaat.code + " : " + str(ysum.endempfaengerstaat.id))
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

class GeschaefteKriegsmaterialNachKategorieEndempfaengerstaat(models.Model):
  """
  Contains sums of arms exports. The entries for a period are assumed to contain the total for that period, except that multiple periods with the same starting point and different end points are assumed to be partial sums of each other.
  Mirrors the structure of the official documents "Ausfuhr von Kriegsmaterial nach Kategorie pro Endempfängerstaat" exactly,
  but do already regularize the data and add structure from text fields.
  Import from csv files works as follows:

  * csv files generated either from official xlsx, or using the "tabula" utility from pdf files, or manually from pdf files without text information.
  * csv files could be validated to an extent, and official complaints/requests filed if data is self-contradictory or (hopefully more likely) mistake in copying from original fixed.
  * The csv files are then imported as follows:
      * First row: Headers
      * Second row: totals ignored
      * Rows that are identical to the header except for the first field are ignored
      * Rows that have no country are ignored (they are totals of previous countries)
      * First column: Contains continent or nothing. If nothing, choose last continent that was encountered.
      * Second column: Country name in German, use to determine country
      * Third column: Country name in French, ignore
      * Middle columns: Sums of exports in a category, exact category depends on header row
      * Last column: Always ignored, contains totals of row

  Display in the admin backend is then customized to also mirror the official document to allow efficient visual checks of imported data.
  The data can then be imported into the regular Geschaefte table completely automatically. """

  checked = models.ManyToManyField(ManualCheck)
  """
  After importing a quarter's transactions, should visually compare display in admin interface with official source (as linked in sources field) and record this here.
  """
  
  sources = models.ManyToManyField(QuellenGeschaefte)
  """
  Should give the official source, and the intermediary csv file (to make fixing errors easier).
  """

  fromDate = models.DateField()
  toDate = models.DateField()
  
  continent = models.ForeignKey(Laendergruppen, on_delete=models.PROTECT)
  """
  This is duplicate information because the continent is known from the country, but we mirror the offical document.
  If the country field isn't in the Laendergruppe continent, then throw some error.
  """
  
  country = models.ForeignKey(Laender, on_delete=models.PROTECT)


  kms = [ "KM1", "KM2", "KM3", "KM4", "KM5", "KM6", "KM7", "KM8", "KM9", "KM10", "KM11", "KM12", "KM13", "KM14", "KM15", "KM16", "KM17", "KM18", "KM19", "KM20", "KM21", "KM22" ]
  KM1 = models.PositiveIntegerField(null=True, blank=True)
  KM2 = models.PositiveIntegerField(null=True, blank=True)
  KM3 = models.PositiveIntegerField(null=True, blank=True)
  KM4 = models.PositiveIntegerField(null=True, blank=True)
  KM5 = models.PositiveIntegerField(null=True, blank=True)
  KM6 = models.PositiveIntegerField(null=True, blank=True)
  KM7 = models.PositiveIntegerField(null=True, blank=True)
  KM8 = models.PositiveIntegerField(null=True, blank=True)
  KM9 = models.PositiveIntegerField(null=True, blank=True)
  KM10 = models.PositiveIntegerField(null=True, blank=True)
  KM11 = models.PositiveIntegerField(null=True, blank=True)
  KM12 = models.PositiveIntegerField(null=True, blank=True)
  KM13 = models.PositiveIntegerField(null=True, blank=True)
  KM14 = models.PositiveIntegerField(null=True, blank=True)
  KM15 = models.PositiveIntegerField(null=True, blank=True)
  KM16 = models.PositiveIntegerField(null=True, blank=True)
  KM17 = models.PositiveIntegerField(null=True, blank=True)
  KM18 = models.PositiveIntegerField(null=True, blank=True)
  KM19 = models.PositiveIntegerField(null=True, blank=True)
  KM20 = models.PositiveIntegerField(null=True, blank=True)
  KM21 = models.PositiveIntegerField(null=True, blank=True)
  KM22 = models.PositiveIntegerField(null=True, blank=True)

  class Meta:
    verbose_name = 'Geschäft: Kriegsmaterial, tatsächliche Ausfuhren, Format ähnlich Seco'
    verbose_name_plural = 'Geschäfte: Kriegsmaterial, tatsächliche Ausfuhren, Format ähnlich Seco'
    
  @staticmethod
  def importCSV(path, pathOriginal, urlOriginal, fromYear, fromMonth, fromDay, toYear, toMonth, toDay):
    """
    Imports a .csv files given by string path, containing data fromDate toDate which are date()-objects.
    """
    try:
      with open(path, newline='') as f:
        fromDate=date(fromYear, fromMonth, fromDay)
        toDate=date(toYear, toMonth, toDay)
        # add this file as a source database entry, one for csv and one for original format, both using url
        # csv
        F=django.core.files.File(f)
        F.name = "KM-" + fromDate.isoformat() + "-" + toDate.isoformat() + ".csv"
        nameCSV = Uebersetzungen(de='Kriegsmaterial, tatsächliche Ausfuhren, ' + fromDate.isoformat() + " bis " + toDate.isoformat() + ", in inoffiziellem .csv Format.")
        nameCSV.save()
        sourceCSV=QuellenGeschaefte(
          name=nameCSV,
          download=F,
          link=urlOriginal
        )
        sourceCSV.save()
        # original
        with open(pathOriginal, "rb") as fo:
          FO=django.core.files.File(fo)
          FO.name = "KM-" + fromDate.isoformat() + "-" + toDate.isoformat() + os.path.splitext(pathOriginal)[1]
          nameOfficial = Uebersetzungen(de='Kriegsmaterial, tatsächliche Ausfuhren, ' + fromDate.isoformat() + " bis " + toDate.isoformat() + ", in diesem Format vom Staatssekretariat für Wirtschaft Seco bekommen.")
          nameOfficial.save()
          sourceOfficial=QuellenGeschaefte(
            name=nameOfficial,
            download=FO,
            link=urlOriginal
          )
          sourceOfficial.save()
        
        # parse the file into database entries
        f.seek(0)
        reader = csv.reader(f)
        rows = iter(reader)
        header = next(rows)
        categoryNames = header[3:-1]
        second = next(rows)
        lastContinentDE = None
        for row in rows:
          if(row[1:] == header[1:]):
            # repetition of header
            continue
          if(row[1] == ""):
            # German country name is missing, French should be missing too
            assert(row[2] == "")
            # country is empty, skip subtotals line
            continue
          if(row[0] == ""):
            continentDE = lastContinentDE
          else:
            continentDE = row[0].split()[0]
            lastContinentDE = continentDE
          try:
            continent = Laendergruppen.objects.get(name__de=continentDE)
          except:
            print("Not found: " + str(continentDE))
            raise
          countryDE = row[1]
          country = Laender.fuzzyGet(countryDE, 'de')
          
          databaseRow = GeschaefteKriegsmaterialNachKategorieEndempfaengerstaat(
            fromDate=fromDate,
            toDate=toDate,
            continent=continent,
            country=country
          )
          rowCategories = row[3:-1]
          for value, name in zip(rowCategories, categoryNames):
            if(value == ""):
              value=0
            setattr(databaseRow, name, value)
          databaseRow.save()
          databaseRow.sources.add(sourceCSV, sourceOfficial)
    except:
      # some of those are going to fail, but deletion order should match creation order so that later deletes aren't necessary
      try:
        GeschaefteKriegsmaterialNachKategorieEndempfaengerstaat.objects.filter(fromDate=fromDate, toDate=toDate).delete()
      except:
        pass
      try:
        sourceCSV.delete()
      except:
        pass
      try:
        nameCSV.delete()
      except:
        pass
      try:
        nameOfficial.delete()
      except:
        pass
      try:
        sourceOfficial.delete()
      except:
        pass

  def __sub__(self, other):
    assert(self.fromDate == other.fromDate)
    assert(self.country == other.country)
    assert(self.continent == other.continent)
    new = GeschaefteKriegsmaterialNachKategorieEndempfaengerstaat(
      fromDate=other.toDate+1,
      toDate=self.toDate,
      country=self.country,
      continent=self.continent)
      
    for km in GeschaefteKriegsmaterialNachKategorieEndempfaengerstaat.kms:
      if(self.getattr(km) == None and other.getattr(km) == None):
        continue
      if(self.getattr(km) == None):
        self.setattr(km, 0)
      if(other.getattr(km) == None):
        other.setattr(km, 0)
      
  
  @staticmethod
  def toGeschaefte():
    """
    Put checked transactons into the main transaction table, discarding the existing entries for this time period.
    Unchecked entries are ignored.
    Algorithm:
      * For each country:
      * For each transaction, sorted by start date (arbitrary), end date (descending)
      * First: Do nothing
      * If the start date doesn't change: Add transaction for difference between end dates
      * Else: Add previous row as is
      *   
    """
    for country in Laender.objects.all():
      transactions = iter(GeschaefteKriegsmaterialNachKategorieEndempfaengerstaat.objects.filter(country=country).order_by('fromDate', '-toDate'))
      lastRow = next(transactions)
      for row in transactions:
        if(row.fromDate == lastRow.fromDate):
          # add lastRow minus row
          for km in row.kms:
            if(lastRow.getattr(km) == None):
              assert(row.getattr(km) == None)
              diff=0
            else:
              diff=lastRow.getattr(km)
              if(row.getattr(km) != None):
                diff -= row.getattr(km)
            g=Geschaefte(
              endempfaengerstaat=country,
              bewilligungstyp=Bewilligungstypen.get(name__de="Einzelbewilligung"),
              richtung=Geschaeftsrichtungen.get(name_de="Bewilligungstypen"),
              exportkontrollnummer=Exportkontrollnummern.get(nummer=km),
              umfang=diff,
              beginn=row.toDate+datetime.timedelta(days=1),
              ende=lastRow.toDate
            )
            g.save()
            g.sources.add(row.sources, lastRow.sources)
        else:
          # add lastRow as is, don't do anything with current row
          pass
        lastRow = row
      # add lastRow as is
  
  def validate(self):
    """
    Do various validation steps:
      * Check country is in continent
      
    """
    for g in GeschaefteKriegsmaterialNachKategorieEndempfaengerstaat.objects.all():
      assert(g.continent in g.country.Laendergruppen)
