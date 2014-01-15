"""
kort-to-osm

Usage:
  kort2osm.py [-d] [-q] [-v] [-c COUNT]
  kort2osm.py -h | --help
  kort2osm.py --version

Options:
  -h --help                Show this help message and exit.
  -d --dry                 Do not actually make changes, only a dry run
  -q --quiet               Run quietly, without any output.
  -v --verbose             Show more verbose output.
  -c COUNT, --count=COUNT  Count of fixes to process [default: 1]
  --version                Show the version and exit.

"""
import os
import sys
import logging
import logging.config
from ConfigParser import ConfigParser

import docopt
from schema import Schema, Use, SchemaError
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
    arguments = docopt.docopt(__doc__, version='kort-to-osm 0.2')
    arg_schema = Schema({
        '--count': Use(int, error='count must be an integer'),
        object: object
    })
    try:
        args = arg_schema.validate(arguments)
    except SchemaError, e:
        sys.exit(e)

    # Set up logging
    if args['--quiet']:
        logging.basicConfig(level=logging.WARNING)
    elif args['--verbose']:
        logging.basicConfig(level=logging.DEBUG)
    else:
        setup_logging()

    # Handle a dry run
    if args['--dry']:
        print '### Dry run: ###'

    # Parse the configuration
    config = ConfigParser()
    config.read(os.path.join(__location__, 'setup.cfg'))

    # Apply the fixes from kort to OSM
    limit = int(args['--count'])
    osm = osm_fix.OsmFix(config)
    osm.apply_kort_fix(limit, args['--dry'])
