import requests
import logging

log = logging.getLogger(__name__)


class KortApi(object):
    def __init__(self, config):
        self.db_api = config.get('Kort', 'db_api')
        self.db_api_key = config.get('Kort', 'db_api_key')
        self.fix_api_url = config.get('Kort', 'completed_fix_api')

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

    def read_fix(self, limit):
        """
        Returns an array of dicts containing fixes from kort
        """
        try:
            r = requests.get(self.fix_api_url)
            return r.json()[0:limit]
        except ValueError:
            return []


class MarkFixError(Exception):
    pass
