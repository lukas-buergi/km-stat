from django.db import models
from django.conf import settings

import datetime
from .utility import *

class Bewilligungstypen(models.Model):
  """ Ob es für das Geschäft oder die Geschäfte eine (oder mehrere) Einzelbewilligungen gebraucht hat, oder nicht. Für Kriegsmaterial braucht es immer eine Einzelbewilligung, sonst gibt es eine Liste von Ländern, für die es keine braucht. Wie heisst die andere Art von Bewilligung? Siehe 514.51 12ff"""
  name = models.ForeignKey(Uebersetzungen, on_delete=models.PROTECT)
  
  def __str__(self):
    if(self.name != ""):
      return(str(self.name))
    else: # Ich glaube nicht dass das eine gute Lösung ist, andererseits sollte der Fall eh nicht eintreten. TODO
      return("Bewilligungstypen " + self.pk)
  
  class Meta:
    verbose_name = 'Bewilligungstyp'
    verbose_name_plural = 'Bewilligungstypen'

class Geschaeftsrichtungen(models.Model):
  """ Ausfuhr, Vermittlung, etc. Sehr theoretisch, habe bisher nur Ausfuhr gesehen. """
  name = models.ForeignKey(Uebersetzungen, on_delete=models.PROTECT)
  """ Ausfuhr, Vermittlung, etc. Sehr theoretisch, habe bisher nur Ausfuhr gesehen. """
  
  def __str__(self):
    if(self.name != ""):
      return(str(self.name))
    else: # Ich glaube nicht dass das eine gute Lösung ist, andererseits sollte der Fall eh nicht eintreten. TODO
      return("Geschaeftsrichtungen " + self.pk)
  
  class Meta:
    verbose_name = 'Geschäftsrichtung'
    verbose_name_plural = 'Geschäftsrichtungen'


class QuellenGeschaefte(models.Model):
  """ Offizielle Quelle für jedes Geschäft. Eine Quelle ist normalerweise Quelle für viele Geschäfte."""

  name = models.ForeignKey(Uebersetzungen, on_delete=models.PROTECT)
  """ Der Name der Quelle, wie der Text des Downloadlinks auf der Secowebseite. Falls die eigentliche Quelle nur Deutsch ist, dann bei den anderen Sprachen zusätzlich Warnung, dass die Quelle Deutsch ist, "(allemand)". """

  download = models.FileField(upload_to='quellenGeschaefte/')
  """ Die Datei, die die Quelle darstellt. Eigene Kopie für den Fall, dass das Seco die Adressen ändert oder so. TODO: Sollte wohl validiert werden, dass die Dateien harmlos sind, obwohl der Upload ja nur von vertrauenswürdigen Menschen kommen sollte. """

  link = models.URLField(max_length=3000)
  """ Link auf die Secoseite, wo der Downloadlink sein sollte. Nicht direkt auf die Datei. Die Adressen des Seco sind sehr lang (mindestens 1500 Zeichen lang gibt es) und es braucht hier eine maximale Länge."""

  def __str__(self):
    if(self.name != ""):
      return(str(self.name))
    else: # Ich glaube nicht dass das eine gute Lösung ist, andererseits sollte der Fall eh nicht eintreten. TODO
      return("QuellenGeschaefte " + self.pk)
  
  class Meta:
    verbose_name = 'Quelle für Geschäfte'
    verbose_name_plural = 'Quellen für Geschäfte'

class GueterArten(models.Model):
  """ Warum das Gut reguliert wird.
  * Kriegsmaterial
  * Besondere militärische Güter - oder einfach nur Kriegsmaterial? Wenn man es separat macht kann man es nachher immer noch gleich anzeigen.
  * Dual use
  * Sanktionsgüter - Das sollte wohl normalerweise ausgenommen werden von den Totalen, oder?"""
  name = models.ForeignKey(Uebersetzungen, on_delete=models.PROTECT)
  
  def __str__(self):
    if(self.name != ""):
      return(str(self.name))
    else: # Ich glaube nicht dass das eine gute Lösung ist, andererseits sollte der Fall eh nicht eintreten. TODO
      return("GueterArten " + self.pk)
  
  class Meta:
    verbose_name = 'Güterart'
    verbose_name_plural = 'Güterarten'

