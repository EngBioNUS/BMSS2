import sympy as sp
from sympy import symbols
from   sympy.matrices import Matrix, zeros
from   math           import ceil

import symengine as se
##from   symengine import Matrix, zeros

##init_printing()
from time import time

nt = 1000

def t(*funcs):
    global nt
    for func in funcs:
        start = time()
        for i in range(nt):
            func()
        print(time()-start)
        
###############################################################################
#Building OI
###############################################################################        
def build_OI(h, x, p, u, f, extend=[]):
    '''
    Returns Observability matrix, number of derivatives and the last Lie derivative.
    If using the extend argument, the list elements are [the previous matrix, the new nd, the previous nd]
    '''
    x_aug   = Matrix(list(x) + list(p)).T
    f_aug   = Matrix(list(f) + [0 for i in range(len(p))])
    start   = 0
    n_start = 0
    
    if len(extend) > 0:
        rows, cols  = extend[0].shape
        M           = zeros(rows+len(h)*extend[1], cols)
        nd          = int(rows/len(h)) -1 + extend[1]
        n_start     = int(rows/len(h)) -1
        M[0:rows,:] = extend[0]
        start       = rows-len(h)

    else:
        M, nd          = build_M(h, x, p)
        M[0:len(h), :] = Matrix([list(h.jacobian(Matrix([x]))) for x in x_aug]).T    
        blocks         = nd

    input_der  = build_input_der(u, nd)
    stop       = start+len(h)
    Li_1       = None if len(extend) == 0 else extend[2]
    
    for block in range(n_start, nd):
        Lieh   = M[start:stop,:]*f_aug
        extra  = zeros(len(h), 1)
        
        if block > 0 and len(u) > 0:
            #Modification for accounting for inputs
            for i in range(block):
                if i < input_der.shape[1] - 1:
                    lo_u   = input_der[:,i]
                    hi_u   = input_der[:,i+1]
                    lo_u   = lo_u.subs(0, symbols(['dummy'])[0])
                    extra += Li_1.jacobian(Matrix([lo_u])) *hi_u
                else:
                    break
        Li_1 = Lieh + extra
        
        start += len(h)
        stop  += len(h)
        
        M[start:stop,:] = Matrix([list(Li_1.jacobian(Matrix([x]))) for x in x_aug]).T 

    return M, nd, Li_1

def get_nd(h, x, p):
    r = len(x) + len(p)
##    return round((r-len(h))/len(h) + 0.5)
    return ceil( (r-len(h))/len(h) )

def build_M(h, x, p):
    nd   = get_nd(h, x, p)
    rows = len(h)*(nd+1)
    cols = len(x)+len(p)
    return zeros(rows, cols), nd

def build_input_der(u, nd):
    u_var = list(u.keys())
    u_nzd = list(u.values())
    
    input_der = []
    for i in range(len(u)): 
        if u_nzd[i] == 'inf':
            new_sym = [u_var[i]] + symbols([u_var[i].name+'_d'+str(ii+1) for ii in range(nd-1)])
        else:
            nu      = min(u_nzd[i], nd-1) 
            new_sym = [u_var[i]] + symbols([u_var[i].name+'_d'+str(ii+1) for ii in range(nu)]) + [0]*(nd-1-nu)
        input_der.append(new_sym)

    return Matrix(input_der)
    
###############################################################################
#Rank Calculation
###############################################################################
def all_zero_on_right(row):
    found_one = -1
    for i in range(len(row)):
        element = row[i]
        if element == 1 and found_one == -1:
            found_one = i
        elif element == 0:
            continue
        else:
            return False, None
    if found_one > -1:
        return True, found_one
    else:
        return False, None
    
def check_full_rank(Ms):
    return PMatrix(Ms).rank() == Ms.shape[1]
    
def update(Ms, x_aug_dict):
    start  = time()
    
    ###############################################################################
    #IMPORTANT: TEMPORARILY CONVERTING MATRIX FROM SYMENGINE TO SYMPY
    ###############################################################################
    Mr     = Ms.rref()[0]
##    Mr     = Matrix(PMatrix(Ms).rref()[0].tolist())
    print('Time for Row Reduction', time()-start)

    ###############################################################################
    #IMPORTANT: RETURNING TO WORKING IN SYMENGINE
    ############################################################################### 
    keys  = list(x_aug_dict.keys())
    found = []

    for i in range(Mr.shape[1]):
        name = keys[i]
        if x_aug_dict[name]:
            continue
        if i >= Mr.shape[0]:
            continue
        row = Mr[i,i:]
        is_independent = False
        
        all_zeros_, index = all_zero_on_right(row) #Speeds up checking
        if all_zeros_:
            is_independent  = True
            name            = keys[index+i]
            
        else:
            rank_changes = elim_recalc(Mr, i)
            if rank_changes:
                is_independent = True
                name           = keys[i]
        
        if is_independent:
            x_aug_dict[name]  = True
            found.append(name)
                            
    return x_aug_dict, found, Mr

