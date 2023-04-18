import os
import pickle
import numpy as np
from dwave.system import DWaveCliqueSampler
from ast import literal_eval
from dimod import BinaryQuadraticModel

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


folder = "random_qubo_benchmark"
files = [file for file in os.listdir(folder) if file[-4:] == ".dat"]
annealing_time = 1000
num_reads = 100

for counter, file in enumerate(files):
    q_dict = read_data_file(folder, file)
    q_mat = q_dict['Q']

    bqm = {
        (str(i), str(j)): q_mat[i, j]
        for i in range(len(q_mat)) 
        for j in range(len(q_mat))
        }

    model = BinaryQuadraticModel(bqm, 'BINARY')

    sampler = DWaveCliqueSampler()
    sample_set = sampler.sample(model, num_reads=num_reads, annealing_time=annealing_time)

    print(sample_set.lowest().first.energy)

    sample_set = sample_set.to_serializable()

    with open(f"{folder}/{file.split('.')[0]}_{annealing_time}" , 'wb') as f:
        pickle.dump(sample_set, f)

    print(f'Calculations done: {counter+1} of {len(files)}')
