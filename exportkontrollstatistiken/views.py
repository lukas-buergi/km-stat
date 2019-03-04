#from django.shortcuts import render

# Create your views here.
## MY CODE BELOW
from django.http import HttpResponse

def index(request):
    return HttpResponse("Hello, world.")
