
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
