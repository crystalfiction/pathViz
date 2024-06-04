# install pipenv
pipenv install

# prompt for pathViz version
$pV = Read-Host "pathViz version [gui/cli]"

# check input
if ($pV -eq "gui") {
    # start gui in pipenv shell
    pipenv run python gui.py
} else {
    # start cli in pipenv shell
    pipenv shell -noexit
}