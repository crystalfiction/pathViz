import os
import pandas as pd
import numpy as np


def query():
    """
    Queries existing snapshots
    """
    # read the snapshots file
    snapshots = pd.read_csv("snapshots.csv").drop(columns=["Unnamed: 0"])

    # get unique snapshot names
    names = snapshots["snapshot"].unique()

    print(str(len(names)) + " snapshots found...")
    for name in names:
        print(name)
