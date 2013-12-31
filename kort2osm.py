from ConfigParser import ConfigParser
from OsmApi import OsmApi
from pprint import pprint
import requests
import errortypes

config = ConfigParser()
config.read('setup.cfg')

# OSM config
osm_user = config.get('Osm', 'username')
osm_pass = config.get('Osm', 'password')
osm_api = config.get('Osm', 'api')
osm_app = config.get('Osm', 'appid')

# Kort config
kort_api = config.get('Kort', 'completed_fix_api')

osm = OsmApi(
    api=osm_api,
    appid=osm_app,
    username=osm_user,
    password=osm_pass
)
pprint(osm.NodeGet(123))
# osm.ChangesetCreate({u"comment": u"My first test"})
# pprint(osm.NodeCreate({u"lon": 1, u"lat": 1, u"tag": {}}))
# osm.ChangesetClose()


# read a solution (from database or API)
r = requests.get(kort_api)
one = r.json()[-1]
pprint(one)

pprint(errortypes.Error(one['error_type']))

# determine OSM solution (modify node/way etc.)
# write data to OSM
