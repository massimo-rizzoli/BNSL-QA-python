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

  STABLE = 0; UNSTABLE = 1
  INTACT = 0; DEFECT = 1
  INDUSTRIAL = 0; HOUSEHOLD = 1
  H = 0; L = 1

  countV = {
    'burningRegimen': [0,0],
    'filterState': [0,0],
    'wasteType': [0,0],
    'co2Concentration': [0,0],
    'filterEfficiency': [0,0],
    'metalsInWaste': [0,0],
    'lightPenetrability': [0,0],
    'dustEmission': [0,0],
    'metalsEmission': [0,0]
  }

  count = 0
  prob = 0
  minZero = 1
  sumZero = 0
  notZero = 0
  countZero = 0

  with open('datasets/Waste2PExp{}.txt'.format(size), 'w') as file:
    #num vars, states of var 1,..., states of var 10
    file.write(str(9) + ' 2 2 2 2 2 2 2 2 2' + '\n')

    for burningRegimen in range(2):
      brprob = 0.85 if burningRegimen == STABLE else 0.15

      for filterState in range(2):
        fsprob = 0.95 if filterState == INTACT else 0.05

        for wasteType in range(2):
          wtprob = 0.29 if wasteType == INDUSTRIAL else 0.71

          for co2Concentration in range(2):
            if burningRegimen == STABLE:
              if co2Concentration == H:
                co2prob = 0.03
              elif co2Concentration == L:
                co2prob = 0.97
            elif burningRegimen == UNSTABLE:
              if co2Concentration == H:
                co2prob = 0.77
              elif co2Concentration == L:
                co2prob = 0.23

            for filterEfficiency in range(2):
              #for the current probabilities and discretization, only filterState matters
              if filterState == INTACT and wasteType == INDUSTRIAL:
                if filterEfficiency == H:
                  feprob = 1
                elif filterEfficiency == L:
                  feprob = 0; continue
              elif filterState == INTACT and wasteType == HOUSEHOLD:
                if filterEfficiency == H:
                  feprob = 1
                elif filterEfficiency == L:
                  feprob = 0; continue
              elif filterState == DEFECT and wasteType == INDUSTRIAL:
                if filterEfficiency == H:
                  feprob = 0; continue
                elif filterEfficiency == L:
                  feprob = 1
              elif filterState == DEFECT and wasteType == HOUSEHOLD:
                if filterEfficiency == H:
                  feprob = 0; continue
                elif filterEfficiency == L:
                  feprob = 1

              for metalsInWaste in range(2):
                if wasteType == INDUSTRIAL:
                  if metalsInWaste == H:
                    mwprob = 0.99
                  elif metalsInWaste == L:
                    mwprob = 0.01
                elif wasteType == HOUSEHOLD:
                  if metalsInWaste == H:
                    mwprob = 0; continue
                  elif metalsInWaste == L:
                    mwprob = 1

                for dustEmission in range(2):
                  if burningRegimen == STABLE and filterEfficiency == H:
                    if dustEmission == H:
                      deprob = 0; continue
                    elif dustEmission == L:
                      deprob = 1
                  elif burningRegimen == STABLE and filterEfficiency == L:
                    if dustEmission == H:
                      deprob = 0.99
                    elif dustEmission == L:
                      deprob = 0.01
                  elif burningRegimen == UNSTABLE and filterEfficiency == H:
                    if dustEmission == H:
                      deprob = 0.003
                    elif dustEmission == L:
                      deprob = 0.997
                  elif burningRegimen == UNSTABLE and filterEfficiency == L:
                    if dustEmission == H:
                      deprob = 1
                    elif dustEmission == L:
                      deprob = 0; continue

                  for lightPenetrability in range(2):
                    if dustEmission == H:
                      if lightPenetrability == H:
                        lpprob = 0.02
                      elif lightPenetrability == L:
                        lpprob = 0.98
                    elif dustEmission == L:
                      if lightPenetrability == H:
                        lpprob = 0.99
                      elif lightPenetrability == L:
                        lpprob = 0.01

                    for metalsEmission in range(2):
                      if metalsInWaste == H and dustEmission == H:
                        if metalsEmission == H:
                          meprob = 1
                        elif metalsEmission == L:
                          meprob = 0; continue
                      elif metalsInWaste == H and dustEmission == L:
                        if metalsEmission == H:
                          meprob = 0.99
                        elif metalsEmission == L:
                          meprob = 0.01
                      elif metalsInWaste == L and dustEmission == H:
                        if metalsEmission == H:
                          meprob = 0; continue
                        elif metalsEmission == L:
                          meprob = 1
                      elif metalsInWaste == L and dustEmission == L:
                        if metalsEmission == H:
                          meprob = 0; continue
                        elif metalsEmission == L:
                          meprob = 1

                      p = brprob * fsprob * wtprob * co2prob * feprob * mwprob * deprob * lpprob * meprob
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

                      countV['burningRegimen'][burningRegimen] += gen
                      countV['filterState'][filterState] += gen
                      countV['wasteType'][wasteType] += gen
                      countV['co2Concentration'][co2Concentration] += gen
                      countV['filterEfficiency'][filterEfficiency] += gen
                      countV['metalsInWaste'][metalsInWaste] += gen
                      countV['lightPenetrability'][lightPenetrability] += gen
                      countV['dustEmission'][dustEmission] += gen
                      countV['metalsEmission'][metalsEmission] += gen
                      file.write('{} {} {} {} {} {} {} {} {}\n'.format(burningRegimen,filterState,wasteType,co2Concentration,filterEfficiency,metalsInWaste,lightPenetrability,dustEmission,metalsEmission)*gen)

  #information about the generated data
  avgZero = sumZero/countZero if countZero != 0 else 0
  minZero = minZero if minZero != 1 else 0
  printResults(countV, count, minZero, avgZero, prob)

if __name__ == '__main__':
  main()
