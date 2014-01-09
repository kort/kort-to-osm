from nose.tools import *  # noqa
from ConfigParser import ConfigParser
from helper import kort_api
from httmock import all_requests, HTTMock


@all_requests
def read_fix_mock(url, request):
    return {
        'status_code': 200,
        'content': (
            '['
            '{'
            '    "osm_id": "123",'
            '    "osm_type": "node"'
            '},'
            '{'
            '    "osm_id": "456",'
            '    "osm_type": "way"'
            '},'
            '{'
            '    "osm_id": "789",'
            '    "osm_type": "relation"'
            '}'
            ']'
        )
    }


@all_requests
def read_fix_empty_mock(url, request):
    return {
        'status_code': 200,
        'content': ''
    }


@all_requests
def read_fix_bad_mock(url, request):
    return {
        'status_code': 400,
        'content': 'Wrong API key'
    }


@all_requests
def put_fix_mock(url, request):
    return {
        'status_code': 200,
        'content': ''
    }


@all_requests
def put_fix_bad_mock(url, request):
    return {
        'status_code': 400,
        'content': ''
    }


class TestKortApi():
    def setup(self):
        self.config = ConfigParser()
        self.config.read('setup.dist.cfg')
        self.api = kort_api.KortApi(self.config)

    def teardown(self):
        pass

    def test_constructor(self):
        assert_true(isinstance(self.api, kort_api.KortApi))

    def test_constructor_config(self):
        eq_(
            self.api.fix_api_url,
            'http://play.kort.ch/server/webservices/mission/fix/completed'
        )
        eq_(self.api.db_api, 'http://kort.sourcepole.ch/db')
        eq_(self.api.db_api_key, 'my-secret-api-key')

    def test_mark_fix(self):
        with HTTMock(put_fix_mock):
            assert_true(self.api.mark_fix(123))

    @raises(kort_api.MarkFixError)
    def test_mark_fix_exception(self):
        with HTTMock(put_fix_bad_mock):
            self.api.mark_fix(123)

    def test_read_fix_one(self):
        with HTTMock(read_fix_mock):
            fixes = self.api.read_fix(1)
            eq_(len(fixes), 1)
            eq_(fixes[0]['osm_id'], '123')
            eq_(fixes[0]['osm_type'], 'node')

    def test_read_fix_two(self):
        with HTTMock(read_fix_mock):
            fixes = self.api.read_fix(2)
            eq_(len(fixes), 2)
            eq_(fixes[1]['osm_id'], '456')
            eq_(fixes[1]['osm_type'], 'way')

    def test_read_fix_many(self):
        with HTTMock(read_fix_mock):
            fixes = self.api.read_fix(50)
            eq_(len(fixes), 3)
            eq_(fixes[2]['osm_id'], '789')
            eq_(fixes[2]['osm_type'], 'relation')

    def test_read_fix_empty(self):
        with HTTMock(read_fix_empty_mock):
            fixes = self.api.read_fix(50)
            eq_(len(fixes), 0)

    def test_read_fix_bad(self):
        with HTTMock(read_fix_bad_mock):
            fixes = self.api.read_fix(50)
            eq_(len(fixes), 0)