class Kontrollregimes(models.Model):
  """ Die verschiedenen Kontrollregimes:
  * KMV (Kriegsmaterial): Anhang 1, KM1-KM22
  * GKV/GKG (946.202 Gesetz, 946.202.1
 Verordnung, zivil und militärisch verwendbare Güter, besondere militärische Güter sowie strategische Güter):
    * Anhänge 1 und 2: Dual Use, MTCR, NSG, CWÜ, Australische Gruppe: [0-9][A-Z][0-9]{3}[a-z][0-9]+
    * Anhang 3: bes. mil. Güter, ML1-ML22
    * Anhang 4: strategische Güter, LEER
    * Anhang 5: k.A., "Güter, die nationalen Ausfuhrkontrollen unterliegen", https://www.admin.ch/opc/de/classified-compilation/20151950/index.html#app4ahref1
  * ChKV (946.202.21, Chemikalien für Chemiewaffen):
    * Liste 1-3: abnehmende Gefährlichkeit, Form [1-3][AB][0-9]+, aber vielleicht haben diese Sachen auch eine Nummer in GKV Anhang 2 Teil 2 um 1C350 rum.
  * Safeguardsverordnung (732.12, gegen nukleare Proliferation): Keine Liste (?), es geht nur um wenige Güter die im Gesetzestext definiert sind.
  * Verordnung über die Ausfuhr und Vermittlung von Gütern zur Internet- und Mobilfunküberwachung (946.202.3): Im Anhang sind GKN aus GKV Anhang 2 aufgelistet
  * EmbG (946.231, Embargos, nicht unbedingt irgendwas mit Kriegsmaterial im weistesten Sinn, oder?): Keine Ahnung wo die Listen sind. """
  name = models.ForeignKey(Uebersetzungen, on_delete=models.PROTECT)
  gueterArt = models.ForeignKey(GueterArten, on_delete=models.PROTECT)
  inkrafttreten = models.DateField()
  aufgehobenwerden = models.DateField(blank=True, null=True)
  
  def __str__(self):
    if(self.name != ""):
      return(str(self.name))
    else: # Ich glaube nicht dass das eine gute Lösung ist, andererseits sollte der Fall eh nicht eintreten. TODO
      return("Kontrollregimes " + self.pk)
  
  class Meta:
    verbose_name = 'Kontrollregime'
    verbose_name_plural = 'Kontrollregimes'

class Exportkontrollnummern(models.Model):
  """ Enthält die Anhänge mit den Beschreibungen der Nummern. Die Beschreibung wird erst bei Gelegenheit eingelesen, aber zumindest die Nummern selbst braucht es bevor ein Geschäft mit dieser Nummer eingetragen wird. """
  kontrollregime = models.ForeignKey(Kontrollregimes, on_delete=models.PROTECT)
  """ Zu welchem Kontrollregime die Nummer gehört. Vor allem relevant falls es doppelte Nummern gibt oder der Inhalt der Listen geändert wird (dann würde man ein neues Kontrollregime erstellen und da eintragen). """
  nummer = models.CharField(max_length=15)
  """ Die Nummer. """
  beschreibung = models.ForeignKey(Uebersetzungen, on_delete=models.PROTECT, blank=True, null=True)
  """ Die Beschreibung aus der Liste. Ich bin nicht sicher ob die übersetzt werden, falls nicht bleiben die anderen Spalten der fehlenden Sprachen halt leer. Ist zumindest vorerst optional."""
  
  def __str__(self):
    if(self.nummer != ""):
      return(str(self.nummer))
    else: # Ich glaube nicht dass das eine gute Lösung ist, andererseits sollte der Fall eh nicht eintreten. TODO
      return("Exportkontrollnummern " + self.pk)
  
  class Meta:
    verbose_name = 'Exportkontrollnummer'
    verbose_name_plural = 'Exportkontrollnummern'

