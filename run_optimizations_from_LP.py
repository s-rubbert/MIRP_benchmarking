import dimod
import pickle
# from dwave.cloud import Client
# The token data is individual (and therefore non-public). 
# If you have an import error here, you need to create your own 
# dwave_token.py file and define the "value" variable as your 
# dwave token.
# import dwave_token
from dwave.system import LeapHybridCQMSampler

# client = Client(token=dwave_token.value)

file = 'lp_benchmark/t_20_v_6_p_4.lp'
time_limit = 120
#file = 'test.lp'

model = dimod.lp.load(file)
print('loading done')

# # The following variables are giving trouble if kept as variables. Luckily they are indeed fixed anyway (see LP file)
# auxx_variables = [name for name in model.variables if '(auxx)' in name]
# for name in auxx_variables:
#     model.fix_variable(name, 1)
# model.fix_variable('z_0_0', 0)

print(f'constraints: {len(model.constraints)}')
trivial_constraints = [label for label, constraint in model.constraints.items() if len(constraint.lhs.variables) == 0]
for label in trivial_constraints:
    model.remove_constraint(label)
print('removed trivial constraints')
print(f'remaining constraints: {len(model.constraints)}')

# sampler = client.get_solver(name='hybrid_constrained_quadratic_model_version1p')
sampler = LeapHybridCQMSampler()
sample_set = sampler.sample_cqm(model, time_limit=time_limit)
# sample_set = sample_set.sampleset

sample_set = sample_set.to_serializable()
print('calculation done')

with open(f"{file.split('.')[0]}_solution_{time_limit}_s" , 'wb') as f:
    pickle.dump(sample_set, f)

print('all done')
# client.close()