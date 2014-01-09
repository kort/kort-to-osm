from osmapi import OsmApi
import pprint
import logging

import errortypes
import kort_api

log = logging.getLogger(__name__)


class OsmFix(object):
    def __init__(self, config):
        osm_user = config.get('Osm', 'username')
        osm_pass = config.get('Osm', 'password')
        osm_api = config.get('Osm', 'api')
        osm_app = config.get('Osm', 'appid')

        self.osm = OsmApi(
            api=osm_api,
            appid=osm_app,
            username=osm_user,
            password=osm_pass
        )
        self.kort_api = kort_api.KortApi(config)

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

    def apply_kort_fix(self, limit=1, dry=False):
        try:
            for kort_fix in self.kort_api.read_fix(limit):
                try:
                    log.debug("---- Fix from Kort: ----")
                    log.debug("%s" % pprint.pformat(kort_fix))

                    osm_entity = self.get_for_type(
                        kort_fix['osm_type'],
                        kort_fix['osm_id']
                    )
                    if not osm_entity:
                        raise OsmEntityNotFoundError("OSM entity not found")

                    log.debug("---- OSM type before fix ----")
                    log.debug("%s" % pprint.pformat(osm_entity['tag']))

                    error_type = errortypes.Error(
                        kort_fix['error_type'],
                        osm_entity
                    )
                    fixed = error_type.apply_fix(kort_fix)
                    fixed_osm_entity, description = fixed

                    log.debug("---- OSM type after fix ----")
                    log.debug("%s" % pprint.pformat(fixed_osm_entity['tag']))
                except (errortypes.ErrorTypeError,
                        OsmEntityNotFoundError,
                        ValueError), e:
                    log.warning(
                        "The fix could not be applied: %s, fix: %s"
                        % (str(e), kort_fix)
                    )
                    fixed_osm_entity = None
                if not dry:
                    if fixed_osm_entity is not None:
                        comment = self.gen_changelog_comment(
                            kort_fix,
                            description
                        )
                        self.submit_entity(
                            kort_fix['osm_type'],
                            fixed_osm_entity,
                            comment
                        )
                    self.kort_api.mark_fix(kort_fix['fix_id'])
        except Exception, e:
            log.exception("Failed to apply fix of Kort to OpenStreetMap")

    def gen_changelog_comment(self, kort_fix, change_description):
        comment = (
            u"Change from kort, user: %s (id: %s), "
            u"fix id: %s, error: %s (source: %s), "
            u"description: %s, "
            u"see this users profile for more information: "
            u"http://www.openstreetmap.org/user/kort-to-osm"
            % (
                kort_fix['username'],
                kort_fix['user_id'],
                kort_fix['fix_id'],
                kort_fix['error_type'],
                kort_fix['source'],
                change_description
            )
        )
        return comment

    def submit_entity(self, type, entity, comment):
        """
        Submits an OSM entity (node, way, relation) to OSM
        """
        self.osm.ChangesetCreate({
            "comment": comment[:255],
            "mechanical": "yes",
        })
        changeset = self.update_for_type(
            type,
            entity
        )
        log.info("%s" % pprint.pformat(changeset))
        self.osm.ChangesetClose()


class OsmEntityNotFoundError(Exception):
    pass
