from time import time_ns
import sys
import torch
from numpy import array_equal
from QUBOMatrix import calcQUBOMatrix
from solverUtils import getPath, getExpectedSolution, printInfoResults, getPath

from dimod.reference.samplers import ExactSolver
from neal import SimulatedAnnealingSampler
from dwave.system import DWaveSampler, EmbeddingComposite
import dwave.inspector


def getParams():
  path = getPath()

  if len(sys.argv) < 3:
    method = 'SA'
  else:
    method = sys.argv[2]

  if len(sys.argv) < 4:
    nReads = 100
  else:
    nReads = int(sys.argv[3])
    
  return path, method, nReads

def getDwaveQubo(Q, indexQUBO):
  qubo = {}
  for i in range(len(indexQUBO)):
    for j in range(i,len(indexQUBO)):
      if Q[i][j] != 0:
        qubo[(indexQUBO[i],indexQUBO[j])] = Q[i,j].item()
  return qubo

def getSampler(method='SA'):
  sampler = None
  if method == 'SA':
    sampler = SimulatedAnnealingSampler()
  elif method == 'QA':
    sampler = EmbeddingComposite(DWaveSampler(solver={'topology__type__eq':'pegasus'}))
    print(sampler.child.properties['topology'])
    print(sampler.child.properties['chip_id'])
    print(sampler.child.properties.keys())
  else:
    sampler = ExactSolver()
  return sampler

def getMinXt(bestSample, indexQUBO, posOfIndex):
  minXt = torch.zeros(len(indexQUBO))
  for index, value in bestSample.items():
    pos = posOfIndex[index]
    minXt[pos] = value
  return minXt

def getMinInfo(record):
  readFound = None
  occurrences = None
  minEnergy = float('inf')
  for i, (xt, energy, occ, *_) in enumerate(record):
    if energy < minEnergy:
      minEnergy = energy
      occurrences = occ
      readFound = i
  return readFound, occurrences
    
def writeCSV(n, probName, alpha, method, nReads, dsName, calcQUBOTime, annealTime, readFound, occurrences, minY, expY, minXt):
  with open('./tests/testsAnneal.csv', 'a') as file:
    if '10K' in dsName:
      examples = 10000
    elif '100K' in dsName:
      examples = 100000
    elif '1M' in dsName:
      examples = 1000000
    template = '{},'*11 + ',,' + '{},'*2 + '\'{}\'' + '\n'
    testResult = template.format(n,probName,alpha,examples,method,nReads,dsName,calcQUBOTime/10**6,annealTime/10**6,readFound,occurrences,minY,expY,minXt.int().tolist())
    file.write(testResult)

def dwaveSolve(Q, indexQUBO, posOfIndex, label, method='SA', nReads=100):

  qubo = getDwaveQubo(Q,indexQUBO)

  sampler = getSampler(method=method)
  startAnneal = time_ns()
  sampleset = sampler.sample_qubo(qubo,num_reads=nReads,label=label)
  endAnneal = time_ns()
  if 'timing' in sampleset.info.keys():
    print(sampleset.info['timing'])
    annealTime = sampleset.info['timing']['qpu_access_time']
  else:
    annealTime = (endAnneal - startAnneal)//10**3
  #dwave.inspector.show(sampleset)
  minXt = getMinXt(sampleset.first.sample,indexQUBO,posOfIndex)
  minX = minXt.view(-1,1)
  minY = torch.matmul(torch.matmul(minXt,Q),minX).item()

  readFound, occurrences = getMinInfo(sampleset.record)

  with open('samplerOut.txt', 'w') as file:
    file.write(str(sampleset))

  return minXt, minY, readFound, occurrences, annealTime

def main():
  startCalcQUBO = time_ns()

  path, method, nReads = getParams()

  #calculate the QUBO matrix given the dataset path
  alpha = '1/(ri*qi)'
  Q,indexQUBO,posOfIndex,n = calcQUBOMatrix(path,alpha=alpha)
  Q = torch.tensor(Q)
  
  #calculate the expected solution value
  expXt, expY = getExpectedSolution(path,Q,indexQUBO,posOfIndex,n)

  endCalcQUBO = time_ns()
  calcQUBOTime = (endCalcQUBO - startCalcQUBO)//10**3

  #find minimum of the QUBO problem xt Q x using the specified sampler
  dsName = path[path.find('/')+1:path.find('.')]
  label = '{} - {} reads'.format(dsName,nReads)
  minXt,minY,readFound,occurrences,annealTime = dwaveSolve(Q,indexQUBO,posOfIndex,label,method=method,nReads=nReads)

  printInfoResults(expXt,expY,minXt,minY,n)
  print('Method: {}\nNumber of reads: {}\nOccurrencies of minX: {}\nFound minX at read: {}\nQUBO formulation time: {}\nAnnealing time: {}'.format(method,nReads,occurrences,readFound, calcQUBOTime/10**6, annealTime/10**6))

  afterName = 'Exp' if 'Exp' in path else '1'
  probName = path[path.find('/')+1:path.find(afterName)]

  writeCSV(n, probName, alpha, method, nReads, dsName, calcQUBOTime, annealTime, readFound, occurrences, minY, expY, minXt)

if __name__ == '__main__':
  main()