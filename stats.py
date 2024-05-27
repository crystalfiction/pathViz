import os
import pandas as pd
import numpy as np
from parse_goals import parse_keys


def get_avg_snapshot_distance(paths):
    # get unique path_ids
    unique_paths = paths["path_id"].unique()
    # unique path vectors to be calculated in snapshot distance
    path_distances = []
    path_goals = []
    # for each unique path_id...
    for pid in unique_paths:
        # filter snapshot for current pid
        path = paths[paths["path_id"] == pid]

        # subset path goals
        goals = path["path_goal"]
        # append the most common goal for path
        path_goal = goals.mode()
        path_goals.append(path_goal[0])

        # drop non-numerics
        path = path.drop(columns=["path_id", "path_goal"])

        # calculate avg distance over axes
        path_axes_distance = path.std()
        # replace empty values
        path_axes_distance = pd.Series([i if i > 0 else 0 for i in path_axes_distance])
        # calculate total avg distance for this path
        path_total_distance = path_axes_distance.std()
        # append to path_distances
        path_distances.append(path_total_distance)

    # assert Series type
    path_distances = pd.Series(path_distances)
    path_goals = pd.Series(path_goals)

    # final calculations
    snapshot_distance = path_distances.std()
    snapshot_goal = path_goals.mode()

    # returns avg snapshot distance as float
    return snapshot_distance, snapshot_goal


def generate_stats():
    # break case
    if not os.path.exists("snapshots.csv"):
        print("No data found... please 'import' first.")
        return None

    print("Generating stats...")
    print("-------------------")

    # parse goal_key
    GOAL_KEY = parse_keys()

    # get snapshots
    snapshots = pd.read_csv("snapshots.csv").drop(columns=["Unnamed: 0"])

    # avg distance traveled by snapshot
    unique_snapshots = snapshots["snapshot"].unique()
    snapshot_distances = []
    snapshot_goals = []
    # for each unique snapshot...
    for id in unique_snapshots:
        # filter dataframe by snapshot id
        snapshot = snapshots[snapshots["snapshot"] == id]
        # subset only path numerical data
        paths = snapshot[["path_id", "path_goal", "x", "y", "z"]]

        # get avg snapshot distance
        snapshot_distance, snapshot_goal = get_avg_snapshot_distance(paths)

        # append to snapshot_distances
        snapshot_distances.append(snapshot_distance)

        # get the goal key_value from GOAL_KEY
        if GOAL_KEY:
            snapshot_goals.append(GOAL_KEY[snapshot_goal[0]])

    # create dataframes
    total_snapshot_distances = pd.DataFrame(
        snapshot_distances, index=unique_snapshots, columns=["avg_distance"]
    )
    total_snapshot_goals = pd.DataFrame(
        snapshot_goals, index=unique_snapshots, columns=["goal"]
    )

    # print results
    # print("Avg Distance by Snapshot")
    # print(total_snapshot_distances)
    # print("-------------------")
    # print("Avg Snapshot Path Goal")
    # print(total_snapshot_goals)
    # print("-------------------")

    # returns list of stats
    return [total_snapshot_distances, total_snapshot_goals]
