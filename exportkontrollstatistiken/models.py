from django.db import models

class Geschaefte(models.Model):
	""" Ein Eintrag steht für ein oder mehrere Geschäfte, je nach Datenlage. """
	
	nummer = model.PositiveIntegerField(blank=True, null=True)
	""" Offizielle Geschäftsnummer, wo vorhanden. Bei älteren Statistiken wo diese Nummer nicht vorhanden ist steht ein Eintrag für mehrere Geschäfte """
	bestimmungsland = model.ForeignKey(Laender, on_delete=PROTECT)
	""" Bestimmungsland oder Endempfängerstaat - TODO: Unterschied genau herausfinden und hier verbessern."""
	kontrollregime = model.ForeignKey(Kontrollregimes, on_delete=PROTECT)
	""" Gesetzliche Grundlage für die Kontrolle, Kriegsmaterial, bes. mil. Güter, etc. Im Prinzip steht das bei der Exportkontrollnummer auch schon. Lassen?"""
	typ = model.ForeignKey(Geschaeftstypen, on_delete=PROTECT)
	""" Einzelbewilligung oder sonst etwas? """
	richtung = model.ForeignKey(Geschaeftsrichtungen, on_delete=PROTECT)
	""" Ausfuhr, Vermittlung, sonstwas? """
	exportkontrollnummer = model.ForeignKey(Exportkontrollnummern, on_delete=PROTECT)
	""" Was wurde exportiert? Vielleicht sollten da mehrere Nummern erlaubt sein, weil ein Gut vielleicht unter mehrere Kontrollregime fallen kann. """
	umfang = model.PositiveIntegerField()
	""" Umfang des Geschäfts in Schweizer Franken. """
	beginn = model.DateField()
	""" Der Beginn des Geschäfts. Normalerweise der 1. Januar des Jahres, weil nichts genaueres bekannt ist. """
	ende = model.DateField()
	""" Das Ende des Geschäftes. Geschäfte können über mehrere Jahren gehen stand irgendwo auf der Secowebseite (macht ja Sinn). Ich schätze das sieht man bei neueren Statistiken an der Nummer und bei älteren wurde das Geschäft wahrscheinlich nur in einem Jahr einbezogen nehme ich an (keine Ahnung). """
	quelle = model.ForeignKey(QuellenGeschaefte, on_delete=PROTECT)
	""" Die offizielle Quelle für den Eintrag. Ich glaube es gibt die immer nur auf Deutsch, sonst müsste man das noch anpassen um auch die anderen anzubieten. """

