# Karte Exportstatistiken und Skandale

## Siehe auch bzw. mögliche Integration mit:

* https://www.seco.admin.ch/seco/de/home/Aussenwirtschaftspolitik_Wirtschaftliche_Zusammenarbeit/Wirtschaftsbeziehungen/exportkontrollen-und-sanktionen/industrieprodukte--dual-use--und-besondere-militaerische-gueter/statistik/2015.html
* https://www.seco.admin.ch/seco/de/home/Aussenwirtschaftspolitik_Wirtschaftliche_Zusammenarbeit/Wirtschaftsbeziehungen/exportkontrollen-und-sanktionen/ruestungskontrolle-und-ruestungskontrollpolitik--bwrp-/zahlen-und-statistiken0.html
* https://github.com/rajaupadhyay/GlobalArmsTrade
* https://github.com/chrismp/SIPRI-import-export-map-timeline
* https://github.com/jramonlab/vuelo-de-sipri-report
* https://github.com/benryan58/sipri_arms
* https://github.com/Rolikasi/military_expenses
* http://enaat.org/eu-export-browser
* https://caat.org.uk/resources/countries/
* https://caat.org.uk/data/exports-uk/
* https://caat.org.uk/resources/companies/
* https://srfdata.github.io/2017-02-kriegsmaterial/#r-script__daten
* Amnesty International Menschenrechtsberichte, kann man daraus Daten extrahieren?
* Integrate Human Development Index?
* Anzahl Arbeitsplätze pro Exportvolumen und Jahr und das den Toten und Verletzten in den Ländern gegenüberstellen?

## Infos alte Webseite

* git https://github.com/Kaju-Bubanja/GSOA
* DB-Config: kriegsmaterial/config/app.php
* Startseite: kriegsmaterial/src/Template/Export/test.ctp
* Controller, der AJAX-Request beantwortet:  kriegsmaterial/src/Controller/ExportController.php

## Datenbanklayout alt

### export-Tabelle

* Code: Ländercode, Bestimmungsland oder Endempfängerstaat?
* Art: Kriegsmaterial, bes. mil. Güter, Dual Use: SELECT *, COUNT(*) FROM export GROUP BY Art
* Kriegsmaterial: nur nach System Wassenaar und in diversen  Kategorien: SELECT *, COUNT(*) FROM export WHERE export.Art="Kriegsmaterial" GROUP BY System, Kategorie
* Besondere militärische Güter: nur nach System ML und in diversen Kategorien: SELECT *, COUNT(*) FROM export WHERE export.Art="Besondere militärische Güter" GROUP BY System, Kategorie
* Dual-Use-Güter: in diversen Systemen und Kategorien, Systeme: Anhang 5, ChKV, NSGI, NSGII, Sanktionen, Wassenaar.
  * SELECT *, COUNT(*) FROM export WHERE export.Art="Dual-Use-Güter" GROUP BY System, Kategorie
  * SELECT *, COUNT(*) FROM exportkontrollstatistiken_geschaefteimport WHERE art="Dual-Use-Güter" GROUP BY system, kategorie 
* System: Wassenaar, ML, Anhang 5, ChKV, NSGI, NSGII, Sanktionen
* Kategorie: 333 Stück, zum Teil Fehler drin.

## Datenbanklayout neu

Siehe models.py

## Seiten neu

### Mehrere Länder

Von oben nach unten:

* Header
* Totalexportvolumen
* Karte
* Filtermaske
* Tabelle mit Ländertotalen 10 Zeilen. Ländertotale aus ganzem Datensatz vorausgewählt. Tabelle nach schlimmsten Exporten sortieren.

### Ein Land

Von oben nach unten:

* Header
* Totalexportvolumen
* Karte
* Filtermaske
* Diagramm mit Problem und Exportvolumen
* Tabelle mit Geschäften 10 Zeilen nach Datum von neu zu alt.

### Bauteile

