import dimod
import numpy as np
import pickle
from dwave.system import LeapHybridCQMSampler

def open_mps(file):
    
    with open(file) as f:
        lines = f.readlines()
    
    lines = np.array(lines)
    row_start = np.argwhere(lines == 'ROWS\n')[0, 0]
    column_start = np.argwhere(lines == 'COLUMNS\n')[0, 0]
    rhs_start = np.argwhere(lines == 'RHS\n')[0, 0]
    bound_start = np.argwhere(lines == 'BOUNDS\n')[0, 0]
    
    return (
        lines[row_start+1:column_start], 
        lines[column_start+1:rhs_start], 
        lines[rhs_start+1:bound_start], 
        lines[bound_start+1:-1]
    )


def read_variables(columns_section, bounds_section):
    
    def read_bounds(bound_type, value, entry):
        if bound_type == 'UP':
            return (entry[0], entry[1], float(value))
        elif bound_type == 'FX':
            return (entry[0], float(value), float(value))
        elif bound_type == 'LO':
            return (entry[0], float(value), entry[2])
        else:
            print(f'Bound type {bound_type} is not supported.')
    
    def declare_dimod_variable(name, discrete, lower, upper):
        if not lower:
            lower = 0
        
        if lower == upper:
            return upper
        elif discrete:
            if upper == 1:
                return dimod.Binary(name)
            else:
                return dimod.Integer(name, lower_bound=lower, upper_bound=upper)
        else:
            return dimod.Real(name, lower_bound=lower, upper_bound=upper)
    
    variables = {}
    int_marker = False
    
    for line in columns_section:
        if not "'MARKER'" in line:
            variables[line.lstrip().split(' ')[0]] = (int_marker, None, None)
        else:
            int_marker = "'INTORG'" in line
            
    for line in bounds_section:
        try:
            bound_type, _, variable_name, value = line.split()
            variables[variable_name] = read_bounds(bound_type, value, variables[variable_name])
        except:
            print(line)
            break
        
    variables = {
        variable_name: declare_dimod_variable(variable_name, discrete, lower, upper)
        for variable_name, (discrete, lower, upper) in variables.items()
    }
            
    return variables


def construct_rows(rows_section, columns_section, rhs_section, bounds_section, variables):
    
    rows_lhs = {
        line.split()[1]: []
        for line in rows_section
    }
    
    rows_rel = {
        line.split()[1]: line.split()[0]
        for line in rows_section
    }
    
    rows_rhs = {
        line.split()[1]: float(line.split()[2])
        for line in rhs_section
    }
    
    for term in columns_section:
        if not "'MARKER'" in term:
            column, row, entry = term.split()
            rows_lhs[row] += [float(entry)*variables[column]]
    
    # bring the right hand side to the left. This avoids extra cases for the objective, which is allowed to have a right hand side as well.
    # For objectives, a right hand side is interpreted as an absolute offset. We keep the offset for comparability.
    for row in rows_rhs.keys():
        rows_lhs[row] += [-rows_rhs[row]]
        
    rows_lhs = {
        row_name: sum(summands)
        for row_name, summands in rows_lhs.items()
    }
    
    return rows_lhs, rows_rel

def build_model(rows_lhs, rows_rel):
    objective = [
        row_name
        for row_name, relation in rows_rel.items()
        if relation == 'N'
    ]

    assert len(objective) == 1, f'There are {len(objective)} objectives. Must be exactly one. Please fix!'

    objective = objective[0]
    
    model = dimod.CQM()
    model.set_objective(-rows_lhs[objective])
    for row, qm in rows_lhs.items():
        if not row == objective and type(qm) is not int:
            if rows_rel[row] == 'L':
                model.add_constraint_from_model(qm, '<=', 0, row)
            elif rows_rel[row] == 'E':
                model.add_constraint_from_model(qm, '==', 0, row)
            elif rows_rel[row] == 'G':
                model.add_constraint_from_model(qm, '>=', 0, row)
            else:
                print(f'unsupported constraint type {rows_rel[row]}!')
                
    return model

def mps_to_cqm(path):
    rows_section, columns_section, rhs_section, bounds_section = open_mps(path)
    variables = read_variables(columns_section, bounds_section)
    rows_lhs, rows_rel = construct_rows(rows_section, columns_section, rhs_section, bounds_section, variables)
    model = build_model(rows_lhs, rows_rel)
    return model

file = 'test_instance.mps'
model = mps_to_cqm('MIRPs/' + file)

sampler = LeapHybridCQMSampler()
# sample_set = sampler.sample_cqm(model, time_limit=5)

sample_set = sample_set.to_serializable()

with open(f"Results/{file.split('.')[0]}" , 'wb') as f:
    pickle.dump(sample_set, f)
