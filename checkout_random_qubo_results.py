import os
import dimod
import numpy as np
import pickle

folder = "random_qubo_benchmark"
files = [file for file in os.listdir(folder) if not file[-4:] == ".dat" and file != "results"] 

results = []

for file in files:
    with open(f"{folder}/{file}", 'rb') as f:
        sample_set = pickle.load(f)
    sample_set = dimod.SampleSet.from_serializable(sample_set)
    
    dimension = int(file.split('_')[4][:-1])
    item = file.split('_')[4][-1]
    time = int(file.split('_')[-1])
    objective = np.round(sample_set.lowest().first.energy, decimals = 3)

    results.append([dimension, item=="a", time, objective])
results = np.array(results)
results = results[np.argsort(results[:, 0] - results[:, 1] + results[:, 2]/10000)]

    # print(f"Dimension: {dimension}")
    # print(f"Item: {item}")
    # print(f"Objective: {objective}")
    # print(f"Annealing time: {time} microseconds")
    # print('')


np.savetxt(f'{folder}/results', results)

slaaab = np.loadtxt(f'{folder}/results')
print(slaaab)