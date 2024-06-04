"""
    Module for reading, parsing, and visualizing DF path data
"""

import os
import typer
from enum import Enum
from dotenv import load_dotenv
from typing_extensions import Annotated

from parse import parse
from visualize import visualize
from stats import get_stats
from utils import clear_cache, save_data, clean_logs
from setup import trySetup

# load env vars
load_dotenv()

# save env vars
DF_PATH = os.getenv("DF_PATH")
DATA_DIR = os.getenv("DATA_DIR")
OUTPUT_DIR = os.getenv("OUTPUT_DIR")
SCRIPT_LOG = "scriptLog.txt"
HACK_SCRIPT = "logPaths.lua"


class Modes(str, Enum):
    """
    Defines choices for the 'mode' argument
    """

    load = "load"
    viz = "viz"
    clear = "clear"
    stats = "stats"


def CLI(
    mode: Modes,
    s: Annotated[bool, typer.Option(help="Save the visual or stats.")] = False,
    g: Annotated[bool, typer.Option(help="Group visual by path goal.")] = False,
    c: Annotated[
        bool, typer.Option(help="Generate KMeans clusters per snapshot.")
    ] = False,
    heat: Annotated[
        bool, typer.Option(help="Generate a time-dependent heatmap.")
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
    # ensure valid dfPath
    if DF_PATH:
        if not os.path.exists(DF_PATH):
            return print("Could not locate the provided DF_PATH directory.")
    else:
        pass

    # try to setup files
    try:
        result = trySetup(DF_PATH, DATA_DIR, OUTPUT_DIR, HACK_SCRIPT)
    except Exception as err:
        return print(f"Error setting up files {err}")

    # evaluate passed mode
    if mode == "load":
        # if load...

        # cleanup any empty logs...
        clean_logs(DATA_DIR)

        # try to parse the logs...
        try:
            # if valid logs exist
            # then parse the logs in DATA_DIR
            logData, logNames = parse(DATA_DIR)
            # print update
            print("Done.")
        except KeyError:
            # else no valid logs exist in DATA_DIR
            return print("No valid data exists in the provided DATA_DIR.")

    elif mode == "viz":
        # if viz mode...

        # break if no snapshots
        if not os.path.exists("snapshots.csv"):
            return print("No data loaded, please run load.")

        # call visualize, pass CLI options
        # and save Plotly figure to fig
        fig, layout = visualize(g, c, heat, limit, orient)

        # if save option passed...
        if s:
            # save the figure
            save_data(OUTPUT_DIR, mode, fig)

        # check that the figure exists...
        if fig is not None:
            # if so, show it
            print("Visualizing data...")
            fig.show()

    elif mode == "stats":
        # if stats mode...

        # break if no snapshots
        if not os.path.exists("snapshots.csv"):
            return print("No data loaded, please run load.")

        stats, verbose = get_stats(limit, orient)

        # if save option passed...
        if s:
            # save the stats
            save_data(OUTPUT_DIR, mode, stats)

    elif mode == "clear":
        # if clear mode...

        # try to clear the cache
        try:
            # clear the cache
            clear_cache()
            # print update
            print("Done.")
        except ValueError:
            # if scriptLog cache is empty
            return print("No data to clear.")


if __name__ == "__main__":
    typer.run(CLI)
