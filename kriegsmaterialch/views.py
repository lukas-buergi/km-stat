from django.shortcuts import redirect

def archiveRedirect(request, url=''):
  return(redirect('https://kriegsmaterialexportverbotsinitiative.archiv.gsoa.ch/' + url, permanent=True))

def mainpageRedirect(request):
  return(redirect('https://www.kriegsmaterial.ch/', permanent=True))
