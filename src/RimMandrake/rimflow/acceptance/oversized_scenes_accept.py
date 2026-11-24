#!/usr/bin/env python3
"""Acceptance test of the per-mod tickets under RIMMANDRAKE_SHRINK_OVERSIZED_SCENES_IN_EVERY_MOD_AFTER_PYRE (owner,
2026-11-24). Written by the filing seat; the builder of a ticket does not edit it. The designs it reads:
design/specs/2026-11-24-oversized-scenes/table.md.

    python3 src/RimMandrake/rimflow/acceptance/oversized_scenes_accept.py <Mod> [--root DIR]
    exit 0  PASS: the small scenes are in and the oversized ones decide nothing
    exit 1  FAIL: each line names what is missing
    exit 2  UNMEASURED: a file it must read is absent or unreadable (never a pass)
    exit 3  no contract for that mod

In-game mods: the named small scenes stand in test_table.json, run on a small list, and decide their bar; each has an
entry function or a program on disk; the oversized scene decides nothing. Held mods: every scene of scenes.json that
carries `split_from` or `shrunk` has its entry function in the named script.
"""
import argparse
import json
import os
import re
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".."))
# bar -> the small scenes that must decide it; gone = scenes that must decide no bar; cmd = (test, text its command holds)
IN_GAME = {
    "FlowWorks": {"bars": {"walk_moat_season": ["sc_walk_reload", "sc_walk_switch", "sc_walk_second_order"],
                           "source_pays_and_refills": ["sc_source_draws", "sc_source_refills", "sc_lake_endless"]},
                  "gone": ["sc_walk", "sc_source_pays", "sc_garden"], "cmd": [("sc_hung_bridge", "--only posts")]},
    "ExplosiveKnockback": {"bars": {"walk_storeroom_raid": ["sc_save_in_air"]},
                           "gone": ["sc_walk_raid", "sc_walk_blasts", "sc_storeroom_bomb_pit"],
                           "cmd": [("sc_pit_fetch", "--ticks 5000")]},
    "GimmeSomeSlack": {"bars": {"walk_scavenger_base": ["sc_save_reload_wire_down"]}, "gone": ["sc_walk"], "cmd": []},
}
LOCKED_HELD = {     # scene that must be gone -> the scenes that replace it, in scenes.json and in the test table
    "Graffiti": {"sc_lived_in_soak": ["sc_mood_returns_to_zero", "sc_message_counts"],
                 "sc_walk": ["sc_marks_survive_reload", "sc_visit_orders"]},
    "LeaningScrub": {"sc_colony_walk": ["sc_claim_survives_reload", "sc_trip_orders"],
                     "floor_persistence": ["floor_reload_once", "floor_growth_offline"]},
}
DESIGNED = ("Contagion", "PyrelandsMechanics", "Cauldron", "FeverWood", "GelatinousSlime", "Stillsand")


class Blind(Exception):
    pass


def load(root, *parts):
    p = os.path.join(root, *parts)
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError) as e:
        raise Blind("%s: %s" % (p, e))


def has_entry(root, path, name):
    try:
        with open(os.path.join(root, path), encoding="utf-8", errors="replace") as f:
            return re.search(r"\bdef\s+%s\b" % re.escape(name), f.read()) is not None
    except OSError:
        return False


def in_game(root, mod, want):
    t = load(root, "design", "concepts", mod, "version", "test_table.json")
    tests, bars = t.get("tests"), t.get("bars")
    if not isinstance(tests, dict) or not isinstance(bars, list) or not tests or not bars:
        raise Blind("%s: test_table.json has no tests or no bars" % mod)
    dec = {b.get("id"): list(b.get("decides") or []) for b in bars if isinstance(b, dict)}
    out = []
    for bar, ids in sorted(want["bars"].items()):
        if bar not in dec:
            out.append("bar %s is not in the table" % bar)
            continue
        for i in ids:
            x = tests.get(i)
            if not isinstance(x, dict):
                out.append("%s is not in the table" % i)
                continue
            if i not in dec[bar]:
                out.append("%s does not decide %s" % (i, bar))
            if x.get("kind") == "live_full":
                out.append("%s runs on the full list" % i)
            if not x.get("cheaper_why"):
                out.append("%s carries no cheaper_why" % i)
            if not x.get("file") or not os.path.exists(os.path.join(root, x["file"])):
                out.append("%s: its file %r is not on disk" % (i, x.get("file")))
    for g in want["gone"]:
        out += ["%s still decides %s" % (g, b) for b, ids in sorted(dec.items()) if g in ids]
        if isinstance(tests.get(g), dict) and tests[g].get("stage") == "6":
            out.append("%s is still a Stage 6 test" % g)
    for i, text in want["cmd"]:
        c = (tests.get(i) or {}).get("command") or ""
        if text not in c:
            out.append("%s: its command does not hold %r" % (i, text))
    return out


def scenes(root, mod):
    s = load(root, "design", "concepts", mod, "scenes.json").get("scenes")
    if not isinstance(s, list) or not s:
        raise Blind("%s: scenes.json has no scenes" % mod)
    return {x["id"]: x for x in s if isinstance(x, dict) and x.get("id")}


def locked(root, mod, want):
    sc, t = scenes(root, mod), load(root, "design", "concepts", mod, "version", "test_table.json").get("tests") or {}
    out = []
    for old, new in sorted(want.items()):
        out += ["%s is still in %s" % (old, w) for w, d in (("scenes.json", sc), ("the test table", t)) if old in d]
        for n in new:
            out += ["%s is not in %s" % (n, w) for w, d in (("scenes.json", sc), ("the test table", t)) if n not in d]
    return out


def designed(root, mod):
    small = [x for x in scenes(root, mod).values() if x.get("split_from") or x.get("shrunk")]
    if not small:
        return ["scenes.json holds no shrunk scene"]
    out = []
    for x in small:
        path, _, name = str(x.get("entry_point") or "").partition("::")
        if not name or not has_entry(root, path, name):
            out.append("%s: entry point %s is not in the script" % (x["id"], x.get("entry_point")))
    return out


def check(root, mod):
    if mod in IN_GAME:
        return in_game(root, mod, IN_GAME[mod])
    if mod in LOCKED_HELD:
        return locked(root, mod, LOCKED_HELD[mod])
    if mod in DESIGNED:
        return designed(root, mod)
    return None


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("mod")
    ap.add_argument("--root", default=REPO)
    a = ap.parse_args(argv)
    try:
        got = check(a.root, a.mod)
    except Blind as e:
        print("UNMEASURED %s" % e)
        return 2
    if got is None:
        print("no contract for %s" % a.mod)
        return 3
    for g in got:
        print("FAIL %s: %s" % (a.mod, g))
    print("%s %s" % ("FAIL" if got else "PASS", a.mod))
    return 1 if got else 0


if __name__ == "__main__":
    sys.exit(main())
