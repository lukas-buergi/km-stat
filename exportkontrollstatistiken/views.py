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

from django.http import HttpResponse
from django.template import loader
from django.db.models import Q
from django.conf import settings
from django.shortcuts import render

from .models import Geschaefte, Uebersetzungen, Laender, Laendergruppen, Geschaeftslaendersummen

import json
import itertools
import copy
import datetime

# TODO: Transform all of this into a class based view
class apiParam():
  """Parses the parameters and provides them in a more practical form or stops if they are wrong."""
  
  granularities = {
    "i" : ["individual", "Geschäfte einzeln und detailliert"],
    "y" : ["summedPerYear", "Summen pro Land und Jahr"],
    "s" : ["summed", "Summen pro Land über gesamten Zeitraum"],
  }

  typesChoices = { # case 1, case 2, no idea how they are called
    "k" : ["Kriegsmaterial", "Kriegsmaterial"],
    "b" : ["Besondere militärische Güter", "Besonderen militärischen Gütern"],
    "d" : ["Dual Use Güter", "Dual Use Gütern"],
  }

  sortByChoices = {
    "v"   : "-umfang",
    "va"  : "umfang",
    "t"   : "-beginn",
    "ta"  : "beginn",
  }
  
  def __init__(self, *args):
    # save the parameters as given. Note that if they aren't (more or less) valid, this will cause an exception later in the constructor, so it's safe to assume they are (more or less) valid.
    self.parameterNames = [ 'granularity', 'countries', 'types', 'year1', 'year2', 'sortBy', 'perPage', 'pageNumber' ]
    if(len(args) != len(self.parameterNames)):
      raise(TypeError)
    self.parameters = dict(zip(self.parameterNames, args))
    

    # save the parameters individually in useful, validated formats

    # pages
    if(self.parameters['perPage'] < 1 or self.parameters['pageNumber'] < 1 ):
      raise(ValueError)
    self.perPage=self.parameters['perPage']
    self.pageNumber=self.parameters['pageNumber']

    self.perPageChoices = [10, 20, 50, 100, 200, 500]
    if(self.perPage not in self.perPageChoices):
      self.perPageChoices+=[self.perPage]
      self.perPageChoices=sorted(self.perPageChoices)

    # various options
    if(self.parameters['granularity'] not in self.granularities):
      raise(ValueError)
    self.granularity=self.granularities[self.parameters['granularity']][0]
    
    if(self.parameters['sortBy'] not in self.sortByChoices):
      raise(ValueError)
    self.sortBy=self.sortByChoices[self.parameters['sortBy']]

    if(self.granularity=="summed" and self.sortBy not in ["-umfang", "umfang"]):
      raise(ValueError)
        
    if(0>self.parameters['year1'] or self.parameters['year1'] > self.parameters['year2']):
      raise(ValueError)
    self.year1=self.parameters['year1']
    self.year2=self.parameters['year2']

    # types
    self.types=[]
    if(self.parameters['types'] == 'none'):
      pass
    else:
      for c in self.parameters['types']:
        if(c not in self.typesChoices):
          raise(ValueError)
        else:
          self.types.append(c)
    
    # countries
    # TODO: needs more advanced parser. Codes are prefix free, 2 chars for countries, 3 chars for groups of countries. all for all, or 0 followed by 2 char region code for other groups of countries.
    countries=self.parameters['countries']
    if(countries=="all"):
      self.countries=~Q(endempfaengerstaat=Laender.objects.get(code='CH'))
      self.countriesSingle=False
    else:
      self.countries=[]
      while(len(countries)>=2):
        code=countries[:2]
        if(code=='CH'):
          continue
        countries=countries[2:]
        try:
          self.countries.append(Q(endempfaengerstaat=Laender.objects.get(code=code)))
        except Laender.DoesNotExist:
          raise(ValueError("Not a valid country code: " + code))
      if(len(countries)!=0):
        raise(ValueError)

      self.countriesSingle = len(self.countries) == 1
      
      # or the countries together
      qcountries=Q()
      for q in self.countries:
        qcountries |= q
      self.countries=qcountries

    # TODO: I have implemented this, right?
    if(self.granularity=="summedPerYear" and not self.countriesSingle and self.sortBy in ["-beginn", "beginn"]):
      raise(NotImplementedError)

  def __str__(self):
    jsParamObject = copy.copy(self.parameters)
    for t in self.typesChoices:
      if t in self.types:
        jsParamObject[t] = True
      else:
        jsParamObject[t] = False
    jsParamObject['paramNames'] = self.parameterNames + ['minYear', 'maxYear']
    jsParamObject['minYear'] = Geschaefte.getFirstYear()
    jsParamObject['maxYear'] = Geschaefte.getLastYear()
    jsCodeString = json.dumps(jsParamObject, separators=(',', ':'))
    return(jsCodeString)

  def getTypes(self, typeFieldName):
    """Get a Q object with the types ORd together. This depends on the field name so it must be given in parameter (values are often exportkontrollnummer__kontrollregime__gueterArt__name or gueterArt__name)."""
    # always false q object
    qtypes=Q(pk=None)
    for c in self.types:
      args = {typeFieldName : Uebersetzungen.objects.get(de=self.typesChoices[c][0])}
      qtypes |= Q(**args)
    return(qtypes)

  def getPage(self, queryset):
    """Slice a queryset or other sliceable object. The queryset is not evaluated at this point I think. """
    assert(self.perPage>0)
    assert(self.pageNumber>0)
    return(queryset[self.perPage*(self.pageNumber-1):self.perPage*self.pageNumber])

