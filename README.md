kort-to-osm
===========

[![Build Status](https://travis-ci.org/kort/kort-to-osm.png?branch=develop)](https://travis-ci.org/kort/kort-to-osm)

Transfer changes from Kort to OpenStreetMap.

## Installation

* Copy setup.dist.cfg to setup.cfg and adapt the values
* Copy logging.dist.yml to logging.yml and adapt the values
* Run the following to install all needed dependencies

```bash
pip install -r requirements.txt
```

### For development
* install the `pre-commit.sh` script as a pre-commit hook in your local repositories:
** `ln -s ../../pre-commit.sh .git/hooks/pre-commit`

## Usage

```bash
$> python kort2osm.py --help
kort-to-osm

Usage:
  kort2osm.py [-d] [-q] [-v] [-c COUNT]
  kort2osm.py -h | --help
  kort2osm.py --version

Options:
  -h, --help               Show this help message and exit.
  -d, --dry                Do not actually make changes, only a dry run
  -q, --quiet              Run quietly, without any output.
  -v, --verbose            Show more verbose output.
  -c COUNT, --count=COUNT  Count of fixes to run through from kort to OSM.
  --version                Show the version and exit.
```

Per default, the script runs only a single change from Kort to OSM.
You can check this change by running a 'dry run' beforehand.
The output is controlled via logging, the 'quiet' and 'verbose' settings each set different log levels.
If neither of them is specified, the settings from the `logging.yml` is used.

## More information

You can find [more information about this project the OSM wiki](http://wiki.openstreetmap.org/wiki/Kort_Game) and for changes made by kort-to-osm see the [profile page of the corresponding OSM user](http://www.openstreetmap.org/user/kort-to-osm).
