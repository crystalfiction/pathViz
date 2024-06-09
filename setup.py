import os
import re
import shutil


def trySetup(dfPath, dataDir, outputDir, hackScript):
    """"""
    # try to create the directories
    try:
        root_data_dir = dataDir.replace("logs/", "")
        if not os.path.exists(root_data_dir):
            os.mkdir(root_data_dir)
        if not os.path.exists(dataDir):
            os.mkdir(dataDir)
        # outputDir
        if not os.path.exists(outputDir):
            os.mkdir(outputDir)
        # scriptLog.txt
        if not os.path.exists("scriptLog.txt"):
            with open("scriptLog.txt", "w") as f:
                f.close()

    except Exception as err:
        return f"Error creating pathViz directories: {err}"

    # read the file
    lines = None
    with open(hackScript, "r") as f:
        lines = f.readlines()

    # loop through the lines
    newLines = []
    for line in lines:
        # and find the filePrefix variable
        found = "local filePrefix" in line
        if found:
            data_path = os.getcwd() + "\\" + dataDir.replace("/", "\\")
            prefix = data_path.replace("\\", "\\\\")
            newLine = re.sub(r"(?<=\").*(?=\")", re.escape(prefix), str(line))

            # if the same directory
            if newLine == re.escape(prefix):
                # return
                print("logPaths.lua already updated...")
                return None
            else:
                newLines.append(newLine)
        else:
            newLines.append(line)

    # if no changes to be made
    if lines != newLines:
        # write the changes
        with open(hackScript, "w") as f:
            for line in newLines:
                f.write(line)

    # relocate the script
    dfhack_dir = "\\hack\\scripts\\"
    fmt_path = dfPath + dfhack_dir + hackScript
    # copy contents to destination file,
    # regardless of if hackScript exists already
    shutil.copyfile(hackScript, fmt_path)

    # if no errors
    return True
