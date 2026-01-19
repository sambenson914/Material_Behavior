# Material functions
import numpy as np
import pandas as pd

class Stress():
    # Optimize for Stress
    def model(strain: np.ndarray, params: dict, stress0: float):
        # Calculate stress from parameters and strain
        # Strain is the change in length over the initial length
        # params is a dictionary that contains E, p1, p2, p3
        # E is the Elastic modulus
        # p1, p2, p3 are parameters to capture the nonlinear region
        delta_strain = strain - strain[0]
        linear = (delta_strain)*params['E']
        plastic = delta_strain * params['p1'] \
                    + delta_strain**2 * params['p2'] \
                    + delta_strain**3 * params['p3'] \
                    + delta_strain**4 * params['p4']
        
        return linear + plastic + stress0
    
    def elastic_param_setup(x0, params: dict):
        # Setup elastic parameters according to x0
        # x0 contains E, the elastic modulus
        params['E'] = x0

        return params
    
    def plastic_param_setup(x0, params: dict):
        # Setup plastic parameters according to x0
        # x0 contains n parameters
        # fill in based on length of x0
        parameter_list = ['p1', 'p2', 'p3', 'p4']
        i = 0
        for param in parameter_list:
            params[param] = x0[i]
            i += 1

        return params
