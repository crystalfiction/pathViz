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

1. 


## Usage

