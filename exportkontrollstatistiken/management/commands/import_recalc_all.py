#!/usr/bin/env python3
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
from django.core.management.base import BaseCommand
from django.core.management import call_command

from exportkontrollstatistiken.models.geschaefte import Exportkontrollnummern, Geschaefte, Kontrollregimes

class Command(BaseCommand):
    help="""
    Warning: Deletes and creates lots of db entries without prompting.
    Fills db from .csv files."""
    def handle(self, **options):
        Geschaefte.objects.all().delete()
        Exportkontrollnummern.objects.all().delete()
        Kontrollregimes.objects.all().delete()
        call_command('import_ekn_ml_km')
        call_command('import_bmg')
        call_command('import_km')
        call_command('recalculate_sums')
        
