NICHT AUSFÜHREN - das ist kein fertiges Skript, nur Schnipsel für die interaktive Konsole

Es geht hier darum so weit wie möglich automatisiert die Beschreibungen der ekn in die Datenbank zu laden - bei denen, die auf admin.ch als html beschrieben werden, sollte das weitestgehend funktionieren. Das sind wenn ich mich nicht täusche KM, ML, ChKV und Anhang 5.

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
