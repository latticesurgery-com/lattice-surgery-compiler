# Contributing

## Getting Started

If you just want to get an idea for what this compiler does, check out https://latticesurgery.com.

If you want to contribute, that's great! This guide is for you. For ideas on what to do or to see where we are at in terms of development, check out our [project board](https://github.com/orgs/latticesurgery-com/projects/1). For any questions do not hesitate to contact us at info@latticesurgery.com.

### Create an issue

You can get start getting involved by creating an [issue](https://github.com/latticesurgery-com/lattice-surgery-compiler/issues/new/choose), this can be either a feature request or bug report.

### Code of conduct

Make sure to check out our [code of conduct]((https://github.com/latticesurgery-com/lattice-surgery-compiler/blob/master/CODE_OF_CONDUCT.md).

## Dev Setup

### Set up of the compiler library
In the project's root folder, create pip virtual environment with: 

`$ python -m venv ./venv`

Activate the venv:

`$ source ./venv/bin/activate`

Then install the package in edit mode:

`$ pip install -e .`

Now you can use this venv to work the package, from the command line and in an IDE. Make sure to select the venv you just created as the python environment for the project in your IDE. Note that this only installs the compiler package, not the visualizer.

### Debugging with the UI

The [visualizer's repository](https://github.com/latticesurgery-com/web-ui) contains instructions on how to set up the visualizer's web server (the one at https://latticesurgery.com). Note that by default, the visualizer queries api.latticesurgery.com. So, if you want to test your local changes with the visualizer,  make sure follow the instructions on how to query your local compiler package instead. 

### Style and type correctness

We enforce style with `black`, `flake8` and `isort`, and type correctness with `mypy`. Our CI checks that pull requests meet the requirements checked with these tools. Check the next section for the easiest way to manage these requirements.

#### Pre commit hooks
 Pre commit-hooks run type and style checks before every commit. Useful to avoid having to wait for feedback from CI and taking some load off of our pipelines.

Set up instructions:
* `pip install pre-commit` and then `pre-commit install` 
* To run: `pre-commit run` or just `git commit ...`, the first time running will take a while since it has to clone all the repos specified in `pre-commit-config.yaml`

If want to run against all files (good for first run to test things out): `pre-commit run -a`. 

### Running tests
To run the entire testsuite:
``` ```
 
To run a particular tests:
``` ```
