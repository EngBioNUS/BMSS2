from sympy import Matrix, Float, Symbol
from BMSS.strike_goldd_simplified import*

###############################################################################
#Model
###############################################################################

x, h = [Symbol(x) for x in ['x', 'h']]
mu_max, synh, Kind, x_max = [Symbol(x) for x in ['mu_max', 'synh', 'Kind', 'x_max']]
Ind = Symbol('Ind')


mu   = mu_max*(1 - x/x_max)
dx  =  x*mu
dh  =  synh*Ind/(Ind+Kind) -h*mu

variables = {'x': x, 'h': h, 'mu_max': mu_max, 'synh': synh, 'Kind': Kind, 'x_max': x_max, 'Ind': Ind}

###############################################################################
#Specify Input for IA
###############################################################################
#User makes changes here
measured_states    = Matrix([x, h])
states             = Matrix([x, h])
unknown_parameters = Matrix([])
diff               = Matrix([dx, dh])
input_conditions   = {Ind: 5}
init_conditions    = {x: Float(0.1, 3), h: Float(0.1, 3)}
decomposition      = [
                      ]


known_parameters = {mu_max : 1, synh : 1, Kind : 1, x_max : 1}
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
