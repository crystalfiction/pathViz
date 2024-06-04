"""
    Parses logs written by dfhack/scripts/logPaths
"""

import os
import time
import pandas as pd
from rich.progress import track

from snapshot import make_snapshot


GOAL_KEY = {}


def parse(dir: str):
    """
    Parse logs in the passed dir,
    then makes aggregated snapshots files.

    Returns logData: dict, logCount: int, regardless of parsing results
    """
    # read the logs
    logData, logCount = read_logs(dir)
    # make snapshots of the logData
    make_snapshot(logData)

    return logData, logCount


def read_logs(dir: str):
    """
    Reads logs in the passed dir

    Returns tuple ({key: snapshotName, value: snapshotDataFrame}, logCount)
    """

    # list to append new scriptLog entries
    scriptLog = []

    # read logNames from passed dir
    logNames = os.listdir(dir)

    # dict of logs
    # key: snapshotName, value: logDf
    logData = {}
    logCount = 0

    # if logFiles exist...
    if len(logNames) > 0:
        # for each log...
        total = 0
        for log in track(logNames, description="Parsing logs..."):
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

                # increment progress bar
                time.sleep(0.01)
                total += 1

        logCount += total

        # print the number of logs currently being processed
        print(f"Processed {total} new logs...")

    # if new logs found, update user
    if logCount > 0:
        print("Writing data file names to cache...")

    # open scriptLog.txt...
    with open("scriptLog.txt", "a") as f:
        # for each log name, append to content of scriptLog.txt
        for logName in scriptLog:
            f.write(logName + "\n")

    # returns logData DataFrame
    return logData, logCount


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
