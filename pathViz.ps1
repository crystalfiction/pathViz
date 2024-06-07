# install pipenv
pip install pipenv

# install dependencies
pipenv install

# prompt for pathViz version
$pV = Read-Host "pathViz version [gui/cli]"

# check input
if ($pV -eq "gui") {
    # install node dependencies
    Set-Location gui && npm install

    # start gui in pipenv shell
    Set-Location .. && pipenv run python gui.py
}
else {
    # start cli in pipenv shell
    pipenv shell -noexit
}