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

import datetime
import calendar

from django.db.models.functions import Concat
from django.contrib import admin

from .models import Uebersetzungen, Kontrollregimes, Exportkontrollnummern, Bewilligungstypen, Geschaeftsrichtungen, Laender, Laendergruppen, QuellenGeschaefte, QuellenProbleme, GueterArten, Geschaefte, ProblemArtenGesetz, ProblemArten, Probleme, GeschaefteKriegsmaterialNachKategorieEndempfaengerstaat

class GeschaefteAdmin(admin.ModelAdmin):
  list_filter = ('beginn', 'ende', 'exportkontrollnummer__kontrollregime__gueterArt')
  list_display = ('__str__', 'beginn', 'ende', 'exportkontrollnummer', 'endempfaengerstaat', 'umfang')
  #list_editable = ('umfang',) # example, should be used for marking entries as verified

class GeschaefteKriegsmaterialNachKategorieEndempfaengerstaatAdmin(admin.ModelAdmin):
  class QuarterListFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = 'quarter'

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'quarter'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (
            ('2019-01', '2019-01'),
            ('2019-02', '2019-02'),
        )

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        if(self.value()):
          year, quarter = self.value().split('-')
          quarter = int(quarter)
          year = int(year)
          fromDate = datetime.date(year, 1, 1)
          toDate = datetime.date(year, quarter*3, calendar.monthrange(year, quarter*3)[1])
          return(queryset.filter(fromDate=fromDate, toDate=toDate))
        else:
          return(queryset)
  def nameDE(self, obj):
    return(obj.country.name.de)
  nameDE.short_description = "Land"
  
  def continentDE(self, obj):
    return(obj.continent.name.de)
  continentDE.short_description = "Kontinent"
  
  def markChecked(self, request, queryset):
    """
    Mark the entries as manually/visually checked against the original source. Should this be boolean, or date, or name+date?
    """
    pass#queryset.update(status='p')
  markChecked.short_description = "Mark selected rows as checked."
  
  ordering = ('continent__seco_km_order', 'country__name__de')
  
  list_display = ('continentDE', 'nameDE', 'KM1', 'KM2', 'KM3', 'KM4', 'KM5', 'KM6', 'KM7', 'KM8', 'KM9', 'KM10', 'KM11', 'KM12', 'KM13', 'KM16', 'KM17', 'KM19', 'KM20', 'KM21', 'fromDate', 'toDate')
  
  list_filter = (QuarterListFilter,)

  actions = [ 'markChecked' ]

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
admin.site.register(Geschaefte, GeschaefteAdmin)
admin.site.register(GeschaefteKriegsmaterialNachKategorieEndempfaengerstaat, GeschaefteKriegsmaterialNachKategorieEndempfaengerstaatAdmin)
admin.site.register(ProblemArtenGesetz)
admin.site.register(ProblemArten)
admin.site.register(Probleme)