class Geschaefte(models.Model):
  """ Ein Eintrag steht für ein oder mehrere Geschäfte, je nach Datenlage. Die Daten gibt es von
  * https://www.seco.admin.ch/seco/de/home/Aussenwirtschaftspolitik_Wirtschaftliche_Zusammenarbeit/Wirtschaftsbeziehungen/exportkontrollen-und-sanktionen/industrieprodukte--dual-use--und-besondere-militaerische-gueter/statistik/2015.html
  * https://www.seco.admin.ch/seco/de/home/Aussenwirtschaftspolitik_Wirtschaftliche_Zusammenarbeit/Wirtschaftsbeziehungen/exportkontrollen-und-sanktionen/ruestungskontrolle-und-ruestungskontrollpolitik--bwrp-/zahlen-und-statistiken0.html """
  
  nummer = models.PositiveIntegerField(blank=True, null=True)
  """ Offizielle Geschäftsnummer, wo vorhanden. Bei Statistiken wo diese Nummer nicht vorhanden ist steht ein Eintrag für mehrere Geschäfte """
  endempfaengerstaat = models.ForeignKey(Laender, on_delete=models.PROTECT)
  """ Ist bei allen verwendeten Statistiken Endempfängerstaat, nicht Bestimmungsland, oder? - TODO: Genau herausfinden und hier verbessern."""  
  bewilligungstyp = models.ForeignKey(Bewilligungstypen, on_delete=models.PROTECT)
  """ Einzelbewilligung. Alles andere ist nicht implementiert."""
  richtung = models.ForeignKey(Geschaeftsrichtungen, on_delete=models.PROTECT)
  """ Ausfuhr. Alles andere ist nicht implementiert. """
  exportkontrollnummer = models.ForeignKey(Exportkontrollnummern, on_delete=models.PROTECT) # TODO: make manytomany
  """ Was wurde exportiert? Vielleicht sollten da mehrere Nummern erlaubt sein, weil ein Gut vielleicht unter mehrere Kontrollregime fallen kann. """
  umfang = models.PositiveIntegerField()
  """ Umfang des Geschäfts in Schweizer Franken. """
  beginn = models.DateField()
  """ Der Beginn des Geschäfts. Normalerweise der 1. Januar des Jahres, weil nichts genaueres bekannt ist. """
  ende = models.DateField()
  """ Das Ende des Geschäftes. Geschäfte können über mehrere Jahren gehen stand irgendwo auf der Secowebseite (macht ja Sinn). Ich schätze das sieht man bei neueren Statistiken an der Nummer und bei älteren wurde das Geschäft wahrscheinlich nur in einem Jahr einbezogen nehme ich an (keine Ahnung). """
  quelle = models.ForeignKey(QuellenGeschaefte, on_delete=models.PROTECT, blank=True, null=True)
  """ Die offizielle Quelle für den Eintrag. Ich glaube es gibt die immer nur auf Deutsch, sonst müsste man das noch anpassen um auch die anderen anzubieten. """

  @staticmethod
  def getJSON(p):
    cnames = ['Datum', 'Art', 'EKN', 'Umfang']
    ctypes = ['untreated', 'untreated', 'untreated', 'money']
    if(True): # not p.countriesSingle
      cnames = ['Ländercode', 'Land'] + cnames
      ctypes = ['country code', 'country name'] + ctypes
    result = apiData(False, cnames, ctypes)

    queryset = Geschaefte.objects.filter(ende__gte=datetime.date(p.year1, 1, 1))
    queryset = queryset.filter(beginn__lte=datetime.date(p.year2, 12, 31))
    queryset = queryset.filter(p.getTypes("exportkontrollnummer__kontrollregime__gueterArt__name"))
    queryset = queryset.filter(p.countries)

    result.setTotal(queryset.count())
    
    queryset = queryset.order_by(p.sortBy)
    
    for g in p.getPage(queryset):
      row=[str(g.beginn), g.exportkontrollnummer.kontrollregime.gueterArt.name.de, g.exportkontrollnummer.nummer, g.umfang]
      if(g.exportkontrollnummer.beschreibung != None and g.exportkontrollnummer.beschreibung.de!=""):
        row[2]=g.exportkontrollnummer.beschreibung.de
      if(not p.countriesSingle):
        row = [g.endempfaengerstaat.code, g.endempfaengerstaat.name.de] + row
      result.addRow(row)

    return(result.getJSON())

  @staticmethod
  def getJSONSummedPerYear(p):
    """Return transactions summed per year. Algorithm:
      * sort by country, year
      * sum up consecutive entries until country or year changes
      * sort according to p.sortBy, but only certain combinations are valid:
        * date asc+des, for a single country (that's the original order after the summing algorithm)
        * value"""
    
    queryset = Geschaefte.objects.filter(ende__gte=datetime.date(p.year1, 1, 1))
    queryset = queryset.filter(beginn__lte=datetime.date(p.year2, 12, 31))
    queryset = queryset.filter(p.getTypes("exportkontrollnummer__kontrollregime__gueterArt__name"))
    queryset = queryset.filter(p.countries)
    
    if(p.sortBy in ["beginn","-beginn"]):
      firstSort=p.sortBy
    else:
       # in that case it can be either because later it's sorted again anyway
      firstSort="beginn"
      
    queryset = queryset.order_by("endempfaengerstaat", firstSort)

    sums=dict()
    curCountry = None
    curYear = None
    for g in queryset:
      if(g.endempfaengerstaat!=curCountry or g.beginn.year!=curYear):
        curCountry = g.endempfaengerstaat
        curYear = g.beginn.year
        curSum = g.umfang
        sums[str(curCountry) + str(curYear)] = [curSum, curYear, curCountry]
      else:
        sums[str(curCountry) + str(curYear)][0] += g.umfang

    reverse=None
    if(p.sortBy == "-umfang"):
      reverse=True
    elif(p.sortBy == "umfang"):
      reverse=False
    
    if(reverse==None):
      order=sums.keys()
      # need this so order is an array in both cases
    else:
      order=sorted(sums, key=lambda key : sums.get(key)[0], reverse=reverse)

    result = apiData(False, ["id", "Name", "Jahr", "Exporte"], ['country code', 'country name', 'untreated', 'money'])
    result.setTotal(len(order))
    for country in p.getPage(order):
      result.addRow([sums[country][2].code, sums[country][2].name.de, sums[country][1], sums[country][0]])
    return(result.getJSON())
      
  def __str__(self):
    return(str(self.beginn)+"-"+str(self.endempfaengerstaat)+"-"+str(self.exportkontrollnummer)+"-"+str(self.umfang))
  
  class Meta:
    verbose_name = 'Geschäft'
    verbose_name_plural = 'Geschäfte'

