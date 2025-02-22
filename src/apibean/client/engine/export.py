import json
import re

class ResponseWrapper:
    def __init__(self, wrapped_object):
        self._wrapped_object = wrapped_object

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

    def __getattribute__(self, name):
        """Ensures that we don't loop into __getattr__."""
        if name == "_wrapped_object":
            return super().__getattribute__(name)
        return getattr(self._wrapped_object, name)

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
