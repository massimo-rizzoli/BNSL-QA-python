from time import time_ns
import torch
from bnslqa.solvers.qubo_matrix import calcQUBOMatrix
from bnslqa.solvers.solver_utils import setBestParams, getExpectedSolution, printInfoResults, getNumExamples, getData
from multiprocessing import Process, Manager

def isMax(a):
  isMax = True
  i = 0
  while isMax and i < len(a):
    if a[i] == 1:
      i = i + 1
    else:
      isMax = False
  return isMax

def incrBinArray(a):
  add = 1
  i = len(a)-1
  while i >= 0 and add == 1:
    if a[i] == 0:
      add = 0
      a[i] = 1
    else:
      a[i] = 0
    i = i - 1

def bruteForce(Q, indexQUBO, posOfIndex, n, optim=True, rangeStart=0, xtStart=None, ret=None):
  if xtStart == None:
    xt = torch.zeros(len(indexQUBO))
  else:
    xt = xtStart.clone()
  minY = float('inf')
  minXt = None
  narcs = n*(n-1)
  #consider only the dij if optin is true
  rangeEnd = narcs if optim else len(indexQUBO)
  finished = False
  while not finished:
    x = xt.view(-1,1)
    y = torch.matmul(torch.matmul(xt,Q),x).item()
    #update min
    if y < minY:
      minY = y
      minXt = xt.clone()
    #check if finished
    if isMax(xt[rangeStart:rangeEnd]):
      finished = True
    else:
      #generate next xt
      incrBinArray(xt[rangeStart:rangeEnd])
      if optim:
        xt = setBestParams(xt,indexQUBO,posOfIndex,n)
  if ret != None:
    ret.append((minXt,minY))
  return minXt, minY

def bruteForceMultiproc(Q, indexQUBO, posOfIndex, n, optim=True):
  ret = Manager().list()
  xtStart = [torch.cat([torch.tensor([i,j]),torch.zeros(len(indexQUBO)-2)]) for i in range(2) for j in range(2)]
  procs = [Process(target=bruteForce,args=(Q,indexQUBO,posOfIndex,n,optim,2,xts,ret)) for xts in xtStart]
  for p in procs: p.start()
  for p in procs: p.join()
  minXt = None
  minY = float('inf')
  for r in ret:
    if r[1] < minY:
      minY = r[1]
      minXt = r[0]
  return minXt,minY

def writeCSV(n, probName, alpha, dsName, calcQUBOTime, timeES, optimisation, minY, expY, minXt, path):
  with open('./tests/tests_exhaustive_search.csv', 'a') as file:
    examples = getNumExamples(path)
    template = '{},'*4 + '\'{}\',' + '{},'*3 + ',,' + '{},'*2 + '\'{}\'' + '\n'
    testResult = template.format(n,probName,alpha,examples, optimisation,dsName,calcQUBOTime/10**6,timeES/10**6,minY,expY,minXt.int().tolist())
    file.write(testResult)

def main(args):
  startCalcQUBO = time_ns()
  path = args.dataset
  #calculate the QUBO matrix given the dataset path
  alpha = '1/(ri*qi)'
  examples, n, states, problemName, solution = getData(path)
  Q,indexQUBO,posOfIndex = calcQUBOMatrix(examples,n,states,alpha=alpha)
  Q = torch.tensor(Q)
  #calculate the expected solution value
  expXt, expY = getExpectedSolution(solution,Q,indexQUBO,posOfIndex,n)
  endCalcQUBO = time_ns()
  calcQUBOTime = (endCalcQUBO - startCalcQUBO)//10**3
  #find minimum of the QUBO problem xt Q x using bruteforce
  dsName = path[path.find('/')+1:path.find('.')]
  optim = True
  startES = time_ns()
  minXt, minY = bruteForceMultiproc(Q,indexQUBO,posOfIndex,n,optim=optim)
  endES = time_ns()
  timeES = (endES - startES)//10**3
  printInfoResults(expXt,expY,minXt,minY,n)
  optimisation = '-'
  if optim:
    optimisation = 'y,r'
  print('Optimization: {}\nQUBO formulation time: {}\nSearch time: {}'.format(optimisation, calcQUBOTime/10**6, timeES/10**6))
  #write data to csv file
  writeCSV(n, problemName, alpha, dsName, calcQUBOTime, timeES, optimisation, minY, expY, minXt, path)
