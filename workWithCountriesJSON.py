NICHT AUSFÜHREN - das ist kein fertiges Skript, nur Schnipsel für die interaktive Konsole

from exportkontrollstatistiken.models import *
import json
f = open('/home/t4b/persönlich/engagement/gsoa/webseite/django/kriegsmaterialch/exportkontrollstatistiken/static/exportkontrollstatistiken/world_countries.json', 'r')
d = json.loads(f.read())
for country in d["features"]:
  pass
