"""settings_registry.py -- the ONE typed table of FlowWorks' Mod Settings for the harness (hose port step 4, design FINAL
§3.10, G5.10 / G6.1).

Each row: key (the harness name = the C# field), owning settings class, field name, Scribe key, shipped default, flip value.
Built from site_spec.SETTINGS (the shipped defaults, which selftest_flowworks_northstar re-reads from the C#) plus the
Scribe keys parsed from each section's C# source (the hose section saves under a `hose_` prefix, so key != Scribe key).
The flip value of a bool is its negation; a number has none (a numeric row is changed only with an explicit value).

Consumers: extensions.py derives SETTINGS_OF / DEFAULTS for its toggles from here; validation_v2.py's defaults tables and
site_spec.toggles() are asserted equal to it (selftest_settings_registry.py). `all_off()` is the every-switch-off fixture
(machinery, river, river-steam and hose switches included); internal migration flags are never in it.
"""
import os
import re

import site_spec as S

SRC = os.path.join(S.MOD_DIR, "Source")
_SCRIBE = re.compile(r'Scribe_Values\.Look\(ref (\w+), "(\w+)"')


def _scribe_keys(cls):
    rel = S.SETTINGS_SOURCES[cls]
    text = open(os.path.join(SRC, rel), encoding="utf-8").read()
    body = text[text.index("class %s" % cls.rsplit(".", 1)[1]):]
    out = {}
    for field, key in _SCRIBE.findall(body):
        out.setdefault(field, key)
    return out


def build():
    rows = []
    for cls, fields in S.SETTINGS.items():
        keys = _scribe_keys(cls)
        for f, v in fields.items():
            rows.append({"key": f, "cls": cls, "field": f, "scribe": keys.get(f), "default": v,
                         "flip": (not v) if isinstance(v, bool) else None,
                         "internal": f in S.INTERNAL_FLAGS})
    return rows


ROWS = build()
BY_KEY = {r["key"]: r for r in ROWS}


def settings_of(keys=None):
    """key -> owning settings class (all keys, or the given ones)."""
    return {r["key"]: r["cls"] for r in ROWS if keys is None or r["key"] in keys}


def defaults(keys=None):
    return {r["key"]: r["default"] for r in ROWS if keys is None or r["key"] in keys}


def flip(key):
    return BY_KEY[key]["flip"]


def toggles():
    """Every player-facing bool switch (internal flags excluded): equals site_spec.toggles()."""
    return sorted(r["key"] for r in ROWS if isinstance(r["default"], bool) and not r["internal"])


def all_off():
    """(cls, field, False) for every switch: the all-off fixture."""
    return [(r["cls"], r["field"], False) for r in ROWS if isinstance(r["default"], bool) and not r["internal"]]
