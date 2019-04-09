from django.http import HttpResponse
from django.template import loader
from django.db.models import Q

from exportkontrollstatistiken.models import Geschaefte, Uebersetzungen, Laender

import csv
import itertools
import datetime

# TODO: Transform all of this into a class based view
class apiParam():
    """Parst die Parameter und stellt sie in praktischeren Formen zur Verfügung bzw. stoppt wenn sie falsch sind."""
    
    # granularity
    granularities = {
        "s" : "summed",
        "i" : "individual",
        "y" : "summedPerYear",
    }
    granularity=None

    

    # countries
    countries=[]

    # types
    typesChoices={
        "k" : "Kriegsmaterial",
        "b" : "Besondere militärische Güter",
        "d" : "Dual Use Güter",
    }
    types=[]

    # sortby
    sortByChoices = {
        "v"     : "-umfang",
        "va"    : "umfang",
        "t"     : "-beginn",
        "ta"    : "beginn",
    }
    sortBy=None
    
    def __init__(self, granularity, countries, types, year1, year2, sortBy, perPage, pageNumber):
        self.perPage=perPage
        self.pageNumber=pageNumber
        
        if(granularity not in self.granularities):
            raise(ValueError)
        self.granularity=self.granularities[granularity]
        
        if(sortBy not in self.sortByChoices):
            raise(ValueError)
        self.sortBy=self.sortByChoices[sortBy]

        if(self.granularity=="summed" and self.sortBy not in ["-umfang", "umfang"]):
            raise(ValueError)
                
        if(0>year1 or year1 > year2):
            raise(ValueError)
        self.year1=year1
        self.year2=year2

        # types
        for c in types:
            if(c not in self.typesChoices):
                raise(ValueError)
            else:
                self.types.append(Q(exportkontrollnummer__kontrollregime__gueterArt__name=Uebersetzungen.objects.get(de=self.typesChoices[c])))

        # or the types together
        qtypes=Q()
        for q in self.types:
            qtypes |= q
        self.types=qtypes
        
        # countries
        if(countries=="all"):
            self.countries=~Q()
            self.countriesSingle=False
        else:
            while(len(countries)>=2):
                code=countries[:2]
                countries=countries[2:]
                try:
                    self.countries.append(Q(endempfaengerstaat=Laender.objects.get(code=code)))
                except Laender.DoesNotExist:
                    raise(ValueError)
            if(len(countries)!=0):
                raise(ValueError)

            self.countriesSingle = len(self.countries) == 1
            
            # or the countries together
            qcountries=Q()
            for q in self.countries:
                qcountries |= q
            self.countries=qcountries

        if(self.granularity=="summedPerYear" and not self.countriesSingle and self.sortBy in ["-beginn", "beginn"]):
            raise(NotImplementedError)

def individual(p, writer):
    queryset = Geschaefte.objects.filter(ende__gte=datetime.date(p.year1, 1, 1))
    queryset = queryset.filter(beginn__lte=datetime.date(p.year2, 12, 31))
    queryset = queryset.filter(p.types)
    queryset = queryset.filter(p.countries)
    
    queryset = queryset.order_by(p.sortBy)
    # TODO: this exact slicing expression is used in 3 places
    queryset = queryset[p.perPage*(p.pageNumber-1):p.perPage*p.pageNumber]
    
    titleRow=["Datum", "Art", "EKN", "Umfang"]
    if(not p.countriesSingle):
        titleRow = ["Ländercode", "Land"] + titleRow
    writer.writerow(titleRow)
    
    for g in queryset:
        row=[g.beginn, g.exportkontrollnummer.kontrollregime.gueterArt.name.de, g.exportkontrollnummer, g.umfang]
        if(not p.countriesSingle):
            row = [g.endempfaengerstaat.code, g.endempfaengerstaat.name.de] + row
        writer.writerow(row)

