import sys
import random
from generatorUtils import printResults

def main():
  if len(sys.argv) < 2:
    print('Number of examples needed')
    exit()
  examples = int(sys.argv[1])
  size = ''
  if examples/10**4 == 1:
    size = '10K'
  elif examples/10**5 == 1:
    size = '100K'
  elif examples/10**6 == 1:
    size = '1M'

  L = 0; N = 1; H = 2;
  F = 0; T = 1; NIL = 2;
  CN = 0; CH = 1;

  countV = {
    'hypovolemia': [0,0,0],
    'anaphylaxis': [0,0,0],
    'artCo2': [0,0,0],
    'sao2': [0,0,0],
    'insuffAnesth': [0,0,0],
    'errLowOutput': [0,0,0],
    'lvedVolume': [0,0,0],
    'strokeVolume': [0,0,0],
    'tpr': [0,0,0],
    'co': [0,0,0],
    'bp': [0,0,0],
    'catechol': [0,0,0],
    'hr': [0,0,0],
    'hrbp': [0,0,0],
    'hrekg': [0,0,0]
  }

  with open('datasets/Alarm{}.txt'.format(size), 'w') as file:
    #num vars, states of var 1,..., states of var 15
    file.write(str(15) + ' 3 3 3 3 3 3 3 3 3 3 3 3 3 3 3' + '\n')

    for i in range(examples):
      r = random.uniform(0,1)
      hypovolemia = T if r <= 0.20 else F
      countV['hypovolemia'][hypovolemia] += 1

      r = random.uniform(0,1)
      anaphylaxis = T if r <= 0.01 else F
      countV['anaphylaxis'][anaphylaxis] += 1

      r = random.uniform(0,1)
      artCo2 = L if r <= 0.07 else N if r <= 0.75 else H
      countV['artCo2'][artCo2] += 1

      r = random.uniform(0,1)
      sao2 = L if r <= 0.28 else N if r <= 0.93 else H
      countV['sao2'][sao2] += 1

      r = random.uniform(0,1)
      insuffAnesth = T if r <= 0.20 else F
      countV['insuffAnesth'][insuffAnesth] += 1

      r = random.uniform(0,1)
      errLowOutput = T if r <= 0.05 else F
      countV['errLowOutput'][errLowOutput] += 1

      r = random.uniform(0,1)
      if hypovolemia == T:
        lvedVolumeProb = [0.98, 0.99]
      elif hypovolemia == F:
        lvedVolumeProb = [0.05, 0.91]
      lvedVolume = L if r <= lvedVolumeProb[0] else N if r <= lvedVolumeProb[1] else H
      countV['lvedVolume'][lvedVolume] += 1

      r = random.uniform(0,1)
      if hypovolemia == T:
        strokeVolumeProb = [0.95, 0.99]
      elif hypovolemia == F:
        strokeVolumeProb = [0.07, 0.95]
      strokeVolume = L if r <= strokeVolumeProb[0] else N if r <= strokeVolumeProb[1] else H
      countV['strokeVolume'][strokeVolume] += 1

      r = random.uniform(0,1)
      if anaphylaxis == T:
        tprProb = [0.98, 0.99]
      elif anaphylaxis == F:
        tprProb = [0.30, 0.70]
      tpr = L if r <= tprProb[0] else N if r <= tprProb[1] else H
      countV['tpr'][tpr] += 1

      r = random.uniform(0,1)
      if strokeVolume == L:
        coProb = [0.87, 0.99]
      elif strokeVolume == N:
        coProb = [0.07, 0.49]
      elif strokeVolume == H:
        coProb = [0.02, 0.19]
      co = L if r <= coProb[0] else N if r <= coProb[1] else H
      countV['co'][co] += 1

      r = random.uniform(0,1)
      #tpr (cols)        L             N             H           #co
      probMat = [ [ [0.98, 0.99], [0.98, 0.99], [0.30, 0.90] ],  #L
                  [ [0.98, 0.99], [0.10, 0.95], [0.05, 0.45] ],  #N
                  [ [0.90, 0.99], [0.05, 0.25], [0.01, 0.10] ] ] #H
      bpProb = probMat[co][tpr]
      bp = L if r <= bpProb[0] else N if r <= bpProb[1] else H
      countV['bp'][bp] += 1

      r = random.uniform(0,1)
      #sao2            L     N     H        #artCo2 #tpr #insuffAnesth
      probMat =[ [ [[ 0.05, 0.10, 0.95 ],   #L       L    F
                    [ 0.05, 0.10, 0.95 ],   #N       L    F
                    [ 0.01, 0.10, 0.30 ]],  #H       L    F
                   [[ 0.05, 0.95, 0.99 ],   #L       N    F
                    [ 0.05, 0.95, 0.99 ],   #N       N    F
                    [ 0.01, 0.30, 0.99 ]],  #H       N    F
                   [[ 0.05, 0.95, 0.95 ],   #L       H    F
                    [ 0.05, 0.95, 0.99 ],   #N       H    F
                    [ 0.01, 0.30, 0.30 ]]   #H       H    F
                 ],
                 [ [[ 0.01, 0.01, 0.01 ],   #L       L    T
                    [ 0.01, 0.01, 0.01 ],   #N       L    T
                    [ 0.01, 0.01, 0.01 ]],  #H       L    T
                   [[ 0.01, 0.01, 0.05 ],   #L       N    T
                    [ 0.01, 0.01, 0.05 ],   #N       N    T
                    [ 0.01, 0.01, 0.01 ]],  #H       N    T
                   [[ 0.01, 0.05, 0.05 ],   #L       H    T
                    [ 0.01, 0.05, 0.05 ],   #N       H    T
                    [ 0.01, 0.01, 0.01 ]]   #H       H    T
                 ],
               ]
      catecholProb = probMat[insuffAnesth][tpr][artCo2][sao2]
      catechol = CN if r <= catecholProb else CH
      countV['catechol'][catechol] += 1

      r = random.uniform(0,1)
      #catechol (cols)   CN            CH          #bp
      probMat = [ [ [0.20, 0.99], [0.02, 0.12] ],  #L
                  [ [0.06, 1.00], [0.01, 0.18] ],  #N
                  [ [0.03, 0.97], [0.00, 0.04] ] ] #H
      hrProb = probMat[bp][catechol]
      hr = L if r <= hrProb[0] else N if r <= hrProb[1] else H
      countV['hr'][hr] += 1

      r = random.uniform(0,1)
      #errLowOutput      F             T           #hr
      probMat = [ [ [0.98, 0.99], [0.98, 0.99] ],  #L
                  [ [0.01, 0.99], [0.40, 0.99] ],  #N
                  [ [0.01, 0.02], [0.30, 0.70] ] ] #H
      hrbpProb = probMat[hr][errLowOutput]
      hrbp = L if r <= hrbpProb[0] else N if r <= hrbpProb[1] else H
      countV['hrbp'][hrbp] += 1

      r = random.uniform(0,1)
      if hr == L:
        hrekgProb = [0.92, 0.96]
      elif hr == N:
        hrekgProb = [0.04, 0.96]
      elif hr == H:
        hrekgProb = [0.04, 0.08]
      hrekg = L if r <= hrekgProb[0] else N if r <= hrekgProb[1] else H
      countV['hrekg'][hrekg] += 1

      file.write('{} {} {} {} {} {} {} {} {} {} {} {} {} {} {}\n'.format(hypovolemia, anaphylaxis, artCo2, sao2, insuffAnesth, errLowOutput, lvedVolume, strokeVolume, tpr, co, bp, catechol, hr, hrbp, hrekg))

  #information about the generated data
  printResults(countV,examples)

if __name__ == '__main__':
  main()