* Karte. Wäre schon so:
  * Pseudokartogramm nach Tobler, ohne zoom oder pan. Dabei wird 
    jedes Längen- und Breitengrad in einer normalen 
    Kartenprojektion einzeln skaliert. Jedes relevante Land hat 
    eine Mindestgrösse, jedes Grad eine kleine Mindestgrösse und 
    der Rest des Platzes wird proportional verteilt, abhängig von 
    Geldwerten und Lage in dem Land. Begründung:
    * Eine normale voll zoom- und verschiebbare Karte ist weder übersichtlich noch effizient
    * Anforderungen:
      * Alle relevanten Länder erkennbar
      * geographischer Zusammenhang erkennbar
      * Konkretisierung: Jedes Grad hat eine Mindestgrösse. Ein (Teil 
    eines oder vielfaches eines) Grades in dem ein relevantes 
    Land ist, hat eine grössere Mindestgrösse, die skaliert wird 
    mit der Länge des Landes. Der Rest des Platzes wird 
    proportional nach Exportzahlen verteilt, die Exportzahlen von 
    Ländern mit Skandalen werden doppelt (oder anderer Faktor) 
    gezählt.
    * Implementierung: Sollte \Theta\left(\left|\text{relevante Länder}\right|\right)
     sein, also voll ok.
      ∗ \frac{\pi}{n} (Breite) und \frac{2\pi}{2n} (Länge) Teile, 
      vielleicht n=180 (dann hätten wir Abschnitte von einem 
      Längen- und Breitengrad)
      ∗ Die Skalierung der Breite und Länge ist vollkommen 
      unabhängig voneinander
    ∗ Backend:
      * Für jedes Land: Gehe durch alle Abschnitte, die das Land 
        schneiden und erhöhe das Maximum des Geldes pro Grad des 
        Grades wenn nötig.
      * API gibt 3n Werte abhängig von den Filtern
      ∗ Das Frontend macht mit den Werten eine 
      Koordinatentransformation
        * Definiere Transformationsfunktion
          1. Array mit den Stücken der Transformation
          2. Koordinate auf ganze Grade gerundet könnte Index sein 
          (wenn man für jedes Grad eine Skalierung will, sonst 
          eine ähnliche Rechnung)
        * Wende diese auf die Koordinaten an
        * Aktualisiere die Darstellung
* Diagramm inspiriert von dem Diagramm auf https://www.nzz.ch/schweiz/die-schweiz-exportiert-waffen-an-die-beiden-erzfeinde-indien-und-pakistan-ld.1463126
  * x-Achse Zeit, y-Achse Geldwerte bzw. Art der Probleme
  * Balkendiagramm mit vertikalen Balken für Exportzahlen
  * horizontale Balken auf verschiedenen Höhen für bewaffnete Konflikte und andere Probleme aus Datenbank
* Filter für mehrere Länder:
  * Länderauswahl (drop down Liste, leitet auf Länderseiten weiter, vorauswahl “Alle”. Später anständig.)
  * Filter Güterauswahl
  * Granularität (einzeln/Jahr/total)
  * Zeitauswahl
  * sortieren nach
    ∗ Betrag aufwärts/abwärts
    ∗ neu/alt nicht bei Ländertotalen, nur bei einzelnen 
      Geschäften
  * Zeilen pro Seite (Dropdown 10, 50, 100, 200, 500 oder so)

* Filter für ein Land:
  * Alle Länder (Link)
  * Filter Güterauswahl
  * Granularität=einzeln, ausgeblendet
  * Zeitauswahl
  * sortieren nach
    ∗ Betrag aufwärts/abwärts
    ∗ neu/alt
  * Zeilen pro Seite (Dropdown 10, 50, 100, 200, 500 oder so)

* Filter Zeitauswahl: Von (Jahr), Bis (Jahr)
* Filter Güterauswahl: Checkboxes für Kriegsmaterial, besondere  militärische Güter, Dual Use. Wenn KM und DU aktiviert, dann automatisch auch BMG?
* Tabelle mit Ländertotalen: ganze Zeile Link auf jeweiliges Land
  * Flagge (nicht aus Datenbank/API)
  * Ländercode
  * Land
  * Volumen

* Tabelle mit Jahrestotalen: Wie Tabelle mit Ländertotalen, nur mit zusätzlicher Spalte für das Jahr

* Tabelle mit Geschäften:
  * Flagge (nicht aus Datenbank/API)
  * Ländercode
  * Land (falls Platz)
  * Zeit (nur Jahr falls genau ein Jahr, sonst genau von-bis)
  * Art
  * Was (so genau wie möglich)
  * Volumen
* Tabelle für einzelnes Land: Wie Tabelle mit Geschäften/Jahrestotalen, nur ohne die Spalten die das Land bezeichnen.

### Programmschnittstellen

