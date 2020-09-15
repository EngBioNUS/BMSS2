from   sympy import symbols
from   sympy.matrices import Matrix, zeros
from   math           import ceil
import string
import sympy as sp

from time import time

nt = 10

def t(*funcs):
    global nt
    for func in funcs:
        start = time()
        for i in range(nt):
            func()
        print(time()-start)

def timethis(message):
    def wrapper(func):
        def helper(*args, **kwargs):
            start  = time()
            result = func(*args, **kwargs)
            print(message, time()-start)
            return result
        return helper
    return wrapper

def format_to_matlab(mat_row):
    '''
    For backend testing only. Do not run.
    '''
    s = str(mat_row)
    s = s[7:len(s)-1]
    s = s[1:len(s)-1]
    s = s.replace('**', '^')

    with open('matlab_comparison.txt', 'w') as file:
        file.write(s)
    return s

###############################################################################
#Globals
###############################################################################
verbose = False

###############################################################################
#Building OI
###############################################################################
@timethis('Time for adding one Lie derivative:')
def add_block(curr_block, block_num, input_der, f_aug, x_aug, last_L):
    '''
    Find the new Lie derivative and create a new block for Oi
    '''
    global verbose
    dummy      = symbols(['dummy'])[0]
    L_h        = curr_block*f_aug
    extra      = zeros(curr_block.shape[0], 1)
    if input_der:
        #Modification for accounting for inputs
        for i in range(block_num-1):
            if i < input_der.shape[1] - 1:
                lo_u   = input_der[:,i]
                hi_u   = input_der[:,i+1]
                lo_u   = lo_u.subs(0, dummy)
                
                if all([True if i == 0 or i == dummy else False for i in lo_u]):
                    continue
                
                extra_ = last_L.jacobian(Matrix(lo_u)) *hi_u
                extra += extra_
            else:
                break

    last_L     = L_h + extra
    
    new_block  = last_L.jacobian(x_aug)
    if verbose:
        print(new_block)

    return new_block, last_L

def get_nd(h, x, p):
    return ceil((len(x) +len(p) -len(h))/len(h))

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

@timethis('Time for building Oi:')
def build_OI(x, p, f, h, u, nd, ics={}):
    x_aug = Matrix(list(x) + list(p)).T
    f_aug = Matrix(list(f) + [0]*len(p))

    Oi        = zeros(rows=len(h)*(nd+1), cols=len(x_aug))
    input_der = build_input_der(u, nd)

    print('Building Oi with '+ str(nd) + ' derivatives and size', Oi.shape)
    
    curr_block    = h.T.jacobian(x_aug)
    Oi[:len(h),:] = curr_block
    last_L        = h
    for block_num in range(1, nd+1):
        curr_block, last_L       = add_block(curr_block, block_num, input_der, f_aug, x_aug, last_L)

        if ics:
            curr_block = curr_block.subs(ics.items())
        
        start                    = block_num*len(h)
        Oi[start:start+len(h),:] = curr_block

    return Oi, input_der, x_aug, f_aug, last_L

def extend_Oi(Oi, input_der, nd, x_aug, f_aug, x, p, f, h, u, last_L):
    print('Extending Oi')
    new_Oi = Matrix(Oi.tolist() + [[0]*len(x_aug)]*len(h))
    
    curr_block    = Oi[-len(h):,:]
    block_num     = nd + 1
    new_input_der = build_input_der(u, block_num)

    new_Oi[-len(h):,:], last_L = add_block(curr_block, block_num, new_input_der, f_aug, x_aug, last_L)

    return new_Oi, block_num, last_L

###############################################################################
#Elimination and Recalculation
###############################################################################
def elim_recalc(Mr, rank, x_aug, h, skip):
    '''
    Assumes initial conditions have been substituted already.
    '''
    print('Elim-recalc for matrix with size', Mr.shape)
    found = []
    
    #Eliminate var
    for i in range(len(x_aug)):
        var = x_aug[i]
        
        if var in skip or var in h or i not in rank:
            continue
        Mr_        = Mr.copy()
        Mr_.col_del(i)
        Mr_, rank_ = Mr_.rref()

        if len(rank) != len(rank_):
            found.append(var)
    print('Found', found)
    return found

@timethis('Time for Row Reduction:')
def check_rank(Oi, ics):
    print('Checking rank for matrix with size', Oi.shape)
    Mr       = Oi.subs(ics.items())
    if 'inf' in  Mr.__str__():
        raise Exception('inf found in Ms. This could be due to a badly chosen initial value.')
    Mr, rank = Mr.rref()
    print('Rank', len(rank))
    return Mr, rank

