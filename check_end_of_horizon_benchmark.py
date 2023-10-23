import os
import dimod
import numpy as np
import pickle

folders = ["Oli_paper_LP_files",]
results = {}
for folder in folders:
    files = [file for file in os.listdir(folder) if "solution" in file] 
    for file in files:
        with open(f"{folder}/{file}", 'rb') as f:
            sample_set = pickle.load(f)

        sample_set = dimod.SampleSet.from_serializable(sample_set)
        sample_set = sample_set.filter(lambda d: d.is_feasible)
        if len(sample_set) > 0:
            objective = np.round(sample_set.lowest().first.energy, decimals = 3)
        else:
            objective = -np.inf

        results[file] = objective

calculation_times = {key.split('_')[-2] for key in results.keys()}  
results = {
    calculation_time: {
        '_'.join(key.split('_')[:-4]): value for key, value in results.items() 
        if key.split('_')[-2] == calculation_time
        }
    for calculation_time in calculation_times
    }

with open('LP_files_MILP_vs_MIQP_Benchmark/results', 'wb') as fp:
    pickle.dump(results, fp)
del results


with open('LP_files_MILP_vs_MIQP_Benchmark/results', 'rb') as fp:
    results = pickle.load(fp)

print(results)