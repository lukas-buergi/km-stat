from django.shortcuts import redirect

def archiveRedirect(request, url=''):
  if(url == None):
    url=""
  return(redirect('https://kriegsmaterialexportverbotsinitiative.archiv.gsoa.ch/' + str(url), permanent=True))

def mainpageRedirect(request):
  return(redirect('https://www.kriegsmaterial.ch/', permanent=True))