###############################################################################
#Core Algorithm
############################################################################### 
def strike_group(x, p, f, h, u, ics):
    '''
    Core algorithm. Edit with extreme caution.
    Builds Oi and checks rank.
    Adds a Lie derivative if necessary and checks rank again.
    Note that the current implementation always uses decomp=False.
    '''
    nd = get_nd(h, x, p)
    Oi, input_der, x_aug, f_aug, last_L = build_OI(x, p, f, h, u, nd, ics)
        
    Mr, rank = check_rank(Oi, ics)

    if len(rank) == len(x_aug):
        found = [i for i in x_aug if i not in h]
        print('Found', found)
        
    else:
        found  = elim_recalc(Mr, rank, x_aug, h, [])
        
        while True:
            Oi, nd, last_L = extend_Oi(Oi.subs(ics.items()), input_der, nd, x_aug, f_aug, x, p, f, h, u, last_L)

            Oi     = Matrix(Mr.tolist() + Oi[-len(h):,:].tolist())
            
            Mr, rank = check_rank(Oi, ics)
            
            if len(rank) == len(x_aug):
                new_found = [i for i in x_aug if i not in h and i not in found]
                found     = [i for i in x_aug if i not in h]
                print('Found', new_found)
                break
            else:
                found_= elim_recalc(Mr, rank, x_aug, h, found)

                if found_:
                    found += found_
                    
                else:
                    break
    return found

###############################################################################
#Decomposition
###############################################################################
def make_group(h, x, p, u, f, ics, group, found):
    '''
    Creates submodels(groups).
    States and parameters in found will not be included in
    the unknowns for analysis.
    '''
    
    xg    = Matrix([x[i] for i in range(len(x)) if x[i] in group])
    fg    = Matrix([f[i] for i in range(len(f)) if x[i] in xg])
    
    terms = get_terms(fg)
    pg    = Matrix([i  for i in p   if  str(i) in terms and  i not in found] +
                   [i  for i in x   if  str(i) in terms and  i not in found and i not in xg and i not in h])
    hg    = Matrix([i  for i in x   if  i      in xg    and (i     in found or i in h)])
    ug    = {i: u[i]   for i in u   if  str(i) in terms}
    icsg  = ics.copy()#{i: ics[i] for i in ics if  i      in xg}

    return hg, xg, pg, ug, fg, icsg

def get_terms(f):
    '''
    Supporting function for make_group. Extracts all terms in an expression.
    '''
    punctuation = string.punctuation.replace('_', '')
    fs = str([i for i in f])
    fs = fs[1:len(fs)-1].replace(' ', '')
    tr = str.maketrans(punctuation, ','*len(punctuation)) 
    fs = fs.translate(tr)
    fs = [i for i in fs.split(',') if i]

    return set(fs)

###############################################################################
#Main Algorithm
###############################################################################
def iterative_decomp(x, p, f, h, u, ics, decomp=[]):
    '''
    Iterates across groups and updates accordingly.
    '''
    found = []
    
    for group in decomp:
        start = time()
        hg, xg, pg, ug, fg, icsg = make_group(h, x, p, u, f, ics, group, found)
        print('States : ', list(xg))
        print('Outputs: ', list(hg))
        print('Params : ', list(pg))
        print('Inputs : ', ug)
        print('ICS    : ', icsg)
        print('Equations:\n'+'\n'.join([str(i) for i in fg]))

        found_ = strike_group(xg, pg, fg, hg, ug, icsg)
        print(time()-start)
        print('...................................................')
        
        found += found_
    return list(h) + found

@timethis('Total Time:')
def strike_goldd(h, x, p, u, f, ics, decomp=[]):
    '''
    Wrap the algorithm and organize the results.
    Also checks input arguments for errors.
    '''
    if len(f) != len(x):
        raise Exception('Number of equations not equal to number of states! '+
                        'Remember to mark on non-differential expressions with "!" if you are using a mark-up file.')
    
    if len(ics) != len(x):
        raise Exception('Number of initial conditions not equal to number of states!')

    decomp1    = decomp if decomp else [list(x)]
    found      = iterative_decomp(x, p, f, h, u, ics, decomp=decomp1)
    x_aug_dict = {i: True if i in found else False for i in list(x)+list(p)}
        
    return x_aug_dict

def analyze_sg_args(sg_args, dst={}):
    result = dst if dst else {}
    for key in sg_args:
        result[key] = strike_goldd(**sg_args[key])
    
    return result
        
if __name__ == '__main__':
    pass