class Probleme(models.Model):
	""" Jeder Eintrag enthält einen konkreten Grund, warum man in ein bestimmtes Land in einem Zeitraum nicht hätte exportieren sollten. Wird in einem Diagramm den tatsächlichen Exporten gegenüber gestellt. """

	land = model.ForeignKey(Laender, on_delete=PROTECT)
	""" Das betroffene Land. """
	beginn = model.DateField()
	""" Beginn des Problems. """
	ende = model.DateField()
	""" Ende des Problems. """
	betroffenesGeschaeft = model.ForeignKey(Geschaefte, blank=True, null=True)
	""" Falls man ein bestimmtes Geschäft dem Problem zuweisen kann, zum Beispiel bei Korruption bei dem Geschäft, dann kommt hier ein Verweis auf das Geschäft. Man kann bewusst nur auf ein Geschäft verweisen. Wenn allgemein alle in dem Zeitraum betroffen sind (also keines spezifisch), dann bleibt das Feld leer. """
	art = model.ForeignKey(Problemarten)
	""" Grobe Kategorisierung des Problems, die bei der Darstellung und so hilft. """
	zusammenfassung = model.ForeignKey(Uebersetzungen)
	""" Zusammenfassung in wenigen Sätzen. """
	quellen = model.ManyToManyField(QuellenProbleme)
	""" Quellen, zum Beispiel Zeitungsberichte. Vorzugsweise mehrere für jede Sprache. """

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
	* Gibt es ein hohes Risiko, dass das Kriegsmaterial unerlaubt weitergegeben wird? (KMV 5 IIe)"""
	kurzbeschreibung = model.ForeignKey(Uebersetzungen)
	""" Kurze Beschreibung des Problems. """
	gesetz = model.ForeignKey(ProblemArtenGesetz, blank=True, null=True)
	""" Gesetz in dem das Problem als Problem bezeichnet wird, falls es eines gibt. """
	ausschlusskriterium = model.BooleanField()
	""" Ob das Problem im Gesetz als Ausschlusskriterium bezeichnet wird. """
	faktor = model.FloatField()
	""" Ein Faktor um Geschäfte grob nach Schlimme zu sortieren. Die Sortierung wird nicht öffentlich so bezeichnet oder als Sortierreihenfolge angeboten, sondern nur dann verwendet, wenn sonst noch keine Reihenfolge ausgewählt wurde. Dafür wird der Umfang des Geschäfts mit dem Faktor multipliziert. Zwischen 1 und 2 inklusiv. Falls ausschlusskriterium wahr ist, gibt es einen zusätzlichen Faktor 2. """

class ProblemArtenGesetz(models.Model):
	""" Liste der Gesetzesabschnitte, die Gründe enthalten, warum Exporte verboten werden. """
	gesetz = model.CharField(max_length=30)
	""" Gesetz in Kurzschreibweise wie "KMV 5 IId". TODO: Übersetzung?"""

class QuellenGeschaefte(models.Model):
	""" Offizielle Quelle für jedes Geschäft. Eine Quelle ist normalerweise Quelle für viele Geschäfte."""
	name = model.ForeignKey(Uebersetzungen)
	""" Der Name der Quelle, wie der Text des Downloadlinks auf der Secowebseite. Falls die eigentliche Quelle nur Deutsch ist, dann bei den anderen Sprachen zusätzlich Warnung, dass die Quelle Deutsch ist, "(allemand)". """
	download = model.FileField()
	""" Die Datei, die die Quelle darstellt. Eigene Kopie für den Fall, dass das Seco die Adressen ändert oder so. TODO: Sollte wohl validiert werden, dass die Dateien harmlos sind, obwohl der Upload ja nur von vertrauenswürdigen Menschen kommen sollte. """
	link = model.URLField()
	""" Link auf die Secoseite, wo der Downloadlink sein sollte. Nicht direkt auf die Datei. """

class QuellenProbleme(models.Model):
	""" Quellen für jedes Problem, als Link. """
	link = model.URLField()
	linkText = model.CharField(max_length=200)
	sprache = model.CharField(max_length=2)
	""" Code für die Sprache der Quelle, DE, FR, IT, EN. """

class Laender(models.Model):
	""" Liste der Länder, in die exportiert wird. Vielleicht braucht das noch lat. und long., aber vielleicht eher nicht?"""
	code = model.CharField(max_length=2)
	""" Ländercode, 2 Grossbuchstaben. """
	name = model.ForeignKey(Uebersetzungen)
	""" Voller Name des Landes. """

class Kontrollregimes(models.Model):
	""" Die verschiedenen Kontrollregimes. Ich glaube im Moment macht es keinen Sinn das Datum des Inkrafttretens und Aufgehobenwordenseins zu speichern. Gibt schon länger nur die gleichen, oder? """
	name = model.ForeignKey(Uebersetzungen)

class Exportkontrollnummern(models.Model):
	""" Enthält die Anhänge mit den Beschreibungen der Nummern. Wird erst bei Gelegenheit eingelesen. """
	kontrollregime = model.ForeignKey(Kontrollregimes)
	""" Zu welchem Kontrollregime die Nummer gehört. Vor allem relevant falls es doppelte Nummern gibt oder der Inhalt der Listen geändert wird (dann würde man ein neues Kontrollregime erstellen und da eintragen). """
	nummer = model.CharField(max_length=10)
	""" Die Nummer. """
	beschreibung = model.ForeignKey(Uebersetzungen)
	""" Die Beschreibung aus der Liste. Ich bin nicht sicher ob die übersetzt werden, falls nicht bleiben die anderen Spalten der fehlenden Sprachen halt leer. """

class Geschaeftstypen(models.Model):
	""" Einzelbewilligung. Ist eine Spalte in den offiziellen Statistiken, deswegen hier halt auch. """
	name = model.ForeignKey(Uebersetzungen)
	""" Einzelbewilligung und Übersetzungen. """

class Geschaeftsrichtungen(models.Model):
	""" Ausfuhr oder Vermittlung oder ??? """
	name = model.ForeignKey(Uebersetzungen)
	""" Ausfuhr oder Vermittlung oder ??? """

class Uebersetzungen(models.Model):
	""" Enthält alles, was übersetzt werden muss. """
	de = model.TextField()
	fr = model.TextField()
	it = model.TextField()
	en = model.TextField()
