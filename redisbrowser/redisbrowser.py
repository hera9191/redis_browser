import json
import sys
from typing import Type, Any, TypeVar

import redis

R = TypeVar('R', bound='RedisBrowser')

class RedisBrowserError(Exception):
    pass


class RedisBrowser(object):
    def __init__(self, host: str = 'localhost', port: int = 6379, key_delim: str = ':', _cls: Type[Any] = redis.StrictRedis,
                 offline=False, **kwargs: Any) -> None:
        """

        :param host: Redis host
        :param port: Redis port
        :param key_delim: key string deliminiter, default: ':'
        :param _cls: class for Redis, default: 'redis.StrinctRedis'
        :param kwargs: additional arguments passed to StrictRedis
        """
        self._key_delim = key_delim
        self._host = host
        self._port = port
        self._cls = _cls
        self._redis = None
        self._kwargs = kwargs
        if offline:
            self._connected = False
        else:
            self._redis = self._cls(host=host, port=port, **kwargs)
            self._connected = True

    def connect(self) -> R:
        """Invoke initialization of Redis class

        :return: RedisBrowser
        """
        self._redis = self._cls(host=self._host, port=self._port, **self._kwargs)
        self._connected = True
        return self

    def connected(self) -> bool:
        return self._connected

    def keys(self, match: str = None) -> list:
        """Return list of all KEYS in the Redis database"""
        if not self._connected:
            raise RedisBrowserError("Not connected")
        keys = []
        cursor = '0'
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
            tree[key] = [key]
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
        :return: nested tree of alle keys match the pattern
        """
        if not keys:
            keys = self.keys(match=match)
        tree = {}
        for key in keys:
            tree.update(self._mk_tree(key, tree=tree))
        return tree