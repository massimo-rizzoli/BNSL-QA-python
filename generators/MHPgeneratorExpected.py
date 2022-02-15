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

  with open('datasets/MHPExp{}.txt'.format(size), 'w') as file:
    #num vars, states of var 1,..., states of var 3
    file.write(str(3) + ' 3 3 3' + '\n')
    count = 0
    #player host car
    for player in range(3):
      for host in range(3):
        for car in range(3):
          gen = 0
          if player != host and car != host:
            if player == car:
              gen = games * (1/3) * (1/3) * (1/2)
              win = win + gen
            else:
              gen = games * (1/3) * (1/3) * 1
          for i in range(int(gen)):
            file.write(str(player) + ' ' + str(host) + ' ' + str(car) + '\n')
            playerCount[player] += 1
            hostCount[host] += 1
            carCount[car] += 1
            count += 1

  #information about the generated data
  print('The player never changes door')
  print('Games played: ' + str(games))
  print('Vicrories:    ' + str(win))
  print('Defeats:      ' + str(games-win))
  print('Actual games: ' + str(count))
  print(' '*9 + 'Door 0   Door 1   Door 2')
  print('Player' + ' '*3 + str(playerCount[0]) + ' '*(9-len(str(playerCount[0]))) + str(playerCount[1]) + ' '*(9-len(str(playerCount[1]))) + str(playerCount[2]))
  print('Host' + ' '*5 + str(hostCount[0]) + ' '*(9-len(str(hostCount[0]))) + str(hostCount[1]) + ' '*(9-len(str(hostCount[1]))) + str(hostCount[2]))
  print('Car' + ' '*6 + str(carCount[0]) + ' '*(9-len(str(carCount[0]))) + str(carCount[1]) + ' '*(9-len(str(carCount[1]))) + str(carCount[2]))

if __name__ == '__main__':
  main()
