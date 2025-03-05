from typing import Optional
from functools import reduce

import json
import httpx
import re

class ResponseWrapper:
    def __init__(self, wrapped_object, session_store, account_store):
        self._wrapped_object = wrapped_object
        self._session_store = session_store
        self._account_store = account_store

    def __getattr__(self, name):
        """Intercepts attribute access and forwards it to the wrapped object."""
        return getattr(self._wrapped_object, name)

    def __setattr__(self, name, value):
        """Intercepts attribute assignment and forwards it to the wrapped object."""
        if name == "_wrapped_object":
            # Allow assignment of the wrapped object itself.
            super().__setattr__(name, value)
        else:
            # Forward other assignments to the wrapped object.
            setattr(self._wrapped_object, name, value)

    def __repr__(self):
        """Returns the representation of the wrapped object."""
        return repr(self._wrapped_object)

    def __str__(self):
        """Returns the string representation of the wrapped object."""
        return str(self._wrapped_object)

    @property
    def __class__(self):
        """Preserves the class of the wrapped object."""
        return self._wrapped_object.__class__

    def _assert_response(self):
        if self._wrapped_object is None:
            raise RuntimeError(
                "The original response instance has not been set on this response wrapper."
            )
        return self._wrapped_object

    def _assert_response_body(self):
        body = self._assert_response().json()
        return body

    def get_id(self):
        return self.get_value_of("id")

    def get_value_of(self, field_name):
        body = self._assert_response_body()
        if field_name not in body:
            raise RuntimeError(
                f"The returned data does not contain the [{ field_name }] field."
            )
        return body.get(field_name)

    def capture_id_refs(self, name_of_id_refs:Optional[str] = None, name_of_key_field = "email"):
        if not self._wrapped_object.is_success:
            raise RuntimeError("The response is not sussess")
        if name_of_id_refs is None:
            name_of_id_refs = self._build_name_of_id_refs()
        if name_of_id_refs not in self._session_store:
            self._session_store[name_of_id_refs] = dict()
        self._session_store[name_of_id_refs].update(**self._extract_ids_map(name_of_key_field))
        return self

    def _build_name_of_id_refs(self):
        return f"{ self._extract_model_name(self._wrapped_object) }_ids_of"

    def _extract_model_name(self, r):
        urlpath = r.request.url.path
        return urlpath.split('/')[-1]

    def _extract_ids_map(self, name_of_key_field="email"):
        return reduce(lambda acc, item: {**acc, item[name_of_key_field]: item["id"]},
                self._get_list_of_items(),
                dict())

    def _get_list_of_items(self):
        resp_body = self._wrapped_object.json()
        if "founds" in resp_body:
            items = resp_body["founds"]
        else:
            items = [ resp_body ]
        return items

    def print(self, details: bool = False):
        response = self._wrapped_object
        if response.status_code == httpx.codes.OK:
            print(response)
        else:
            print(response)
            print(json.dumps(response.json(), indent=2))

    def print_body(self):
        print(json.dumps(self._wrapped_object.json(), indent=2))

    def print_curl(self):
        print(Curlify(self._wrapped_object.request).to_curl())


class Curlify:
    DEFAULT_EXCLUDE_HEADERS = [
        "host",
        "content-length",
        "accept-encoding",
        "connection",
        "user-agent",
    ]

    def __init__(self, request, exclude_headers = DEFAULT_EXCLUDE_HEADERS,
            compressed=False, verified=True):
        self.req = request
        self.exclude_headers = exclude_headers
        self.compressed = compressed
        self.verified = verified

    def to_curl(self) -> str:
        """to_curl function returns a string of curl to execute in shell.
        """
        return self.build()

    def build(self) -> str:
        """build curl command string

        Returns:
            str: string represents curl command
        """
        quote = f'curl -X {self.req.method} "{self.req.url}" -H {self.headers()}'
        if self.req.method != 'GET':
            quote = quote + f" -d '{self.decode_body()}'"

        parts = re.split(r'\s(?=-[dH])', quote)

        if self.compressed:
            parts.append("--compressed")
        if not self.verified:
            parts.append("--insecure")

        quote = " \\\n".join(parts)
        return quote

    def headers(self) -> str:
        """convert the request's headers to string

        Returns:
            str: return string of headers
        """
        headers = [f'"{k}: {v}"' for k, v in self.req.headers.items() if k not in self.exclude_headers]

        return " -H ".join(headers)

    def decode_body(self):
        body = self.read_body()

        if body and isinstance(body, bytes):
            content_type = self.req.headers.get("content-type", None)
            if content_type and content_type == "application/json":
                return json.dumps(json.loads(body.decode()), indent=2)
            return body.decode()

        return body

    def read_body(self):
        if hasattr(self.req, "body"):
            return self.req.body

        return self.req.read()
