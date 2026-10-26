#!/usr/bin/env python3
"""selftest_sithline_settings_roundtrip.py -- SITHLINE_ROUNDTRIP_FIX_INT_WRITTEN_AS_FLOAT: drives validation.py's
live settings_roundtrip chain (the production chain body, not a copy) against a fake bridge whose
jawa/mod_settings_field parses a value the way JawaBenchModSettingsFieldTools.CoerceSettingsValue does
(bool.Parse / int.Parse / float.Parse, InvariantCulture). Every field must round-trip, and every written test value
must differ from the field's value so the round trip proves something. Offline; no game.

    python3 src/RimStarWars/SithLine/selftest_sithline_settings_roundtrip.py
"""
import contextlib
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import validation as V  # noqa: E402

FAILS = []


def check(name, cond, detail=""):
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, "" if cond else detail))
    if not cond:
        FAILS.append(name)


def _cs_parse(ty, raw):
    """C#'s strict parse for the four field kinds the tool coerces; None = the tool returns Fail."""
    s = str(raw).strip()
    if ty == "bool":
        return {"true": True, "false": False}.get(s.lower())
    if ty == "int":
        return int(s) if re.fullmatch(r"[+-]?\d+", s) else None
    try:
        return float(s)
    except ValueError:
        return None


def _cs_str(ty, v):
    if ty == "bool":
        return "True" if v else "False"
    if ty == "int":
        return str(int(v))
    return "%g" % float(v)


class FakeSession(object):
    def __init__(self, fields, values):
        self.fields, self.values, self.writes = fields, dict(values), []

    def call(self, tool, **p):
        assert tool == "jawa/mod_settings_field", tool
        f = p["field"]
        if f not in self.fields:
            return {"success": False, "message": "no such field"}
        ty = self.fields[f]
        if p.get("action") == "set":
            v = _cs_parse(ty, p.get("value"))
            if v is None:
                return {"success": False, "message": "Could not coerce '%s' to %s" % (p.get("value"), ty)}
            self.writes.append((f, _cs_str(ty, self.values[f]), _cs_str(ty, v)))
            self.values[f] = v
        return {"success": True, "value": _cs_str(ty, self.values[f])}


class FakeT(object):
    """The slice of modcheck's chain probe the settings chain touches; no upstream latch, so every field reports."""

    def __init__(self, session):
        self.session, self.upstream_failed, self.results = session, False, {}

    @contextlib.contextmanager
    def component(self, name, **_kw):
        try:
            yield
            self.results[name] = None
        except V.ExpectationFailed as e:
            self.results[name] = str(e)


def run(values):
    fields = V.settings_fields()
    sess = FakeSession(fields, values)
    t = FakeT(sess)
    chain = dict(V.suite.chains)["settings_roundtrip"]
    chain(t)
    return fields, sess, t


def main():
    if V.suite is None:
        check("modcheck importable", False, "validation.suite is None (modcheck import failed)")
        return 1
    fields = V.settings_fields()
    check("sanity: the settings probe sees an int field", "int" in fields.values(), repr(fields))
    shipped = {"bool": True, "int": 12, "float": 0.25}
    for label, vals in (("shipped-like values", {f: shipped[ty] for f, ty in fields.items()}),
                        ("all-zero values", {f: (False if ty == "bool" else 0) for f, ty in fields.items()})):
        _f, sess, t = run(vals)
        check("%s: every field has a component" % label, len(t.results) == len(fields), repr(sorted(t.results)))
        bad = dict((n, r) for n, r in t.results.items() if r is not None)
        check("%s: every field round-trips through a strict C# parse" % label, not bad, repr(bad))
        vacuous = [f for f, before, written in sess.writes if before == written]
        check("%s: every test write differs from the field's value" % label, not vacuous, repr(vacuous))
        check("%s: every field restored" % label, sess.values == vals, repr(sess.values))
    print("sithline settings roundtrip: %d failure(s) -> %s" % (len(FAILS), "OK" if not FAILS else "FAILED"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
