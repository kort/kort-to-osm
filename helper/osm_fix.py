from osmapi import OsmApi
import requests
import pprint
import logging

log = logging.getLogger(__name__)


class OsmFix(object):
    def __init__(self, config):
        osm_user = config.get('Osm', 'username')
        osm_pass = config.get('Osm', 'password')
        osm_api = config.get('Osm', 'api')
        osm_app = config.get('Osm', 'appid')

        self.kort_api = config.get('Kort', 'completed_fix_api')

        self.osm = OsmApi(
            api=osm_api,
            appid=osm_app,
            username=osm_user,
            password=osm_pass
        )

    def get_for_type(self, type, id):
        """
        Returns the 'getter' of the requested OSM type
        """
        if type == 'node':
            return self.osm.NodeGet(id)
        if type == 'way':
            return self.osm.WayGet(id)
        if type == 'relation':
            return self.osm.RelationGet(id)

    def update_for_type(self, type, new_values):
        """
        Returns the 'update' method of the requested OSM type
        """
        if type == 'node':
            return self.osm.NodeUpdate(new_values)
        if type == 'way':
            return self.osm.WayUpdate(new_values)
        if type == 'relation':
            return self.osm.RelationUpdate(new_values)

    def read_kort_fix(self, limit):
        """
        Returns an array of dicts containing fixes from kort
        """
        r = requests.get(self.kort_api)
        return r.json()[0:limit]

    def submit_entity(self, type, entity, comment):
        """
        Submits an OSM entity (node, way, relation) to OSM
        """
        self.osm.ChangesetCreate({
            "comment": comment,
            "mechanical": "yes",
            "bot": "yes"
        })
        changeset = self.update_for_type(
            type,
            entity
        )
        log.info("%s" % pprint.pformat(changeset))
        self.osm.ChangesetClose()
