import requests


if requests.compat.is_py2:
    from urlparse import parse_qs
elif requests.compat.is_py3:
    from urllib.parse import parse_qs


def to_bytes(some_str, encoding="utf8"):
    if isinstance(some_str, requests.compat.str):
        some_bytes = some_str.encode(encoding)
    return some_bytes


def to_str(some_bytes, encoding="utf8"):
    if isinstance(some_bytes, requests.compat.bytes):
        some_str = some_bytes.decode(encoding)
    else:
        some_str = some_bytes
    return some_str


class URL(object):
    def __init__(self, url_str):
        """parse url query part into dict

        :param url: url to parse

        Usage::

            >>> params = parse_query("http://www.example.com/?foo=bar&baz")
            {'foo': 'bar', 'baz': None}

        """
        parsed_url = requests.compat.urlparse(to_str(url_str))
        netloc_parts = parsed_url.netloc.split("@")
        if len(netloc_parts) == 1:
            username = password = None
            host_str = netloc_parts[0]
        else:
            username, password = netloc_parts[0].split(":")
            host_str = netloc_parts[1]

        host_parts = host_str.split(":")
        host = host_parts[0]

        if len(host_parts) == 1:
            port = 80
        else:
            port = int(host_parts[1])

        params = [
            (key, val[0] if val[0] else None)
            for key, val in parse_qs(parsed_url.query, True).items()
        ]

        self._info = dict(
            scheme=parsed_url.scheme or "http",
            username=username,
            password=password,
            host=host,
            port=port,
            path=parsed_url.path or "/",
            params=params,
            fragment=parsed_url.fragment
        )

    def forge(self):
        parts = [
            self.scheme,
            self.netloc,
            self.path,
            "?".format() if self.query else ""
            "#".format(self.fragment) if self.fragment else "",
        ]
        return "".join(parts)

    __str__ = __unicode__ = forge

    @property
    def scheme(self):
        return self._info["scheme"]

    @property
    def netloc(self):
        if self.username is None or self.password is None:
            netloc = self.host
        else:
            netloc = "{0}:{1}@{2}".format(
                self.username,
                self.password,
                self.host
            )
        if self.port != 80:
            netloc = "{0}:{1}".format(netloc, self.port)
        return netloc

    @property
    def username(self):
        return self._info["username"]

    @property
    def password(self):
        return self._info["password"]

    @property
    def host(self):
        return self._info["host"]

    @property
    def port(self):
        return self._info["port"]

    @property
    def path(self):
        return self._info["path"]

    @path.setter
    def path(self, new_val):
        self._info["path"] = new_val
        return new_val

    @property
    def params(self):
        return dict(self._info["params"])

    @params.setter
    def params(self, new_params):
        if isinstance(new_params, dict):
            self._info["params"] = list(new_params.items())
        else:
            self._info["params"] = list(new_params)
        return new_params

    @property
    def query(self):
        query = []
        for key, val in self._info["params"]:
            if val is None:
                query.append(requests.compat.quote(to_bytes(key)))
            else:
                param = {to_bytes(key): to_bytes(val)}
                query.append(requests.compat.urlencode(param))
        return "&".join(query)

    def append_params(self, new_params):
        self._info["params"].update(new_params)
        return self.params

    @property
    def fragment(self):
        return self._info["fragment"]