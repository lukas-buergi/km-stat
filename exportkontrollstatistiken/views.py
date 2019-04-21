from django.http import HttpResponse
from django.template import loader
from django.db.models import Q
from django.conf import settings

from exportkontrollstatistiken.models import Geschaefte, Uebersetzungen, Laender, Geschaeftslaendersummen

import csv
import itertools
import datetime
import json

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
        self.types=[]
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

class apiData():
    """The data that is returned by an API query. Methods to add data and return json of accumulated data. Does some sanity checks on the data.
    The JSON contains exactly the following dict:
        {
        'total' : amount of results on all pages
        'cnames' : [column title 1, ..., column title n,],
        'ctypes' :   [ country code, country name, date, money, untreated ],
        'countries' :
            {
                'country code 1' : 0,
                'country code 2' : 1,
                ...
                'country code m' : m-1,
            }
        'data' :
            [
                [data country 1 column 1, ..., data country 1 column n],
                ...
                [data country m column 1, ..., data country m column n],
            ]
        }
    The 'ctypes' entry has the types of the columns in order.
    The 'countries' entry exists only if we know the countries are unique in all data rows and need to index the data by country. """
    data = dict()
    """This attribute is the one that is converted to json and sent."""
    def __init__(self, uniqueCountry, columnNames, columnTypes):
        assert(len(columnNames) == len(columnTypes))
        if(uniqueCountry):
            self.data['countries'] = dict()
            self.uniqueCountry = True
        self.data['total'] = 0
        self.data['cnames'] = columnNames
        self.data['ctypes'] = columnTypes
        self.countryCodeColumn = None
        for (index, t) in enumerate(columnTypes):
            if(t=='country code'):
                if(self.countryCodeColumn == None):
                    self.countryCodeColumn = index
                else:
                    # doesn't make sense to have multiple
                    raise(ValueError)
        if(self.countryCodeColumn == None):
            raise(ValueError)
            
        self.data['data'] = []

    def addRow(self, row):
        if(self.uniqueCountry):
            self.data['countries'][row[self.countryCodeColumn]] = len(self.data['data'])
        self.data['data'].append(row)
        self.data['total'] += 1

    def addRows(self, rows):
        for row in rows:
            self.addRow(row)
    
    def getJSON(self):
        """ Returns a string that is the JSON representation of self.data. """
        if(settings.DEBUG):
            return(json.dumps(self.data, indent=2))
        else:
            return(json.dumps(self.data, separators=(',', ':')))

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

def summed(p):
    """Sum transactions per country.

    Begin and end are both inclusive.

    Algorithm:
        * Get entries for year2 sorted by country
        * Get entries for (year1-1) sorted by country
        * Slice both of them correctly
        * Iterate through both sets in parallel
            * subtract the latter from the former in each entry
            * add up the selected types
        * Sort according to p.sortBy
    """

    queryset2 = Geschaeftslaendersummen.objects.filter(jahr=p.year2)
    queryset2 = queryset2.filter(p.getTypes("gueterArt__name"))
    queryset2 = queryset2.filter(p.countries)
    queryset2 = queryset2.order_by("endempfaengerstaat")

    queryset1 = Geschaeftslaendersummen.objects.filter(jahr=(p.year1-1))
    queryset1 = queryset1.filter(p.getTypes("gueterArt__name"))
    queryset1 = queryset1.filter(p.countries)
    queryset1 = queryset1.order_by("endempfaengerstaat")
    # TODO: Should I make a method for the above duplicate code?

    # TODO: This can be done more elegantly with the new apiData class
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

    result = apiData(True, ["id", "Name", "Exporte"], ['country code', 'country name', 'money'])
    for country in order:
        result.addRow([country, sums[country][0].name.de, sums[country][1]])
    return(result.getJSON())

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

    # write response
    if(p.granularity=="summed"):
        response.write(summed(p))
    elif(p.granularity=="summedPerYear"):
        writer = csv.writer(response)
        summedPerYear(p, writer)
    elif(p.granularity=="individual"):
        writer = csv.writer(response)
        individual(p, writer)

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
