# Replay Rules Engine

The Replay Rules Engine is a piece of software which allows for a set of rules to be created which affect playback of URLs in the Wayback Machine. These effects can be to block a playback, allow a playback, or modify the playback contents before playing back the request.

## Running

The project can be run with `make run`, which will ensure that dependencies are installed before running the Django server. The Makefile assumes a virtualenv location of `venv`; if you do not wish to use this location, you will just need to install the dependencies manually in your virtualenv with `pip install -r requirements.txt`.

The rules engine is built for Python 3.

## Developing

There are two make targets of note: `make test` runs all tests via Django's test command and then computes coverage, and `make lint` runs flake8 on the project; `make check` runs both tests and lint. If you add an app via `./manage.py startapp <appname>`, make sure to add that appname to the `--source` flag of the `coverage run` command in the Makefile.

## License

Rules engine for interacting with Wayback Machine playbacks
Copyright &copy; 2018 Internet Archive

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