json für die Daten:

* eine für jede Tabellenart von oben, die alle relevanten Filterparameter unterstützt
  * individuelle Geschäfte
  * Summen pro Land in dem Zeitraum
  * Summen pro Jahr und Land in dem Zeitraum
  Jeweils genau dann mit Ländercode und -namen falls mehr als ein 
  Land ausgewählt ist.
* eine für die Kartentransformation, die die selben Parameter 
  nimmt, aber nur die Skalierfaktoren zurückgibt. Ähnlich wie 
  Summen pro Land in dem Zeitraum.
* eine für die Problemanzeige in Tabellen und den 
  Doppelbalkendiagramme


## Zu tun

Geplante Schritte:

* animierte übergänge schreiben
  * karte
    * Datenbankanfrage senden
    * Animation zu leerer Karte starten (kein Info-Popups, keine Verzerrung), mit Lademeldung
    * Zu neuer Karte wechseln sobald Daten angekommen, ohne Animation
  * tabelle
    * Datenbankanfrage senden
    * Kontrast der Tabelle in Animation verringern, mit Lademeldung
    * Zu neuer Tabelle wechseln sobald Daten angekommen, ohne Animation
* Kartenskalierung
    * Ländergrössen (in L-/Bgraden) aus der json-Karte auslesen
    * eigentliche api schreiben, vielleicht vorher schon auf view-Klassen umstrukturieren
    * js-funktion schreiben, die die Transformation macht
* Aufräumen
* Problem/Skandaldatenbank ausbauen, Detailseite für einzelne Länder schreiben

# Wordpress, “Ausgeschossen”-Kampagne

Wurde von Lukas ausgeschalten, entfernt. Archivierung wäre zu viel Aufwand.

## Ansprechpersonen

* Lukas
* vielleicht Andi
* wer hat die ursprünglich gemacht?

## Infos

* Gar nicht so viel Inhalt glaube ich, aber war von der Darstellung mal schön/extra angepasst
* Passwort für Account admin im Wordpress: ohp3aiTha6eengohri2A
* Wartungsmodus durch SeedPod Coming Soon Page and Maintenance Mode Lite Plugin, unbedingt wieder deinstallieren wenn nicht mehr gebraucht. Für eingeloggte Benutzer ist die Seite normal erreichbar.
* 2019-02-24 aktualisiert worden, inkl. Plugins, hat aber trotzdem nicht wieder funktioniert.

## Zu tun

* Das Übersetzungsplugin macht die Hauptseite kaputt, wenn es 
  aktiviert wird.
* Das Theme Concept macht die Hauptseite kaputt, wenn es 
  aktiviert wird
* Andere 404-Probleme haben mit kaputten Links zu tun, die statt 
  auf kriegsmaterial.ch auf 
  kriegsmaterial.ch.augustus.sui-inter.net/kriegsmaterial/ 
  verweisen.
* Wahrscheinlich gibt es weitere Probleme

# MediaWiki, Exportskandale und -informationen

* Offline.
* Man könnte mal durch die Daten/Artikel gehen und das irgendwo wieder online bringen, aber das wäre eine Riesenarbeit, weil auch vieles inhaltlich veraltet ist.
* Die paar Artikel die ich angeschaut habe brauchen alle eine Überarbeitung bzw. sind weit von der Qualität von z.B. der GSoA-Zeitung entfernt.
* Die Seite mit den Exportstatistiken verlinkt auf Seiten dieses Wiki, von denen es für jeden Skandal eine geben sollte
* Problem mit CSS/Theme
* Sonst scheint es oberflächlich betrachtet zu funktionieren

# Abstimmungswebseite Kriegsmaterialexportverbot

## Ansprechpersonen

* Lukas
* wer hat die ursprünglich gemacht?

##

* https://github.com/lukas-buergi/kriegsmaterialexportverbotsinitiative
* https://kriegsmaterialexportverbotsinitiative.archiv.gsoa.ch/
* Ich weiss nicht, wie die Webseite funktioniert (hat). Abgesehen von statischem html habe ich nur einen sehr erwachsen benannten “fckeditor” gefunden.
* Wurden die aktiven Teile einfach gelöscht? Das würde zum 404 passen, den man bekommt, wenn man einen Kommentar schreiben will

## Zu tun

* Restliche aktive Teile und Kommentarformulare entfernen.
