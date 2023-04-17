import os
import pickle
import numpy as np
import dimod
from dwave.system import LeapHybridCQMSampler
from ast import literal_eval

def read_data_file(folder_name, file_name):
    '''Reads a dat file for Cplex, where there are semicolons at the end of every line.
        Inputs: 
            folder_name
            file_name
        Outputs:
            parameter_dict: Dictionary with parameter names as keys and arrays as values'''
    with open(folder_name + '/' + file_name,'r') as f:
        data = f.read().split(";\n")
    parameter_dict = {}
    for line in data:
        if line[:2] == '//' or line[:1] == '#':
            if 'comment' in parameter_dict.keys():
                parameter_dict['comment'] += '\n' + line.replace('//','').replace('#','').replace('\n',' ')
            else:
                parameter_dict['comment'] = line.replace('//','').replace('#','').replace('\n',' ')
        elif line != '':
            parameter_name, parameter_string = line.split(" = ")
            parameter = literal_eval(' '.join(parameter_string.split()).replace('[ ','[').replace(' ]',']').replace(' ',', '))
            if np.shape(parameter) != ():
                parameter = np.array(parameter)
        parameter_dict[parameter_name] = parameter
    return(parameter_dict)


folder = "tsp_qbo_benchmark"
files = [file for file in os.listdir(folder) if file[-4:] == ".dat"]
time_limit = 15
sampler = LeapHybridCQMSampler()

for counter, file in enumerate(files):
    q_dict = read_data_file(folder, file)
    q_mat = q_dict['Q']
    q_mat = np.reshape(
        q_mat, 
        (len(q_mat)**2, len(q_mat)**2)
        )
    n_nodes = q_dict['N']

    variables = np.array([
        [
            dimod.Binary(f'x_{time}_{node}') 
            for node in range(n_nodes)
        ] 
        for time in range(n_nodes)
    ])

    constraint_lhs = ([
        sum([
            variables[time, node] 
            for node in range(n_nodes)
            ])
        for time in range(n_nodes)
        ] + [
        sum([
            variables[time, node] 
            for time in range(n_nodes)
            ])
        for node in range(n_nodes)
        ])

    variables = np.reshape(variables, (-1,))
    objective = variables @ q_mat @ variables
    
    model = dimod.CQM()
    model.set_objective(objective)
    for constraint in constraint_lhs:
        model.add_constraint_from_model(constraint, '==', 1)

    sample_set = sampler.sample_cqm(model, time_limit=time_limit)
    
    print(sample_set.filter(lambda d: d.is_feasible).lowest().first.energy)
    
    sample_set = sample_set.to_serializable()
    
    with open(f"{folder}/{file.split('.')[0]}_{time_limit}" , 'wb') as f:
        pickle.dump(sample_set, f)

    print(f'File: {counter+1} of {len(files)}')
