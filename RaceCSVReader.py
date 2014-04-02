def filterByClass(filterclass, top, data):
  count = 0
  for line in data:
    player = line.split(',')
    if player[0] == 'LoginStatus':
       continue
    if player[4] == filterclass or filterclass == 'All':
      ## Comment out the following if you want to see dead characters.
      if 'Dead' in player[-1]:
        continue
      count += 1
      print str(count) + ": " + str(player)
      if count >= int(top):
        break

scion = 0
marauder = 0
witch = 0
templar = 0
duelist = 0
ranger = 0
shadow = 0

filename = raw_input("Filename: ")
rawdata = open(filename, 'r')
data = rawdata.readlines()

for line in data:
  playerclass = line.split(',')[4]
  if playerclass == 'Marauder':
    marauder += 1
  if playerclass == 'Scion':
    scion += 1
  if playerclass == 'Witch':
    witch += 1
  if playerclass == 'Templar':
    templar += 1
  if playerclass == 'Duelist':
    duelist += 1
  if playerclass == 'Ranger':
    ranger += 1
  if playerclass == 'Shadow':
    shadow += 1


print 'Marauder:' + str(marauder)
print 'Scion:' + str(scion)
print 'Witch:' + str(witch)
print 'Templar:' + str(templar)
print 'Duelist:' + str(duelist)
print 'Ranger:' + str(ranger)
print 'Shadow:' + str(shadow)


classtoview = raw_input("Which Top Class players would you like to see?")
howmany = raw_input("how many?")

filterByClass(classtoview, howmany, data)
