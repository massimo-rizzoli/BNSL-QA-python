import random
import sys
from generatorUtils import printResults

def main():
  if len(sys.argv) < 2:
    print('Number of examples needed')
    exit()
  examples = int(sys.argv[1])
  size = ''
  if examples/10**4 == 1:
    size = '10K'
  elif examples/10**5 == 1:
    size = '100K'
  elif examples/10**6 == 1:
    size = '1M'

  LOW = 0; HIGH = 1
  POS = 1; NEG = 0
  T = 1; F = 0

  pollutionCount = [0,0]
  smokerCount = [0,0]
  cancerCount = [0,0]
  xrayCount = [0,0]

  with open('datasets/LC4Vars{}.txt'.format(size), 'w') as file:
    #num vars, states of var 1,..., states of var 5
    file.write(str(4) + ' 2 2 2 2' + '\n')
    for i in range(examples):
      #random pollution choice
      pollution = LOW if random.uniform(0,1) <= 0.90 else HIGH
      pollutionCount[pollution] += 1

      #random smoker choice
      smoker =  T if random.uniform(0,1) <= 0.30 else F
      smokerCount[smoker] += 1

      #calculate cancer
      prob = None
      if pollution == HIGH and smoker == T:
        cprob = 0.05
      elif pollution == HIGH and smoker == F:
        cprob = 0.02
      elif pollution == LOW and smoker == T:
        cprob = 0.03
      elif pollution == LOW and smoker == F:
        cprob = 0.001
      cancer = T if random.uniform(0,1) <= cprob else F
      cancerCount[cancer] += 1

      #calculate xray
      if cancer == T:
        xprob = 0.90
      elif cancer == F:
        xprob = 0.20
      xray = T if random.uniform(0,1) <= xprob else F
      xrayCount[xray] += 1

      file.write(str(pollution) + ' ' + str(smoker) + ' ' + str(cancer) + ' ' + str(xray) + '\n')

  #information about the generated data
  countV = {
    'pollution': pollutionCount,
    'smoker': smokerCount,
    'cancer': cancerCount,
    'xray': xrayCount,
  }
  printResults(countV,examples)

if __name__ == '__main__':
  main()
