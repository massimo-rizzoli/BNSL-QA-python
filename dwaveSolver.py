import torch
from QUBOMatrix import calcQUBOMatrix
from solverUtils import getPath, getExpectedSolution, printInfoResults, getPath

def dwaveQA(Q, indexQUBO, posOfIndex, n):
  pass

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