# install pipenv
pip install pipenv

# install dependencies
pipenv install

# install node dependencies
Set-Location gui && npm install

# start gui in pipenv shell
Set-Location .. && pipenv run python gui.py