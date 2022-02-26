import json
import os
import random
from bnslqa.generators.generator_utils import printResults, getGraph, getTopOrder, getSolutionVector

def addCounts(out, variables, variableRealisations, examples,
              countV, probV, cumulProb, countGen, notZero,
              countZero, sumZero, minZero):
  p = 1
  for varName in variables:
    p *= probV[varName]

  gen = examples * p
  cumulProb += p
  gen = round(gen)
  countGen = countGen + gen
  if gen != 0:
    notZero += 1
  else:
    countZero += 1
    sumZero += p
    if p != 0:
      minZero = min(minZero, p)

  for varName in variables:
    varRealis = variableRealisations[varName]
    countV[varName][varRealis] += gen

  setting = ' '.join(map(str, [ variableRealisations[varName] for varName in variables ]))
  out.write('{}\n'.format(setting)*gen)
  return countV, cumulProb, countGen, notZero, countZero, sumZero, minZero

def getCptEntry(cpt, parents, variableRealisations):
  if len(parents) == 0:
    return cpt
  else:
    firstParentRealis = variableRealisations[parents[0]]
    return getCptEntry(cpt[firstParentRealis], parents[1:], variableRealisations)


def calcProbRec(varNames, out, variables, states, variableRealisations, examples, countV, probV, cumulProb, countGen, notZero, countZero, sumZero, minZero):
  if len(varNames) == 0:
    return addCounts(out, variables, variableRealisations, examples,
                     countV, probV, cumulProb, countGen, notZero,
                     countZero, sumZero, minZero)
  else:
    varName = varNames[0]
    cpt = variables[varName]['cpt']
    parents = variables[varName]['parents']
    for varRealis in range(states[varName]):
      variableRealisations[varName] = varRealis
      cptEntry = getCptEntry(cpt, parents, variableRealisations)
      if varRealis == states[varName] - 1:
        # compute probability of last state from the rest
        probV[varName] = 1 - sum(cptEntry)
      else:
        probV[varName] = cptEntry[varRealis]
      countV, cumulProb, countGen, notZero, countZero, sumZero, minZero = calcProbRec(varNames[1:], out, variables,
                                                                                      states, variableRealisations,
                                                                                      examples, countV, probV,
                                                                                      cumulProb, countGen, notZero,
                                                                                      countZero, sumZero, minZero)
    return countV, cumulProb, countGen, notZero, countZero, sumZero, minZero

def generateExpected(out, variables, varsTopOrder, states, examples, countV):
  varNames = varsTopOrder
  variableRealisations = {}
  probV = {}
  countGen = 0
  cumulProb = 0
  minZero = 1
  sumZero = 0
  notZero = 0
  countZero = 0
  countV, cumulProb, countGen, notZero, countZero, sumZero, minZero = calcProbRec(varNames, out, variables,
                                                                                  states, variableRealisations,
                                                                                  examples, countV, probV,
                                                                                  cumulProb, countGen, notZero,
                                                                                  countZero, sumZero, minZero)
  avgZero = sumZero/countZero if countZero != 0 else 0
  minZero = minZero if minZero != 1 else 0
  printResults(countV, countGen, minZero, avgZero, cumulProb)


def getVarRealis(r, cptEntry, states):
  if len(cptEntry) == 0:
    return states[0]
  else:
    if r < cptEntry[0]:
      return states[0]
    else:
      return getVarRealis(r - cptEntry[0], cptEntry[1:], states[1:])

def generate(out, variables, varsTopOrder, states, examples, countV):
  variableRealisations = {}
  probV = {}
  for i in range(examples):
    for varName in varsTopOrder:
      cpt = variables[varName]['cpt']
      parents = variables[varName]['parents']
      cptEntry = getCptEntry(cpt, parents, variableRealisations)
      r = random.uniform(0,1)
      varRealis = getVarRealis(r, cptEntry, [ i for i in range(states[varName]) ])
      variableRealisations[varName] = varRealis
      if varRealis == states[varName] - 1:
        # compute probability of last state from the rest
        probV[varName] = 1 - sum(cptEntry)
      else:
        probV[varName] = cptEntry[varRealis]
      countV[varName][varRealis] += 1
    setting = ' '.join(map(str, [ variableRealisations[varName] for varName in variables ]))
    out.write('{}\n'.format(setting))
  printResults(countV, examples)



def main(args):
  problemPath = args.problem
  examples = args.size
  expected = args.expected
  name = args.name

  if not os.path.exists(problemPath):
    args.parser.exit(1,'Error: \'{}\' file does not exist\n'.format(problemPath))

  with open(problemPath,'r') as problemFile:
    problem = json.loads(problemFile.read())

    variables = problem['variables']
    states = { varName: len(variables[varName]['states']) for varName in variables }
    maxVarLen = max(states.values())
    countV = {}
    for varName in variables:
      countV[varName] = [0 for i in range(maxVarLen)]

    if 'toporder' not in problem.keys():
      varsTopOrder = getTopOrder(getGraph(variables))
      if varsTopOrder is None:
        args.parser.exit(1,'Error: cannot find a topological order for \'{}\'. Is the problem acyclic?\n'.format(problemPath))
    else:
      # for backwards compatibility (datasets generated exactly as for the experiments)
      varsTopOrder = problem['toporder']

    dsName = name if name is not None else ''.join([problem['name'], 'Exp' if expected else ''])
    with open('datasets/{}.txt'.format(dsName), 'w') as out:
      nVars = len(variables)
      out.write(' '.join( [str(nVars), '{} '.format(maxVarLen)*nVars, '\n'] ))

      out.write('{}\n{}\n'.format( problem['name'], ' '.join(map(str,getSolutionVector(problem['solution']))) ))

      if expected:
        generateExpected(out, variables, varsTopOrder, states, examples, countV)
      else:
        generate(out, variables, varsTopOrder, states, examples, countV)
      print('Generated dataset: datasets/{}.txt'.format(dsName))
