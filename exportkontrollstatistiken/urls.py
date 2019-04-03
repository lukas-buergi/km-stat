from django.urls import path

from . import views

urlpatterns = [
    path('api/g/<granularity>/<countries>/<types>/<int:year1>/<int:year2>/<sortby>/<int:perpage>/<int:pageNumber>', views.gapi, name='gapi'),
    path('table', views.table, name='table'),
    path('worldmap', views.worldmap, name='worldmap'),
]
