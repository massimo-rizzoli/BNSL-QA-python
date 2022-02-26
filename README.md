# Bayesian Network Structure Learning with Quantum Annealing implementation

## Introduction
This work is a python implementation of [O'Gorman et al.](https://doi.org/10.1140/epjst/e2015-02349-9) **Bayesian Network Structure Learning** encoding into a **Quadratic Unconstrained Binary Optimisation** (**QUBO**) problem.
The encoded **QUBO** problem is solved using either a **Simulated Annealing** or **Quantum Annealing** approach using the libraries and **quantum annealers** provided by [D-Wave Systems](https://www.dwavesys.com/).

## Installation

First of all, clone the repository and enter the folder.

```
git clone https://github.com/massimo-rizzoli/BNSL-QA-python.git
cd BNSL-QA-python
```

### Python Environment

#### With Pyenv

Create a python 3.9.7 virtual environment named `bnslqa-env`

```
pyenv virtualenv 3.9.7 bnslqa-env
```

Set the `bnslqa-env` environment as the local environment for the `BNSL-QA-python` folder (the environment will be automatically activated when entering the folder)

```
pyenv local bnslqa-env
```

Update `pip`

```
python -m pip install -U pip
```

Install the requirements

```
pip install -r requirements.txt
```

#### With Python Venv

The project was developed with `python 3.9.7`, so it is recommended to use this version (you can check with `python --version`).

Create a python virtual environment named `bnslqa-env`

```
python -m venv bnslqa-env
```

Activate the `bnslqa-env` environment

```
source bnslqa-env/bin/activate
```

Update `pip`

```
python -m pip install -U pip
```

Install the requirements

```
pip install -r requirements.txt
```

**Note:** each time you will open a shell, you will have to manually activate the environment as shown above, before being able to use the project.

### D-Wave

If you do not have one already, create an account on [D-Wave Leap](https://cloud.dwavesys.com/leap/signup/), then proceed with the configuration by running the following command in the cloned repository folder:

```
dwave setup
```

You will be asked for several settings, but you can just leave the default. At a certain point it will prompt for an `Authentication Token`, which can be found on the [D-Wave Leap Dashboard](https://cloud.dwavesys.com/leap/).

For further information, you can visit D-Wave's page on [Installing Ocean Tools](https://docs.ocean.dwavesys.com/en/stable/overview/install.html#set-up-your-environment).
