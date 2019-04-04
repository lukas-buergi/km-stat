from django.http import HttpResponse
from django.template import loader
from django.db.models import Q

from exportkontrollstatistiken.models import Geschaefte, Uebersetzungen, Laender

import csv
import itertools
import datetime

# TODO: Where does this belong?
class apiParam():
    """Parst die Parameter und stellt sie praktischer zur Verfügung. TODO
        * Für die Typen eine Liste der Uebersetzungen-Objekte, die Namen von angefragten Typen sind.
        * Für die Länder eine Liste von Länder-Objekten, deren Geschäfte angefragt wurden"""
    
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
    
    def __init__(self, granularity, countries, types, year1, year2, sortby, perpage, pageNumber):
        if(granularity not in self.granularities):
            raise(ValueError)
        self.granularity=self.granularities[granularity]
        
        if(sortby not in self.sortByChoices):
            raise(ValueError)
        self.sortBy=self.sortByChoices[sortby]

        if(self.granularity=="summed" and self.sortBy not in ["-umfang", "umfang"]):
            raise(ValueError)
                
        if(0>year1 or year1 > year2):
            raise(ValueError)

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

    

def gapi(request, granularity, countries, types, year1, year2, sortby, perpage, pageNumber):
    """Die view, die die Geschäftsdaten an das Frontend liefert. Das Format ist csv, weil das deutlich datensparsamer ist als der eingebaute JSON serializer (Faktor >2, soweit ich das gesehen habe).
    Die Parameter erklären sich zusammen mit der apiParam Klasse."""

    # input validation and preparation
    try:
        p=apiParam(granularity, countries, types, year1, year2, sortby, perpage, pageNumber)
    except ValueError:
        raise
        return(HttpResponse("Invalid parameter."))
    
    # prepare queryset as far as possible
    queryset = Geschaefte.objects.filter(ende__gte=datetime.date(year1, 1, 1))
    queryset = queryset.filter(beginn__lte=datetime.date(year2, 12, 31))
    queryset = queryset.filter(p.types)
    queryset = queryset.filter(p.countries)

    # prepare response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="exporte-' + countries + "-" + types + "-" + str(year1) + "-" + str(year2) + "-" + str(pageNumber) + '.csv"'
    writer = csv.writer(response)

    # write response
    if(p.granularity=="summed"):
        # sort by country
        # sum up consecutive entries
        # until the country changes
        # sort by value TODO: Complain if other sort requested
        queryset = queryset.order_by("endempfaengerstaat")
        sums=dict()
        curCountry = None
        for g in queryset:
            if(g.endempfaengerstaat!=curCountry):
                curCountry=g.endempfaengerstaat
                curSum=g.umfang
                sums[curCountry] = curSum
            else:
                sums[curCountry]+=g.umfang

        if(p.sortBy=="-umfang"):
            reverse=True
        else:
            reverse=False
        
        for country in sorted(sums, key=sums.get, reverse=reverse):
            writer.writerow([country.code, country.name.de, sums[country]])
                
        
    elif(p.granularity=="summedPerYear"):
        # sort by country, year
        # sum up consecutive entries
        # until country or year changes
        # sort according to p.sortBy, but only certain combinations are valid:
        # * date asc+des, for a single country (that's the original order after the summing algorithm)
        # * value, descending (sort like for p.granularity=="summed")

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
            order=sums
        else:
            order=sorted(sums, key=lambda key : sums.get(key)[0], reverse=reverse) # does this work? TODO
        
        for country in order:
            writer.writerow([sums[country][2].code, sums[country][2].name.de, sums[country][1], sums[country][0]])

        
    elif(p.granularity=="individual"):
        queryset = queryset.order_by(p.sortBy)
        queryset = queryset[perpage*(pageNumber-1):perpage*pageNumber]
        
        titleRow=["Datum", "Art", "EKN", "Umfang"]
        if(not p.countriesSingle):
            titleRow = ["Ländercode", "Land"] + titleRow
        writer.writerow(titleRow)
        
        for g in queryset:
            row=[g.beginn, g.exportkontrollnummer.kontrollregime.gueterArt.name.de, g.exportkontrollnummer, g.umfang]
            if(not p.countriesSingle):
                row = [g.endempfaengerstaat.code, g.endempfaengerstaat.name.de] + row
            writer.writerow(row)

    return(response)

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
