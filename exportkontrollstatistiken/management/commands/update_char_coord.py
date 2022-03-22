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
import json
from django.core.management.base import BaseCommand
from django.core.management import call_command

from exportkontrollstatistiken.models.geschaefte import Exportkontrollnummern, Geschaefte, Kontrollregimes
from exportkontrollstatistiken.models.utility import Laender

class Command(BaseCommand):
    help="""
    Writes characteristic coordinations from database into .json file."""
    def handle(self, **options):
        # add characteristic coordinates to each country
        d = {}
        path='/code/exportkontrollstatistiken/static/exportkontrollstatistiken/world_countries.json'
        with open(path, 'r') as f:
            d = json.loads(f.read())
            d['coordinates'] = dict()

            print("Regions which are on map but not in database:")
            for index, country in enumerate(d["features"]):
                cid = country['id']
                try:
                    countryDBObject = Laender.objects.get(code=cid)
                except Laender.DoesNotExist:
                    print(cid)
                    continue
                try:
                    del country['latitude']
                    del country['longitude']
                except KeyError:
                    pass
                d['coordinates'][cid] = {
                                            'lon' : countryDBObject.longitude,
                                            'lat' : countryDBObject.latitude,
                                        }
        with open(path, 'w') as f:
            json.dump(d, f, separators=(',', ':'))