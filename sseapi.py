import logging
import urllib3
import requests
import os
import json

urllib3.disable_warnings()

LOGGER = logging.getLogger(__name__)

# the default minimum elements needed to make an RPC call
DEFAULT_MINIMUM_PATH = 2


class SSEAPI_PY(object):
    def __init__(self, base_url, **kwargs):
        self._current_path = []
        self._session = None
        self._verify = kwargs.get('verify', False)
        if base_url[-1] != '/':
            base_url += '/'

        # TODO refactor this, it feels messy
        base_url.replace('http://', 'https://')
        if base_url[:8] != 'https://':
            base_url = 'https://'+base_url

        self.urls = {
            'rpc': {'url': base_url + 'rpc'},
            'auth': {'url': base_url + 'account/login'},
            'formula': {'url': base_url + 'formula', 'min': 1}
        }
        [LOGGER.debug('%s url %s', x, v['url']) for x, v in self.urls.items()]
        self.kwargs = kwargs

        self._auth = (
                os.getenv('SSE_USERNAME', kwargs.get('username')),
                os.getenv('SSE_PASSWORD', kwargs.get('password')))

    def __call__(self, **kwargs):
        """Here is an example of instantiating the SSEAPI_PY object and calling a simple
        endpoint.


          c = SSEAPI_PY('192.168.50.20', username='root', password='somepassword')
          c.api.get_versions()
          r = c.api.get_versions().json()
          {'error': None,
             'ret': {'deps': [['alembic', '0.9.0'],
                              ['APScheduler', '3.2.0'],
                              ['asyncio_extras', '1.3.0'],
                              ...
             'warnings': []}
        """
        # NOTE formula path is special, the data should be a raw post body and
        # it has no secondary element
        is_formula = self._current_path[0] == 'formula'

        minimum = self.urls.get(self._current_path[0],
                                self.urls['rpc']).get('min',
                                                      DEFAULT_MINIMUM_PATH)
        LOGGER.debug('minimun %s', minimum)
        if len(self._current_path) >= minimum or is_formula:
            # There is enough information to make the api call
            LOGGER.debug('making %s api call', '.'.join(self._current_path))
            LOGGER.debug('kwargs %s', list(kwargs.keys()))
            data = {'resource': self._current_path[0],
                    'method': self._current_path[1],
                    'kwarg': kwargs
                    }
            url = 'rpc'
            if is_formula:
                url = 'formula'
            return self.__post(_data=data, _api=url, **kwargs)
        else:
            # Not enough information
            LOGGER.error('Not enough information to make an api call')
            return None

    def __getattr__(self, name):
        """
        >>> c = SSEAPI_PY('192.168.50.20', username='root', password='somepassword')
        >>> v = c.api
        >>> c._current_path
        ['api']
        >>> v = c.api.get_versions
        >>> c.current_path
        ['api', 'get_versions']
        """

        if len(self._current_path) < 2:
            self._current_path.append(name)
        else:
            # Replace the last method with this one
            self._current_path[1] = name
        return self

    def reset(self):
        """
        >>> c = SSEAPI_PY('192.168.50.20', username='root', password='somepassword')
        >>> v = c.api.get_versions
        >>> c._current_path
        ['api', 'get_versions']
        >>> c.reset()
        >>> c.current_path
        []
        """
        self._current_path = []

    def __session(self):
        if not self._session:
            LOGGER.debug('authenticating now')
            session = requests.Session()
            session.auth = self._auth
            session.verify = self._verify
            if not all(self._auth):
                LOGGER.error('missing username or password')
                self._session = None
            else:
                LOGGER.debug('url %s', self.urls['auth']['url'])
                req = session.get(self.urls['auth']['url'])
                if req.status_code == 200:
                    h = {'X-Xsrftoken': req.headers['X-Xsrftoken']}
                    session.headers.update(h)
                    self._session = session
                    LOGGER.debug('authenticated %s', req.text)
                else:
                    LOGGER.error('unable to authenticate %s', req.status_code)
            self._session = session
        return self._session

    def __post(self, _api='rpc', _data={}, **kwargs):

        session = self.__session()
        LOGGER.debug('url: %s', _api)

        path = self.urls.get(_api)['url']
        LOGGER.debug('path: %s', path)

        session.headers.update({'Content-Type': 'application/json'})
        LOGGER.debug('_data %s', _data)
        res = session.post(path, data=json.dumps(_data))
        try:
            json_res = res.json()
        except Exception as exc:
            LOGGER.error(exc)
            json_res = res.text
        LOGGER.debug('JSON_RES %s', json_res)
        self.reset()
        return json_res
