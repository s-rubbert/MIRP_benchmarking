import dimod
import pickle
import os
# from dwave.cloud import Client
# The token data is individual (and therefore non-public). 
# If you have an import error here, you need to create your own 
# dwave_token.py file and define the "value" variable as your 
# dwave token.
import dwave_token
from dwave.system import LeapHybridCQMSampler

folders = ["LP_files_MILP_vs_MIQP_Benchmark/MIQP", "MILP_vs_MIQP_Benchmark/MILP"][1:]
n_folders = len(folders)

for folder_counter, folder in enumerate(folders):
    files = [file for file in os.listdir(folder) if file[-3:] == ".lp"][:1]
    n_files = len(files)
    time_limit = 5
    sampler = LeapHybridCQMSampler()

    for file_counter, file in enumerate(files):
        print(f'loading file {file_counter+1} of {n_files} in folder {folder_counter+1} of {n_folders}:')
        model = dimod.lp.load(folder + "/" + file)

        print(f'-> calculating')
        sampler = LeapHybridCQMSampler()
        sample_set = sampler.sample_cqm(model, time_limit=time_limit)
        # sample_set = sample_set.sampleset

        sample_set = sample_set.to_serializable()

        print(f'-> storing results')
        with open(
            folder + "/" + f"{file.split('.')[0]}_solution_{time_limit}_s",
            'wb') as f:
            pickle.dump(sample_set, f)

print('calculations done')