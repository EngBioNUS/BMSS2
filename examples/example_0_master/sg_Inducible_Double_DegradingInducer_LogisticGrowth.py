from sympy import Matrix, Float, Symbol
from BMSS.strike_goldd_simplified import*

###############################################################################
#Model
###############################################################################

x, ind, m, p = [Symbol(x) for x in ['x', 'ind', 'm', 'p']]
mu_max, x_max, degind, k_ind, synm, degm, synp, n_ind = [Symbol(x) for x in ['mu_max', 'x_max', 'degind', 'k_ind', 'synm', 'degm', 'synp', 'n_ind']]


mu = mu_max*(1 - x/x_max)
dx   = mu*x
dind = -degind*ind
dm   =  synm*ind**n_ind/(ind**n_ind + k_ind**n_ind) - degm*m
dp   =  synp*m - mu*p

variables = {'x': x, 'ind': ind, 'm': m, 'p': p, 'mu_max': mu_max, 'x_max': x_max, 'degind': degind, 'k_ind': k_ind, 'synm': synm, 'degm': degm, 'synp': synp, 'n_ind': n_ind}

###############################################################################
#Specify Input for IA
###############################################################################
#User makes changes here
measured_states    = Matrix([x, ind, m, p])
states             = Matrix([x, ind, m, p])
unknown_parameters = Matrix([])
diff               = Matrix([dx, dind, dm, dp])
input_conditions   = {}
init_conditions    = {x: Float(0.1, 3), ind: Float(0.1, 3), m: Float(0.1, 3), p: Float(0.1, 3)}
decomposition      = [[x],
                      [p],
                      [m, p],
                      [ind, m, p]
                      ]


known_parameters = {mu_max : 1, x_max : 1, degind : 1, k_ind : 1, synm : 1, degm : 1, synp : 1, n_ind : 1}
diff = diff.subs(known_parameters.items())


###############################################################################
#Call Strike-Goldd
###############################################################################
def run_strike_goldd():
    start_time = time()
    x_aug_dict = strike_goldd(measured_states, 
                              states, 
                              unknown_parameters, 
                              input_conditions, 
                              diff, 
                              init_conditions, 
                              decomposition)
    print("Total time: ",time()-start_time)
    print(x_aug_dict)
    return x_aug_dict

if __name__ == '__main__':
    pass
