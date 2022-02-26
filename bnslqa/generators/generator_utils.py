import copy
import torch

def getSolutionVector(adj):
  adj = torch.tensor(adj)
  n = adj.shape[0]
  # add filler zeros and reshape so that the main diagonal is on the first column
  adj = torch.cat([adj.view(-1),torch.zeros(n)]).view(-1,n+1)
  # remove the last row (filler zeros) and the first column (originally main diagonal)
  adj = adj[:n-1,1:]
  # make it a 1D tensor
  adj = torch.reshape(adj,(-1,))
  return adj.int().tolist()

def getTopOrder(graph):
  topOrder = []
  varsNoParents = [ varName for varName in graph if len(graph[varName]['parents']) == 0 ]
  while len(varsNoParents) > 0:
    v = varsNoParents.pop(0)
    topOrder.append(v)
    children = copy.deepcopy(graph[v]['children'])
    for u in children:
      graph[v]['children'].remove(u)
      graph[u]['parents'].remove(v)
      if len(graph[u]['parents']) == 0:
        varsNoParents.append(u)
  edgesPresent = False
  for varName in graph:
    if len(graph[varName]['children']) != 0:
      edgesPresent = True
      break
  if edgesPresent:
    return None
  else:
    return topOrder

def getGraph(variables):
  graph = { varName: {'parents': [], 'children': []} for varName in variables}
  for varName in variables:
    graph[varName]['parents'] = copy.deepcopy(variables[varName]['parents'])
    for parent in variables[varName]['parents']:
      graph[parent]['children'].append(varName)
  return graph


def printResults(countV, examplesGenerated, minZero=None, avgZero=None, cumulProb=None):
  print('Examples generated: ' + str(examplesGenerated))
  if cumulProb: print('Cumulative probability: {}'.format(cumulProb))
  if minZero: print('Min zero probability: {}'.format(minZero))
  if avgZero: print('Avg zero probability: {}'.format(avgZero))
  names = countV.keys()
  firstColW = max(map(len,names))
  colW = 10
  cols = ' '*firstColW
  nStates =  max(map(len,countV.values()))
  for i in range(nStates):
    cols +=  ' '*(colW-7) + 'State {}'.format(i)
  print(cols)
  for var, states in countV.items():
    rowVar = str(var) + ' '*(firstColW-len(str(var)))
    for state in states:
      stateStr = '{0:.4f}'.format(state/examplesGenerated)
      rowVar += ' '*(colW-len(stateStr)) + stateStr
    print(rowVar)
