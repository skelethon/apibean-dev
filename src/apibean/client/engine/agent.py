from typing import Self

import httpx

from .curli import Curli

class Agent:

    def __init__(self, curli):
        self._curli = curli

    def as_account(self, *args, **kwargs) -> Self:
        self._curli.as_account(*args, **kwargs)
        return self

    def in_session(self, *args, **kwargs):
        self._curli.in_session(*args, **kwargs)
        return self

    @property
    def _account(self):
        return getattr(self._curli, "_account")
    
    @property
    def _session(self):
        return getattr(self._curli, "_session")

    def auth(self, *args, **kwargs):
        return self.login(*args, **kwargs)

    def login(self, username = None, password = None, body = None, url:str = "auth/login", **kwargs):
        body = dict() if not isinstance(body, dict) else body

        if username:
            body['username'] = username
        if password:
            body['password'] = password

        if kwargs:
            kwargs = dict(filter(lambda item: item[0] != 'json', kwargs.items()))

        r = self._curli.post(url, json = body, **kwargs)

        if r.status_code == httpx.codes.OK:
            body = r.json()
            access_token = body.get("access_token", None)
            if access_token is None:
                raise RuntimeError("access_token not found")
            self.as_account(access_token = access_token)

        return r

    def logout(self, url:str = "auth/logout", **kwargs):
        r = self._curli.get(url, **kwargs)
        if r.status_code == httpx.codes.OK:
            self.as_account(access_token = None)
        return r

    def reset(self, url, *args, **kwargs):
        ...

    def activate_user_id(self, user_id, password = None, url:str = "auth/activate", **kwargs):
        """Any user excepts anon & root could use this API to activate his account
        """
        backup_profile = self._account.profile
        user_response = self._curli.as_account("root").get("user/" + user_id)
        self._curli.as_account(backup_profile)
        activation_code = user_response.json().get("activation_code")
        return self.activate(activation_code, password, url=url, **kwargs)

    def activate(self, activation_code, password = None, url:str = "auth/activate", **kwargs):
        r = self._curli.post(url, json = dict(activation_code=activation_code, password=password), **kwargs)
        return r
