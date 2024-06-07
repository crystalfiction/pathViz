import os
import time
import pandas as pd
import shutil

from utils import clear_cache


def save_snapshot(dir: str):
    """"""
    # if no data has been loaded yet...
    if not os.path.exists("snapshot.csv"):
        return print("No data loaded.")

    t = time.localtime()
    current_time = time.strftime("%Y%d%H%M", t)
    fileName = current_time

    # format passed dir
    dir_fmt = dir + fileName + "/"

    # copy the snapshot to a new snapshot folder
    files = []
    # if output dir exists
    if os.path.exists(dir_fmt):
        # get files
        files = os.listdir(dir_fmt)
    else:
        # else make dir
        os.makedirs(dir_fmt)

    snapshot_csv = "snapshot.csv"
    snapshot_json = "snapshot.json"

    # if snapshot files already exist
    if snapshot_csv and snapshot_json in files:
        print("Snapshot already made. Load new data first.")
        return None

    # else create them
    if snapshot_csv not in files:
        os.rename("snapshot.csv", dir_fmt + "snapshot.csv")
    if snapshot_json not in files:
        os.rename("snapshot.json", dir_fmt + "snapshot.json")

    # clear the cache
    clear_cache()

    # return formatted directory
    return dir_fmt


def make_snapshot(logs: dict):
    """
    Accepts formatted logs from read_logs
    and creates/updates snapshot.csv & snapshot.json
    """
    # list of dataframes combine into final_df
    new_logs = []
    # for each snapshot in the logs dict
    for snapshot in logs.keys():
        # get the snapshot's dataframe
        new_log = logs[snapshot].reset_index(drop=True)
        # then append to new_logs
        new_logs.append(new_log)

    # if new_logs exist...
    logs_df = None
    if len(new_logs) > 0:
        # if more than 1 new_log...
        if len(new_logs) > 1:
            # concat to 1 dataframe
            logs_df = pd.concat(new_logs)

        # if only 1 new log...
        else:
            # logs_df = single new_log
            logs_df = new_logs[0]

    # if snapshots csv already exists...
    # to be used as the returned DataFrame
    final_df = None

    # if new_logs...
    if logs_df is not None:
        print("Making snapshot...")

        # if snapshots file exists
        if os.path.exists("snapshot.csv"):
            # combine new logs with existing
            existing = pd.read_csv("snapshot.csv").drop(columns=["Unnamed: 0"])
            # then set final_df to combined frame
            final_df = pd.concat([existing, logs_df]).reset_index(drop=True)

        # else (if snapshots file not found)
        else:
            # initialize snapshots file
            final_df = pd.concat(new_logs).reset_index(drop=True)

        # ensure dtypes
        final_df["snapshot"] = final_df["snapshot"].astype("str")
        final_df["path_id"].astype("str")

        # prefix the path_ids with snapshot_id
        final_df["path_id"] = final_df["snapshot"] + "_" + final_df["path_id"]

        # create snapshot files
        final_df.to_csv("snapshot.csv")
        final_df.to_json("snapshot.json", orient="columns")
