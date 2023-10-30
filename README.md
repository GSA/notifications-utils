# notifications-utils

Shared Python code for US Notify applications. Standardizes how to do logging, rendering message templates, parsing spreadsheets, talking to external services and more.

## Setting up

You must install [`poetry`](https://python-poetry.org/docs/#installation) to work on this library.

If you're using Homebrew, you can `brew install poetry` to get up and running quickly.

### Python version

This repo is written in Python 3.

## To test the library

```
# install dependencies, etc.
make bootstrap

# run the tests
make test
```

## To sync your poetry.lock file after manual pyproject.toml edits

```
# run the make command
make py-lock
```

This will ensure that the transitive dependencies won't be modified and remain compatible.

## To update a Python dependency

```
# use poetry to manage the dependencies
poetry update <dependency> [<dependency>...]
```

This will tell Poetry to do the following:

- Look for the latest compatible version of the dependency/dependencies
- Install the version(s) it finds
- Update and sync the poetry.lock file

## License && public domain

Work in [commit `a86d365`](https://github.com/GSA/notifications-utils/commit/a86d365009da4aaefc27b38a1b444b72aee1efdd) is licensed by the UK government under the MIT license. Work after that commit is in the worldwide public domain. See [LICENSE.md](./LICENSE.md) for more information.

## Contributing

As stated in [CONTRIBUTING.md](CONTRIBUTING.md), all contributions to this project will be released under the CC0 dedication. By submitting a pull request, you are agreeing to comply with this waiver of copyright interest.
