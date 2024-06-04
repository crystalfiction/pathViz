""""
TODO: update readme for gui
TODO: implement CLI options to viz/stats modes
"""

import os
import subprocess
import json
import secrets
from flask import Flask, session, request
from dotenv import load_dotenv

from setup import trySetup
from parse import parse
from visualize import visualize
from stats import get_stats
from snapshot import save_snapshot
from utils import clear_cache, save_data, clean_logs

# load env vars
load_dotenv()

# save env vars
DF_PATH = ""
DATA_DIR = os.getenv("DATA_DIR") + "logs/"
OUTPUT_DIR = os.getenv("OUTPUT_DIR")
SCRIPT_LOG = "scriptLog.txt"
HACK_SCRIPT = "logPaths.lua"

# load flask app
app = Flask(__name__)
KEY = secrets.token_urlsafe(16)
app.secret_key = KEY


@app.route("/api", methods=["POST"])
def api():
    """
    Primary API endpoint
    """
    # if post request...
    if request.method == "POST":
        result = {"status": True, "data": ""}

        mode = request.args.get("mode")
        if mode == "load":
            # if load...
            # cleanup any empty logs...
            clean_logs(DATA_DIR)

            parsed = None
            count = 0
            try:
                # if valid logs exist
                # then parse the logs in DATA_DIR
                parsed, count = parse(DATA_DIR)
            except Exception as err:
                # raise error if error unknown
                result["status"] = False
                result["data"] = "Unkown error occurred while parsing logs"

            # if logs were parsed or data exists
            # save snapshots.json as response data
            f = open("snapshots.json")
            data = json.load(f)
            result["data"] = data
            result["count"] = count
            f.close()
            # flag success
            result["status"] = True

        if mode == "viz":
            # if viz mode...
            # break if no snapshots
            if not os.path.exists("snapshots.csv"):
                result["status"] = False
                result["verbose"] = "No data found, please run load."
                return result

            # call visualize, pass CLI options
            # and save Plotly figure to fig
            g = False
            c = False
            heat = False
            limit = 0
            orient = "btm"
            fig, layout = visualize(g, c, heat, limit, orient)

            # if save option passed...
            # if s:
            #     # save the figure
            #     save_data(OUTPUT_DIR, mode, fig)

            # check that the figure exists...
            if fig is not None:
                # if so, set to result
                result["fig"] = fig.to_json()
                result["layout"] = layout.to_json()

        if mode == "stats":
            # if stats mode...
            # break if no snapshots
            if not os.path.exists("snapshots.csv"):
                result["status"] = False
                result["verbose"] = "No data found, please run load."
                return result

            limit = 0
            orient = "btm"
            stats, verbose = get_stats(limit, orient)

            # save the stats
            save_data(OUTPUT_DIR, mode, stats)
            result["verbose"] = "Stats files generated in the output directory."

        if mode == "snapshot":
            # if snapshot mode...

            # save the current snapshot
            test = save_snapshot(DATA_DIR)
            if test is not None:
                result["verbose"] = "Snapshot saved. See " + test

        if mode == "clear":
            # try to clear the cache
            try:
                # clear the cache
                clear_cache()
                result["verbose"] = "Cleared cache."
            except ValueError:
                # if scriptLog cache is empty
                result["verbose"] = "No data to clear."

        # return result regardless
        return result


@app.route("/setup", methods=["GET", "POST"])
def setup():
    """
    GET: Checks if isSetup in session; skips setup if so
    POST: Calls trySetup() to try and setup the user; returns result status
    """
    # if get request
    if request.method == "GET":
        result = {"status": True, "data": ""}

        # if a dfPath is in the session
        if "dfPath" in session:
            # trySetup with it and return results
            print("Found existing session data...")
            test_dfPath = session["dfPath"]
            result["isSetup"] = trySetup(test_dfPath, DATA_DIR, OUTPUT_DIR, HACK_SCRIPT)
        else:
            # else nothing to do
            result["status"] = False

        return result

    # if post request
    if request.method == "POST":
        result = {"status": True, "data": ""}

        # check if dfPath arg passed
        DF_PATH = request.args.get("dfPath")
        # save to session
        session["dfPath"] = DF_PATH

        # try to set up
        result["isSetup"] = trySetup(DF_PATH, DATA_DIR, OUTPUT_DIR, HACK_SCRIPT)

        # save results to session
        session["status"] = True

        return result


def main():
    """
    Open subprocess for front/backend dev environments,
    connect to same pipe
    """

    # start frontend
    f_end = subprocess.Popen("cd gui && npm start", shell=True)

    # start flask app
    app.run()

    # force kill f_end on exit
    f_end.kill()


if __name__ == "__main__":
    main()
