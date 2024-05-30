"""
    Parses logs written by dfhack/scripts/logPaths
"""

import os
import pandas as pd


GOAL_KEY = {}


def parse_logs(dir: str):
    """
    Parse logs in the passed dir,
    then makes aggregated snapshots files.
    """
    print("Parsing logs...")

    # read the logs
    logData = read_logs(dir)
    # if new logs exist...
    if logData is not None:
        # make snapshots of the logData
        make_snapshots(logData)
    else:
        # else, raise KeyError
        raise KeyError()


def read_logs(dir: str):
    """
    Reads logs in the passed dir

    Returns dict where {key: snapshotName, value: snapshotDataFrame
    """

    # list to append new scriptLog entries
    scriptLog = []

    # read logNames from passed dir
    logNames = os.listdir(dir)
    # if no logs exist...
    if len(logNames) == 0:
        # return None before processing
        return None

    # dict of logs
    # key: snapshotName, value: logDf
    logData = {}

    # if logFiles exist...
    if len(logNames) > 0:
        # for each log...
        for log in logNames:
            # test if log as already been parsed...
            if not test_log(log):
                # if not...

                # remove the file suffix
                snapshotName = log.replace(".txt", "")
                # read the log file to logDf as DataFrame
                logDf = pd.read_csv(dir + log, header=None, index_col=False)
                # format logdf
                logDf = logDf.rename(
                    columns={0: "path_id", 1: "path_goal", 2: "x", 3: "y", 4: "z"}
                )
                # replace snapshot column with formatted name snapshotName
                logDf["snapshot"] = snapshotName

                # add entry to logData dict with...
                # key: snapshotName, value: logDf
                logData[snapshotName] = logDf

                # append the un-formatted log file name to scriptLog
                scriptLog.append(log)

    # print the number of logs currently being processed
    print(str(len(scriptLog)) + " new logs found...")

    # if scriptLog is not empty
    # i.e. if new logs were found
    if len(scriptLog) > 0:
        # open scriptLog.txt...
        with open("scriptLog.txt", "a") as f:
            # print user update
            print("Writing data file names to cache...")
            # for each log name, append to content of scriptLog.txt
            for logName in scriptLog:
                f.write(logName + "\n")

        # returns logData DataFrame
        return logData
    else:
        # if no new logs, return None
        return None


def test_log(log: str):
    """
    Accepts a log, where log = the name of a
    log in data/, and tests if exists in scriptLog.txt

    Returns True if already parsed, else False
    """
    # check if log has already been read
    parsed = False
    with open("scriptLog.txt", "r") as f:
        lines = f.readlines()
        for row in lines:
            if row.find(log) != -1:
                # log name was found
                parsed = True

    # returns True if log exists in scriptLog, else False
    return parsed


def make_snapshots(logs: dict):
    """
    Accepts formatted logs from read_logs
    and creates/updates snapshots.csv & snapshots.json
    """
    print("Making snapshots...")

    # list of dataframes combine into final_df
    new_logs = []
    # for each snapshot in the logs dict
    for snapshot in logs.keys():
        # get the snapshot's dataframe
        new_log = logs[snapshot].reset_index(drop=True)
        # then append to new_logs
        new_logs.append(new_log)

    # if more than one log was passed...
    if len(new_logs) > 1:
        # combine all into one DataFrame
        logs_df = pd.concat(new_logs)
    else:
        # else convert to single DataFrame
        logs_df = new_logs[0]

    # to test whether snapshots file exists
    existing = None
    # to be used as the returned DataFrame
    final_df = None
    # if snapshots csv already exists...
    if os.path.exists("snapshots.csv"):
        # combine new logs with existing
        existing = pd.read_csv("snapshots.csv").drop(columns=["Unnamed: 0"])
        # then set final_df to combined frame
        final_df = pd.concat([existing, logs_df]).reset_index(drop=True)
    else:
        # else set final_df as new_logs
        final_df = pd.concat(new_logs).reset_index(drop=True)

    # ensure dtypes
    final_df["snapshot"] = final_df["snapshot"].astype("str")

    # prefix the path_ids with snapshot_id
    final_df["path_id"] = (
        final_df["snapshot"].astype("str") + "_" + final_df["path_id"].astype("str")
    )

    # create snapshot files
    final_df.to_csv("snapshots.csv")
    final_df.to_json("snapshots.json", orient="records")
