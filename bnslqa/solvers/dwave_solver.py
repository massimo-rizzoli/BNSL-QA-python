from time import time_ns
import os
import torch
from bnslqa.solvers.qubo_matrix import calcQUBOMatrix
from bnslqa.solvers.solver_utils import getExpectedSolution, printInfoResults, getNumExamples, getData

from dimod.reference.samplers import ExactSolver
from neal import SimulatedAnnealingSampler
from dwave.system import DWaveSampler, EmbeddingComposite


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
  with open('./tests/tests_anneal.csv', 'a') as file:
    examples = getNumExamples(path)
    if method != 'QA':
      annealTime = '-'
    template = '{},'*12 + ',,' + '{},'*2 + '\'{}\'' + '\n'
    testResult = template.format(n,probName,alpha,examples,method,nReads,annealTime,dsName,calcQUBOTime/10**6,annealTimeRes/10**6,readFound,occurrences,minY,expY,minXt.int().tolist())
    file.write(testResult)

def dwaveSolve(Q, indexQUBO, posOfIndex, label, method='SA', nReads=10000, annealTime=99):
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

def main(args):
  startCalcQUBO = time_ns()
  path = args.dataset
  method = args.strategy
  nReads = args.reads
  annealTime = args.anneal
  #calculate the QUBO matrix given the dataset path
  alpha = '1/(ri*qi)'
  examples, n, states, problemName, solution = getData(path)
  Q, indexQUBO, posOfIndex = calcQUBOMatrix(examples,n,states,alpha=alpha)
  Q = torch.tensor(Q)
  #calculate the expected solution value
  expXt, expY = getExpectedSolution(solution,Q,indexQUBO,posOfIndex,n)
  endCalcQUBO = time_ns()
  calcQUBOTime = (endCalcQUBO - startCalcQUBO)//10**3
  #find minimum of the QUBO problem xt Q x using the specified sampler
  dsName = path[path.find('/')+1:path.find('.')]
  label = '{} - {} reads'.format(dsName,nReads)
  minXt,minY,readFound,occurrences,annealTimeRes = dwaveSolve(Q,indexQUBO,posOfIndex,label,method=method,nReads=nReads,annealTime=annealTime)
  printInfoResults(expXt,expY,minXt,minY,n)
  print('Method: {}\nNumber of reads: {}\nOccurrencies of minX: {}\nFound minX at read: {}\nQUBO formulation time: {}\nAnnealing time: {}'.format(method,nReads,occurrences,readFound, calcQUBOTime/10**6, annealTimeRes/10**6))
  #write data to csv file
  writeCSV(n, problemName, alpha, method, nReads, annealTime,
           dsName, calcQUBOTime, annealTimeRes, readFound,
           occurrences, minY, expY, minXt, path)
