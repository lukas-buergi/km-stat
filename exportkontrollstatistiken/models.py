from django.db import models

class Uebersetzungen(models.Model):
	""" Enthält alles, was übersetzt werden muss. """

	de = models.TextField(blank=True)
	fr = models.TextField(blank=True)
	it = models.TextField(blank=True)
	en = models.TextField(blank=True)

	def __str__(self):
		""" Sollte je nach Spracheinstellung die richtige Sprache zurückgeben und dann auf andere Sprachen zurückfallen wenn es diese nicht gibt. TODO. """
		return(self.de)

	class Meta:
		verbose_name = 'Übersetzung'
		verbose_name_plural = 'Übersetzungen'

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


class Laender(models.Model):
	""" Liste der Länder, in die exportiert wird. Vielleicht braucht das noch lat. und long., aber vielleicht eher nicht?"""
	code = models.CharField(max_length=2)
	""" Ländercode, 2 Grossbuchstaben. """
	name = models.ForeignKey(Uebersetzungen, on_delete=models.PROTECT)
	""" Voller Name des Landes. """

	def __str__(self):
		return(self.code)
	
	class Meta:
		verbose_name = 'Land'
		verbose_name_plural = 'Länder'

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
	* GKV/GKG (946.202.1/946.202, zivil und militärisch verwendbare Güter, besondere militärische Güter sowie strategische Güter):
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
	nummer = models.CharField(max_length=10)
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
	""" Einzelbewilligung oder sonst etwas? """
	richtung = models.ForeignKey(Geschaeftsrichtungen, on_delete=models.PROTECT)
	""" Ausfuhr, Vermittlung, sonstwas? """
	exportkontrollnummer = models.ForeignKey(Exportkontrollnummern, on_delete=models.PROTECT)
	""" Was wurde exportiert? Vielleicht sollten da mehrere Nummern erlaubt sein, weil ein Gut vielleicht unter mehrere Kontrollregime fallen kann. """
	umfang = models.PositiveIntegerField()
	""" Umfang des Geschäfts in Schweizer Franken. """
	beginn = models.DateField()
	""" Der Beginn des Geschäfts. Normalerweise der 1. Januar des Jahres, weil nichts genaueres bekannt ist. """
	ende = models.DateField()
	""" Das Ende des Geschäftes. Geschäfte können über mehrere Jahren gehen stand irgendwo auf der Secowebseite (macht ja Sinn). Ich schätze das sieht man bei neueren Statistiken an der Nummer und bei älteren wurde das Geschäft wahrscheinlich nur in einem Jahr einbezogen nehme ich an (keine Ahnung). """
	quelle = models.ForeignKey(QuellenGeschaefte, on_delete=models.PROTECT)
	""" Die offizielle Quelle für den Eintrag. Ich glaube es gibt die immer nur auf Deutsch, sonst müsste man das noch anpassen um auch die anderen anzubieten. """
	
	class Meta:
		verbose_name = 'Geschäft'
		verbose_name_plural = 'Geschäfte'

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
	* Gibt es ein hohes Risiko, dass das Kriegsmaterial unerlaubt weitergegeben wird? (KMV 5 IIe)"""
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
