from os import read
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
    num_reads = 100
  else:
    num_reads = int(sys.argv[3])
    
  return path, method, num_reads

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
  readN = None
  occurrences = None
  minEnergy = float('inf')
  for i, (xt, energy, occ, *_) in enumerate(record):
    if energy < minEnergy:
      minEnergy = energy
      occurrences = occ
      readN = i
  return readN, occurrences
    
def dwaveSolve(Q, indexQUBO, posOfIndex, label, method='SA', num_reads=100):

  qubo = getDwaveQubo(Q,indexQUBO)

  sampler = getSampler(method=method)
  sampleset = sampler.sample_qubo(qubo,num_reads=num_reads,label=label)
  dwave.inspector.show(sampleset)
  minXt = getMinXt(sampleset.first.sample,indexQUBO,posOfIndex)
  minX = minXt.view(-1,1)
  minY = torch.matmul(torch.matmul(minXt,Q),minX).item()

  readN, occurrences = getMinInfo(sampleset.record)

  with open('samplerOut.txt', 'w') as file:
    file.write(str(sampleset))

  return minXt, minY, readN, occurrences

def main():
  path, method, num_reads = getParams()

  #calculate the QUBO matrix given the dataset path
  Q,indexQUBO,posOfIndex,n = calcQUBOMatrix(path,alpha='1/(ri*qi)')
  Q = torch.tensor(Q)
  
  #calculate the expected solution value
  expXt, expY = getExpectedSolution(path,Q,indexQUBO,posOfIndex,n)

  #find minimum of the QUBO problem xt Q x using the specified sampler
  problemName = path[path.find('/')+1:path.find('.')]
  label = '{} - {} reads'.format(problemName,num_reads)
  minXt, minY, readN, occurrences = dwaveSolve(Q,indexQUBO,posOfIndex,label,method=method,num_reads=num_reads)
  
  printInfoResults(expXt,expY,minXt,minY,n)
  print('Method: {}\nNumber of reads: {}\nOccurrencies of minX: {}\nFound minX at read: {}'.format(method,num_reads,occurrences,readN))

if __name__ == '__main__':
  main()