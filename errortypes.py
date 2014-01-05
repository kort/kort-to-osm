class ErrorType(object):
    def __init__(self, osm_type):
        if osm_type is None:
            raise ValueError("The passed osm_type is not set")
        self.osm_type = osm_type

    def apply_fix(self, kort_fix):
        pass


class MissingTagErrorType(ErrorType):
    @classmethod
    def handles_error(cls, error):
        return False

    def apply_fix(self, kort_fix):
        osm_tag = kort_fix['osm_tag']
        if osm_tag in self.osm_type['tag']:
            raise ErrorTypeError(
                "Tag %s already exists (%s)"
                % (osm_tag, self.osm_type['tag'][osm_tag])
            )
        self.osm_type['tag'][osm_tag] = kort_fix['answer']
        return (
            self.osm_type,
            "Set tag '%s' to '%s'" % (osm_tag, kort_fix['answer'])
        )


class PoiNameErrorType(MissingTagErrorType):
    @classmethod
    def handles_error(cls, error):
        return error == 'poi_name'


class MissingTrackTypeErrorType(MissingTagErrorType):
    @classmethod
    def handles_error(cls, error):
        return error == 'missing_track_type'


class MissingMaxspeedErrorType(MissingTagErrorType):
    @classmethod
    def handles_error(cls, error):
        return error == 'missing_maxspeed'


class ReligionErrorType(MissingTagErrorType):
    @classmethod
    def handles_error(cls, error):
        return error == 'religion'


class MotorwayRefErrorType(MissingTagErrorType):
    @classmethod
    def handles_error(cls, error):
        return error == 'motorway_ref'


class MissingCuisineErrorType(MissingTagErrorType):
    @classmethod
    def handles_error(cls, error):
        return error == 'missing_cuisine'


class LanguageErrorType(ErrorType):
    @classmethod
    def handles_error(cls, error):
        return error == 'language_unknown'

    def apply_fix(self, kort_fix):
        try:
            orig_tag = kort_fix['osm_tag'].replace(':XX', '')
            new_tag = '%s:%s' % (orig_tag, kort_fix['answer'])
            orig_value = self.osm_type['tag'][orig_tag]

            if (new_tag in self.osm_type['tag'] and
                    self.osm_type['tag'][new_tag] == orig_value):
                raise ErrorTypeError("The fix has already been applied")

            self.osm_type['tag'].update({
                new_tag: orig_value
            })
        except KeyError, e:
            raise ErrorTypeError("Tag '%s' not found on osm_type", e)
        return (
            self.osm_type,
            "Set tag '%s' to '%s'" % (new_tag, self.osm_type['tag'][orig_tag])
        )


class WayWoTagsErrorType(ErrorType):
    @classmethod
    def handles_error(cls, error):
        return error == 'way_wo_tags'

    def apply_fix(self, kort_fix):
        raise ErrorTypeError(
            "Errors with type way_wo_tags are considered false positives"
        )


class ErrorTypeError(Exception):
    pass


def itersubclasses(cls, _seen=None):
    """
    itersubclasses(cls)
    Generator over all subclasses of a given class, in depth first order.
    """

    if not isinstance(cls, type):
        raise TypeError('itersubclasses must be called with '
                        'new-style classes, not %.100r' % cls)
    if _seen is None:
        _seen = set()
    try:
        subs = cls.__subclasses__()
    except TypeError:  # fails only when cls is type
        subs = cls.__subclasses__(cls)
    for sub in subs:
        if sub not in _seen:
            _seen.add(sub)
            yield sub
            for sub in itersubclasses(sub, _seen):
                yield sub


def Error(error, osm_type):
    for cls in itersubclasses(ErrorType):
        if cls.handles_error(error):
            return cls(osm_type)
    raise ValueError("No class found to handle error '%s'" % error)
