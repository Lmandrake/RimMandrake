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


def load_conf(path=CONF_PATH):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def profile_path(conf):
    return os.environ.get("RM_COMPANION_PROFILE") or conf["profile_file"]


# The grant's one timestamp shape: an extended ISO date AND time (seconds, fraction and offset optional). Checked
# before fromisoformat, which on 3.11+ also takes compact and date-only forms: str(20261101) would parse as a
# midnight expiry and a malformed grant would read OK (blind review 2026-10-29 #2). Anything else is LAPSED.
EXPIRES_RX = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(:\d{2}(\.\d{1,7})?)?(Z|[+-]\d{2}:\d{2})?$")


def _parse(ts):
    if not isinstance(ts, str) or not EXPIRES_RX.match(ts.strip()):
        raise ValueError("expiresUtc %r is not an ISO date-time string" % (ts,))
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
