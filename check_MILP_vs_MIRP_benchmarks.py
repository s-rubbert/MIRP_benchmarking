import os
import dimod
import numpy as np
import pickle

folders = ["MILP_vs_MIQP_Benchmark/MILP", "MILP_vs_MIQP_Benchmark/MIQP"]
results = {}
for folder in folders:
    files = [file for file in os.listdir(folder) if "solution" in file] 
    for file in files:
        key = tuple(np.array(
            file.split('_')[1:7] + [file.split('_')[8]]
            ).astype(int))

        with open(f"{folder}/{file}", 'rb') as f:
            sample_set = pickle.load(f)

        sample_set = dimod.SampleSet.from_serializable(sample_set)
        sample_set = sample_set.filter(lambda d: d.is_feasible)
        if len(sample_set) > 0:
            objective = np.round(sample_set.lowest().first.energy, decimals = 3)
        else:
            objective = -np.inf

        if not key in results.keys():
            if file[:4] == 'MILP':
                results[key] = [objective, None]
            else:
                results[key] = [None, objective]
        else:
            if file[:4] == 'MILP':
                results[key][0] = objective 
            else:
                results[key][1] = objective

calculation_times = {key[-1] for key in results.keys()}   
results = {
    calculation_time: {
        key[:-1]: value for key, value in results.items() 
        if key[-1] == calculation_time
        }
    for calculation_time in calculation_times
    }

with open('MILP_vs_MIQP_Benchmark/results', 'wb') as fp:
    pickle.dump(results, fp)
del results


with open('MILP_vs_MIQP_Benchmark/results', 'rb') as fp:
    results = pickle.load(fp)

print(results)