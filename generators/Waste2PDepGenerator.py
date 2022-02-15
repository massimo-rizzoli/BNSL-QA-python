import sys
import random
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

  with open('datasets/Waste2PDep{}.txt'.format(size), 'w') as file:
    #num vars, states of var 1,..., states of var 10
    file.write(str(9) + ' 2 2 2 2 2 2 2 2 2' + '\n')

    for i in range(examples):
      burningRegimen = STABLE if random.uniform(0,1) <= 0.85 else UNSTABLE
      countV['burningRegimen'][burningRegimen] += 1

      filterState = INTACT if random.uniform(0,1) <= 0.95 else DEFECT
      countV['filterState'][filterState] += 1

      wasteType = INDUSTRIAL if random.uniform(0,1) <= 0.29 else HOUSEHOLD
      countV['wasteType'][wasteType] += 1

      if burningRegimen == STABLE:
        co2prob = 0.03
      elif burningRegimen == UNSTABLE:
        co2prob = 0.77
      co2Concentration = H if random.uniform(0,1) <= co2prob else L
      countV['co2Concentration'][co2Concentration] += 1

      if filterState == INTACT and wasteType == INDUSTRIAL:
        feprob = 1
      elif filterState == INTACT and wasteType == HOUSEHOLD:
        feprob = 0.9##
      elif filterState == DEFECT and wasteType == INDUSTRIAL:
        feprob = 0.1##
      elif filterState == DEFECT and wasteType == HOUSEHOLD:
        feprob = 0
      filterEfficiency = H if random.uniform(0,1) <= feprob else L
      countV['filterEfficiency'][filterEfficiency] += 1

      if wasteType == INDUSTRIAL:
        mwprob = 0.99
      elif wasteType == HOUSEHOLD:
        mwprob = 0
      metalsInWaste = H if random.uniform(0,1) <= mwprob else L
      countV['metalsInWaste'][metalsInWaste] += 1

      if burningRegimen == STABLE and filterEfficiency == H:
        deprob = 0
      elif burningRegimen == STABLE and filterEfficiency == L:
        deprob = 0.99
      elif burningRegimen == UNSTABLE and filterEfficiency == H:
        deprob = 0.2##
      elif burningRegimen == UNSTABLE and filterEfficiency == L:
        deprob = 0.8##
      dustEmission = H if random.uniform(0,1) <= deprob else L
      countV['dustEmission'][dustEmission] += 1

      if dustEmission == H:
          lpprob = 0.02
      elif dustEmission == L:
          lpprob = 0.99
      lightPenetrability = H if random.uniform(0,1) <= lpprob else L
      countV['lightPenetrability'][lightPenetrability] += 1

      if metalsInWaste == H and dustEmission == H:
          meprob = 1
      elif metalsInWaste == H and dustEmission == L:
          meprob = 0.99
      elif metalsInWaste == L and dustEmission == H:
          meprob = 0.1##
      elif metalsInWaste == L and dustEmission == L:
          meprob = 0
      metalsEmission = H if random.uniform(0,1) <= meprob else L
      countV['metalsEmission'][metalsEmission] += 1

      file.write('{} {} {} {} {} {} {} {} {}\n'.format(burningRegimen,filterState,wasteType,co2Concentration,filterEfficiency,metalsInWaste,lightPenetrability,dustEmission,metalsEmission))

  #information about the generated data
  printResults(countV,examples)

if __name__ == '__main__':
  main()
