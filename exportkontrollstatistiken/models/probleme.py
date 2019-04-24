from django.db import models
from django.conf import settings

from .geschaefte import Geschaefte
from .utility import Uebersetzungen
from .utility import Laender

class QuellenProbleme(models.Model):
  """ Quellen für jedes Problem, als Link. """
  link = models.URLField()
  linkText = models.CharField(max_length=200)
  sprache = models.CharField(max_length=2)
  """ Code für die Sprache der Quelle, DE, FR, IT, EN. """
  
  def __str__(self):
    if(self.linkText != ""):
      return(str(self.linkText))
    else: # Ich glaube nicht dass das eine gute Lösung ist, andererseits sollte der Fall eh nicht eintreten. TODO
      return("QuellenProbleme " + self.pk)
  
  class Meta:
    verbose_name = 'Quelle für Probleme'
    verbose_name_plural = 'Quellen für Probleme'

class ProblemArtenGesetz(models.Model):
  """ Liste der Gesetzesabschnitte, die Gründe enthalten, warum Exporte verboten werden. """
  gesetz = models.CharField(max_length=30)
  """ Gesetz in Kurzschreibweise wie "514.511 5 IId". Dann kann man automatisch eine sprachabhängige längere Variante generieren. """
  
  class Meta:
    verbose_name = 'Gesetz das Problemart stützt'
    verbose_name_plural = 'Gesetze die Problemarten stützten'

class ProblemArten(models.Model):
  """ Kategorisierung der Probleme unter anderem nach Erwähnung in KMV. Einträge sollten mindestens sein:
  * KMV 5 Ic: Geht es da drum das Land mit Waffen zu fördern? Glaub das lassen wir weg
  * Trägt das Land zum Erhalt des Friedens, der internationalen Sicherheit und der regionalen Stabilität bei? (KMV 5 Ia)
  * Exportieren andere Länder da nicht hin? (KMV 5 Ie)
  * Hält das Land Völkerrecht ein? (KMV 5 Id)
  * Respektiert das Land die Menschenrechte mehr oder weniger? (KMV 5 Ib)
  * Hat das Land Kindersoldaten? (KMV 5 Ib)
  * Verletzt das Land die Menschenrechte schwerwiegend und systematisch (KMV 5 IIb)
  * Internationaler bew. Konflikt (KMV 5 IIa)
  * Gibt es ein hohes Risiko, dass das Kriegsmaterial gegen die Zivilbevölkerung eingesetzt wird? (KMV 5 IId)
  * Interner bew. Konflikt (KMV 5 IIa)
  * Gibt es ein hohes Risiko, dass das Kriegsmaterial unerlaubt weitergegeben wird? (KMV 5 IIe)

  Gute Quellen dafür sind mindestens:
  * AI Berichte zur Menschenrechtslage
  * Uppsala Conflict Data Program https://ucdp.uu.se"""
  kurzbeschreibung = models.ForeignKey(Uebersetzungen, on_delete=models.PROTECT)
  """ Kurze Beschreibung des Problems. """
  gesetz = models.ForeignKey(ProblemArtenGesetz, blank=True, null=True, on_delete=models.PROTECT)
  """ Gesetz in dem das Problem als Problem bezeichnet wird, falls es eines gibt. """
  ausschlusskriterium = models.BooleanField()
  """ Ob das Problem im Gesetz als Ausschlusskriterium bezeichnet wird. """
  faktor = models.FloatField()
  """ Ein Faktor um Geschäfte grob nach Schlimme zu sortieren. Die Sortierung wird nicht öffentlich so bezeichnet oder als Sortierreihenfolge angeboten, sondern nur dann verwendet, wenn sonst noch keine Reihenfolge ausgewählt wurde. Dafür wird der Umfang des Geschäfts mit dem Faktor multipliziert. Zwischen 1 und 2 inklusiv. Falls ausschlusskriterium wahr ist, gibt es einen zusätzlichen Faktor 2. """
  
  class Meta:
    verbose_name = 'Problemart'
    verbose_name_plural = 'Problemarten'

class Probleme(models.Model):
  """ Jeder Eintrag enthält einen konkreten Grund, warum man in ein bestimmtes Land in einem Zeitraum nicht hätte exportieren sollten. Wird in einem Diagramm den tatsächlichen Exporten gegenüber gestellt. """

  land = models.ForeignKey(Laender, on_delete=models.PROTECT)
  """ Das betroffene Land. """
  beginn = models.DateField()
  """ Beginn des Problems. """
  ende = models.DateField()
  """ Ende des Problems. """
  betroffenesGeschaeft = models.ForeignKey(Geschaefte, blank=True, null=True, on_delete=models.PROTECT)
  """ Falls man ein bestimmtes Geschäft dem Problem zuweisen kann, zum Beispiel bei Korruption bei dem Geschäft, dann kommt hier ein Verweis auf das Geschäft. Man kann bewusst nur auf ein Geschäft verweisen. Wenn allgemein alle in dem Zeitraum betroffen sind (also keines spezifisch), dann bleibt das Feld leer. """
  art = models.ForeignKey(ProblemArten, on_delete=models.PROTECT)
  """ Grobe Kategorisierung des Problems, die bei der Darstellung und so hilft. """
  zusammenfassung = models.ForeignKey(Uebersetzungen, on_delete=models.PROTECT)
  """ Zusammenfassung in wenigen Sätzen. """
  quellen = models.ManyToManyField(QuellenProbleme)
  """ Quellen, zum Beispiel Zeitungsberichte. Vorzugsweise mehrere für jede Sprache. """
  
  class Meta:
    verbose_name = 'Problem'
    verbose_name_plural = 'Probleme'
