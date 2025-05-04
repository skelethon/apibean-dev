from typing import Self

import urllib.parse

from ._decorators import deprecated
from ._helpers import ResponseWrapper

from ._consts import JF_BASE_URL
from ._consts import JF_ACCESS_TOKEN
from ._store import Store

class Curli:

    def __init__(self, invoker, session_store: Store, account_store: Store):
        self._invoker = invoker
        self._session = session_store
        self._account = account_store

    @property
    def invoker(self):
        return self._invoker

    @invoker.setter
    def invoker(self, value):
        self._invoker = value

    @deprecated
    def globals(self, **kwargs) -> Self:
        return self.default(**kwargs)

    def default(self, **kwargs) -> Self:
        self._session.default(**kwargs)
        return self

    def as_account(self, profile = None, **kwargs) -> Self:
        if profile is not None:
            self._account.profile = profile
        self._account.update(**kwargs)
        return self

    def in_session(self, profile = None, **kwargs) -> Self:
        if profile is not None:
            self._session.profile = profile

        kwargs = dict(kwargs)
        if JF_BASE_URL in kwargs:
            if kwargs[JF_BASE_URL] is not None:
                self._session[JF_BASE_URL] = kwargs[JF_BASE_URL]
            del kwargs[JF_BASE_URL]
        self._session.update(**kwargs)

        return self

    def _build_request(self, url, *args, headers = None, **kwargs):
        base_url = kwargs.get(JF_BASE_URL, self._session[JF_BASE_URL])
        if not url.startswith('http') and base_url:
            url = urllib.parse.urljoin(base_url + '/', url.lstrip('/'))

        if not isinstance(headers, dict):
            headers = {}

        session_headers = self._session['headers']
        if isinstance(session_headers, dict):
            headers = {**headers, **session_headers}

        access_token = kwargs.get(JF_ACCESS_TOKEN, self._account[JF_ACCESS_TOKEN])
        if isinstance(access_token, str) and access_token:
            headers = {**headers, "Authorization": f"Bearer {access_token}"}
        if JF_ACCESS_TOKEN in kwargs:
            del kwargs[JF_ACCESS_TOKEN]

        return (url, args, dict(kwargs, headers=headers))

    def _wrap_response(self, response):
        return ResponseWrapper(response, session_store=self._session, account_store=self._account)

    def request(self, method, url, *args, **kwargs):
        url, args, kwargs = self._build_request(url, *args, **kwargs)
        return self._wrap_response(self._invoker.request(method, url, *args, **kwargs))

    def get(self, url, *args, **kwargs):
        url, args, kwargs = self._build_request(url, *args, **kwargs)
        return self._wrap_response(self._invoker.get(url, *args, **kwargs))

    def head(self, url, *args, **kwargs):
        url, args, kwargs = self._build_request(url, *args, **kwargs)
        return self._wrap_response(self._invoker.head(url, *args, **kwargs))

    def options(self, url, *args, **kwargs):
        url, args, kwargs = self._build_request(url, *args, **kwargs)
        return self._wrap_response(self._invoker.options(url, *args, **kwargs))

    def post(self, url, *args, **kwargs):
        url, args, kwargs = self._build_request(url, *args, **kwargs)
        return self._wrap_response(self._invoker.post(url, *args, **kwargs))

    def put(self, url, *args, **kwargs):
        url, args, kwargs = self._build_request(url, *args, **kwargs)
        return self._wrap_response(self._invoker.put(url, *args, **kwargs))

    def patch(self, url, *args, **kwargs):
        url, args, kwargs = self._build_request(url, *args, **kwargs)
        return self._wrap_response(self._invoker.patch(url, *args, **kwargs))

    def delete(self, url, *args, **kwargs):
        url, args, kwargs = self._build_request(url, *args, **kwargs)
        return self._wrap_response(self._invoker.delete(url, *args, **kwargs))
