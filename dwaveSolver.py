import torch
from QUBOMatrix import calcQUBOMatrix
from solverUtils import getPath, getExpectedSolution, printInfoResults, getPath

from dimod import BinaryQuadraticModel, Vartype
from dimod.reference.samplers import ExactSolver

def dwaveQA(Q, indexQUBO, posOfIndex, n):
  qubo = {}
  for i in range(len(indexQUBO)):
    for j in range(i,len(indexQUBO)):
      if Q[i][j] != 0:
        qubo[(indexQUBO[i],indexQUBO[j])] = Q[i,j].item()
  print()
  print(qubo)

  #bqm = BinaryQuadraticModel(linear,quadratic,offset,Vartype.BINARY)
  bqm = BinaryQuadraticModel.from_qubo(qubo)

  sampler = ExactSolver()
  response = sampler.sample(bqm)
  print(response.first)

  minXt = torch.zeros(len(indexQUBO))
  for index, value in response.first.sample.items():
    pos = posOfIndex[index]
    minXt[pos] = value

  minX = minXt.view(-1,1)
  minY = torch.matmul(torch.matmul(minXt,Q),minX).item()

  #with open('dimodOut.txt', 'w') as file:
    #file.write(str(response))

  return minXt, minY

def main():
  path = getPath()

  #calculate the QUBO matrix given the dataset path
  Q,indexQUBO,posOfIndex,n = calcQUBOMatrix(path,alpha='1/(ri*qi)')
  Q = torch.tensor(Q)
  
  #calculate the expected solution value
  expXt, expY = getExpectedSolution(path,Q,indexQUBO,posOfIndex,n)

  #find minimum of the QUBO problem xt Q x using dwave's Quantum Annealer
  minXt, minY = dwaveQA(Q,indexQUBO,posOfIndex,n)
  
  printInfoResults(expXt,expY,minXt,minY,n)

if __name__ == '__main__':
  main()