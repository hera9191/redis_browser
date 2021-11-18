from typing import Any, TypeVar, Optional, Union

import redis

R = TypeVar("R", bound="RedisBrowser")


class RedisBrowserError(Exception):
    pass


class RedisBrowser(object):
    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        key_delim: str = ":",
        _client: redis.Redis = None,
        offline=False,
        **kwargs: Any
    ) -> None:
        """

        :param host: Redis host
        :param port: Redis port
        :param key_delim: key string deliminiter, default: ':'
        :param _client: Redis client object, default: 'redis.StrictRedis'
        :param kwargs: additional arguments passed to StrictRedis
        """
        self._key_delim = key_delim
        self._host = host
        self._port = port
        self._client = _client
        self._redis: Optional[redis.Redis] = None
        self._kwargs = kwargs
        if offline:
            self._connected = False
        else:
            if self._client:
                self._redis = self._client
                self._connected = True
            else:
                self._redis = self.connect()

    def connect(self) -> redis.Redis:
        """Invoke initialization of Redis class

        :return: RedisBrowser
        """
        rc = redis.StrictRedis(host=self._host, port=self._port, **self._kwargs)
        self._connected = True
        return rc

    def connected(self) -> bool:
        return self._connected

    def keys(self, match: str = None) -> list:
        """Return list of all KEYS in the Redis database"""
        if not self._connected:
            raise RedisBrowserError("Not connected")
        keys: list[Union[str, int]] = []
        cursor: Union[str, int] = "0"
        while cursor != 0:
            cursor, data = self._redis.scan(cursor=cursor, match=match, count=500)
            keys.extend(data)
        keys.sort()
        return keys

    def _mk_tree(self, key: str, tree: dict = None, key_delim: str = None) -> dict:
        """Make nested dictionary based on single key string and key_delim

        :param key: full key name
        :param tree: Optional key tree to update
        :param key_delim: Key strin delimiter, default: ':'
        :return: nested dictionary
        """
        if not key_delim:
            key_delim = self._key_delim
        if not tree:
            tree = {}
        if key_delim not in key:
            tree[key] = {"__leaf__": True}  # leaf
        else:
            root, rest = key.split(key_delim, 1)
            if root in tree:
                tree[root].update(self._mk_tree(rest, tree=tree[root]))
            else:
                tree[root] = self._mk_tree(rest)
        return tree

    def keys_tree(self, match: str = None, keys: list = None) -> dict:
        """Create tree of keys based on match patten

        :param match: key pattern to search
        :param keys: ad-hoc list of keys to buid keys tree
        :return: nested tree of alle keys match the pattern
        """
        if not keys:
            keys = self.keys(match=match)
        tree: dict[str, str] = {}
        for key in keys:
            tree.update(self._mk_tree(key, tree=tree))
        return tree


def redis_browser_cli():
    import argparse
    import json

    ap = argparse.ArgumentParser("Print hirearchy tree or list of Redis keys")
    ap.add_argument(
        "-H",
        "--host",
        type=str,
        default="localhost",
        help="Redis host (default: %(default)s)",
    )
    ap.add_argument(
        "-p", "--port", type=int, default=6379, help="Redis port (default: %(default)s)"
    )
    ap.add_argument(
        "-d",
        "--delimiter",
        type=str,
        default=":",
        help="Delimiter useed for keys hirearchy (default: %(default)s)",
    )
    ap.add_argument(
        "-m",
        "--match",
        type=str,
        nargs="?",
        default="*",
        help="Pattern to key match (default: %(default)s)",
    )
    ap.add_argument(
        "cmd",
        nargs="?",
        choices=["tree", "list"],
        default="tree",
        help="Print tree [default] of keys or list",
    )
    args = ap.parse_args()
    rb = RedisBrowser(
        host=args.host, port=args.port, key_delim=args.delimiter, decode_responses=True
    )
    if args.cmd == "tree":
        tree = rb.keys_tree(match=args.match)
        print(json.dumps(tree, indent=4))
    elif args.cmd == "list" or args.cmd is None:
        keys = rb.keys(match=args.match)
        print(json.dumps(keys, indent=4))
