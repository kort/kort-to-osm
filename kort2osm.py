from ConfigParser import ConfigParser
from helper import osm_fix
import argparse
import logging
import os
import logging.config
import yaml

parser = argparse.ArgumentParser()
parser.add_argument(
    "-d",
    "--dry",
    help="do not actually make changed, only a dry run",
    action="store_true"
)
parser.add_argument(
    "-q",
    "--quiet",
    help="run quietly without any output",
    action="store_true"
)
parser.add_argument(
    "-v",
    "--verbose",
    help="show more verbose output",
    action="store_true"
)
parser.add_argument(
    "-c",
    "--count",
    help="count of fixes to run through from kort to OSM",
    type=int
)
args = parser.parse_args()


def setup_logging(path='logging.yml', default_level=logging.INFO):
    """
    Setup logging configuration
    """
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = yaml.load(f.read())
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)

if args.quiet:
    logging.basicConfig(level=logging.WARNING)
elif args.verbose:
    logging.basicConfig(level=logging.DEBUG)
else:
    setup_logging()
log = logging.getLogger(__name__)

if args.dry:
    print "### Dry run: ###"

config = ConfigParser()
config.read('setup.cfg')
limit = args.count if args.count is not None else 1

# apply the fixes from kort to OSM
osm = osm_fix.OsmFix(config)
osm.apply_kort_fix(limit, args.dry)
