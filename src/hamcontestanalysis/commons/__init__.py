"""Common package entrypoint."""

from functools import lru_cache

from pyhamtools import Callinfo
from pyhamtools import LookupLib


@lru_cache()
def get_call_info() -> Callinfo:
    """Get initialized call_info object."""
    call_info = Callinfo(LookupLib(lookuptype="countryfile"))
    return call_info


__all__ = [
    "get_call_info",
]
