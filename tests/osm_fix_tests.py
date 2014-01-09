from nose.tools import *  # noqa
from ConfigParser import ConfigParser
from helper import osm_fix, kort_api, errortypes
import osmapi
import mock


class TestOsmFix():
    def setup(self):
        self.config = ConfigParser()
        self.config.read('setup.dist.cfg')
        self.osm = osm_fix.OsmFix(self.config)

        # Setup mock for osmapi
        self.node_mock_data = {
            'node': 'mock',
            'tag': {'name': 'DE name'},
        }
        self.fixed_node_mock_data = {
            'osm': 'fixed',
            'tag': {
                'name': 'DE name',
                'name:de': 'DE name',
            }
        }
        self.way_mock_data = {
            'way': 'mock',
            'tag': {},
        }
        self.relation_mock_data = {
            'relation': 'mock',
            'tag': {},
        }
        self.fix_mock_data = [
            {
                'osm_type': 'node',
                'osm_tag': 'name:XX',
                'osm_id': '12354212',
                'error_type': 'language_unknown',
                'fix_id': '1111',
                'username': 'testuser',
                'user_id': '0',
                'source': 'keepright',
            }
        ]
        self.node_comment = (
            u"Change from kort, user: testuser (id: 0), "
            u"fix id: 1111, error: language_unknown (source: keepright), "
            u"description: test description, "
            u"see this users profile for more information: "
            u"http://www.openstreetmap.org/user/kort-to-osm"
        )

        # osmapi
        self.osm.osm.NodeGet = mock.Mock(
            return_value=self.node_mock_data
        )
        self.osm.osm.WayGet = mock.Mock(
            return_value=self.way_mock_data
        )
        self.osm.osm.RelationGet = mock.Mock(
            return_value=self.relation_mock_data
        )
        self.osm.osm.RelationGet = mock.Mock(
            return_value=self.relation_mock_data
        )

        # KortApi
        self.osm.kort_api.read_fix = mock.Mock(
            return_value=self.fix_mock_data
        )
        self.osm.kort_api.mark_fix = mock.Mock(
            return_value=True
        )

        # errortypes
        self.error_type_mock = mock.Mock()
        self.error_type_mock.apply_fix = mock.Mock(
            return_value=(
                self.fixed_node_mock_data,
                'test description'
            )
        )
        errortypes.Error = mock.Mock(
            return_value=self.error_type_mock
        )

    def teardown(self):
        pass

    def test_constructor(self):
        assert_true(isinstance(self.osm, osm_fix.OsmFix))

    def test_constructor_config(self):
        assert_true(isinstance(self.osm.osm, osmapi.OsmApi))
        assert_true(isinstance(self.osm.kort_api, kort_api.KortApi))

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

    def test_apply_kort_fix(self):
        self.osm.submit_entity = mock.Mock()
        self.osm.apply_kort_fix(1, False)

        self.osm.submit_entity.assert_called_once_with(
            'node',
            self.fixed_node_mock_data,
            self.node_comment
        )

        self.osm.kort_api.mark_fix.assert_called_once_with(
            '1111'
        )

    def test_apply_kort_fix_osmentitynotfound(self):
        self.osm.submit_entity = mock.Mock()
        self.osm.get_for_type = mock.Mock(
            return_value=None
        )
        self.osm.apply_kort_fix(1, False)

        assert_false(self.osm.submit_entity.called)
        assert_true(self.osm.kort_api.mark_fix.called)

    def test_apply_kort_fix_errortypeerror(self):
        self.osm.submit_entity = mock.Mock()
        errortypes.Error = mock.Mock(
            side_effect=errortypes.ErrorTypeError("Test")
        )
        self.osm.apply_kort_fix(1, False)

        assert_false(self.osm.submit_entity.called)
        assert_true(self.osm.kort_api.mark_fix.called)

    def test_apply_kort_fix_dry(self):
        self.osm.submit_entity = mock.Mock()
        self.osm.apply_kort_fix(1, True)

        assert_false(self.osm.submit_entity.called)
        assert_false(self.osm.kort_api.mark_fix.called)
