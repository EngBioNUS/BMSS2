from sympy import Matrix, Float, Symbol
from BMSS.strike_goldd_simplified import*

###############################################################################
#Model
###############################################################################

x, s, h = [Symbol(x) for x in ['x', 's', 'h']]
mu_max, Ks, Y, synh, Kind = [Symbol(x) for x in ['mu_max', 'Ks', 'Y', 'synh', 'Kind']]
Ind = Symbol('Ind')


mu   = mu_max*s/(s+Ks)

dx  =  x*mu
ds  = -dx/Y
dh  =  synh*Ind/(Ind+Kind) -h*mu

variables = {'x': x, 's': s, 'h': h, 'mu_max': mu_max, 'Ks': Ks, 'Y': Y, 'synh': synh, 'Kind': Kind, 'Ind': Ind}

###############################################################################
#Specify Input for IA
###############################################################################
#User makes changes here
measured_states    = Matrix([x, s, h])
states             = Matrix([x, s, h])
unknown_parameters = Matrix([synh, Kind])
diff               = Matrix([dx, ds, dh])
input_conditions   = {Ind: 6}
init_conditions    = {x: Float(1, 3), s: Float(1, 3), h: Float(1, 3)}
decomposition      = [[x, s, h]
                      ]


known_parameters = {Y : 3}
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
