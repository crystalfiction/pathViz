"""
    Module for reading, parsing, and visualizing DF path data
"""

import os
import time
import typer
from enum import Enum

import pandas as pd
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from dotenv import load_dotenv

from parse import parse_logs
from visualize import make_visuals


load_dotenv()

DATA_DIR = os.getenv("DATA_DIR")
OUTPUT_DIR = os.getenv("OUTPUT_DIR")
SCRIPT_LOG = "scriptLog.txt"


class OnWatch:
    """
    Starts monitoring changes @ data_dir
    """

    watch_dir = DATA_DIR

    def __init__(self):
        self.observer = Observer()

    def run(self):
        event_handler = Handler()
        self.observer.schedule(event_handler, self.watch_dir)
        self.observer.start()
        try:
            while True:
                time.sleep(5)
        except KeyboardInterrupt:
            self.observer.stop()
            print("Stopped monitoring data changes.")

        self.observer.join()


class Handler(FileSystemEventHandler):
    """
    Checks for FileSystem events
    """

    @staticmethod
    def on_any_event(event):
        if event.is_directory:
            return None
        elif event.event_type == "created":
            pass
        elif event.event_type == "modified":
            pass


def clear_cache():
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


def save_data(mode, data):
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
        elif mode == "stats":
            content = pd.merge(data[0], data[1], on=data[0].index)
            content = content.rename(columns={"key_0": "snapshot"})
            content = content.set_index("snapshot")
            content.to_csv(OUTPUT_DIR + mode + fileName + ".csv")
    else:
        return print("File already exists...")


def test_logs():
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


# define the mode choices
class Modes(str, Enum):
    load = "load"
    viz = "viz"
    clear = "clear"


def main(mode: Modes):
    # ensure directories exist
    if not os.path.exists(DATA_DIR):
        os.mkdir(DATA_DIR)

    if not os.path.exists(OUTPUT_DIR):
        os.mkdir(OUTPUT_DIR)

    # test args
    if mode == "load":
        # if load mode...
        # cleanup any empty logs
        test_logs()

        # parse logs
        parse_logs(DATA_DIR)

    elif mode == "viz":
        # if viz mode
        fig = make_visuals()

        # if save flagged
        doSave = typer.prompt("Export to file? [y/n]")
        if doSave.lower() != "n":
            save_data(mode, fig)

        # show fig regardless
        if fig is not None:
            fig.show()
        else:
            return print("No data found... please 'import' first.")

    elif mode == "clear":
        # if clear mode
        clear_cache()


if __name__ == "__main__":
    if DATA_DIR is None or OUTPUT_DIR is None:
        print("Please specify your data & output directories in the .env file.")
    else:
        typer.run(main)
