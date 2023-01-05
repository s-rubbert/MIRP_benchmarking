import dimod
import numpy as np
import pickle
from dwave.system import LeapHybridCQMSampler


file = 'LR1_1_DR1_3_VC1_V7a_t45.lp'
# file = 'test.lp'

model = dimod.lp.load('LP/' + file)
print('loading done')

# The following variables are giving trouble if kept as variables. Luckily they are indeed fixed anyway (see LP file)
auxx_variables = [name for name in model.variables if '(auxx)' in name]
for name in auxx_variables:
    model.fix_variable(name, 1)
model.fix_variable('z_0,0', 0)

trivial_constraints = [label for label, constraint in model.constraints.items() if len(constraint.lhs.variables) == 0]
for label in trivial_constraints:
    model.remove_constraint(label)
print('removed trivial constraints')
print(f'remaining constraints: {len(model.constraints)}')

sampler = LeapHybridCQMSampler()
sample_set = sampler.sample_cqm(model, time_limit=3600)

print('calculation done')

sample_set = sample_set.to_serializable()

with open(f"Results/{file.split('.')[0]}" , 'wb') as f:
    pickle.dump(sample_set, f)

print('all done')