##    m1, p1 = symbols(['m1', 'p1'])
##    synm1, degm, synp1, degp = symbols(['synm', 'degm', 'synp', 'degp'])
##    g1, g2, g3, g4 = symbols(['g1', 'g2', 'g3', 'g4'])
##    u1 = symbols(['u1'])[0]
##
##    dm1 = synm1 - degm*m1 - u1*g1*g2*g3*g4
##    dp1 = synp1*m1 - degp*p1 + u1
##    
##    x = Matrix([m1, p1])
##    h = Matrix([p1])
##    p = Matrix([synm1, degm, synp1, degp, g1, g2, g3, g4])
##    f = Matrix([dm1, dp1])
##    u = {u1: 0}
##    
##    x_aug = Matrix(list(x) + list(p)).T
##    f_aug = Matrix(list(f) + [0]*len(p))
##
##    nd        = get_nd(h, x, p)
##    Oi        = zeros(rows=len(h)*(nd+1), cols=len(x_aug))
##    input_der = build_input_der(u, nd)
##
##    print('Building Oi with '+ str(nd) + ' derivatives.')
##    
##    curr_block  = h.T.jacobian(x_aug)
##    Oi[:len(h),:] = curr_block
##    
##    for block_num in range(1, nd+1):
##        curr_block               = add_block(curr_block, block_num, input_der, f_aug, x_aug)
##        start                    = block_num*len(h)
##        Oi[start:start+len(h),:] = curr_block



##    a, n1, r3, g1, g2, k1, k2, k3, k4, k5, k6, k7, m1, m2, m3, m4, m5, m6, m7, n2, p1, p2, p3, q1, q2, r1, r2, r4 = symbols(['a', 'n1', 'r3', 'g1', 'g2', 'k1', 'k2', 'k3', 'k4', 'k5', 'k6', 'k7', 'm1', 'm2', 'm3', 'm4', 'm5', 'm6', 'm7', 'n2', 'p1', 'p2', 'p3', 'q1', 'q2', 'r1', 'r2', 'r4'])
##    x1, x2, x3, x4, x5, x6, x7 = symbols(['x1', 'x2', 'x3', 'x4', 'x5', 'x6', 'x7'])
##    u1 = symbols(['u1'])[0]
##
##    dx1 = n1*x6**a/(g1**a+x6**a) -m1*x1/(k1+x1) +q1*x7*u1
##    dx1 = dx1.subs(a, 1)
##    dx2 = p1*x1 -r1*x2 +r2*x3    -m2*x2/(k2+x2)    
##    dx3 = r1*x2 -r2*x3           -m3*x3/(k3+x3)
##    dx4 = n2*g2**2/(g2**2+x3**2) -m4*x4/(k4+x4)
##    dx5 = p2*x4 -r3*x5 +r4*x6    -m5*x5/(k5+x5)
##    dx6 = r3*x5 -r4*x6           -m6*x6/(k6+x6)
##    dx7 = p3                     -m7*x7/(k7+x7) -(p3+q2*x7)*u1
##
##    x = Matrix([x1, x2, x3, x4, x5, x6, x7])
##    p = Matrix([n1, r3, g1, g2, m1, m2, m3, m4, m5, m6, m7, n2, p1, p2, p3, q1, q2, r1, r2, r4])
##    f = Matrix([dx1, dx2, dx3, dx4, dx5, dx6, dx7])
##    h = Matrix([x1, x2, x3, x4])
##    u = {u1: 0}
##    ics = {state: 0 for state in x}
##
##    found = []
##    
##    hg, xg, pg, ug, fg, icsg = make_group(h, x, p, u, f, ics, [x1, x7], [])
##    decomp = [[x1, x4], [x2, x3], [x3, x4], [x1, x7]]
##    decomp = [[x1, x7]]
####    found = iterative_decomp(x, p, f, h, u, ics, decomp=decomp)
##
##    nd = get_nd(hg, xg, pg)
##    Oi, input_der, x_aug, f_aug = build_OI(xg, pg, fg, hg, ug, 9)


    
##    print(found)
##    
##    h = Matrix([i for i in x if i in h or i in found])
##    p = Matrix([i for i in p if i not in found])
##
##    found = iterative_decomp(x, p, f, h, u, ics, decomp=[[x2, x3]])
##
##    
##    answer = set([x1, x2, x3, x4, m4, n2, x6, x7, x2, p3, q1, m1, m7, q2])
    

############################################################
############################################################
##    found = []
##    
##    hg, xg, pg, ug, fg, icsg = make_group(h, x, p, u, f, ics, [x1, x4], found)
##    
##    Oi, input_der, nd, x_aug, f_aug = build_OI(xg, pg, fg, hg, ug)

