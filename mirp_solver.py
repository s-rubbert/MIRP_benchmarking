import numpy as np
import scipy.optimize as opt
import scipy.sparse as sparse


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
    
    variables = {}
    # keep int_marker, i.e., the information whether a variable is discrete in here. Not necessary 
    # immidiately but allows easy expansion of the code. 
    int_marker = False
    
    for line in columns_section:
        if not "'MARKER'" in line:
            variables[line.lstrip().split(' ')[0]] = (int_marker, 0, [None, 1][1*int_marker])
        else:
            int_marker = "'INTORG'" in line
            
    for line in bounds_section:
        try:
            bound_type, _, variable_name, value = line.split()
            variables[variable_name] = read_bounds(bound_type, value, variables[variable_name])
        except:
            print(line)
            break
        
    variable_indices = {name: index for index, (name, _) in enumerate(variables.items())}
    bounds, discrete = [None for i in range(len(variables))], [None for i in range(len(variables))]
    for name, entry in variables.items():
        bounds[variable_indices[name]] = entry[1:]
        discrete[variable_indices[name]] = entry[0]
    
    return variable_indices, np.array(bounds), np.array(discrete)


def read_equalities(rows_section, columns_section, rhs_section, variable_indices):
    
    def vectorize(rows_lhs):
        row_indices = {name: index for index, name in enumerate(rows_lhs.keys())}
        entries, index_1, index_2 = [], [], []
        for row, terms in rows_lhs.items():
            for entry, variable in terms:
                entries.append(entry)
                index_1.append(row_indices[row])
                index_2.append(variable_indices[variable])
        
        matrix_lhs = sparse.csr_array(
            (entries, (index_1, index_2)),
            shape=(len(row_indices), len(variable_indices))
        )
        
        vector_rhs = np.zeros(len(rows_lhs))
        for name, index in row_indices.items():
            try:
                vector_rhs[index] = rows_rhs[name]
            except:
                None
        
        return matrix_lhs, vector_rhs, row_indices
        
    
    rows_lhs = {
        line.split()[1]: []
        for line in rows_section
    }
    
    for term in columns_section:
        if not "'MARKER'" in term:
            column, row, entry = term.split()
            rows_lhs[row].append([float(entry), column])
    
    rows_rel = {
        line.split()[1]: line.split()[0]
        for line in rows_section
    }
    
    rows_rhs = {
        line.split()[1]: float(line.split()[2])
        for line in rhs_section
    }
    
    # construct upper bound and equality constraint matrices
    ubs = {key: entry for key, entry in rows_lhs.items() if rows_rel[key] == 'L'}
    lbs = {key: entry for key, entry in rows_lhs.items() if rows_rel[key] == 'G'}
    eqs = {key: entry for key, entry in rows_lhs.items() if rows_rel[key] == 'E'}
    obj = {key: entry for key, entry in rows_lhs.items() if rows_rel[key] == 'N'}
    assert len(obj) == 1, 'There has to be exactly one objective!'
    
    A_ub, b_ub, row_indices_ub = vectorize(ubs)#sparse.vstack([build_mat(ubs), -build_mat(lbs)])
    A_lb, b_lb, row_indices_lb = vectorize(lbs)
    # solver convention: only use upper bounds -> translate lower bounds
    row_indices_ub.update({name: index+A_ub.shape[0] for name, index in row_indices_lb.items()})
    A_ub, b_ub = sparse.vstack([A_ub, -A_lb]), np.concatenate([b_ub, -b_lb])
    # keep going with equations and the objective
    A_eq, b_eq, row_indices_eq = vectorize(eqs)
    c, offset, _ = vectorize(obj)
    # the objective is usually not sparse
    c = c.todense()[0]
    offset = offset[0]
    
    return c, A_ub, b_ub, A_eq, b_eq, offset, row_indices_ub, row_indices_eq


def time_mask(start, end, max_t, variable_indices):
    def is_in_timeframe(name):
        # grouping of variables:
        if 'x_(' == name[:3]:
            res = np.any([
                start <= int(t[:-1]) < end
                for t in np.array(name.split(','))[[1, 3]]
            ])
        elif 'supplyAtNode_(' == name[:14]:
            res = start <= int(name.split(',')[1][:-1]) < end
        elif 'alphaSlack_(' == name[:12]:
            res = start <= int(name.split(',')[1][:-1]) < end
        elif 'betaSlack_(' == name[:11]:
            res = start <= int(name.split(',')[1][:-1]) < end
        elif 'z_(' == name[:3]:
            res = start <= int(name.split(',')[1][:-1]) < end
        elif 'f_(' == name[:3]:
            res = start <= int(name.split(',')[1][:-1]) < end
        elif 'supplyOnVessel_' == name[:15]:
            res = start <= int(name.split(',')[1]) < end
        elif name[-7:] == 'Slack_0' or name[-6:] == 'Node_0' or name[-3:] == '0,0':
            res = start == 0
        elif 'ending' == name[:6]:
            res = end >= max_t
        elif '_relaxation_slack' in name:
            res = True
        else:
            raise ValueError(f'Masking failed! {name} not recognized.')
        return res
        
    mask = np.zeros(len(variable_indices), dtype=bool)
    for name, index in variable_indices.items():
        mask[index] = is_in_timeframe(name)
    return mask


def ship_mask(ship, variable_indices):
    def belongs_to_ship(name):
        # grouping of variables:
        if 'x_(' == name[:3]:
            res = int(name.split(',')[4]) == ship
        elif 'z_(' == name[:3]:
            res = int(name.split(',')[2]) == ship  
        elif 'f_(' == name[:3]:
            res = int(name.split(',')[2]) == ship
        elif 'supplyOnVessel_' == name[:15]:
            res = int(name.split(',')[0].split('_')[1]) == ship
        else:
            res = True
        return res
        
    mask = np.zeros(len(variable_indices), dtype=bool)
    for name, index in variable_indices.items():
        mask[index] = belongs_to_ship(name)
    return mask


def subproblem(cur_sol, mask, c, A_ub, b_ub, A_eq, b_eq, bounds, discrete, discreteness_mask):
    
    indices_in = np.arange(len(mask))[mask] 
    indices_out = np.arange(len(mask))[np.logical_not(mask)]
    
    new_A_ub = A_ub[:, indices_in]
    ub_mask = new_A_ub.getnnz(1) > 0
    off_A_ub = A_ub[:, indices_out]
    
    new_A_eq = A_eq[:, indices_in]
    eq_mask = new_A_eq.getnnz(1) > 0
    off_A_eq = A_eq[:, indices_out]
    
    off_sol = cur_sol[indices_out]
    new_b_ub = b_ub - (off_A_ub @ off_sol)
    new_b_eq = b_eq - off_A_eq @ off_sol
    
    new_c = c[indices_in]
    
    new_bounds = bounds[indices_in]
    new_discrete = discrete[indices_in]
    new_discreteness_mask = discreteness_mask[indices_in]
    
    return (
        new_c, new_A_ub[ub_mask, :], 
        new_b_ub[ub_mask], 
        new_A_eq[eq_mask, :],
        new_b_eq[eq_mask], 
        new_bounds, 
        new_discrete,
        new_discreteness_mask
    )