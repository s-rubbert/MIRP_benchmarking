print(f'overall variables: {len(model.variables)}')
vars = set(model.variables)

xs = set([var for var in vars if 'x_' in var])
xs5 = set([var for var in xs if len(var.split(',')) == 5])
xsaux = set([var for var in xs if 'aux' in var])
print(f'normal arcs: {len(xs5)}')
print(f'border node arcs: {len(xsaux)}')

vars = vars - xs5 - xsaux
supplies = set([var for var in vars if 'supply' in var or 'Supply' in var])
print(f'supply variables: {len(supplies)}')
vars = vars - supplies

slacks = set([var for var in vars if 'Slack' in var])
print(f'slack variables: {len(slacks)}')
vars = vars - slacks

zs = set([var for var in vars if 'z_' in var])
print(f'z variables: {len(zs)}')
vars = vars - zs

fs = set([var for var in vars if 'f_' in var])
print(f'loading/unloading variables: {len(fs)}')
vars = vars - fs

if len(vars) == 0:
    print('all variables accounted for')
else:
    print(f'{len(vars)} unaccounted variables')