"""A disk cache for the model's slow, repeated results (2026-11-25): the all-favourable search (scenarios.all_favourable) and the
Monte Carlo draws (scenarios.scenario_mc). The page's build and the tests ask for the same ones again and again.

A result is kept under a key that hashes everything it can depend on: the text of every model module (*.py beside this one), the
value of every input in the registry, and the call's own arguments. Any change to any of them is a new key, so a kept result is
never stale. Files live in .cache/ beside this module (ignored by git); CM_NO_CACHE=1 turns the cache off. Writes are atomic,
so tests running side by side never read half a file. CI keeps the folder between runs (.github/workflows/tests.yml).
"""
from __future__ import annotations

import glob
import hashlib
import os
import pickle
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, ".cache")
_CODE: list = [None]               # the hash of the model's modules, once a process (they do not change while it runs)


def _code_hash() -> bytes:
    if _CODE[0] is None:
        h = hashlib.sha256()
        for f in sorted(glob.glob(os.path.join(HERE, "*.py"))):
            with open(f, "rb") as fh:
                h.update(os.path.basename(f).encode() + b"\0" + fh.read())
        _CODE[0] = h.digest()
    return _CODE[0]


def key(*args) -> str:
    """The key of a result: the model's modules, every input's value now, and `args` (their repr)."""
    import inputs as I
    h = hashlib.sha256(_code_hash())
    h.update(repr(sorted((k, repr(v.value)) for k, v in I.REGISTRY.items())).encode())
    h.update(repr(args).encode())
    return h.hexdigest()[:32]


def load(kind: str, k: str):
    if os.environ.get("CM_NO_CACHE"):
        return None
    try:
        with open(os.path.join(ROOT, kind, k + ".pkl"), "rb") as fh:
            return pickle.load(fh)
    except (OSError, EOFError, KeyError, TypeError, pickle.UnpicklingError, AttributeError, ImportError):
        return None


def save(kind: str, k: str, value) -> None:
    if os.environ.get("CM_NO_CACHE"):
        return
    try:
        d = os.path.join(ROOT, kind)
        os.makedirs(d, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=d, suffix=".tmp")
        with os.fdopen(fd, "wb") as fh:
            pickle.dump(value, fh)
        os.replace(tmp, os.path.join(d, k + ".pkl"))
    except OSError:
        pass
