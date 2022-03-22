#######################################################################
# Copyright Lukas Bürgi 2022
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

from exportkontrollstatistiken.models import Uebersetzungen
from django.core.management.base import BaseCommand
import django

class Command(BaseCommand):
    help="""Delete all translations which are unused."""
    def handle(self, **options):
        for u in Uebersetzungen.objects.all():
            try:
                u.delete()
            except django.db.models.deletion.ProtectedError:
                pass