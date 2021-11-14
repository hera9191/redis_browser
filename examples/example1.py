import json
import sys

from redis_browser import RedisBrowser


def main():
    match = None
    if len(sys.argv) > 1:
        match = sys.argv[1]
    rb = RedisBrowser(host='localhost', port=6379, db=0, decode_responses=True, key_delim=':')
    rb.connect()

    # All keys
    print(f"\nList all keys:")
    keys = rb.keys()
    print(json.dumps(keys, indent=4))

    # Keys via pattern
    if match:
        print(f"\nList all keys match '{match}' pattern:")
        keys = rb.keys(match=match)
        print(json.dumps(keys, indent=4))

    # Tree
    print(f"\nTree from all keys")
    tree = rb.keys_tree()
    print(json.dumps(tree, indent=4))

    # Custom keys
    mykeys = ['a:c:b', 'a:d:f']
    print(f"\nTree from custom keys list '{keys}':")
    tree = rb.keys_tree(keys=mykeys)
    print(json.dumps(tree, indent=4))
    pass


if __name__ == '__main__':
    main()
