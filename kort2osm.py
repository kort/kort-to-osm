"""
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

"""
import os
import logging
import logging.config
from ConfigParser import ConfigParser

import docopt
import yaml

from helper import osm_fix


__location__ = os.path.realpath(
    os.path.join(
        os.getcwd(),
        os.path.dirname(__file__)
    )
)


def setup_logging(
        path=os.path.join(__location__, 'logging.yml'),
        default_level=logging.INFO):
    """
    Setup logging configuration
    """
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = yaml.load(f.read())
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)


if __name__ == '__main__':
    arguments = docopt.docopt(__doc__, version='kort-to-osm 0.1')

    # Set up logging
    if arguments['--quiet']:
        logging.basicConfig(level=logging.WARNING)
    elif arguments['--verbose']:
        logging.basicConfig(level=logging.DEBUG)
    else:
        setup_logging()

    # Handle a dry run
    if arguments['--dry']:
        print '### Dry run: ###'

    # Parse the configuration
    config = ConfigParser()
    config.read(os.path.join(__location__, 'setup.cfg'))

    # Apply the fixes from kort to OSM
    try:
        limit = int(arguments['--count'])
    except TypeError:
        limit = 1
    osm = osm_fix.OsmFix(config)
    osm.apply_kort_fix(limit, arguments['--dry'])
