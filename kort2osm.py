from ConfigParser import ConfigParser
from helper import errortypes
from helper import kort_db_api
from helper import osm_fix
import pprint
import argparse
import logging

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

if args.quiet:
    logging.basicConfig(level=logging.WARNING)
elif args.verbose or args.dry:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

if args.dry:
    log.info("### Dry run: ###")

config = ConfigParser()
config.read('setup.cfg')

osm = osm_fix.OsmFix(config)

# read a fix from kort
limit = args.count if args.count is not None else 1
for kort_fix in osm.read_kort_fix(limit):
    try:
        log.debug("---- Fix from Kort: ----")
        log.debug("%s" % pprint.pformat(kort_fix))

        osm_entity = osm.get_for_type(
            kort_fix['osm_type'],
            kort_fix['osm_id']
        )

        log.debug("---- OSM type before fix ----")
        log.debug("%s" % pprint.pformat(osm_entity['tag']))

        error_type = errortypes.Error(kort_fix['error_type'], osm_entity)
        fixed_osm_entity, description = error_type.apply_fix(kort_fix)

        log.debug("---- OSM type after fix ----")
        log.debug("%s" % pprint.pformat(fixed_osm_entity['tag']))
    except (errortypes.ErrorTypeError, ValueError), e:
        log.info("The fix could not be applied: %s" % e.value)
        fixed_osm_entity = None
    if not args.dry:
        if fixed_osm_entity is not None:
            comment = (
                u"Change from kort, user: %s (id: %s), "
                u"fix id: %s, error: %s (source: %s), description: %s"
                % (
                    kort_fix['username'],
                    kort_fix['user_id'],
                    kort_fix['fix_id'],
                    kort_fix['error_type'],
                    kort_fix['source'],
                    description
                )
            )
            osm.submit_entity(
                kort_fix['osm_type'],
                fixed_osm_entity,
                comment
            )
        kort_api = kort_db_api.KortDbApi(config)
        kort_api.mark_fix(kort_fix['fix_id'])
