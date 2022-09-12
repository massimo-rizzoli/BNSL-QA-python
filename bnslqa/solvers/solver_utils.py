import torch

def getExpectedSolution(solution, Q, indexQUBO, posOfIndex, n):
  narcs = n*(n-1)
  expXt = torch.cat([torch.tensor(solution),torch.zeros(len(indexQUBO)-narcs)])
  expXt = setBestParams(expXt,indexQUBO,posOfIndex,n)
  #calculate expY accordingly
  expX = expXt.view(-1,1)
  expXtQ = torch.matmul(expXt,Q)
  expY = torch.matmul(expXtQ,expX).item()
  return expXt, expY

def getData(filename):
  with open(filename,'r') as f:
    lines = f.read().splitlines()
    #get info from first line
    info = lines.pop(0).split(' ')
    n = int(info[0])
    #number of states for each variable
    states = [ int(si) for si in info[1:n+1]]
    problemName = lines.pop(0)
    solution = list(map(int,lines.pop(0).split(' ')))
    #get examples
    examples = []
    for l in lines:
      ls = l.split(' ')
      examples += [[ int(x) for x in ls ]]
  return examples, n, states, problemName, solution

def dfs(v, G, visited, succ):
  #mark v as visited
  visited[v] = True
  #add adjacent nodes ov v to its successors
  succ[v] = succ[v].union(G[v])
  for u in G[v]:
    if not visited[u]:
      dfs(u,G,visited,succ)
    #add the successors of u to the successors of v
    succ[v] = succ[v].union(succ[u])

def findSucc(G, n):
  succ = [set() for i in range(n)]
  visited = [False for i in range(n)]
  #start exploration from every node
  for v in range(n):
    if not visited[v]:
      dfs(v,G,visited,succ)
  return succ

def completeGraph(G, n, succ):
  for u in range(n):
    for v in range(u+1,n):
      #if there is no edge between u and v
      if not (u in G[v]) and not (v in G[u]):
        #if u is not a successor of v add the edge (u,v)
        #else v comes before u, so to avoid cycles add the edge (v,u)
        if not (u in succ[v]):
          G[u].append(v)
        else:
          G[v].append(u)
        #refresh successor list
        succ = findSucc(G,n)

def setBestParams(xt, indexQUBO, posOfIndex, n):
  narcs = n*(n-1)
  countEdgesToVar = [0 for i in range(n)]
  for e in range(narcs):
    if xt[e] == 1:
      dij = indexQUBO[e]
      j = dij[2]
      countEdgesToVar[j] += 1
  #set correct penalties
  # 1. y
  for v in range(n):
    yv1 = ('y',v,1)
    yv2 = ('y',v,2)
    posYv1 = posOfIndex[yv1]
    posYv2 = posOfIndex[yv2]
    xt[posYv1] = 0
    xt[posYv2] = 0

    if countEdgesToVar[v] == 0:
      xt[posYv2] = 1
    elif countEdgesToVar[v] == 1:
      xt[posYv1] = 1
  # 2. r
  #explore graph and find successor lists for every node
  #generate adjacency vector
  G = [[] for i in range(n)]
  for a in range(narcs):
    if xt[a] == 1:
      dij = indexQUBO[a]
      i = dij[1]; j = dij[2]
      G[i].append(j)
  #calculate succesor list
  succ = findSucc(G,n)
  #complete the graph so that it becomes a fully connected DAG (avoid cicles)
  completeGraph(G,n,succ)
  #from successor list set r
  numR = int(n * (n - 1) / 2)
  posFirstR = posOfIndex[('r',0,1)]
  for a in range(posFirstR, posFirstR + numR):
    rij = indexQUBO[a]
    i = rij[1]; j = rij[2]
    if i in succ[j]:
      xt[a] = 0
    else:
      xt[a] = 1
  return xt

def printAdjMat(n, xt):
  narcs = n*(n-1)
  adjMat = torch.cat([torch.cat([torch.zeros(n-1).view(-1,1),xt[:narcs].view(-1,n)],dim=-1).view(-1),torch.zeros(1)]).view(n,n).int().tolist()
  for i in range(n):
    s = '[' + str(adjMat[i][0]) + ','
    for j in range(1,n-1):
      s += ' ' + str(adjMat[i][j]) + ','

    s += ' ' + str(adjMat[i][n-1]) + ']'
    print(s)

def getNumExamples(filename):
  with open(filename,'r') as f:
    # first line info on data
    return len(f.read().splitlines()) - 1

def printInfoResults(expXt, expY, minXt, minY, n):
  print('Expected adjacency matrix:')
  printAdjMat(n,expXt)
  print()
  print('Solution adjacency matrix:')
  printAdjMat(n,minXt)
  print()
  print('Expected solution:')
  print('expY = ' + str(expY))
  print('expX = ' + str(expXt.int().tolist()))
  print()
  print('Minimum found:')
  print('minY = ' + str(minY))
  print('minX = ' + str(minXt.int().tolist()))
  print()
  print('minY/expY = ' + str(minY/expY))
  print()
