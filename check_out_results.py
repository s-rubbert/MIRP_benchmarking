import dimod
import numpy as np
import pickle

file = 'lp_benchmark/t_20_v_6_p_4_solution_120_s'

with open(f"{file.split('.')[0]}", 'rb') as f:
    sample_set = pickle.load(f)
print(f"{file.split('.')[0]}")
print('')

sample_set = dimod.SampleSet.from_serializable(sample_set)
print(f"Number samples: {len(sample_set)}")
#print(sample_set.aggregate())

sample_set_red = sample_set.filter(lambda d: d.is_feasible)
print(f'Number feasible samples: {len(sample_set_red)}')
if len(sample_set_red) > 0:
    print(f'minimal energy: {sample_set_red.lowest().first.energy}')
    print(f'Double check feasibility successful: {sample_set_red.lowest().first.is_feasible}')
else:
    satisfaction_array = np.array([sample.is_satisfied for sample in sample_set.data()])
    n_broken_constraints = np.sum(np.logical_not(satisfaction_array), axis=1)
    print(f'minimal number of broken constraints {min(n_broken_constraints)}')
    
    constraint_labels = np.array(sample_set.info['constraint_labels'])
    if min(n_broken_constraints) < 20:
        index = np.argmin(n_broken_constraints)
        print('')
        print(f'The broken constraints are: {constraint_labels[satisfaction_array[index]]}')
        
print('')
print({key: sample_set.info[key] for key in ['qpu_access_time', 'charge_time', 'run_time', 'problem_id']})