def elim_recalc(Mr, col_num):
##    ###IMPORTANT: TEMPORARILY CONVERTING MATRICES FROM SYMENGINE TO SYMPY
##    Mr_copy   = PMatrix(Mr)
    Mr_copy   = Mr.copy() 
    curr_rank = Mr_copy.rank()
    Mr_copy.col_del(col_num)
    new_rank  = Mr_copy.rank()
    
    return new_rank != curr_rank

###############################################################################
#Core IA
###############################################################################
def check_identifiability(M, ics, x_aug_dict):
    Ms        = M.subs(ics)
    if 'inf' in  Ms.__str__():
        raise Exception('inf found in Ms. This could be due to a badly chosen initial value.')
    found, Mr = update(Ms, x_aug_dict)[1:]
        
    return x_aug_dict, found, Mr, Ms

def strike_group(h, x, p, u, f, ics, skip=[]):
    
    x_aug_dict = dict(zip(list(x) + list(p), [False]*len(list(x) + list(p))))
    for key in skip:
        x_aug_dict[key] = True

    start = time()
    M, nd, Li_1 = build_OI(h, x, p, u, f)
    print('Time for Building OI with '+str(nd)+' derivatives.', time()-start)
    found, Mr, Ms = check_identifiability(M, ics, x_aug_dict)[1:]
    print('Found: ', found)
    extra_   = 0
    
    while len(found) < len(x_aug_dict) and nd < len(x_aug_dict):
        rows           = M.shape[0]
        print('Adding 1 more Lie derivative')
        start          = time()
        M, nd, Li_1    = build_OI(h, x, p, u, f, extend=[M, 1, Li_1])
        print('Time for Building OI', time()-start)
        M[0:rows,:] = Mr
        found_, Mr, Ms = check_identifiability(M, ics, x_aug_dict)[1:]
        print('Found: ', found_)
        if len(found_) == 0:
            if extra_:
                #Breaks if two more derivatives have been added but no new variables have been found.
                break
            else:
                extra_ += 1
        else:
            extra_ = 0
            found.extend(found_)

    return x_aug_dict, Mr, Ms

###############################################################################
#Decomposition
###############################################################################
def make_group(h, x, p, u, f, ics, group, x_aug_dict={}):
    xg   = Matrix(group)
    hg   = Matrix([i    for i in h             if i    in xg])
    fg   = Matrix([f[i] for i in range(len(f)) if x[i] in xg])
    pg   = Matrix([i    for i in p             if not x_aug_dict.get(i, False) and in_f(i, fg)] + [i for i in x if i not in xg and in_f(i, fg)])
    ug   = {key: u[key]   for key in u   if in_f(key, fg)}
    icsg = {key: ics[key] for key in ics if key in xg}
    skip = [i             for i in xg    if x_aug_dict.get(i, False)]
    
    return hg, xg, pg, ug, fg, icsg, skip

def in_f(p, f):
    s1 = str(p)
    for line in f:
        s2 = str(line)
        if s1 in s2:
            return True
    return False

###############################################################################
#Top Level Function
###############################################################################
def strike(h, x, p, u, f, ics, decomp=[]):
    groups     = [x] if len(decomp) == 0 else decomp
    x_aug_dict = {key: True  if key in h else False for key in list(x) + list(p)}
    r          = []
    s          = []
    
    for group in groups:
        hg, xg, pg, ug, fg, icsg, skip = make_group(h, x, p, u, f, ics, group, x_aug_dict)
        
        print('Output(h): ')
        print(hg)
        print('States(x): ')
        print(xg)
        print('Params(p): ')
        print(pg)
        print('Equations(f): ')
        print(fg)
        print('Initial Conditions(ics): ')
        print(icsg)
        print()
        x_aug_dict_group, Mr, Ms = strike_group(hg, xg, pg, ug, fg, icsg, skip)
        r.append(Mr)
        s.append(Ms)
        for key in x_aug_dict_group:
           if x_aug_dict_group[key]:
               x_aug_dict[key] = True
        print(x_aug_dict_group)
        print('............................................')
    return x_aug_dict, r, s


##start_time=time()
##x_aug_dict, r, s=strike(h, x, p, u, f, ics, decomp=[[x0], [x2, x3], [x0, x1, x2, x3]])
##print('\nTotal time: ',time()-start_time)

#M, nd, Li_1 = build_OI(h, x, p, u, f, extend=[])
#x_aug_dict, Mr, Ms = strike_group(h, x, p, u, f, ics)

##print(M)
##x_aug_dict = dict(zip(list(x) + list(p), [False]*len(list(x) + list(p))))
##x_aug_dict, found, Mr, Ms = check_identifiability(M, ics, x_aug_dict)
##
###x_aug_dict, Mr, Ms = strike_group(h, x, p, u, f, ics)
##print(x_aug_dict)

##M, nd = build_OI(h, x, p, u, f)
##M, nd = build_OI(h, x, p, u, f, [M, 1])
##
##start = time()
##x_aug_dict, r, s = strike(h, x, p, u, f, ics, decomp=[[x1, x2, x3]])
##print(time()-start)
##print(x_aug_dict)
##M=s[0]
