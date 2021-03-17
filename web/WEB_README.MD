### Overview

This project has been switched from Pyramid to Django web framework.

It also has undergone a shift in philophy over managing its environment and dependencies.
Pipenv is being use to manage dependencies.

##### Virtual Environment
```
pip install pipenv # installs pipenv

cd path/to/project_root
pipenv shell # creates and/or enables project's virtual environment
pipenv install -r requirements.txt # reads requirements.txt and installs to virtual environment

pipenv install <PACKAGE> # to install arbitrary python package
```
##### Web server

```
pipenv shell # to enable virtual environment
cd ./web/
python manage.py runserver # serves on localhost:8000

alternatively, run ./deploy.sh which creates/activates environment and installs all dependencies from requirements.txt, then runs server in debug mode
```
