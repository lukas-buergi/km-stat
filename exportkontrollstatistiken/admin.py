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

from .models import Uebersetzungen, Kontrollregimes, Exportkontrollnummern, Laender, Laendergruppen, QuellenProbleme, GueterArten, Geschaefte, ProblemArtenGesetz, ProblemArten, Probleme

class GeschaefteAdmin(admin.ModelAdmin):
  list_filter = ('beginn', 'ende', 'exportkontrollnummer__kontrollregime__gueterArt')
  list_display = ('__str__', 'beginn', 'ende', 'exportkontrollnummer', 'endempfaengerstaat', 'umfang')
  #list_editable = ('umfang',) # example, should be used for marking entries as verified

admin.site.register(Uebersetzungen)
admin.site.register(Kontrollregimes)
admin.site.register(Exportkontrollnummern)
admin.site.register(Laender)
admin.site.register(Laendergruppen)
admin.site.register(QuellenProbleme)
admin.site.register(GueterArten)
admin.site.register(Geschaefte, GeschaefteAdmin)
admin.site.register(ProblemArtenGesetz)
admin.site.register(ProblemArten)
admin.site.register(Probleme)
