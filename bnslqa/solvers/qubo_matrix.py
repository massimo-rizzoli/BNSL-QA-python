from bnslqa.solvers.qubo_values import getValues

def red(s):
  return "\033[91m{}\033[00m".format(s)
def green(s):
  return "\033[92m{}\033[00m".format(s)
def blue(s):
  return "\033[94m{}\033[00m".format(s)

def printMatrix(m, index, startRow=0, endRow=None, startCol=0, endCol=None, cellW=10, indexW=5):
  if endRow == None:
    endRow = len(m)
  if endCol == None:
    endCol = len(m[0])

  #indexes for the columns of the matrix
  s=' '*indexW
  for x in range(startCol,endCol):
    tmp = index[x][0] + str(index[x][1]) + str(index[x][2])
    s += ' '*(cellW-len(tmp)-1) + tmp + ' '
  print(s)
  print(' '*indexW + '-'*cellW*(endCol-startCol))

  for i in range(startRow,endRow):
    #indexes for the rows of the matrix
    tmp = index[i][0] + str(index[i][1]) + str(index[i][2])

    s = tmp + ' '*(indexW-len(tmp)-1) + '|'
    for j in range(startCol,endCol):
      fn = str('{:.2f}'.format(m[i][j]))
      if m[i][j] == 0:
        fnc = fn
      else:
        if m[i][j] > 0:
          fnc = red(fn)
        else:
          fnc = blue(fn)
      s += ' '*(cellW-len(fn)-1) + fnc + '|'
    print(s)
    print(' '*indexW + '-'*cellW*(endCol-startCol))


def calcQUBOMatrix(examples, n, states, alpha='1/(ri*qi)'):
  #get and calculate values
  parentSets, w, deltaMax, deltaTrans, deltaConsist = getValues(examples,n,states,alpha=alpha)
  #calculate d
  d = [ ('d',j,i) for j in range(n) for i in range(n) if j != i ]
  #calculate y (m=2)
  y = [ ('y',i,l+1) for i in range(n) for l in range(2)]
  #calculate r
  r = [ ('r',j,i) for j in range(n) for i in range(n) if j < i ]
  #calculate index array for rows and columns of the QUBO matrix
  indexQUBO = d + y + r
  iqLen = len(indexQUBO)
  #init QUBO matrix Q
  Q = [ [ 0. for j in range(iqLen) ] for i in range(iqLen) ]
  #calculate map for indexQUBO
  posOfIndex = calcPosOfIndex(indexQUBO)
  #add Hscore component to Q
  addHscore(Q, posOfIndex, n, parentSets, w)
  #add Hmax component to Q
  addHmax(Q,posOfIndex,n,deltaMax)
  #add Htrans component to Q
  addHtrans(Q, posOfIndex, n, deltaTrans)
  #add Hconsist component to Q
  addHconsist(Q, posOfIndex, n, deltaConsist)
  return Q,indexQUBO,posOfIndex

def addHscore(Q, posOfIndex, n, parentSets, w):
  for i in range(n):
    for parentSet in parentSets[i]:
      if parentSet != ():
        if len(parentSet) == 1:
          #elements of the diagonal
          j = parentSet[0]
          index = ('d',j,i)
          col = row = posOfIndex[index]
          Q[row][col] += w[i][parentSet]
        else:
          #elements outside the diagonal
          x = parentSet[0]; y = parentSet[1]
          indexR = ('d',x,i)
          indexC = ('d',y,i)
          row = posOfIndex[indexR]
          col = posOfIndex[indexC]
          Q[row][col] += w[i][parentSet]


def addHmax(Q, posOfIndex, n, deltaMax):
  for i in range(n):
    #Hmaxi(di,yi) = deltaMax[i] * (m - di - yi)**2
    toSquare = []
    #add m=2
    m = 2
    #add all dji
    for j in range(n):
      if j != i:
        toSquare.append(('d',j,i,-1))
    #add all yil for m=2
    toSquare.append(('y',i,1,-1))
    toSquare.append(('y',i,2,-2))
    #elements of the diagonal:
    #   square of elements (m excluded since it is a constant)
    #   double products with m
    for index in toSquare:
      col = row = posOfIndex[index[:3]]
      #add penalty multiplied by the square of the coefficient
      Q[row][col] += deltaMax[i] * (index[3]**2)
      #add penalty multiplied by m and the coefficient of the index
      Q[row][col] += deltaMax[i] * (2*m*index[3])
    #outside the diagonal: all pairs of indices
    for j in range(len(toSquare)):
      indexR = toSquare[j]
      row = posOfIndex[indexR[:3]]
      for k in range(j+1,len(toSquare)):
        indexC = toSquare[k]
        col = posOfIndex[indexC[:3]]
        #add penalty multiplied by the double product of the coefficients
        Q[row][col] += deltaMax[i] * (2*indexR[3]*indexC[3])

def addHtrans(Q, posOfIndex, n, deltaTrans):
  for i in range(n):
    for j in range(i+1,n):
      for k in range(j+1,n):
        #Htransijk(rij,rik,rjk) = deltaTrans * (rik + rij*rjk - rij*rik - rjk*rik)
        rij = ('r',i,j)
        rik = ('r',i,k)
        rjk = ('r',j,k)
        #coeff for rik
        col = row = posOfIndex[rik]
        Q[row][col] += deltaTrans
        #coeff for rij*rjk
        row = posOfIndex[rij]
        col = posOfIndex[rjk]
        Q[row][col] += deltaTrans
        #coeff for rij*rik
        row = posOfIndex[rij]
        col = posOfIndex[rik]
        Q[row][col] += -deltaTrans
        #coeff for rjk*rik (rik comes before -> row)
        row = posOfIndex[rik]
        col = posOfIndex[rjk]
        Q[row][col] += -deltaTrans

def addHconsist(Q, posOfIndex, n, deltaConsist):
  for i in range(n):
    for j in range(i+1,n):
      #Hconsistij(dij,dji,rij) = deltaConsist*(dji*rij + dij - dij*rij)
      dij = ('d',i,j)
      dji = ('d',j,i)
      rij = ('r',i,j)
      #coeff for dji*rij
      row = posOfIndex[dji]
      col = posOfIndex[rij]
      Q[row][col] += deltaConsist
      #coeff for dij
      col = row = posOfIndex[dij]
      Q[row][col] += deltaConsist
      #coeff for dij*rij
      row = posOfIndex[dij]
      col = posOfIndex[rij]
      Q[row][col] += -deltaConsist

def calcPosOfIndex(indexQUBO):
  posOfIndex = {}
  for i in range(len(indexQUBO)):
    index = indexQUBO[i]
    posOfIndex[index] = i
  return posOfIndex
