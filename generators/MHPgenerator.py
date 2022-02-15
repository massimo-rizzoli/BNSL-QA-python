import random
import sys

def main():
  if len(sys.argv) < 2:
    print('Number of games needed')
    exit()
  games = int(sys.argv[1])
  win = 0
  playerCount = [0,0,0]
  hostCount = [0,0,0]
  carCount = [0,0,0]
  size = ''
  if games/10**4 == 1:
    size = '10K'
  elif games/10**5 == 1:
    size = '100K'
  elif games/10**6 == 1:
    size = '1M'

  with open('datasets/MHP{}.txt'.format(size), 'w') as file:
    #num vars, states of var 1,..., states of var 3
    file.write(str(3) + ' 3 3 3' + '\n')
    for i in range(0,games):
      doors = [0,1,2]

      #random player choice
      player = doors[random.randint(0,len(doors)-1)]
      playerCount[player] += 1

      #random car placement
      car = doors[random.randint(0,len(doors)-1)]
      carCount[car] += 1

      #calculate host
      if player == car:
        doors.remove(player)
        host = doors[random.randint(0,len(doors)-1)]
      else:
        doors.remove(player)
        doors.remove(car)
        host = doors[0]
      #host = doors[random.randint(0,len(doors)-1)] #to generate it independently (alternative to if)
      hostCount[host] += 1

      #count victories
      if player == car:
        win = win + 1
      #print(str(player) + ' '*6 + str(host) + ' '*6 + str(car))
      file.write(str(player) + ' ' + str(host) + ' ' + str(car) + '\n')

  #information about the generated data
  print('The player never changes door')
  print('Games played: ' + str(games))
  print('Vicrories:    ' + str(win))
  print('Defeats:      ' + str(games-win))
  print(' '*9 + 'Door 0   Door 1   Door 2')
  print('Player' + ' '*3 + str(playerCount[0]) + ' '*(9-len(str(playerCount[0]))) + str(playerCount[1]) + ' '*(9-len(str(playerCount[1]))) + str(playerCount[2]))
  print('Host' + ' '*5 + str(hostCount[0]) + ' '*(9-len(str(hostCount[0]))) + str(hostCount[1]) + ' '*(9-len(str(hostCount[1]))) + str(hostCount[2]))
  print('Car' + ' '*6 + str(carCount[0]) + ' '*(9-len(str(carCount[0]))) + str(carCount[1]) + ' '*(9-len(str(carCount[1]))) + str(carCount[2]))

if __name__ == '__main__':
  main()
