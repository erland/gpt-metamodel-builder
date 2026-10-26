#!/usr/bin/env python3
"""Accelerated YAML loads must preserve safe parsing and fallback behavior."""
import importlib
import io
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import safe_yaml


def main():
    text = "name: test\nvalue: [1, true, null]\n"
    expected = yaml.safe_load(text)
    assert safe_yaml.safe_load(text) == expected
    assert safe_yaml.safe_load(text.encode()) == expected
    assert safe_yaml.safe_load(io.StringIO(text)) == expected
    assert safe_yaml._SAFE_LOADER in (yaml.SafeLoader, getattr(yaml, "CSafeLoader", yaml.SafeLoader))
    # Every execution path must reject unsafe Python object construction.
    bad = "!!python/object/apply:os.system ['echo never']"
    for loader in (yaml.SafeLoader, getattr(yaml, "CSafeLoader", yaml.SafeLoader)):
        try:
            yaml.load(bad, Loader=loader)
        except yaml.YAMLError:
            pass
        else:
            raise AssertionError("Unsafe YAML tag accepted")
    try:
        safe_yaml.safe_load(bad)
    except yaml.YAMLError:
        pass
    else:
        raise AssertionError("Unsafe YAML tag accepted by shared loader")
    print("Safe YAML loader PASS")


if __name__ == "__main__":
    main()
