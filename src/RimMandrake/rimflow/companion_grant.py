#!/usr/bin/env python3
"""companion_grant.py - reads the companion's test-profile grant, `<SaveData>\\JawaBench\\companion_profile.json`
(item COMPANION_GRANT_WIRE_LAPSES_AT_BEDTIME). It is the one reader used by:

  - ops_watch's `companion` family, which emits `companion.grant_hours_left`. An alarm target in
    ops_watch_rules.json fires before the grant lapses, which is the early warning.
  - `rimflow next` (cli._apply_grant_preflight). While the state is not OK, it withholds items whose needs are in
    `hold_needs`, so a seat (and the Dispatcher's --peek) is routed to other work instead of bouncing a live ticket.

States, per design/RimMandrake/companion_handshake.md ("absent, invalid, expired or unknown = campaign"):
  OK          profile in test_profiles and over hold_within_min left
  LAPSING     profile in test_profiles, under hold_within_min left
  LAPSED      expired, absent, torn, non-test profile, or no parseable expiresUtc (the companion reads it as campaign)
  UNMEASURED  the JawaBench folder itself cannot be seen (C: not mounted, path moved): blind, which also holds

This never writes the grant. Renewing it is not this program's call (see companion_grant.json `_why`).

    python3 src/RimMandrake/rimflow/companion_grant.py [--json]     exit 0 OK, 1 LAPSING/LAPSED, 2 UNMEASURED
"""
import datetime, json, os, re, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
CONF_PATH = os.path.join(HERE, "companion_grant.json")


# The `needs` values rimflow knows (priority.BY_GAME's keys; selftest_companion_grant pins the two equal). Mirrored,
# not imported: ops_watch imports this module top-level, outside the rimflow package.
KNOWN_NEEDS = ("offline", "deploy", "game-up", "bridge", "harvest", "owner")


def load_conf(path=CONF_PATH):
    """-> the config, VALIDATED. A malformed setting raises ValueError, never loads: every caller treats a raise as
    blind and holds (cli preflight -> default needs withheld; ops_watch -> grant_visible 0 -> GRANT_UNSEEN). Without
    this, hold_needs "bridge" became the needs ('b','r',...) and no live item was withheld (blind review 2 #2)."""
    with open(path, encoding="utf-8") as f:
        conf = json.load(f)
    if not isinstance(conf, dict):
        raise ValueError("%s is not a JSON object" % path)
    needs = conf.get("hold_needs")
    if (not isinstance(needs, list) or not needs
            or not all(isinstance(n, str) and n in KNOWN_NEEDS for n in needs)):
        raise ValueError("hold_needs %r must be a non-empty list of known needs %s" % (needs, KNOWN_NEEDS))
    prof = conf.get("test_profiles")
    if not isinstance(prof, list) or not prof or not all(isinstance(x, str) and x for x in prof):
        raise ValueError("test_profiles %r must be a non-empty list of strings" % (prof,))
    hw = conf.get("hold_within_min")
    if isinstance(hw, bool) or not isinstance(hw, (int, float)) or not hw > 0:
        raise ValueError("hold_within_min %r must be a positive number" % (hw,))
    if not isinstance(conf.get("profile_file"), str) or not conf["profile_file"]:
        raise ValueError("profile_file %r must be a non-empty path" % (conf.get("profile_file"),))
    return conf


def profile_path(conf):
    return os.environ.get("RM_COMPANION_PROFILE") or conf["profile_file"]


# The grant's one timestamp shape: an extended ISO date AND time (seconds, fraction and offset optional). Checked
# before fromisoformat, which on 3.11+ also takes compact and date-only forms: str(20261101) would parse as a
# midnight expiry and a malformed grant would read OK (blind review 2026-10-29 #2). Anything else is LAPSED.
# Its parts are range-checked by name too: fromisoformat NORMALISES an out-of-range offset (-07:60 reads as -08:00)
# instead of refusing it, so a malformed grant would read OK an hour off (blind review 2 #1).
EXPIRES_RX = re.compile(r"^\d{4}-\d{2}-\d{2}T(?P<hh>\d{2}):(?P<mi>\d{2})(:(?P<ss>\d{2})(\.\d{1,7})?)?"
                        r"(Z|(?P<osign>[+-])(?P<oh>\d{2}):(?P<om>\d{2}))?$")


def _parse(ts):
    m = EXPIRES_RX.match(ts.strip()) if isinstance(ts, str) else None
    if not m:
        raise ValueError("expiresUtc %r is not an ISO date-time string" % (ts,))
    if (int(m["hh"]) > 23 or int(m["mi"]) > 59 or (m["ss"] is not None and int(m["ss"]) > 59)
            or (m["oh"] is not None and (int(m["oh"]) > 23 or int(m["om"]) > 59))):
        raise ValueError("expiresUtc %r has an out-of-range time or offset part" % (ts,))
    t = datetime.datetime.fromisoformat(ts.strip().replace("Z", "+00:00"))
    if t.tzinfo is None:
        t = t.replace(tzinfo=datetime.timezone.utc)
    return t.timestamp()


def read(path=None, now=None, conf=None):
    """-> {state, hours_left, expires, profile, file, why}. Never raises for the grant's own content."""
    conf = conf or load_conf()
    path = path or profile_path(conf)
    now = time.time() if now is None else now
    out = {"state": "LAPSED", "hours_left": 0.0, "expires": None, "profile": None, "file": path, "why": ""}
    if not os.path.isdir(os.path.dirname(path)):
        out.update(state="UNMEASURED", hours_left=None,
                   why="the grant's folder %s is not visible from here" % os.path.dirname(path))
        return out
    try:
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
    except FileNotFoundError:
        out["why"] = "no grant file: the companion runs campaign"
        return out
    except (OSError, ValueError) as e:
        out["why"] = "grant file unreadable (%s): the companion runs campaign" % type(e).__name__
        return out
    if not isinstance(d, dict):
        out["why"] = "grant file is not a JSON object: the companion runs campaign"
        return out
    out.update(profile=d.get("profile"), expires=d.get("expiresUtc"))
    if d.get("profile") not in conf["test_profiles"]:
        out["why"] = "profile %r is not a test profile" % d.get("profile")
        return out
    try:
        exp = _parse(d["expiresUtc"])
    except (KeyError, TypeError, ValueError):
        out["why"] = "expiresUtc %r is missing or unparseable" % d.get("expiresUtc")
        return out
    left = (exp - now) / 3600.0
    out["hours_left"] = left
    if left <= 0:
        out["why"] = "expired at %s" % d["expiresUtc"]
    elif left * 60 < conf["hold_within_min"]:
        out.update(state="LAPSING", why="lapses at %s, under hold_within_min %d min" % (d["expiresUtc"],
                                                                                        conf["hold_within_min"]))
    else:
        out.update(state="OK", why="lapses at %s" % d["expiresUtc"])
    return out


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    g = read()
    if "--json" in argv:
        print(json.dumps(g, indent=1))
    else:
        hl = "-" if g["hours_left"] is None else "%.1f h" % g["hours_left"]
        print("companion grant %s: %s left; %s (%s)" % (g["state"], hl, g["why"], g["file"]))
    return {"OK": 0, "UNMEASURED": 2}.get(g["state"], 1)


if __name__ == "__main__":
    sys.exit(main())
