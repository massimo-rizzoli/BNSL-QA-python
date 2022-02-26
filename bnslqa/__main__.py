import argparse
from random import choices
import bnslqa.generators.generator as gen
import bnslqa.generators.mhp_legacy as mhp_legacy
from bnslqa.solvers import exact_solver, dwave_solver

def main():
  parser = argparse.ArgumentParser(description='Implementation of Bayesian Network Structure Learning using Quantum Annealing',
                                   prog='python -m bnslqa')
  subparsers = parser.add_subparsers(help='sub-command help')

  solver_parser = subparsers.add_parser('solve', help='estimate BN structure from data',
                                        description='',
                                        epilog='''Example: \'python -m bnslqa solve datasets/WasteExp.txt QA -r 10000 -a 99\'
                                        will use D-Wave\'s Quantum Annealer to solve the WasteExp problem, with 10000 reads
                                        each with an annealing time of 99 microseconds''')
  solver_parser.add_argument('dataset', type=str, help='dataset path')
  solver_parser.add_argument('strategy', type=str, choices=['ES','SA','QA'],
                             help='strategy to be used (Exhaustive Search, Simulated Annealing, Quantum Annealing)')
  solver_parser.add_argument('-r','--reads', type=int, metavar='NUM', default=10**4,
                             help='number of reads for annealing strategies, SA has no limits, QA can have at most 10000 [default: 10000]')
  solver_parser.add_argument('-a','--anneal', type=int, metavar='T', default=99,
                             help='annealing time in microseconds for each read (only for QA), up to 2000 [default: 99]')

  generator_parser = subparsers.add_parser('generate',
                                           help='generate problem dataset',
                                           description='Generate a dataset for a specific problem',
                                           epilog='''Example: \'python -m bnslqa generate problems/Waste.json --size 10000 --expected\'
                                           will generate an expected dataset of size 10000 for the problem Waste
                                           as datasets/WasteExp.txt''')
  generator_parser.add_argument('problem', type=str,
                                help='path to the json file defining the problem')
  generator_parser.add_argument('-s', '--size', default=10**4, type=int,
                                help='number of examples (BN variables settings) to generate [default: 10000]')
  generator_parser.add_argument('-e', '--expected', action='store_true',
                                help='generate a dataset with expected values (no variance)')
  generator_parser.add_argument('-n', '--name', default=None, type=str,
                                help='dataset name, will be saved in datasets/NAME.txt [default: based on parameters and problem definition]')
  generator_parser.add_argument('-l', '--legacy', action='store_true',
                                help='MHP only: generate the dataset the same way as used for the original experiments. Note: this already the case for the other problems')
  generator_parser.set_defaults(func=gen.main)
  generator_parser.set_defaults(parser=generator_parser)

  args = parser.parse_args()

  if 'func' not in args:
    if 'strategy' in args:
      if args.strategy == 'ES':
        args.func = exact_solver.main
      else:
        args.func = dwave_solver.main
    else:
      parser.print_usage()
      parser.exit(1)

  if 'legacy' in args:
    if args.legacy:
      if 'mhp' in args.problem.lower():
        args.func = mhp_legacy.main

  args.func(args)

if __name__ == '__main__':
  main()