def summedPerYear(p, writer):
    """Return transactions summed per year. Algorithm:
        * sort by country, year
        * sum up consecutive entries until country or year changes
        * sort according to p.sortBy, but only certain combinations are valid:
            * date asc+des, for a single country (that's the original order after the summing algorithm)
            * value"""
    
    queryset = Geschaefte.objects.filter(ende__gte=datetime.date(p.year1, 1, 1))
    queryset = queryset.filter(beginn__lte=datetime.date(p.year2, 12, 31))
    queryset = queryset.filter(p.types)
    queryset = queryset.filter(p.countries)
    
    if(p.sortBy in ["beginn","-beginn"]):
        firstSort=p.sortBy
    else:
         # in that case it can be either because later it's sorted again anyway
        firstSort="beginn"
        
    queryset = queryset.order_by("endempfaengerstaat", firstSort)

    for g in queryset:
        print(g)

    sums=dict()
    curCountry = None
    curYear = None
    for g in queryset:
        if(g.endempfaengerstaat!=curCountry or g.beginn.year!=curYear):
            curCountry = g.endempfaengerstaat
            curYear = g.beginn.year
            curSum = g.umfang
            sums[str(curCountry) + str(curYear)] = [curSum, curYear, curCountry]
        else:
            sums[str(curCountry) + str(curYear)][0] += g.umfang

    reverse=None
    if(p.sortBy == "-umfang"):
        reverse=True
    elif(p.sortBy == "umfang"):
        reverse=False
    
    if(reverse==None):
        order=sums.keys()
        # need this so order is an array in both cases
    else:
        order=sorted(sums, key=lambda key : sums.get(key)[0], reverse=reverse)

    # TODO: this exact slicing expression is used in 3 places
    order=order[p.perPage*(p.pageNumber-1):p.perPage*p.pageNumber]

    for country in order:
        writer.writerow([sums[country][2].code, sums[country][2].name.de, sums[country][1], sums[country][0]])

def summed(p, writer):
    """Sum transactions per country. Algorithm:
        * sort by country
        * sum up consecutive entries until the country changes
        * sort by value"""

    queryset = Geschaefte.objects.filter(ende__gte=datetime.date(p.year1, 1, 1))
    queryset = queryset.filter(beginn__lte=datetime.date(p.year2, 12, 31))
    queryset = queryset.filter(p.types)
    queryset = queryset.filter(p.countries)
    
    queryset = queryset.order_by("endempfaengerstaat")
    sums=dict()
    
    # use dummy country here so we can compare pk instead of whole objects
    # which probably saves one db query per db entry
    # didn't provide a big speed up, but still some I think
    curCountry = Laender("XX", None, 0,0,0,0)
    # TODO: this addition takes forever
    for g in queryset:
        if(g.endempfaengerstaat.pk!=curCountry.pk):
            curCountry=g.endempfaengerstaat
            curSum=g.umfang
            sums[curCountry] = curSum
        else:
            sums[curCountry]+=g.umfang

    if(p.sortBy=="-umfang"):
        reverse=True
    else:
        reverse=False

    order = sorted(sums, key=sums.get, reverse=reverse)

    # TODO: this exact slicing expression is used in 3 places
    order = order[p.perPage*(p.pageNumber-1):p.perPage*p.pageNumber]

    titleRow=["id", "name", "Exporte"]
    writer.writerow(titleRow)
    
    for country in order:
        writer.writerow([country.code, country.name.de, sums[country]])

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
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="exporte-' + countries + "-" + types + "-" + str(year1) + "-" + str(year2) + "-" + str(pageNumber) + '.csv"'
    writer = csv.writer(response)

    # write response
    if(p.granularity=="summed"):
        summed(p, writer)
    elif(p.granularity=="summedPerYear"):
        summedPerYear(p, writer)
    elif(p.granularity=="individual"):
        individual(p, writer)

    return(response)

# TODO: Restructure table and worldmap so that they can be included in other pages. Include them on the index.
# TODO: Make table and worldmap take arguments

def table(request):
    queryset = Geschaefte.objects.all()[:5]
    template = loader.get_template('exportkontrollstatistiken/table.html')
    context = {
        'queryset': queryset,
    }
    return HttpResponse(template.render(context, request))

def worldmap(request):
    template = loader.get_template('exportkontrollstatistiken/worldmap.html')
    context = {}
    return HttpResponse(template.render(context, request))

def index(request):
    template = loader.get_template('exportkontrollstatistiken/index.html')
    context = {}
    return HttpResponse(template.render(context, request))
