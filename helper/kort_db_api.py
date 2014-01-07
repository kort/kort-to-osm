import requests
import logging

log = logging.getLogger(__name__)


class KortDbApi(object):
    def __init__(self, config):
        self.db_api = config.get('Kort', 'db_api')
        self.db_api_key = config.get('Kort', 'db_api_key')

    def mark_fix(self, fix_id):
        table_name = 'kort.fix'
        column = 'in_osm'
        where_clause = 'fix_id = %s' % fix_id
        params = {'where': where_clause, 'key': self.db_api_key}
        payload = {column: 't'}

        # make request
        url = self.db_api + '/' + table_name + '/' + column
        r = requests.put(
            url,
            params=params,
            data=payload
        )
        if r.status_code == requests.codes.ok:
            log.info("Successfully marked fix as 'in_osm'")
        else:
            raise MarkFixError(
                "Error while marking fix as 'in_osm': %s"
                % r.text
            )


class MarkFixError(Exception):
    pass
