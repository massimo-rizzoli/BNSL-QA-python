import random
import sys

def main():
  if len(sys.argv) < 2:
    print('Number of games needed')
    exit()
  games = int(sys.argv[1])
  win = 0
  hostCount = [0,0,0]
  carCount = [0,0,0]
  size = ''
  if games/10**4 == 1:
    size = '10K'
  elif games/10**5 == 1:
    size = '100K'
  elif games/10**6 == 1:
    size = '1M'

  hostAfterCar = [{},{},{}]
  for i in range(3):
    for j in range(3):
      #if i != j:
        hostAfterCar[i][j] = 0

  with open('datasets/MHP2Vars{}.txt'.format(size), 'w') as file:
    #num vars, states of var 1,..., states of var 2
    file.write(str(2) + ' 3 3' + '\n')
    for i in range(0,games):
      doors = [0,1,2]

      #random car placement
      car = doors[random.randint(0,len(doors)-1)]
      carCount[car] += 1

      #calculate host (uniformly choose either of the remaining doors)
      doors.remove(car)
      host = doors[random.randint(0,len(doors)-1)]
      hostCount[host] += 1

      hostAfterCar[car][host] += 1

      #count victories
      win = win + 1
      #print(str(player) + ' '*6 + str(host) + ' '*6 + str(car))
      file.write(str(host) + ' ' + str(car) + '\n')

  #information about the generated data
  print('The player alwais chooses the door with the car')
  print('Games played: ' + str(games))
  print('Vicrories:    ' + str(win))
  print('Defeats:      ' + str(games-win))
  print(' '*9 + 'Door 0   Door 1   Door 2')
  print('Host' + ' '*5 + str(hostCount[0]) + ' '*(9-len(str(hostCount[0]))) + str(hostCount[1]) + ' '*(9-len(str(hostCount[1]))) + str(hostCount[2]))
  print('Car' + ' '*6 + str(carCount[0]) + ' '*(9-len(str(carCount[0]))) + str(carCount[1]) + ' '*(9-len(str(carCount[1]))) + str(carCount[2]))

  for i in range(3):
    s = 'after car in door ' + str(i) + ': {'
    for j in range(3):
      #if i != j:
        tmp = str(hostAfterCar[i][j])
        width = 6
        s += 'host door ' + str(j) + ': ' + str(tmp) + ' '*(width - len(tmp))
    s += '}'
    print(s)

if __name__ == '__main__':
  main()