def gapi(request, granularity, countries, types, year1, year2, sortBy, perPage, pageNumber):
  """Die view, die die Geschäftsdaten an das Frontend liefert.
  Die Parameter erklären sich zusammen mit der apiParam Klasse."""

  # input validation and preparation
  try:
    p=apiParam(granularity, countries, types, year1, year2, sortBy, perPage, pageNumber)
  except ValueError:
    raise # TODO: This line is not for production.
    return(HttpResponse("Invalid parameter."))

  # prepare response
  response = HttpResponse(content_type='application/json')
  response['Content-Disposition'] = 'attachment; filename="exporte-' + countries + "-" + types + "-" + str(year1) + "-" + str(year2) + "-" + str(pageNumber) + '.json"'
  
  # write response
  if(p.granularity=="summed"):
    response.write(Geschaeftslaendersummen.getJSONSummed(p))
  elif(p.granularity=="summedPerYear"):
    response.write(Geschaeftslaendersummen.getJSONSummedPerYear(p))
  elif(p.granularity=="individual"):
    response.write(Geschaefte.getJSON(p))

  return(response)

# TODO: Do I want to keep/update those separate views? They don't currently work.
# Would probably be a good idea.

def table(request):
  template = loader.get_template('exportkontrollstatistiken/table.html')
  context = {}
  return HttpResponse(template.render(context, request))

def worldmap(request):
  template = loader.get_template('exportkontrollstatistiken/worldmap.html')
  context = {}
  return HttpResponse(template.render(context, request))

def mainpage(request, granularity, countries, types, year1, year2, sortBy, perPage, pageNumber):
  # input validation and preparation
  try:
    params=apiParam(granularity, countries, types, year1, year2, sortBy, perPage, pageNumber)
  except ValueError:
    raise # TODO: This line is not for production.
    return(HttpResponse("Invalid parameter."))
  template = loader.get_template('exportkontrollstatistiken/index.html')
  params.typesChoices = { # hides du from interface. TODO: finish import
    "k" : ["Kriegsmaterial", "Kriegsmaterial"],
    "b" : ["Besondere militärische Güter", "Besonderen militärischen Gütern"],
  } 
  context = {
    'p' : params,
    'regions' : Laendergruppen.objects.all().order_by('name__de'), # TODO: sort by active language
    'countries' : Laender.objects.all().order_by('name__de'), # TODO: same as above
    'firstYear' : Geschaefte.getFirstYear(),
    'lastYear' : Geschaefte.getLastYear(),
  }
  return HttpResponse(template.render(context, request))

def index(request):
  return(mainpage(request, "s", "all", "kb", Geschaefte.getFirstYear(), Geschaefte.getLastYear(), "v", 10, 1))

def webmanifest(request):
  return(render(request, 'exportkontrollstatistiken/favicon/site.webmanifest', {}))

def test(request):
  params=apiParam("s", "all", "kb", 2001, 2018, "v", 35, 1)
  context = {
    'p' : params,
  }
  return(render(request, 'exportkontrollstatistiken/test.html', context))
