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


from django.urls import path

from . import views

urlpatterns = [
  path('api/g/<granularity>/<countries>/<types>/<int:year1>/<int:year2>/<sortBy>/<int:perPage>/<int:pageNumber>', views.gapi, name='gapi'),
  #path('table', views.table, name='table'),
  #path('worldmap', views.worldmap, name='worldmap'),
  path('<granularity>/<countries>/<types>/<int:year1>/<int:year2>/<sortBy>/<int:perPage>/<int:pageNumber>', views.mainpage, name='mainpage'),
  path('', views.index, name='index'),
  path('site.webmanifest', views.webmanifest, name='webmanifest'),
  path('test', views.test, name='test'),
]
