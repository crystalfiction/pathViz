import math
import pandas as pd
import numpy as np


def normalize_list(list):
    # normalize list between 0:1
    norm = [float(i) / sum(list) for i in list]
    return norm
