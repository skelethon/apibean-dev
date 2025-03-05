from typing import Self

import urllib.parse

from ._helpers import ResponseWrapper

class Curli:

    def __init__(self, invoker, session_store, account_store):
        self._invoker = invoker
        self._session = session_store
        self._account = account_store

    def globals(self, **kwargs) -> Self:
        self._session.globals(**kwargs)
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
        if "base_url" in kwargs:
            if kwargs["base_url"] is not None:
                self._session["base_url"] = kwargs["base_url"]
            del kwargs["base_url"]
        self._session.update(**kwargs)

        return self

    def _build_request(self, url, *args, headers = None, **kwargs):
        if not url.startswith('http') and self._session['base_url']:
            url = urllib.parse.urljoin(self._session['base_url'] + '/', url.lstrip('/'))

        if not isinstance(headers, dict):
            headers = {}

        session_headers = self._session['headers']
        if isinstance(session_headers, dict):
            headers = {**headers, **session_headers}

        access_token = self._account['access_token']
        if isinstance(access_token, str) and access_token:
            headers = {**headers, "Authorization": f"Bearer {access_token}"}

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
