from django.http import HttpResponse
from django.template import loader
from django.db.models import Q

from exportkontrollstatistiken.models import Geschaefte, Uebersetzungen, Laender, Geschaeftslaendersummen

import csv
import itertools
import datetime

# TODO: Transform all of this into a class based view
class apiParam():
    """Parses the parameters and provides them in a more practical form or stops if they are wrong."""
    
    # granularity
    granularities = {
        "i" : ["individual", "Geschäfte einzeln und detailliert"],
        "y" : ["summedPerYear", "Summen pro Land und Jahr"],
        "s" : ["summed", "Summen pro Land über gesamten Zeitraum"],
    }
    granularity=None

    # countries
    countries=[]

    # types
    typesChoices = { # case 1, case 2, no idea how they are called
        "k" : ["Kriegsmaterial", "Kriegsmaterial"],
        "b" : ["Besondere militärische Güter", "Besonderen militärischen Gütern"],
        "d" : ["Dual Use Güter", "Dual Use Gütern"],
    }
    types=[] # types in typesChoices

    # sortby
    sortByChoices = {
        "v"     : "-umfang",
        "va"    : "umfang",
        "t"     : "-beginn",
        "ta"    : "beginn",
    }
    sortBy=None
    
    def __init__(self, granularity, countries, types, year1, year2, sortBy, perPage, pageNumber):
        self._str = granularity + '/' + countries + '/' + types + '/' + str(year1) + '/' + str(year2) + '/' + sortBy + '/' + str(perPage) + '/' + str(pageNumber)
        
        self.perPage=perPage
        self.pageNumber=pageNumber
        
        if(granularity not in self.granularities):
            raise(ValueError)
        self.granularity=self.granularities[granularity][0]
        
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
                self.types.append(c)
        
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

    def __str__(self):
        return(self._str)

    def getTypes(self, typeFieldName):
        """Get a Q object with the types ORd together. This depends on the field name so it must be given in parameter (values are often exportkontrollnummer__kontrollregime__gueterArt__name or gueterArt__name)."""
        qtypes=Q()
        for c in self.types:
            args = {typeFieldName : Uebersetzungen.objects.get(de=self.typesChoices[c][0])}
            qtypes |= Q(**args)
        return(qtypes)

    def getPage(self, queryset):
        """Slice a queryset or other sliceable object. The queryset is not evaluated at this point I think. """
        return(queryset[self.perPage*(self.pageNumber-1):self.perPage*self.pageNumber])

def individual(p, writer):
    queryset = Geschaefte.objects.filter(ende__gte=datetime.date(p.year1, 1, 1))
    queryset = queryset.filter(beginn__lte=datetime.date(p.year2, 12, 31))
    queryset = queryset.filter(p.getTypes("exportkontrollnummer__kontrollregime__gueterArt__name"))
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
    queryset = queryset.filter(p.getTypes("exportkontrollnummer__kontrollregime__gueterArt__name"))
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
    """Sum transactions per country.

    Begin and end are both inclusive.
    
    Format: csv, columns:
        1. 'id', 2 letter iso country code
        2. <translated column description>, the name of the country
        3. <translated column description>, the sum of of the exports

    Algorithm:
        * Get entries for year2 sorted by country
        * Get entries for (year1-1) sorted by country
        * Slice both of them correctly
        * Iterate through both sets in parallel and subtract the latter from the former in each entry
        * Sort according to p.sortBy
    """

    # TYPES BROKEN
    queryset2 = Geschaeftslaendersummen.objects.filter(jahr=p.year2)
    queryset2 = queryset2.filter(p.getTypes("gueterArt__name"))
    queryset2 = queryset2.filter(p.countries)
    queryset2 = queryset2.order_by("endempfaengerstaat")

    queryset1 = Geschaeftslaendersummen.objects.filter(jahr=(p.year1-1))
    queryset1 = queryset1.filter(p.getTypes("gueterArt__name"))
    queryset1 = queryset1.filter(p.countries)
    queryset1 = queryset1.order_by("endempfaengerstaat")
    # TODO: Should I make a method for the above duplicate code?

    sums = dict()
    for country in zip(queryset1, queryset2):
        if(country[0].endempfaengerstaat.code in sums):
            sums[country[0].endempfaengerstaat.code][1] += country[1].umfang - country[0].umfang
        else:
            sums[country[0].endempfaengerstaat.code]=[country[0].endempfaengerstaat, (country[1].umfang-country[0].umfang)]

    
    if(p.sortBy=="-umfang"):
        reverse=True
    else:
        reverse=False

    order = sorted(sums, key=lambda key : sums.get(key)[1], reverse=reverse)
    order = p.getPage(order)

    titleRow=["id", "name", "Exporte"]
    writer.writerow(titleRow)
    
    for country in order:
        writer.writerow([country, sums[country][0].name.de, sums[country][1]])

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
    regions = { # TODO THIS REALLY DOESN'T BELONG HERE
        "AF":"Africa",
        "NA":"North America",
        "OC":"Oceania",
        "AN":"Antarctica",
        "AS":"Asia",
        "EU":"Europe",
        "SA":"South America",
    }
    context = {
        'p' : params,
        'regions' : regions,
        'countries' : Laender.objects.all(),
    }
    return HttpResponse(template.render(context, request))

def index(request):
    return(mainpage(request, "s", "all", "kbd", 2001, 2019, "v", 300, 1))
