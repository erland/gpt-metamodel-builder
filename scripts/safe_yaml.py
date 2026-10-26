"""Safe PyYAML parsing with optional LibYAML acceleration.

CSafeLoader has the safe constructor policy of SafeLoader; never use yaml.Loader
or UnsafeLoader for untrusted MMP content.
"""
import yaml

_SAFE_LOADER = getattr(yaml, "CSafeLoader", yaml.SafeLoader)


def safe_load(stream):
    return yaml.load(stream, Loader=_SAFE_LOADER)
