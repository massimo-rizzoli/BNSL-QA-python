from time import time_ns
import sys
import os
import torch
from QUBOMatrix import calcQUBOMatrix
from solverUtils import getPath, getExpectedSolution, printInfoResults, getPath, getNumExamples

from dimod.reference.samplers import ExactSolver
from neal import SimulatedAnnealingSampler
from dwave.system import DWaveSampler, EmbeddingComposite


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
  if len(sys.argv) < 5:
    annealTime = 1
  else:
    annealTime = int(sys.argv[4])
  return path, method, nReads, annealTime

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
    sampler = EmbeddingComposite(DWaveSampler(profile=os.getenv('DWAVE_PROFILE'),solver={'topology__type__eq':'pegasus'}))
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
  for i, (_, energy, occ, *_) in enumerate(record):
    if energy < minEnergy:
      minEnergy = energy
      occurrences = occ
      readFound = i
  return readFound, occurrences

def writeCSV(n, probName, alpha, method, nReads, annealTime,
             dsName, calcQUBOTime, annealTimeRes, readFound,
             occurrences, minY, expY, minXt, path):
  with open('./tests/testsAnneal.csv', 'a') as file:
    examples = getNumExamples(path)
    if method != 'QA':
      annealTime = '-'
    template = '{},'*12 + ',,' + '{},'*2 + '\'{}\'' + '\n'
    testResult = template.format(n,probName,alpha,examples,method,nReads,annealTime,dsName,calcQUBOTime/10**6,annealTimeRes/10**6,readFound,occurrences,minY,expY,minXt.int().tolist())
    file.write(testResult)

def dwaveSolve(Q, indexQUBO, posOfIndex, label, method='SA', nReads=100, annealTime=1):
  qubo = getDwaveQubo(Q,indexQUBO)
  sampler = getSampler(method=method)
  startAnneal = time_ns()
  if method == 'QA':
    sampleset = sampler.sample_qubo(qubo,num_reads=nReads,label=label,annealing_time=annealTime)
  else:
    sampleset = sampler.sample_qubo(qubo,num_reads=nReads,label=label)
  endAnneal = time_ns()
  if 'timing' in sampleset.info.keys():
    print(sampleset.info['timing'])
    annealTime = sampleset.info['timing']['qpu_access_time']
  else:
    annealTime = (endAnneal - startAnneal)//10**3
  minXt = getMinXt(sampleset.first.sample,indexQUBO,posOfIndex)
  minX = minXt.view(-1,1)
  minY = torch.matmul(torch.matmul(minXt,Q),minX).item()
  readFound, occurrences = getMinInfo(sampleset.record)
  return minXt, minY, readFound, occurrences, annealTime

def main():
  startCalcQUBO = time_ns()
  path, method, nReads, annealTime = getParams()
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
  minXt,minY,readFound,occurrences,annealTimeRes = dwaveSolve(Q,indexQUBO,posOfIndex,label,method=method,nReads=nReads,annealTime=annealTime)
  printInfoResults(expXt,expY,minXt,minY,n)
  print('Method: {}\nNumber of reads: {}\nOccurrencies of minX: {}\nFound minX at read: {}\nQUBO formulation time: {}\nAnnealing time: {}'.format(method,nReads,occurrences,readFound, calcQUBOTime/10**6, annealTimeRes/10**6))
  #write data to csv file
  afterName = 'Exp' if 'Exp' in path else '1'
  probName = path[path.find('/')+1:path.find(afterName)]
  writeCSV(n, probName, alpha, method, nReads, annealTime,
           dsName, calcQUBOTime, annealTimeRes, readFound,
           occurrences, minY, expY, minXt, path)

if __name__ == '__main__':
  main()
