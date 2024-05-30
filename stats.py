import pandas as pd
from pandas import DataFrame
import pprint

from utils import parse_keys


GOAL_KEY = {}


def get_stats(limit: int, orient: str):
    """
    - total avg distance per path
    - snapshots
      - total avg distance by snapshot
      - most common goal by snapshot
    - goals
      - total avg distance by goal
      - most common goal
    """
    # read snapshots from snapshots.csv
    snapshots = pd.read_csv("snapshots.csv").drop(columns=["Unnamed: 0"])

    # define return vars
    output = []
    stats = {}

    # get total avg distance
    apd = avg_path_dist(snapshots, limit, orient)
    output.append(f"Total avg dist travelled: {apd}")
    apd_df = pd.DataFrame({"avg_path_dist": apd}, index=[0])
    stats["apd"] = apd_df

    # get avg dist per snapshot
    dps = dist_per_snapshot(snapshots, limit, orient)

    # get common goal per snapshot
    gps = goal_per_snapshot(snapshots, limit, orient)

    # get avg dist per goal
    dpg, mcg = dist_per_goal(snapshots, limit, orient)

    # combine snapshot dfs
    by_snapshot = dps.merge(gps, on="snapshot")
    output.append(by_snapshot)
    stats["snapshot"] = by_snapshot

    output.append(f"Most common goal: {mcg}")
    mcg_df = pd.DataFrame({"most_common_goal": mcg}, index=[0])
    stats["mcg"] = mcg_df

    # combine goal dfs
    by_goal = dpg
    output.append(by_goal)
    stats["goal"] = by_goal

    # print the results
    print("-----------------------------------")
    print("pathViz Stats")
    print("-----------------------------------")
    for o in output:
        pprint.pprint(o)
        print("")
    print("-----------------------------------")

    # return the list of stat values
    # for saving
    return stats


def dist_per_goal(df: DataFrame, limit: int, orient: str):
    """"""
    GOAL_KEY = parse_keys()

    # if --limit passed...
    sids = df["snapshot"].unique()
    if limit > 0:
        # TODO: account for limit=1

        # check if --orient option passed...
        # defaults to "btm"
        if orient == "top":
            # if option passed
            # slice the first n=limit snapshots
            sids = sids[:limit]
        elif orient == "btm":
            # else slice the last n=limit snapshots
            sids = sids[-limit : len(sids)]

    # account for limiting
    filter = [True if r in sids else False for r in df["snapshot"]]
    working = df[filter]

    # get most common goals
    mcg = working["path_goal"].mode()[0]
    mcg_fmt = GOAL_KEY[mcg]

    # get unique goal ids
    gids = working["path_goal"].unique()

    # for each gid
    goal_dists = []
    for gid in gids:
        # filter df
        by_goal = working[working["path_goal"] == gid]
        # get avg path dist
        apd = avg_path_dist(by_goal, 0, orient)
        goal_dists.append(apd)

    gids_fmt = [GOAL_KEY[gid] for gid in gids]

    avg_dist_per_goal = pd.DataFrame(goal_dists, index=gids_fmt).rename(
        columns={0: "avg_dist"}
    )
    avg_dist_per_goal.index.name = "goal"

    return avg_dist_per_goal, mcg_fmt


def goal_per_snapshot(df: DataFrame, limit: int, orient: str):
    """"""
    GOAL_KEY = parse_keys()
    sids = df["snapshot"].unique()

    # if --limit passed...
    if limit > 0:
        # TODO: account for limit=1

        # check if --orient option passed...
        # defaults to "btm"
        if orient == "top":
            # if option passed
            # slice the first n=limit snapshots
            sids = sids[:limit]
        elif orient == "btm":
            # else slice the last n=limit snapshots
            sids = sids[-limit : len(sids)]

    goals = []
    for sid in sids:
        curr_shot = df[df["snapshot"] == sid]
        c_goal = curr_shot["path_goal"].mode()[0]
        goal = GOAL_KEY[c_goal]
        goals.append(goal)

    common_goal_per_snapshot = pd.DataFrame(
        goals, index=["00" + str(s) for s in sids]
    ).rename(columns={0: "common_goal"})
    common_goal_per_snapshot.index.name = "snapshot"

    return common_goal_per_snapshot


def dist_per_snapshot(df: DataFrame, limit: int, orient: str):
    """"""
    sids = df["snapshot"].unique()

    # if --limit passed...
    if limit > 0:
        # TODO: account for limit=1

        # check if --orient option passed...
        # defaults to "btm"
        if orient == "top":
            # if option passed
            # slice the first n=limit snapshots
            sids = sids[:limit]
        elif orient == "btm":
            # else slice the last n=limit snapshots
            sids = sids[-limit : len(sids)]

    snapshot_dists = []
    for sid in sids:
        curr_shot = df[df["snapshot"] == sid]
        curr_apd = avg_path_dist(curr_shot, limit, orient)
        snapshot_dists.append(curr_apd)

    avg_dist_per_shot = pd.DataFrame(
        snapshot_dists, index=["00" + str(s) for s in sids]
    ).rename(columns={0: "avg_dist"})
    avg_dist_per_shot.index.name = "snapshot"

    return avg_dist_per_shot


def avg_path_dist(df: DataFrame, limit: int, orient: str):
    """"""

    sids = df["snapshot"].unique()

    # if --limit passed...
    if limit > 0:
        # TODO: account for limit=1

        # check if --orient option passed...
        # defaults to "btm"
        if orient == "top":
            # if option passed
            # slice the first n=limit snapshots
            sids = sids[:limit]
        elif orient == "btm":
            # else slice the last n=limit snapshots
            sids = sids[-limit : len(sids)]

    # account for limiting
    filter = [True if r in sids else False for r in df["snapshot"]]
    working = df[filter]

    # get unique path_ids
    pids = working["path_id"].unique()

    paths = []
    # for each path id in snapshot collection
    for pid in pids:
        # filter the df
        path = working[working["path_id"] == pid]
        # get the sum of the first row's x,y,z
        start_pt = path.iloc[0].astype("int64").sum()
        # get the sum of the last row's x,y,z
        end_pt = path.iloc[-1].astype("int64").sum()
        # get the absolute difference between start/end
        dist = abs(start_pt - end_pt)
        # append to paths list
        paths.append(dist)

    # convert paths to series
    paths = pd.Series(paths)
    # save return var
    total_avg_dist = round(paths.mean(), 2)

    return total_avg_dist
