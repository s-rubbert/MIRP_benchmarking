import os
import dimod
import numpy as np
import pickle

folder = "tsp_qbo_benchmark"
files = [file for file in os.listdir(folder) if not file[-4:] == ".dat" and file != "results"] 

results = []

for file in files:
    with open(f"{folder}/{file}", 'rb') as f:
        sample_set = pickle.load(f)
    sample_set = dimod.SampleSet.from_serializable(sample_set)
    
    
    dimension = int(file.split('_')[-2][:-1])**2
    item = file.split('_')[-2][-1]
    time = int(file.split('_')[-1])
    objective = np.round(sample_set.filter(lambda d: d.is_feasible).lowest().first.energy, decimals = 3)

    results.append([dimension, item=="a", time, objective])
results = np.array(results)
results = results[np.argsort(results[:, 0] - results[:, 1] + results[:, 2]/10000)]

np.savetxt(f'{folder}/results', results)

slaaab = np.loadtxt(f'{folder}/results')
print(slaaab)