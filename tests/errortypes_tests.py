from nose.tools import *  # noqa
from helper import errortypes


class TestErrorTypes():
    def setup(self):
        pass

    def teardown(self):
        pass

    @raises(ValueError)
    def test_invalid_errortype(self):
        errortypes.Error('test123', {})

    def test_poi_name_errortype(self):
        error_type = errortypes.Error('poi_name', {})
        assert_true(isinstance(error_type, errortypes.PoiNameErrorType))

    def test_missing_track_errortype(self):
        error_type = errortypes.Error('missing_track_type', {})
        assert_true(isinstance(error_type, errortypes.MissingTrackTypeErrorType))  # noqa

    def test_maxspeed_errortype(self):
        error_type = errortypes.Error('missing_maxspeed', {})
        assert_true(isinstance(error_type, errortypes.MissingMaxspeedErrorType))  # noqa

    def test_religion_errortype(self):
        error_type = errortypes.Error('religion', {})
        assert_true(isinstance(error_type, errortypes.ReligionErrorType))

    def test_motorway_errortype(self):
        error_type = errortypes.Error('motorway_ref', {})
        assert_true(isinstance(error_type, errortypes.MotorwayRefErrorType))

    def test_cuisine_errortype(self):
        error_type = errortypes.Error('missing_cuisine', {})
        assert_true(isinstance(error_type, errortypes.MissingCuisineErrorType))

    def test_language_errortype(self):
        error_type = errortypes.Error('language_unknown', {})
        assert_true(isinstance(error_type, errortypes.LanguageErrorType))

    def test_way_wo_tags_errortype(self):
        error_type = errortypes.Error('way_wo_tags', {})
        assert_true(isinstance(error_type, errortypes.WayWoTagsErrorType))

    def test_missing_tag_fix(self):
        test_node = {
            'node': 'mock',
            'tag': {
                'name': 'Testname'
            }
        }
        error_type = errortypes.MissingTagErrorType(test_node)
        fix = {
            'osm_tag': 'maxspeed',
            'answer': 80,
        }
        result, msg = error_type.apply_fix(fix)
        assert_equals(
            result,
            {
                'node': 'mock',
                'tag': {
                    'name': 'Testname',
                    'maxspeed': 80,
                }
            }
        )
        assert_equals(msg, "Set tag 'maxspeed' to '80'")

    def test_unknown_language(self):
        test_node = {
            'node': 'mock',
            'tag': {
                'name': 'Testname',
                'name:en': 'Test name',
            }
        }
        error_type = errortypes.LanguageErrorType(test_node)
        fix = {
            'osm_tag': 'name:XX',
            'answer': 'fr',
        }
        result, msg = error_type.apply_fix(fix)
        assert_equals(
            result,
            {
                'node': 'mock',
                'tag': {
                    'name': 'Testname',
                    'name:en': 'Test name',
                    'name:fr': 'Testname',
                }
            }
        )
        assert_equals(msg, "Set tag 'name:fr' to 'Testname'")

    @raises(errortypes.ErrorTypeError)
    def test_unknown_language_german(self):
        test_node = {
            'node': 'mock',
            'tag': {
                'name': 'Testname',
                'name:en': 'Test name',
            }
        }
        error_type = errortypes.LanguageErrorType(test_node)
        fix = {
            'osm_tag': 'name:XX',
            'answer': 'de',
        }
        result, msg = error_type.apply_fix(fix)
