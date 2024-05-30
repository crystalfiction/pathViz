import os
import time
import xmltodict
import pandas as pd
from pandas import DataFrame
import numpy as np
from plotly.graph_objects import Figure
from sklearn.cluster import KMeans
from sklearn.neighbors import KernelDensity


GOAL_KEY = {}
SCRIPT_LOG = "scriptLog.txt"


def clean_logs(dir: str):
    """
    Tests whether any blank logs exist in
    the DATA_DIR and removes them
    """
    logs = os.listdir(dir)
    # test logs...
    for l in logs:
        logPath = dir + l
        test = None
        with open(logPath, "r") as f:
            content = f.readline()
            if content == "":
                test = True

        # if test passed...
        if test is not None:
            # delete the empty log
            os.remove(logPath)


def save_data(dir: str, mode: str, data: Figure):
    """
    Writes passed 'data' to new file in OUTPUT_DIR
    depending on the passed 'mode'.
        - fileName = {mode}{current_time}.png, i.e. 'viz20240529.png'
    """
    files = []
    # if output dir exists
    if os.path.exists(dir):
        # get files
        files = os.listdir(dir)
    else:
        # else make dir
        os.makedirs("output/")

    t = time.localtime()
    current_time = time.strftime("%Y%d%H%M", t)
    fileName = current_time

    # if file doesn't already exist
    if fileName not in files:
        # write it
        content = ""
        # if viz mode...
        if mode == "viz":
            # write figure to image file
            content = data
            content.write_image(dir + mode + fileName + ".png")
    else:
        return print("File already exists...")


def clear_cache():
    """
    Wipes the contents of logScript.txt
    and removes existing snapshots.csv & snapshots.json
    """
    with open(SCRIPT_LOG, "w") as log:
        # close the log and reset contents
        log.close()

    # print update
    print("Script cache cleared...")

    # remove snapshots
    try:
        os.remove("snapshots.csv")
        os.remove("snapshots.json")
        print("Removed snapshots files...")
    except:
        print("No snapshots found...")


def get_density(df: DataFrame):
    """
    Calculates probability density for dataset

    Returns passed dataframe with scored 'n_dist' col
    """
    # split features/labels
    X = df[["x", "y", "z"]]
    X_labels = df[["path_id", "path_goal", "snapshot"]]

    # fit X to KDE model
    kde = KernelDensity(kernel="gaussian", bandwidth=1)
    kde.fit(X)

    # score each point on its density probability
    density = kde.score_samples(X)
    # round to .2f
    density = [round(i) for i in density]
    # normalize between 0:1
    normalized = normalize_data(density)

    # merge the data/features after fitting
    processed = X.merge(X_labels, on=X.index, sort=False).drop(columns=["key_0"])

    # add distances to df['n_dist'] col
    processed["n_density"] = pd.Series(normalized).astype("float")

    # return the processed df
    return processed
    # return None


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
