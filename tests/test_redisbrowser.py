import pytest

from redisbrowser.redisbrowser import RedisBrowser


@pytest.mark.xfail
def test_known_bug():
    assert 1 / 0 == 1


def test_not_connected():
    rb = RedisBrowser(offline=True)
    assert rb.connected() is False


def test_connected():
    rb = RedisBrowser()
    assert rb.connected() is True


def test_single_key():
    rb = RedisBrowser()
    assert rb.keys_tree(keys=['css:foo:bar:baz']) == {'css': {'foo': {'bar': {'baz': ['baz']}}}}
