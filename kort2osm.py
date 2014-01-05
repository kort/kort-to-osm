from ConfigParser import ConfigParser
from osmapi import OsmApi
import pprint
import requests
import errortypes
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

# OSM config
osm_user = config.get('Osm', 'username')
osm_pass = config.get('Osm', 'password')
osm_api = config.get('Osm', 'api')
osm_app = config.get('Osm', 'appid')

# Kort config
kort_api = config.get('Kort', 'completed_fix_api')
db_api = config.get('Kort', 'db_api')
db_api_key = config.get('Kort', 'db_api_key')

osm = OsmApi(
    api=osm_api,
    appid=osm_app,
    username=osm_user,
    password=osm_pass
)


def osm_type_get_factory(type, id):
    if type == 'node':
        return osm.NodeGet(id)
    if type == 'way':
        return osm.WayGet(id)
    if type == 'relation':
        return osm.RelationGet(id)


def osm_type_update_factory(type, new_values):
    if type == 'node':
        return osm.NodeUpdate(new_values)
    if type == 'way':
        return osm.WayUpdate(new_values)
    if type == 'relation':
        return osm.RelationUpdate(new_values)


def mark_fix(fix_id):
    table_name = 'kort.fix'
    column = 'in_osm'
    where_clause = 'fix_id = %s' % fix_id
    params = {'where': where_clause, 'key': db_api_key}
    payload = {column: 't'}

    # make request
    url = db_api + '/' + table_name + '/' + column
    r = requests.put(
        url,
        params=params,
        data=payload
    )
    if r.status_code == requests.codes.ok and not args.quiet:
        log.info("Successfully marked fix as 'in_osm'")
    else:
        raise MarkFixError("Error while marking fix as 'in_osm': %s" % r.text)


# read a solution (from database or API)
r = requests.get(kort_api)
limit = args.count if args.count is not None else 1
for kort_fix in r.json()[0:limit]:
    try:
        log.debug("---- Fix from Kort: ----")
        log.debug("%s" % pprint.pformat(kort_fix))

        osm_type = osm_type_get_factory(
            kort_fix['osm_type'],
            kort_fix['osm_id']
        )

        log.debug("---- OSM type before fix ----")
        log.debug("%s" % pprint.pformat(osm_type['tag']))

        error_type = errortypes.Error(kort_fix['error_type'], osm_type)
        fixed_osm_type, description = error_type.apply_fix(kort_fix)

        log.debug("---- OSM type after fix ----")
        log.debug("%s" % pprint.pformat(fixed_osm_type['tag']))
    except (errortypes.ErrorTypeError, ValueError), e:
        log.info("The fix could not be applied: %s" % e.value)
        fixed_osm_type = None
    if not args.dry:
        if fixed_osm_type is not None:
            osm.ChangesetCreate({
                u"comment": (
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
            })
            changeset = osm_type_update_factory(
                kort_fix['osm_type'],
                fixed_osm_type
            )
            log.info("%s" % pprint.pformat(changeset))

            osm.ChangesetClose()
        mark_fix(kort_fix['fix_id'])


class MarkFixError(Exception):
    pass
