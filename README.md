# pathViz

pathViz was born at the crossroads of data science, game development, and complex simulation algorithms. <u>Its primary goal is to provide an accessible tool for analyzing dwarven path activity in Dwarf Fortress</u>. The purpose is to improve overall understanding of dwarf activity within the context of a player's unique fort structure.

There are existing tools for path analysis, such as `dfhack/unit-path`, which visualizes the path of a single, selected unit using the GUI. This is useful in analyzing individual behaviors, but it doesn't give the full picture of fortress activity...

## Structure

The overall structure of pathViz consists of two parts:
1. `logPaths.lua` - the dfhack script to be run from the ingame dfhack console; housed in `hack/scripts/` of your game directory
   1. logs dwarf paths once every ingame week (currently not configurable)
2. `pathViz/pathViz.py` - a simple, python command-line module for interacting with pathViz

## Setup

<b>Requirements:</b>
- [Python 3.10.11](https://www.python.org/downloads/release/python-31011/)
- [pipenv 2023.12.1](https://pypi.org/project/pipenv/2023.12.1/)

1. Make sure you have the requirements above, as well as the latest version of [pip](https://pypi.org/project/pip/) installed on your system
2. Clone the `pathViz/` repo
3. Open up your command-line and `cd` into the `pathViz` directory, wherever you downloaded it to, then run pipenv w/ `pipenv install pathViz`
   1. This will take a few minutes, while it downloads the relevant python packages.
4. Locate the `logPaths.lua` script, and update the `filePrefix` variable at the top.
   1. Change this value to the location of your `pathViz/data/` directory; in my case it is `C:/Users/rocke/Documents/pathViz/data/`
5. Locate your game directory, then move the `logPaths.lua` script from the `pathViz/` folder to the `/hack/scripts/` sub-directory
   1. This ensures dfhack will recognize this script from the ingame console
6. Locate the `.env` file in `pathViz/`
   1. Change the `DATA_DIR` and `OUTPUT_DIR` environment variables to the relative path of `data/` and `output/` in `pathViz/` respectively; i.e. `DATA_DIR='data/'` and `OUTPUT_DIR='output/`
   2. These variables are useful if you would like to split your data into sub-directories (multiple forts, a/b testing, etc.)
7. Finally, before running any commands, go back to your command-line, make sure its still in the `pathViz/` directory, then run `pipenv shell`


## Usage

The `logPaths.lua` script is enabled through the `dfhack` ingame console. You can enable it by simply entering `enable logPaths`
- Once enabled, once an ingame week, it will log all currently active dwarf paths to the `data/` directory, under the file name `fileName.txt` where `fileName` is the current ingame date

The `pathViz` python app is primarily a command-line tool
- It can be called from your system command-line with the python command `python pathViz.py <mode>`, and currently supports 4 modes...
  - the general workflow is `import > viz/stats > clear`

### Import

`python pathViz.py import`

When `import` mode is selected, pathViz will read through the relevant directories and check for new logs.

*Running other modes before importing will result in errors*

- If new logs are found, it will parse and write them to the `scriptLog.txt` file, which acts as a simple memory cache for `pathViz`
  - Then, it combines all of the parsed logs to a single `snapshots.csv` & `snapshots.json` (depending on your use case)

### Viz

`python pathViz.py viz`

When `viz` mode is selected, pathViz will read any logs created by `import` and generate 3D Scatterplot of your data.

The `-s` flag can be used if you'd like to save your plot to a file: `python pathViz viz -s`.
- The path used for writing this file is `output/` by default, else whatever the `OUTPUT_DIR` environment variable has been set to

### Stats

`python pathViz.py stats`

When `stats` mode is selected, pathViz will generated key stats from your imported data.

`avg_snapshot_distance` - the first stat represents the overall distance between each path for each snapshot
- helpful in determining path efficiency, density, etc.

`avg_snapshot_goal` - the second stat represents the most common `path_goal` for each snapshot.
- acts as a classifier for each path, providing a useful metric for roughly determining dwarf activity when the snapshot was made.

Stats can also be saved with the `-s` flag: `python pathViz.py stats -s`
- this will write the generated stats to a `.csv` file in your `output/` folder

### Clear

`python pathViz.py clear`

When `clear` mode is selected, pathViz will wipe all existing logs from memory (removes `snapshots` files and reverts `scriptLog.txt`).
- <u>This does not delete the logs generated by `logPaths.lua`</u>, in case you'd like to backup existing logs in a different folder before importing new logs