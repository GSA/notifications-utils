# notifications-utils

This is the shared Python code for the Notiy.gov applications.  It standardizes
how to do logging, rendering message templates, parsing spreadsheets, talking to
external services, and more.

Our other repositories are:

- [notifications-admin](https://github.com/GSA/notifications-admin)
- [notifications-utils](https://github.com/GSA/notifications-utils)
- [us-notify-compliance](https://github.com/GSA/us-notify-compliance/)
- [notify-python-demo](https://github.com/GSA/notify-python-demo)

## Before You Start

You will need the following items:

- Admin priviliges and SSH access on your machine; you may need to work with
  your organization's IT support staff if you're not sure or don't currently
  have this access.

**NOTE: If you've set up the API project, you will have most of the project prerequisites installed already.**

These instructions are modified and slightly simplified from the
[Notify.gov API set up instructions](https://github.com/GSA/notifications-api#before-you-start);
they're tailored specifically for this project.

## Local Environment Setup

This project is currently set up as a Python 3.9.x-based module.

These instructions will walk you through how to set your machine up with all of
the required tools for this project.

### Project Pre-Requisite Setup

On MacOS, using [Homebrew](https://brew.sh/) for package management is highly
recommended. This helps avoid some known installation issues. Start by following
the installation instructions on the Homebrew homepage.

**Note:** You will also need Xcode or the Xcode Command Line Tools installed. The
quickest way to do this is is by installing the command line tools in the shell:

```sh
xcode-select –-install
```

#### Homebrew Setup

If this is your first time installing Homebrew on your machine, you may need to
add its binaries to your system's `$PATH` environment variable so that you can
use the `brew` command. Try running `brew help` to see if Homebrew is
recognized and runs properly. If that fails, then you'll need to add a
configuration line to wherever your `$PATH` environment variable is set.

Your system `$PATH` environment variable is likely set in one of these
locations:

For BASH shells:
- `~/.bashrc`
- `~/.bash_profile`
- `~/.profile`

For ZSH shells:
- `~/.zshrc`
- `~/.zprofile`

There may be different files that you need to modify for other shell
environments.

Which file you need to modify depends on whether or not you are running an
interactive shell or a login shell
(see [this Stack Overflow post](https://stackoverflow.com/questions/18186929/what-are-the-differences-between-a-login-shell-and-interactive-shell)
for an explanation of the differences).  If you're still not sure, please ask
the team for help!

Once you determine which file you'll need to modify, add these lines before any
lines that add or modify the `$PATH` environment variable; near or at the top
of the file is appropriate:

```sh
# Homebrew setup
eval "$(/opt/homebrew/bin/brew shellenv)"
```

This will make sure Homebrew gets setup correctly. Once you make these changes,
either start a new shell session or source the file
(`source ~/.FILE-YOU-MODIFIED`) you modified to have your system recognize the
changes.

Verify that Homebrew is now working by trying to run `brew help` again.

### System-Level Package Installation

There are several packages you will need to install for your system in order to
get the app running (and these are good to have in general for any software
development).

Start off with these packages since they're quick and don't require additional
configuration after installation to get working out of the box:

- [jq](https://stedolan.github.io/jq/) - for working with JSON in the command
  line
- [git](https://git-scm.com/) - for version control management
- [vim](https://www.vim.org/) - for editing files more easily in the command
  line
- [wget](https://www.gnu.org/software/wget/) - for retrieving files in the
  command line

You can install them by running the following:

```sh
brew install jq git vim wget
```

#### Python Installation

Now we're going to install a tool to help us manage Python versions and
virtual environments on our system.  First, we'll install
[pyenv](https://github.com/pyenv/pyenv) and one of its plugins,
[pyenv-virtualenv](https://github.com/pyenv/pyenv-virtualenv), with Homebrew:

```sh
brew install pyenv pyenv-virtualenv
```

When these finish installing, you'll need to make another adjustment in the
file that you adjusted for your `$PATH` environment variable and Homebrew's
setup. Open the file, and add these lines to it:

```
# pyenv setup
export PYENV_ROOT="$HOME/.pyenv"
command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
```

Once again, start a new shell session or source the file in your current shell
session to make the changes take effect.

Now we're ready to install the Python version we need with `pyenv`, like so:

```sh
pyenv install 3.12
```

This will install the latest version of Python 3.12.

_NOTE: This project currently runs on Python 3.12.x._

#### Python Dependency Installation

Lastly, we need to install the tool we use to manage Python dependencies within
the project, which is [poetry](https://python-poetry.org/).

Visit the
[official installer instructions page](https://python-poetry.org/docs/#installing-with-the-official-installer)
and follow the steps to install Poetry directly with the script.

This will ensure `poetry` doesn't conflict with any project virtual environments
and can update itself properly.

### First-Time Project Setup

Once all of pre-requisites for the project are installed and you have a
cloud.gov account, you can now set up the API project and get things running
locally!

First, clone the respository in the directory of your choosing on your machine:

```sh
git clone git@github.com:GSA/notifications-utils.git
```

Now go into the project directory (`notifications-utils` by default), create a
virtual environment, and set the local Python version to point to the virtual
environment (assumes version Python `3.12.2` is what is installed on your
machine):

```sh
cd notifications-utils
pyenv virtualenv 3.12.2 notify-utils
pyenv local notify-utils
```

_If you're not sure which version of Python was installed with `pyenv`, you can check by running `pyenv versions` and it'll list everything available currently._

## Switching to different environment

Once all of pre-requisites for the project are installed and to switch to newer environment with newer python version follow the below steps to create new virtual environment.

First install the newer Python version we need with `pyenv`, (say the planned upgrade to 3.12) like so :

```sh
pyenv install 3.12
```

Now go into the project directory (`notifications-api` by default), create a
virtual environment, and set the local Python version to point to the virtual
environment (assumes version Python `3.12.2` is what is installed on your
machine):

```sh
cd notifications-api
pyenv virtualenv 3.12.2 notify-utils-upgrade
pyenv local notify-utils-upgrade
```

_If you're not sure which version of Python was installed with `pyenv`, you can check by running `pyenv versions` and it'll list everything available currently.You can deactivate the current environment by running `source deactivate` or `deactivate`.Close the terminal and reopen a new terminal should show the newer virtual environment._
_You can get version ,executable, and other details for this environment by running `poetry env info`._

## Running the Project and Routine Maintenance

The first time you run the project you'll need to run the project setup from the
root project directory:

```sh
make bootstrap
```

This command is handled by the `Makefile` file in the root project directory, as
are a few others.

_NOTE: You'll want to occasionally run `make bootstrap` to keep your project up-to-date, especially when there are dependency updates._

## Testing the library

You can run tests for this library with the following command:

```sh
make test
```

## Git Hooks

We're using [`pre-commit`](https://pre-commit.com/) to manage hooks in order to
automate common tasks or easily-missed cleanup. It's installed as part of
`make bootstrap` and is limited to this project's virtualenv.

To run the hooks in advance of a `git` operation, use
`poetry run pre-commit run`. For running across the whole codebase (useful after
adding a new hook), use `poetry run pre-commit run --all-files`.

The configuration is stored in `.pre-commit-config.yaml`. In that config, there
are links to the repos from which the hooks are pulled, so hop through there if
ou want a detailed description of what each one is doing.

We do not maintain any hooks in this repository.

## To update the version of this library

We follow the
[Semantic Versioning](https://semver.org/#summary) principles:

>Given a version number MAJOR.MINOR.PATCH, increment the:
>
>MAJOR version when you make incompatible API changes
>MINOR version when you add functionality in a backward compatible manner
>PATCH version when you make backward compatible bug fixes

You'll need to modify two files with matching version numbers:

- Line 3 in `pyproject.toml`
- Line 11 in `setup.py` (this will be deprecated in the near future)

Once you finish making these adjustments, commit the changes and create a new
Pull Request (or add them to an existing one) for review and acceptance. This
will make the new version available for the other repos to consume.

## Python Dependency Management

We're using [`Poetry`](https://python-poetry.org/) for managing our Python
dependencies and local virtual environments. When it comes to managing the
Python dependencies, there are a couple of things to bear in mind.

For situations where you manually manipulate the `pyproject.toml` file, you
should use the `make py-lock` command to sync the `poetry.lock` file. This will
ensure that you don't inadvertently bring in other transitive dependency updates
that have not been fully tested with the project yet.

If you're just trying to update a dependency to a newer (or the latest) version,
you should let Poetry take care of that for you by running the following:

```sh
poetry update <dependency> [<dependency>...]
```

You can specify more than one dependency together. With this command, Poetry
will do the following for you:

- Find the latest compatible version(s) of the specified dependency/dependencies
- Install the new versions
- Update and sync the `poetry.lock` file

In either situation, once you are finished and have verified the dependency
changes are working, please be sure to commit both the `pyproject.toml` and
`poetry.lock` files.

## Known Installation Issues

### Python Installation Errors

On M1 Macs, if you get a `fatal error: 'Python.h' file not found` message, try a
different method of installing Python. The recommended approach is to use
[`pyenv`](https://github.com/pyenv/pyenv), as noted above in the installation
instructions.

If you're using PyCharm for Python development, we've noticed some quirkiness
with the IDE and the interaction between Poetry and virtual environment
management that could cause a variety of problems to come up during project
setup and dependency management. Other tools, such as Visual Studio Code, have
proven to be a smoother experience for folks.

## License && public domain

Work in
[commit `a86d365`](https://github.com/GSA/notifications-utils/commit/a86d365009da4aaefc27b38a1b444b72aee1efdd)
is licensed by the UK government under the MIT license. Work after that commit
is in the worldwide public domain. See [LICENSE.md](./LICENSE.md) for more
information.

## Contributing

As stated in [CONTRIBUTING.md](CONTRIBUTING.md), all contributions to this
project will be released under the CC0 dedication. By submitting a pull request,
you are agreeing to comply with this waiver of copyright interest.
