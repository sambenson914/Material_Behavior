# Section datasets 

import numpy as np
import pandas as pd
import os
from pathlib import Path
import matplotlib.pyplot as plt 
from matplotlib.widgets import SpanSelector
import pickle as pkl

class Selection():
    def __init__(self):
        self.begin = 0
        self.end = 0

    def indices(self, begin, end):
        # Define beginning and end of selected data
        self.begin = begin
        self.end = end

    def bool():
        # User clicks on the plot.
        print('User selection initiated.')
        RectangleSelector.set_active(not RectangleSelector.active)

    def plot(df, region, filename):
        # Select the data after plotting
        # df contains the data to be selected
        # region will inform the user which region of the data to select
        # self contains the indices that will be selected.
        # filename is the name of the file for records.

        def display(xbegin, xend):
            # Display Selection
            print(f'Selection from {xbegin:0.2g} to {xend:0.2g}')
            return df

        # Selection plot
        fig, ax = plt.subplots()
        ax.plot(df.iloc[:,0], df.iloc[:,1])
        ax.set_title(f'Select {region}\n{filename}.')
        ax.set_xlabel(df.columns[0])
        ax.set_ylabel(df.columns[1])

        span = SpanSelector(
                            ax, 
                            display, 
                            'horizontal', 
                            props=dict(facecolor='blue', alpha=0.2),
                            )
        plt.show()

        # Populate the selected region
        xbegin = span.extents[0]
        xend = span.extents[1]
        df['Selection'] = 0
        maskSelection = (df.iloc[:,0] >= xbegin) & (df.iloc[:,0] <= xend)
        df.Selection[maskSelection] = 1

        return df

class Data():

    def __init__(self, data, region):
        self.data = data
        self.region = region

    def analyze(self):
        # Import and prepare data for parameter analysis
        for key, df in self.data.items():
            # Find the specified region
            region_identified = Selection.plot(df, self.region, key)
            self.data.update({key: region_identified})
        return self

    def import_from_extension(path: str):
        # Check file extension and import accordingly
        if str.endswith(path, '.xlsx') or str.endswith(path, 'xlsb'):
            df = pd.read_excel(path)
        elif str.endswith(path, '.csv'):
            df = pd.read_csv(path)
        elif str.endswith(path, '.pickle'):
            print(f'Skipping pickle file since it is assumed this is the output file.')
            return pd.DataFrame()
        else:
            assert print(f'File type not setup to be import. The file ends with "{str.split(path, ".")[-1]}".')
        return df

    def find_files(path: str):
        # Use the folder location to find files to import
        # path is the folder location for files to import
        # data stores the imported data in a dictionary
        data = {}
        files = os.listdir(path)
        for file in files:
            filepath = os.path.join(path, file)
            df = Data.import_from_extension(filepath)
            if len(df) > 0:
                data.update({str.split(file, '.')[0]: df})

        return data

def main(data_path):
    # Import files into data
    data_import = Data.find_files(data_path)
    data = Data(data_import, 'linear') 

    # Analyze Data for Linear and Nonlinear Regions
    data = data.analyze()

    # Output to pickle
    with open(os.path.join(data_path, 'sorted_data.pickle'), 'wb') as handle:
        pkl.dump(data, handle)

if __name__ == '__main__':
    # Determine location of images
    parent_path = Path(__file__).resolve().parents[1]
    data_path = os.path.join(parent_path, 'data')
    main(data_path)