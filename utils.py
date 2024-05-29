import math
import xmltodict
import pandas as pd
from pandas import DataFrame
import numpy as np
from sklearn.cluster import KMeans
from sklearn.neighbors import KernelDensity


GOAL_KEY = {}


def get_density(df: DataFrame):
    """"""
    # remove non-numerical cols
    X = df[["x", "y", "z"]]
    X_features = df[["path_id", "path_goal", "snapshot"]]

    # fit X to the model
    kde = KernelDensity(kernel="gaussian", bandwidth=1)
    kde.fit(X)
    density = kde.score_samples(X)
    density = [round(i) for i in density]
    normalized = normalize_data(density)

    # merge the data/features after fitting
    processed = X.merge(X_features, on=X.index, sort=False).drop(columns=["key_0"])

    # add distances to df['n_dist'] col
    processed["n_density"] = pd.Series(normalized).astype("float")

    # return the processed df
    return processed


def parse_keys():
    """
    Parses path goals in goals_key.xml

    Returns formatted goals as dict GOAL_KEYS
    """
    # parse the xml file to dict
    xml = None
    with open("goals_key.xml", "r", encoding="utf8") as f:
        content = f.read()
        xml = xmltodict.parse(content)

    key_dict = xml["enum-type"]["enum-item"]
    for i, k in enumerate(key_dict):
        # convert list to '-1' based
        i = i - 1

        # add to GOAL_KEY dict
        GOAL_KEY[i] = k["@name"]

    return GOAL_KEY


def get_kmeans(snapshot: DataFrame):
    """
    Calculates KMeans clustering for the passed snapshot

    Returns cluster center coordinates and inertia
    """

    # subset numericals from the snapshot
    snapshot_prep = snapshot[["x", "y", "z"]]

    # instantiate KMeans model
    kmeans = KMeans(n_clusters=1, n_init="auto")
    # fit snapshot to model
    snapshot_k = kmeans.fit(snapshot_prep)
    # get the cluster centers
    cluster_center = snapshot_k.cluster_centers_
    # get the inertia
    inertia = snapshot_k.inertia_

    # return the snapshot KMeans data
    return cluster_center, inertia


def normalize_data(data):
    return (data - np.min(data)) / (np.max(data) - np.min(data))
