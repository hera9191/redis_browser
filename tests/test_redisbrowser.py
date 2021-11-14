import pytest

from redis_browser import RedisBrowser

@pytest.mark.xfail
def test_known_bug():
    assert 1 / 0 == 1


def test_not_connected():
    rb = RedisBrowser(offline=True, decode_responses=True)
    assert rb.connected() is False


def test_connected(redisdb):
    redisdb.set('css:foo:bar:baz', 'spam')
    rb = RedisBrowser(decode_responses=True)
    assert rb.keys() == ['css:foo:bar:baz']
    assert rb.connected() is True


def test_single_key(redisdb):
    keys = ['css:foo:bar:biz']
    rb = RedisBrowser(decode_responses=True)
    assert rb.keys_tree(keys=keys) == {'css': {'foo': {'bar': {'biz': ['biz']}}}}


def test_keys_tree(redisdb):
    redisdb.set('css:foo:bar:baz', 'spam')
    redisdb.set('css:foo:ham', 'spam')
    rb = RedisBrowser(decode_responses=True)
    assert rb.keys_tree() == {'css': {'foo': {'bar': {'baz': ['baz']}, 'ham': ['ham']}}}
