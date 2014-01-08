from nose.tools import *  # noqa
from ConfigParser import ConfigParser
from helper import osm_fix
import osmapi
import mock


class TestOsmFix():
    def setup(self):
        self.config = ConfigParser()
        self.config.read('setup.dist.cfg')
        self.osm = osm_fix.OsmFix(self.config)

        # Setup mock for osmapi
        self.node_mock_data = {
            'node': 'mock'
        }
        self.way_mock_data = {
            'way': 'mock'
        }
        self.relation_mock_data = {
            'relation': 'mock'
        }
        self.osm.osm.NodeGet = mock.Mock(
            return_value=self.node_mock_data
        )
        self.osm.osm.WayGet = mock.Mock(
            return_value=self.way_mock_data
        )
        self.osm.osm.RelationGet = mock.Mock(
            return_value=self.relation_mock_data
        )

    def teardown(self):
        pass

    def test_constructor(self):
        assert_true(isinstance(self.osm, osm_fix.OsmFix))

    def test_constructor_config(self):
        eq_(
            self.osm.kort_api_url,
            'http://play.kort.ch/server/webservices/mission/fix/completed'
        )
        assert_true(isinstance(self.osm.osm, osmapi.OsmApi))
        assert_true(isinstance(self.osm.kort_db_api, kort_db_api.KortDbApi))

    def test_get_for_type_node(self):
        data = self.osm.get_for_type('node', 123)
        eq_(data, self.node_mock_data)
        self.osm.osm.NodeGet.assert_called_with(123)
        assert_false(self.osm.osm.WayGet.called)
        assert_false(self.osm.osm.RelationGet.called)

    def test_get_for_type_way(self):
        data = self.osm.get_for_type('way', '345')
        eq_(data, self.way_mock_data)
        self.osm.osm.WayGet.assert_called_with('345')
        assert_false(self.osm.osm.NodeGet.called)
        assert_false(self.osm.osm.RelationGet.called)

    def test_get_for_type_relation(self):
        data = self.osm.get_for_type('relation', u'789')
        eq_(data, self.relation_mock_data)
        self.osm.osm.RelationGet.assert_called_with(u'789')
        assert_false(self.osm.osm.NodeGet.called)
        assert_false(self.osm.osm.WayGet.called)
