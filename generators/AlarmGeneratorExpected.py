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

  count = 0
  prob = 0
  minZero = 1
  sumZero = 0
  notZero = 0
  countZero = 0

  with open('datasets/AlarmExp{}.txt'.format(size), 'w') as file:
    #num vars, states of var 1,..., states of var 15
    file.write(str(15) + ' 3 3 3 3 3 3 3 3 3 3 3 3 3 3 3' + '\n')

    for hypovolemia in range(2):
      probMat = [0.80, 0.20, 0.00]
      hypovolemiaProb = probMat[hypovolemia]

      for anaphylaxis in range(2):
        probMat = [0.99, 0.01, 0.00]
        anaphylaxisProb = probMat[anaphylaxis]

        for artCo2 in range(3):
          probMat = [0.07, 0.68, 0.25]
          artCo2Prob = probMat[artCo2]

          for sao2 in range(3):
            probMat = [0.28, 0.64, 0.08]
            sao2Prob = probMat[sao2]

            for insuffAnesth in range(2):
              probMat = [0.80, 0.20, 0.00]
              insuffAnesthProb = probMat[insuffAnesth]

              for errLowOutput in range(2):
                probMat = [0.95, 0.05, 0.00]
                errLowOutputProb = probMat[errLowOutput]

                for lvedVolume in range(3):
                  #lvedVolume  L     N     H     #hypovolemia
                  probMat = [[0.05, 0.86, 0.09], #F
                             [0.98, 0.01, 0.01]] #T
                  lvedVolumeProb = probMat[hypovolemia][lvedVolume]
                  # print('lvedVolumeProb[hyp={}][lved={}]: {}'.format(hypovolemia,lvedVolume,probMat[hypovolemia][lvedVolume]))

                  for strokeVolume in range(3):
                    #strokeVolume  L     N     H   #hypovolemia
                    probMat = [[0.07, 0.88, 0.05], #F
                               [0.95, 0.04, 0.01]] #T
                    strokeVolumeProb = probMat[hypovolemia][strokeVolume]

                    for tpr in range(3):
                      #tpr         L     N     H     #anaphylaxis
                      probMat = [[0.30, 0.40, 0.30], #F
                                 [0.98, 0.01, 0.01]] #T
                      tprProb = probMat[anaphylaxis][tpr]

                      for co in range(3):
                        #co          L     N     H     #strokeVolume
                        probMat = [[0.87, 0.12, 0.01], #L
                                   [0.07, 0.42, 0.51], #N
                                   [0.02, 0.16, 0.82]] #H
                        coProb = probMat[strokeVolume][co]

                        for bp in range(3):
                          #tpr (cols)            L                   N                   H             #co
                          probMat = [ [ [0.98, 0.01, 0.01], [0.98, 0.01, 0.01], [0.30, 0.60, 0.10] ],  #L
                                      [ [0.98, 0.01, 0.01], [0.10, 0.85, 0.05], [0.05, 0.40, 0.55] ],  #N
                                      [ [0.90, 0.09, 0.01], [0.05, 0.20, 0.75], [0.01, 0.09, 0.90] ] ] #H
                          bpProb = probMat[co][tpr][bp]

                          for catechol in range(2):
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
                            tmpProb = probMat[insuffAnesth][tpr][artCo2][sao2]
                            catecholProb = tmpProb if catechol == CN else 1-tmpProb

                            for hr in range(3):
                              #catechol (cols)      CN                  CH             #bp
                              probMat = [ [ [0.20, 0.79, 0.01], [0.02, 0.10, 0.88] ],  #L
                                          [ [0.06, 0.94, 0.00], [0.01, 0.17, 0.82] ],  #N
                                          [ [0.03, 0.94, 0.03], [0.00, 0.04, 0.96] ] ] #H
                              hrProb = probMat[bp][catechol][hr]

                              for hrbp in range(3):
                                #errLowOutput          F                   T             #hr
                                probMat = [ [ [0.98, 0.01, 0.01], [0.98, 0.01, 0.01] ],  #L
                                            [ [0.01, 0.98, 0.01], [0.40, 0.59, 0.01] ],  #N
                                            [ [0.01, 0.01, 0.98], [0.30, 0.40, 0.30] ] ] #H
                                hrbpProb = probMat[hr][errLowOutput][hrbp]

                                for hrekg in range(3):
                                  #hrekg       L     N     H     #hr
                                  probMat = [[0.92, 0.04, 0.04], #L
                                             [0.04, 0.92, 0.04], #N
                                             [0.04, 0.04, 0.92]] #H
                                  hrekgProb = probMat[hr][hrekg]

                                  p = hypovolemiaProb * anaphylaxisProb * artCo2Prob * sao2Prob * insuffAnesthProb * errLowOutputProb * lvedVolumeProb * strokeVolumeProb * tprProb * coProb * bpProb * catecholProb * hrProb * hrbpProb * hrekgProb
                                  gen = examples * p
                                  prob += p
                                  gen = round(gen)
                                  count = count+gen
                                  if gen != 0:
                                    notZero += 1
                                  else:
                                    countZero += 1
                                    sumZero += p
                                    if p != 0:
                                      minZero = min(minZero, p)

                                  countV['hypovolemia'][hypovolemia] += gen
                                  countV['anaphylaxis'][anaphylaxis] += gen
                                  countV['artCo2'][artCo2] += gen
                                  countV['sao2'][sao2] += gen
                                  countV['insuffAnesth'][insuffAnesth] += gen
                                  countV['errLowOutput'][errLowOutput] += gen
                                  countV['lvedVolume'][lvedVolume] += gen
                                  countV['strokeVolume'][strokeVolume] += gen
                                  countV['tpr'][tpr] += gen
                                  countV['co'][co] += gen
                                  countV['bp'][bp] += gen
                                  countV['catechol'][catechol] += gen
                                  countV['hr'][hr] += gen
                                  countV['hrbp'][hrbp] += gen
                                  countV['hrekg'][hrekg] += gen

                                  file.write('{} {} {} {} {} {} {} {} {} {} {} {} {} {} {}\n'.format(hypovolemia, anaphylaxis, artCo2, sao2, insuffAnesth, errLowOutput, lvedVolume, strokeVolume, tpr, co, bp, catechol, hr, hrbp, hrekg)*gen)

  avgZero = sumZero/countZero if countZero != 0 else 0
  minZero = minZero if minZero != 1 else 0
  #information about the generated data
  printResults(countV, count, minZero, avgZero, prob)

if __name__ == '__main__':
  main()
