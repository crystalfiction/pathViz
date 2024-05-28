# pathViz

pathViz was born at the crossroads of data science, game development, and complex simulation algorithms. <u>Its primary goal is to provide an accessible tool for analyzing dwarven path activity in Dwarf Fortress</u>. The purpose is to improve overall understanding of dwarf activity within the context of a player's unique fort structure.

There are existing tools for path analysis, such as `dfhack/unit-path`, which visualizes the path of a single, selected unit using the GUI. This is useful in analyzing individual behaviors, but it doesn't give the full picture of fortress activity...

## Structure

The overall structure of pathViz consists of two parts:
1. `logPaths.lua` - the dfhack script to be run from the ingame dfhack console; housed in `hack/scripts/` of your game directory
   1. logs dwarf paths once every ingame week (currently not configurable)
2. `pathViz/pathViz.py` - a simple, python command-line module for interacting with pathViz

## Screenshots

Here are a few screenshots demonstrating usage, using a new fort I started as the subject. The screenshots were logged over the first game year...

![topDown_overlaid](images/topDown_overlaid.png)
A top-down view, roughly overlaid with the game screen for reference.

![newfort_y1](images/newFort_y1.png)
The top down view with the visual isolated.

![newFort_y1_3d](images/newFort_y1_3d.png)
A skewed, 3D angle for scale.

![newFort_y1_zoomed](images/newFort_y1_zoomed.png)
The central structure, zoomed in. We can see some high-traffic areas beginning to form (the ovular structure at the top is my trade floor), as well as my services and workshop floors towards the lower z-levels.

## Setup

<b>Requirements:</b>
- [Python 3.10.11](https://www.python.org/downloads/release/python-31011/)
- [pipenv 2023.12.1](https://pypi.org/project/pipenv/2023.12.1/)

1. Ensure you have the requirements, as well as the latest version of [pip](https://pypi.org/project/pip/) installed and accessible on your PATH.
2. Download the latest release of pathViz to wherever, in my case I just use "C:\Users\rocke\Documents\pathViz"
   1. <i>Make sure this is not located on a cloud drive, or you will most likely encounter file permissions errors due to reads/writes to the system.</i>
3. Open your terminal and `cd` into `pathViz/`, then run `pipenv install` to install pathViz's package dependencies (this may take a few minutes)
   1. If you have issues with `pipenv`, they have detailed documentation around common troubleshooting
4. Once packages are installed, run `pipenv shell` to activate the virtual environment
5. Optional:
   1. Locate the `pathViz/.env` file and open it. This file tells pathViz which directories to use when parsing and outputing log data.
      1. By default, both `DATA_DIR` (where the dfhack script logs path data to) and `OUTPUT_DIR` (where `pathViz` logs saved data) are set to `data/` and `output/`, respectively, but feel free to set them wherever, as long as they are in the `pathViz/` directory.
6. Locate the `logPaths.lua` file and open it. Locate the `filePrefix` variable at the top, and change it to `pathViz`'s data directory
   1. if `.env` was left untouched, this will be the system path to the `pathViz/` directory, or in my case `C:\\Users\\rocke\\Documents\\pathViz\\data\\` (make sure to escape your backslashes, unless you know what you're doing)
7. Move the `logPaths.lua` file to the `hack/scripts/` sub-directory in your Dwarf Fortress game folder (`Dwarf Fortress/hack/scripts/`)
   1. If your game is already running, open the dfhack console with `ctrl-shift-p` and run `:lua require('script-manager').reload()` to force dfhack to recognize new scripts.


## Usage

Now that everything is in the right place, here's how to get things up and running:
1. Go back to the game, open the dfhack console again, and run `enable logPaths`
   1. This will enable the script to start logging paths every ingame week, as well as write the paths currently active when the script was enabled.
1. Once you have some data, you can check out the `modes` for usage below
<br><br>

<b>load</b> - `python pathViz.py load`

Loads data existing in the `pathViz/{DATA_DIR}/` sub-directory, then creates a combined `snapshots.csv` file in the root directory. `snapshots.csv` is generated via `pandas.<DataFrame>.to_csv()`.

- `DATA_DIR`: environment variable representing the relative path to the pathViz data directory; set from the `.env` file
- Logs the parsed scripts to `scriptLog.txt`, which acts as a simple memory cache
<br><br>

<b>viz</b> - `python pathViz.py viz`

Reads data existing in the `pathViz/{DATA_DIR}/` sub-directory, then generates a `Plotly` visual from the loaded path data.

- Once run, will prompt asking whether to export the visual to the set `OUTPUT_DIR` directory, set in the `.env` file.
<br><br>

<b>clear</b> - `python pathViz.py clear`

Clears data loaded to the app, preserving the log files in the set `DATA_DIR` directory. Logs are intentionally left persistent for more control over user-defined path data organization.
- *This means you will <b>manually</b> have to relocate the log files if you don't want them to be considered in the next `load` call.*
