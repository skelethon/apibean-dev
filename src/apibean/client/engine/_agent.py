from typing import Self

import httpx

from ._curli import Curli

class Agent:
    """The Agent object class wraps some of the operations of authenticating users and 
    switching between these accounts during interactions.

    Properties:
    - `ACCOUNT_AUTH_FIELDS`: The names of the fields containing user authentication
        information of an account.
        In which:

        * id: Unique identifier of the user in the system (usually a UUID code).
        * email: Unique email address of the user, this is also the login name.
        * access_token: Access code according to the JWT protocol.
        * refresh_token: Secret code used to refresh the access_token.
        * expiration: Time when the access_token code expires. The access_token must
            be refreshed before this time.
    """

    ACCOUNT_AUTH_FIELDS = ['id', 'email', 'access_token', 'refresh_token', 'expiration']

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
            self.as_account(**self._extract_cached(r))

        return r

    def _extract_cached(self, r):
        body = r.json()
        params = {key: body[key] for key in self.ACCOUNT_AUTH_FIELDS if key in body}
        for field_name in ["id", "access_token"]:
            self._check_available(params, field_name)
        return params

    def _check_available(self, data, field_name):
        if field_name not in data:
            raise RuntimeError(f"{ field_name } not found")
        field_value = data.get(field_name)
        if field_value is None:
            raise RuntimeError(f"{ field_name } is null")
        if not field_value:
            raise RuntimeError(f"{ field_name } is empty")

    def change_password(self, current_password, new_password, url:str = "auth/change-password", **kwargs):
        return self._curli.post(url,
                json=dict(current_password=current_password, new_password=new_password),
                **kwargs)

    def refresh_token(self, url:str = "auth/refresh-token", **kwargs):
        email = self._account.get("email")
        if not email:
            raise RuntimeError("email not found")

        refresh_token = self._account.get("refresh_token")
        if not refresh_token:
            raise RuntimeError("refresh_token not found")

        r = self._curli.post(url, json=dict(email=email, refresh_token=refresh_token), **kwargs)

        if r.status_code == httpx.codes.OK:
            self.as_account(**self._extract_cached(r))

        return r

    def logout(self, url:str = "auth/logout", **kwargs):
        r = self._curli.get(url, **kwargs)
        if r.status_code == httpx.codes.OK:
            self.as_account(access_token = None)
        return r

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
