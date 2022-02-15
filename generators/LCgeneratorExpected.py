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
  dyspnoeaCount = [0,0]

  count = 0
  prob = 0
  minZero = 1
  sumZero = 0
  notZero = 0
  countZero = 0

  with open('datasets/LCExp{}.txt'.format(size), 'w') as file:
    #num vars, states of var 1,..., states of var 5
    file.write(str(5) + ' 2 2 2 2 2' + '\n')

    for pollution in range(2):
      pprob = 0.90 if pollution == LOW else 0.10

      for smoker in range(2):
        sprob = 0.30 if smoker == T else 0.70

        for cancer in range(2):
          if pollution == HIGH and smoker == T:
            if cancer == T:
              cprob = 0.05
            elif cancer == F:
              cprob =  0.95
          elif pollution == HIGH and smoker == F:
            if cancer == T:
              cprob = 0.02
            elif cancer == F:
              cprob = 0.98
          elif pollution == LOW and smoker == T:
            if cancer == T:
              cprob = 0.03
            elif cancer == F:
              cprob = 0.97
          elif pollution == LOW and smoker == F:
            if cancer == T:
              cprob = 0.001
            elif cancer == F:
              cprob = 0.999

          for xray in range(2):
            if cancer == T:
              if xray == POS:
                xprob = 0.90
              elif xray == NEG:
                xprob = 0.10
            elif cancer == F:
              if xray == POS:
                xprob = 0.20
              elif xray == NEG:
                xprob = 0.80

            for dyspnoea in range(2):
              if cancer == T:
                if dyspnoea == T:
                  dprob = 0.65
                elif dyspnoea == F:
                  dprob = 0.35
              elif cancer == F:
                if dyspnoea == T:
                  dprob = 0.30
                elif dyspnoea == F:
                  dprob = 0.70

              p = pprob * sprob * cprob * xprob * dprob
              gen = examples * p
              prob += p

              gen = round(gen)
              count = count+gen
              if gen != 0:
                notZero += 1
              else:
                countZero += 1
                sumZero += p
                if p != 0:
                  minZero = min(minZero, p)

              pollutionCount[pollution] += gen
              smokerCount[smoker] += gen
              cancerCount[cancer] += gen
              xrayCount[xray] += gen
              dyspnoeaCount[dyspnoea] += gen
              for i in range(gen):
                file.write(str(pollution) + ' ' + str(smoker) + ' ' + str(cancer) + ' ' + str(xray) + ' ' + str(dyspnoea) + '\n')

  #information about the generated data
  avgZero = sumZero/countZero if countZero != 0 else 0
  minZero = minZero if minZero != 1 else 0
  countV = {
    'pollution': pollutionCount,
    'smoker': smokerCount,
    'cancer': cancerCount,
    'xray': xrayCount,
    'dyspnoea': dyspnoeaCount,
  }
  printResults(countV, count, minZero, avgZero, prob)

if __name__ == '__main__':
  main()
