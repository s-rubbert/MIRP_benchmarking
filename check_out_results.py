import dimod
import numpy as np
import pickle

file = 'LR1_1_DR1_3_VC1_V7a_t45.mps'

with open(f"Results/{file.split('.')[0]}", 'rb') as f:
    sample_set = pickle.load(f)
print(f"Results/{file.split('.')[0]}")

sample_set = dimod.SampleSet.from_serializable(sample_set)
print(f"Number samples: {len(sample_set)}")
#print(sample_set.aggregate())

sample_set = sample_set.filter(lambda d: d.is_feasible)
print(f'Number feasible samples: {len(sample_set)}')
if len(sample_set) > 0:
    print(f'minimal energy: {sample_set.first.energy}')
    print(f'Double check feasibility successful: {sample_set.first.is_feasible}')
