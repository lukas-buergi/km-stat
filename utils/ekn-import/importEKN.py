#######################################################################
# Copyright Lukas Bürgi 2019
#
# This file is part of km-stat.
#
# km-stat is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# km-stat is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public
# License for more details.
#
# You should have received a copy of the GNU Affero General Public
# License along with km-stat.  If not, see
# <https://www.gnu.org/licenses/>.
########################################################################

NICHT AUSFÜHREN - das ist kein fertiges Skript, nur Schnipsel für die interaktive Konsole

Es geht hier darum so weit wie möglich automatisiert die Beschreibungen der ekn in die Datenbank zu laden - bei denen, die auf admin.ch als html beschrieben werden, sollte das weitestgehend funktionieren. Das sind wenn ich mich nicht täusche KM, ChKV und Anhang 5.

Anhang 5 ist so kurz, dass ich es komplett von Hand gemacht habe.

# ChKV ekn import
# html table to csv using libreoffice
f = open('946.202.21-ChKV-Dreisprachig-2013-10-01.csv')
for line in chkv:
  if(line[0]==""):
    line[0]=chkvArray[-1][0]
  chkvArray.append(line)

chkvUnique = []
chkvIt = chkvArray.__iter__()
chkvUnique.append(chkvIt.__next__())
for line in chkvIt:
  if(line[0] == chkvUnique[-1][0]):
    for i in [1, 2, 3]:
      chkvUnique[-1][i] += '<br>' + line[i]
  else:
    chkvUnique.append(line)
for line in chkvUnique:
  for cell in line:
    cell=cell.replace('\\n', ' ')

r = open('946.202.21-ChKV-Dreisprachig-2013-10-01-zwischenschritt-1.csv', 'w')
writer = csv.writer(r)
writer.writerows(chkvUnique)
r.close()
