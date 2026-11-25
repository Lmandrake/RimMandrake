#!/usr/bin/env python3
"""companion_grant.py - reads the companion's test-profile grant, `<SaveData>\\JawaBench\\companion_profile.json`
(item COMPANION_GRANT_WIRE_LAPSES_AT_BEDTIME). It is the one reader used by:

  - ops_watch's `companion` family, which emits `companion.grant_test`. Its alarm target in ops_watch_rules.json
    fires when the file does not name a test profile.
  - `rimflow next` (cli._apply_grant_preflight). While the state is not OK, it withholds items whose needs are in
    `hold_needs`, so a seat (and the Dispatcher's --peek) is routed to other work instead of bouncing a live ticket.

`expiresUtc` is not read. The companion ignores it since f3c90ff50c, and all four games load a companion at or after
that commit (handshake read 2026-11-24, item RIMMANDRAKE_REMOVE_GRANT_EXPIRY_CHECKS_ONCE_FOUR_COMPANIONS_REDEPLOYED).

States, per design/RimMandrake/companion_handshake.md:
  OK          profile in test_profiles
  LAPSED      absent, torn, not an object, or a profile that is not a test profile (the companion reads it as campaign)
  UNMEASURED  the JawaBench folder itself cannot be seen (C: not mounted, path moved): blind, which also holds

This never writes the grant.

    python3 src/RimMandrake/rimflow/companion_grant.py [--json]     exit 0 OK, 1 LAPSED, 2 UNMEASURED
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
CONF_PATH = os.path.join(HERE, "companion_grant.json")


# The `needs` values rimflow knows (priority.BY_GAME's keys; selftest_companion_grant pins the two equal). Mirrored,
# not imported: ops_watch imports this module top-level, outside the rimflow package.
KNOWN_NEEDS = ("offline", "deploy", "game-up", "bridge", "harvest", "owner")
LIVE_NEEDS = ("bridge", "game-up")    # the needs that drive the live game: no valid config lets them through a lapsed grant


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
    if not set(LIVE_NEEDS) <= set(needs) or "offline" in needs:     # a hold that lets live work through, or hides offline
        raise ValueError("hold_needs %r must hold %s and never offline" % (needs, LIVE_NEEDS))
    prof = conf.get("test_profiles")
    if not isinstance(prof, list) or not prof or not all(isinstance(x, str) and x for x in prof):
        raise ValueError("test_profiles %r must be a non-empty list of strings" % (prof,))
    if not isinstance(conf.get("profile_file"), str) or not conf["profile_file"]:
        raise ValueError("profile_file %r must be a non-empty path" % (conf.get("profile_file"),))
    return conf


def profile_path(conf):
    return os.environ.get("RM_COMPANION_PROFILE") or conf["profile_file"]


def read(path=None, conf=None):
    """-> {state, profile, file, why}. Never raises for the grant's own content."""
    conf = conf or load_conf()
    path = path or profile_path(conf)
    out = {"state": "LAPSED", "profile": None, "file": path, "why": ""}
    if not os.path.isdir(os.path.dirname(path)):
        out.update(state="UNMEASURED", why="the grant's folder %s is not visible from here" % os.path.dirname(path))
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
    out["profile"] = d.get("profile")
    if d.get("profile") not in conf["test_profiles"]:
        out["why"] = "profile %r is not a test profile" % d.get("profile")
        return out
    out.update(state="OK", why="profile %r" % d.get("profile"))
    return out


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    g = read()
    if "--json" in argv:
        print(json.dumps(g, indent=1))
    else:
        print("companion grant %s: %s (%s)" % (g["state"], g["why"], g["file"]))
    return {"OK": 0, "UNMEASURED": 2}.get(g["state"], 1)


if __name__ == "__main__":
    sys.exit(main())
