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
