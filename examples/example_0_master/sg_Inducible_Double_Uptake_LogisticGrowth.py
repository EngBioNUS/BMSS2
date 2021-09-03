from sympy import Matrix, Float, Symbol
from BMSS.strike_goldd_simplified import*

###############################################################################
#Model
###############################################################################

x, inde, indi, m, p = [Symbol(x) for x in ['x', 'inde', 'indi', 'm', 'p']]
mu_max, x_max, upind, k_ind, synm, degm, synp, n_ind = [Symbol(x) for x in ['mu_max', 'x_max', 'upind', 'k_ind', 'synm', 'degm', 'synp', 'n_ind']]


mu = mu_max*(1 - x/x_max)
dx    = mu*x
dinde = -upind*inde
dindi =  upind*inde
dm    =  synm*indi**n_ind/(indi**n_ind + k_ind**n_ind) - degm*m
dp    =  synp*m - mu*p

variables = {'x': x, 'inde': inde, 'indi': indi, 'm': m, 'p': p, 'mu_max': mu_max, 'x_max': x_max, 'upind': upind, 'k_ind': k_ind, 'synm': synm, 'degm': degm, 'synp': synp, 'n_ind': n_ind}

###############################################################################
#Specify Input for IA
###############################################################################
#User makes changes here
measured_states    = Matrix([x, p])
states             = Matrix([x, inde, indi, m, p])
unknown_parameters = Matrix([])
diff               = Matrix([dx, dinde, dindi, dm, dp])
input_conditions   = {}
init_conditions    = {x: Float(0.1, 3), inde: Float(0.1, 3), indi: Float(0.1, 3), m: Float(0.1, 3), p: Float(0.1, 3)}
decomposition      = [[x],
                      [p],
                      [m, p],
                      [inde, indi, m, p]
                      ]


known_parameters = {mu_max : 1, x_max : 1, upind : 1, k_ind : 1, synm : 1, degm : 1, synp : 1, n_ind : 1}
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
