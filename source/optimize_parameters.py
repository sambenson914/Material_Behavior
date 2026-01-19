# Optimize Parameters

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import least_squares
import material_func as mat_func
from pathlib import Path
import os
import pickle as pkl
from sort_data import Data # for pickle file import

class Optimize():
    def __init__(self):
        self.params = {}
        self.model = np.array([0])
        self.test = np.array([0])
        self.x = np.array([0])
        self.model_func = mat_func.Stress
        self.param_setup = mat_func.Stress.elastic_param_setup
        self.bounds = ([0, 1], [0, 1])
        self.x0 = [0.5, 0.5]
        self.result = {}
        self.result_type = 'E'
        self.result_path = os.path.join(Path(__file__).resolve().parents[1], 'data\\sorted_data.pickle')
        self.df = pd.DataFrame()
        self.filename = 'file.csv'

    def objective(self, x0):
        # Setup parameters
        self.params =  self.param_setup(x0, self.params)

        # Calculate the model result
        self.model = self.model_func(self.x, self.params, self.df.iloc[0, 1])
        error = np.sqrt((self.model - self.test)**2)/len(self.test)
        return error
    
    def plot(optimize, result_path, df):
        # Plot results
        plt.figure()
        plt.plot(optimize.x, optimize.test, 'b', label = 'Test')
        plt.plot(optimize.x, optimize.model, 'r-', label = 'Model')
        plt.xlabel(f'{df.columns[0]}')
        plt.ylabel(f'{df.columns[1]}')
        plt.legend()
        plt.tight_layout()
        plt.savefig(result_path + '.jpg')
        plt.title(f'{df.columns[1]}-{df.columns[0]}')

    def optimization(self):

        # Setup data
        df = self.df
        self.x = np.array(df.iloc[:,0])
        self.test = np.array(df.iloc[:,1])

        # Run optimization
        result = least_squares(self.objective, self.x0, bounds = self.bounds).x

        # Test the result
        self.params =  self.param_setup(result, self.params)
        self.model = self.model_func(self.x, self.params, np.array(self.df.iloc[0, 1]))
        Optimize.plot(self, self.result_path, df)

        # Save permanent result for each file
        result_types = str.split(self.result_type, '_')
        i = 0
        self.result.update({'filename': self.filename})

        for type in result_types[:-1]:
            # save each parameter
            self.result.update({type: result[i]})
            i += 1

        # create output of results
        with open(self.result_path + '_results.pickle', 'wb') as handle:
            pkl.dump(self.result, handle)

def main():
    
    # Determine location of data
    parent_path = Path(__file__).resolve().parents[1]

    # Import pickle file
    data_path = os.path.join(parent_path, 'data\sorted_data.pickle')
    with open(data_path, 'rb') as handle:
        data = pkl.load(handle)

    results_path = os.path.join(parent_path, 'results')
    result_df = pd.DataFrame()

    for filename, df in data.data.items():

        # Linear portion
        linear = np.argwhere(df.Selection == 1)

        # Linear parameter estimation
        elastic = Optimize()
        elastic.model_func = mat_func.Stress.model
        elastic.param_setup = mat_func.Stress.elastic_param_setup
        elastic.bounds = ([10], [1000000])  # MPa
        elastic.x0 = 10000.0
        elastic.params = {'E': 0, 'p1': 0, 'p2': 0, 'p3': 0, 'p4': 0}
        elastic.result_type = 'E_'
        elastic.result_path = os.path.join(results_path, f'elastic\\{filename}')
        elastic.df = df[df.Selection == 1]
        elastic.filename = filename
        elastic.optimization()

        # Nonlinear parameter estimation
        plastic = elastic 
        plastic.param_setup = mat_func.Stress.plastic_param_setup
        plastic.params = {'E': 0}
        plastic.bounds = ([-1000000, -1000000, -1000000, -1000000], [1000000, 1000000, 1000000, 1000000])
        plastic.x0 = [1, 1, 1, 1]
        plastic.result_type = 'p1_p2_p3_p4_'
        plastic.df = df[df.index > linear[-1][0]]
        plastic.result_path = os.path.join(results_path, f'plastic\\{filename}')
        plastic.optimization()
        
        # Save results to file_path
        result_df = pd.concat([result_df, pd.DataFrame(plastic.result,index = [0])],ignore_index=True)
    
    # Output parameters
    result_df.to_csv(plastic.result_path + '.csv')
    

if __name__ == '__main__':
    main()