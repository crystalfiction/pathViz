"""
    Module for reading, parsing, and visualizing DF path data
"""

import os
import time
import typer
from enum import Enum

import pandas as pd
from dotenv import load_dotenv
from typing_extensions import Annotated
from plotly.graph_objects import Figure

from parse import parse_logs
from visualize import visualize

# load env vars
load_dotenv()

# save env vars
DATA_DIR = os.getenv("DATA_DIR")
OUTPUT_DIR = os.getenv("OUTPUT_DIR")
SCRIPT_LOG = "scriptLog.txt"


def clear_cache():
    """
    Wipes the contents of logScript.txt
    and removes existing snapshots.csv & snapshots.json
    """
    with open(SCRIPT_LOG, "w") as log:
        # close the log and reset contents
        log.close()

    # remove snapshots
    try:
        os.remove("snapshots.csv")
        os.remove("snapshots.json")
        print("Cleared cache.")
    except:
        print("No snapshots found... please run 'import' first.")


def save_data(mode: str, data: Figure):
    """
    Writes passed 'data' to new file in OUTPUT_DIR
    depending on the passed 'mode'.
        - fileName = {mode}{current_time}.png, i.e. 'viz20240529.png'
    """
    files = []
    # if output dir exists
    if os.path.exists(OUTPUT_DIR):
        # get files
        files = os.listdir(OUTPUT_DIR)
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
            content.write_image(OUTPUT_DIR + mode + fileName + ".png")
    else:
        return print("File already exists...")


def clean_logs():
    """
    Tests whether any blank logs exist in
    the DATA_DIR and removes them
    """
    logs = os.listdir(DATA_DIR)
    # test logs...
    for l in logs:
        logPath = DATA_DIR + l
        test = None
        with open(logPath, "r") as f:
            content = f.readline()
            if content == "":
                test = True

        # if test passed...
        if test is not None:
            # delete the empty log
            os.remove(logPath)


class Modes(str, Enum):
    """
    Defines choices for the 'mode' argument
    """

    load = "load"
    viz = "viz"
    clear = "clear"


def main(
    mode: Modes,
    s: Annotated[bool, typer.Option(help="Save the visual once created.")] = False,
    g: Annotated[bool, typer.Option(help="Group visual by path goal.")] = False,
    c: Annotated[
        bool, typer.Option(help="Generate KMeans clusters per snapshot.")
    ] = False,
    limit: Annotated[
        int, typer.Option(help="Limit the number of snapshots visualized.")
    ] = 0,
    orient: Annotated[
        str, typer.Option(help="How to orient the snapshot limit ['top'|'btm']")
    ] = "btm",
):
    """
    Accepts a 'mode' along with options
        --s: save
        --g: group by goal
        --c: show clusters
        --limit: limit the number of snapshots visualized
        --orient: orient the snapshot limitation by
            'top' (earliest) or 'btm' (latest)
    """
    # ensure directories exist
    if not os.path.exists(DATA_DIR):
        os.mkdir(DATA_DIR)
    if not os.path.exists(OUTPUT_DIR):
        os.mkdir(OUTPUT_DIR)

    # evaluate passed mode
    if mode == "load":
        # if load...

        # cleanup any empty logs...
        clean_logs()

        # then parse the logs in DATA_DIR
        parse_logs(DATA_DIR)

    elif mode == "viz":
        # if viz mode...

        # call visualize, pass CLI options
        # and save Plotly figure to fig
        fig = visualize(g, c, limit, orient)

        # if save option passed...
        if s:
            # save the figure
            save_data(mode, fig)

        # check that the figure exists...
        if fig is not None:
            # if so, show it
            print("Visualizing data...")
            fig.show()
        else:
            # else return error
            return print("No data found... please 'import' first.")

    elif mode == "clear":
        # if clear mode...

        # clear the cache
        clear_cache()


if __name__ == "__main__":
    if DATA_DIR is None or OUTPUT_DIR is None:
        print("Please specify your data & output directories in the .env file.")
    else:
        typer.run(main)
