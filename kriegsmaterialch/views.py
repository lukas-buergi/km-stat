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

from django.shortcuts import redirect

def archiveRedirect(request, url=''):
  if(url == None):
    url=""
  return(redirect('https://kriegsmaterialexportverbotsinitiative.archiv.gsoa.ch/' + str(url), permanent=True))

def mainpageRedirect(request):
  return(redirect('https://www.kriegsmaterial.ch/', permanent=True))
