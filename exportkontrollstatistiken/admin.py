from django.contrib import admin

from .models import Uebersetzungen, Kontrollregimes, Exportkontrollnummern, Bewilligungstypen, Geschaeftsrichtungen, Laender, Laendergruppen, QuellenGeschaefte, QuellenProbleme, GueterArten, Geschaefte, ProblemArtenGesetz, ProblemArten, Probleme

admin.site.register(Uebersetzungen)
admin.site.register(Kontrollregimes)
admin.site.register(Exportkontrollnummern)
admin.site.register(Bewilligungstypen)
admin.site.register(Geschaeftsrichtungen)
admin.site.register(Laender)
admin.site.register(Laendergruppen)
admin.site.register(QuellenGeschaefte)
admin.site.register(QuellenProbleme)
admin.site.register(GueterArten)
admin.site.register(Geschaefte)
admin.site.register(ProblemArtenGesetz)
admin.site.register(ProblemArten)
admin.site.register(Probleme)
