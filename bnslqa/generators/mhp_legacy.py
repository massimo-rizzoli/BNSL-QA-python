import random
import json
from bnslqa.generators.generator_utils import printResults, getSolutionVector

def generate(out, examples, countV):
  for i in range(examples):
    doors = [0,1,2]

    player = doors[random.randint(0,len(doors)-1)]
    countV['player'][player] += 1

    car = doors[random.randint(0,len(doors)-1)]
    countV['car'][car] += 1

    if player == car:
      doors.remove(player)
      host = doors[random.randint(0,len(doors)-1)]
    else:
      doors.remove(player)
      doors.remove(car)
      host = doors[0]
    countV['host'][host] += 1

    out.write('{} {} {}\n'.format(player,host,car))

  printResults(countV,examples)


def generateExpected(out, examples, countV):
  countGen = 0
  for player in range(3):
    for host in range(3):
      for car in range(3):
        gen = 0
        if player != host and car != host:
          if player == car:
            gen = examples * (1/3) * (1/3) * (1/2)
          else:
            gen = examples * (1/3) * (1/3) * 1
        gen = int(gen)
        countV['player'][player] += gen
        countV['host'][host] += gen
        countV['car'][car] += gen
        countGen += gen
        out.write('{} {} {}\n'.format(player,host,car)*gen)

  printResults(countV,countGen)


def main(args):
  problemPath = args.problem
  examples = args.size
  expected = args.expected
  name = args.name
  with open(problemPath,'r') as problemFile:
    problem = json.loads(problemFile.read())
    countV = {
      "player": [0,0,0],
      "host": [0,0,0],
      "car": [0,0,0]
    }
    dsName = name if name is not None else ''.join(['MHP', 'Exp' if expected else ''])
    with open('datasets/{}.txt'.format(dsName), 'w') as out:
      nVars = 3
      maxVarLen = 3
      out.write(' '.join( [str(nVars), '{} '.format(maxVarLen)*nVars, '\n'] ))
      out.write('{}\n{}\n'.format( problem['name'], ' '.join(map(str,getSolutionVector(problem['solution']))) ))
      if expected:
        generateExpected(out, examples, countV)
      else:
        generate(out, examples, countV)
      print('Generated dataset: datasets/{}.txt'.format(dsName))
