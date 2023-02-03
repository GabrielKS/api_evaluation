# README
This is my solution to an evaluation given to me. See `test_instructions.md` for details on the assignment.

## Requirements
The project uses Python 3.10 with the Pipenv packaging tool and the Flask, Requests, and Gunicorn libraries.

## Installation
Clone the GitHub repository, `cd` into it, and run `pipenv init` to set up the Python environment and install the necessary libraries. The database will be generated automatically when it is first called for; simply ensure that a file called `errors_database.db` in the repo root can be created.

## Use
To run on a production server, use `run_prod.sh`, which will run a server on port 8000. To run in debug mode, use `run_debug.sh`.

## Testing
A full suite of unit tests is included. These can be run against a local debug server with `run_tests.sh` or against the production server at `http://apieval.gabrielks.com/` with `run_tests_prod.sh`.
