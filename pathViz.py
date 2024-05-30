"""
    Module for reading, parsing, and visualizing DF path data
"""

import os
import typer
from enum import Enum

import pandas as pd
from dotenv import load_dotenv
from typing_extensions import Annotated

from parse import parse_logs
from visualize import visualize
from utils import clear_cache, save_data, clean_logs

# load env vars
load_dotenv()

# save env vars
DATA_DIR = os.getenv("DATA_DIR")
OUTPUT_DIR = os.getenv("OUTPUT_DIR")


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
    # ensure directories exist
    if not os.path.exists(DATA_DIR):
        os.mkdir(DATA_DIR)
    if not os.path.exists(OUTPUT_DIR):
        os.mkdir(OUTPUT_DIR)

    # evaluate passed mode
    if mode == "load":
        # if load...

        # cleanup any empty logs...
        clean_logs(DATA_DIR)

        # then parse the logs in DATA_DIR
        parse_logs(DATA_DIR)

        # print update
        print("Done.")

    elif mode == "viz":
        # if viz mode...

        # call visualize, pass CLI options
        # and save Plotly figure to fig
        fig = visualize(g, c, heat, limit, orient)

        # if save option passed...
        if s:
            # save the figure
            save_data(OUTPUT_DIR, mode, fig)

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

        # print update
        print("Done.")


if __name__ == "__main__":
    if DATA_DIR is None or OUTPUT_DIR is None:
        print("Please specify your data & output directories in the .env file.")
    else:
        typer.run(main)
