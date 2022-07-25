import dimod
import numpy as np
import pickle

file = 'test_instance.mps'

with open(f"Results/{file.split('.')[0]}.txt", 'rb') as f:
    sample_set = pickle.load(f)

sample_set = dimod.SampleSet.from_serializable(sample_set)
print(f"Number samples: {len(sample_set)}")
print(sample_set.aggregate())
