#!/usr/bin/env python3
"""The live check sc_switch_light (northstar/scene_rows.switch_light, bar switch_light_reads_state) against a fake game, offline.

A live check that has only ever been run on a good game proves nothing. Here a fake bridge plays the game: it keeps two batteries, the
switch and the switchLight setting, and answers the probe verbs the scene uses (battery:, flick:, set:, switchlights) with a lamp from a
lamp rule. On the shipped rule (green closed+powered, red open+powered, dark unpowered or setting off) every row must PASS; on each
planted wrong game (colours swapped, a lamp stuck at its first reading, the far side never read, the setting ignored) at least one row
must FAIL; on a probe that cannot answer every row must be UNMEASURED, never PASS. Exit 0 PASS, 1 FAIL.

    python3 src/RimMandrake/GimmeSomeSlack/selftest_gss_switch_light_scene.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "northstar"))
import scene_rows as S  # noqa: E402


def good(closed, west, east, setting):
    if not setting or not (west or east):
        return "Dark"
    return "Green" if closed else "Red"


class Fake:
    def __init__(self, rule, answer=True):
        self.rule, self.answer = rule, answer
        x, z = S.SC0
        self.sw, self.bw, self.be = (x + 10, z + 5), (x + 2, z + 4), (x + 19, z + 4)
        self.full = {self.bw: False, self.be: False}
        self.closed, self.setting, self.first = True, True, None

    def call(self, *a, **k):
        return {"success": True}

    def ticks(self, n):
        pass

    def probe(self, cmd):
        if cmd.startswith("battery:"):
            at, how = cmd[8:].split("=")
            self.full[tuple(int(v) for v in at.split(","))] = how == "full"
            return {"success": True}
        if cmd.startswith("flick:"):
            self.closed = cmd.endswith("=on")
            return {"success": True, "on": self.closed}
        if cmd.startswith("set:switchLight="):
            self.setting = cmd.endswith("true")
            return {"success": True}
        if cmd == "switchlights":
            if not self.answer:
                return {"success": False, "error": "no probe"}
            lamp = self.rule(self, self.closed, self.full[self.bw], self.full[self.be], self.setting)
            return {"success": True, "setting": self.setting, "switches": [{"pos": list(self.sw), "lamp": lamp}]}
        return {"success": True}


class Row:
    @staticmethod
    def ops(d, cells):
        return ";".join("%s:%d,%d" % (d, x, z) for x, z in cells)

    @staticmethod
    def row(rows, rid, status, cls, detail):
        rows.append({"id": rid, "status": status, "class": cls, "detail": detail})


def run(rule, answer=True):
    rows = []
    S.switch_light(Fake(rule, answer), Row, rows)
    return {r["id"]: r["status"] for r in rows}


def stuck(f, c, w, e, s):
    v = good(c, w, e, s)
    f.first = f.first or v
    return f.first


PLANTED = {
    "colours swapped": lambda f, c, w, e, s: {"Green": "Red", "Red": "Green"}.get(good(c, w, e, s), "Dark"),
    "lamp stuck at its first reading (stale)": stuck,
    "the far (east) side never read": lambda f, c, w, e, s: good(c, w, False, s),
    "the setting ignored": lambda f, c, w, e, s: good(c, w, e, True),
    "no lamp at all (the base)": lambda f, c, w, e, s: "Dark",
}


def main():
    bad = []
    ok = run(lambda f, c, w, e, s: good(c, w, e, s))
    if sorted(ok) != sorted(S.SWITCH_LIGHT_ROWS) or any(v != "PASS" for v in ok.values()):
        bad.append("good game: %s" % ok)
    print("good game:", "all %d PASS" % len(ok) if not bad else ok)
    for name, rule in PLANTED.items():
        r = run(rule)
        caught = any(v == "FAIL" for v in r.values())
        print("planted [%s]: %s" % (name, "CAUGHT (%s)" % ", ".join(k for k, v in r.items() if v == "FAIL") if caught else "NOT CAUGHT"))
        if not caught:
            bad.append(name)
    blind = run(lambda f, c, w, e, s: good(c, w, e, s), answer=False)
    if any(v != "UNMEASURED" for v in blind.values()):
        bad.append("blind probe read as %s" % blind)
    print("blind probe:", "all UNMEASURED" if all(v == "UNMEASURED" for v in blind.values()) else blind)
    print("PASS" if not bad else "FAIL: %s" % bad)
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
