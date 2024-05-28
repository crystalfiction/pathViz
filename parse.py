"""
    Parses logs written by dfhack/scripts/logPaths
"""

import os
import pandas as pd
import numpy as np
import math


def read_logs(dir):
    # define scriptLog
    scriptLog = []

    # get the logNames
    logNames = os.listdir(dir)
    # if no logs, break
    if len(logNames) == 0:
        return None

    # dict of logs
    logData = {}

    # if logFiles exist...
    if len(logNames) > 0:
        # for each log...
        for log in logNames:
            if not test_log(log):
                # add entry to logData dict as DataFrame
                snapshotName = log.replace(".txt", "")
                logDf = pd.read_csv(dir + log, header=None, index_col=False)
                logDf = logDf.rename(
                    columns={0: "path_id", 1: "path_goal", 2: "x", 3: "y", 4: "z"}
                )
                logDf["snapshot"] = snapshotName
                logData[snapshotName] = logDf
                logDf["z"] = logDf["z"].apply(math.floor)

                # push to scriptLog to document updates
                scriptLog.append(log)

    print(str(len(scriptLog)) + " new logs found...")

    # if scriptLog is not empty
    if len(scriptLog) > 0:
        # loop through scriptLog...
        with open("scriptLog.txt", "a") as f:
            print("Writing data file names to cache...")
            for logName in scriptLog:
                f.write(logName + "\n")

        # if new scripts, returns dict of logData DF
        return logData
    else:
        # if no new scripts, returns None
        return None


def test_log(log):
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


def make_snapshots(logs):
    print("Making snapshots...")

    new_logs = []
    # make it from passed logs
    for logName in logs.keys():
        new_log = logs[logName].reset_index(drop=True)
        new_logs.append(new_log)

    # flatten new_logs to logs_df
    if len(new_logs) > 1:
        logs_df = pd.concat(new_logs)
    else:
        logs_df = new_logs[0]

    # if snapshots csv exists
    existing = None
    final_df = None
    if os.path.exists("snapshots.csv"):
        # concat with existing
        existing = pd.read_csv("snapshots.csv").drop(columns=["Unnamed: 0"])
        final_df = pd.concat([existing, logs_df]).reset_index(drop=True)
    else:
        # set final_df to new_logs
        final_df = pd.concat(new_logs).reset_index(drop=True)

    # create snapshot files
    final_df.to_csv("snapshots.csv")
    final_df.to_json("snapshots.json", orient="records")


def normalize_cols(df):
    numerics = ["x", "y", "z"]
    for n in numerics:
        # normalization
        df[n] = (df[n] - df[n].min()) / (df[n].max() - df[n].min())

    # returns normalized dataframe
    return df


def parse_logs(dir):
    print("Parsing logs...")

    # read the logs
    logData = read_logs(dir)
    if logData is not None:
        # snapshot logData to 'parsed' dir
        make_snapshots(logData)
    else:
        print("No new logs found.")
