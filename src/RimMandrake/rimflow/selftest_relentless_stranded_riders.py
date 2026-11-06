#!/usr/bin/env python3
"""PROOFYIELD_REPAIR_THREE_OF_THIRTEEN_MEASURED: a built item whose mods are not on the game rides a staging, and the owner's
24 h yield measure says HIGHER only when both fields beat the baseline."""
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import relentless_game as G     # noqa: E402
import relentless_live_round as LR     # noqa: E402

FAILS = []


def ok(cond, what):
    print(("ok   " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


def gap_row(item, admit="running_load", sha="aaaa11112222", crit="A2"):
    return {"at": "2026-11-06T20:58:00Z", "item": item, "criterion": crit, "sha": sha, "outcome": "NOT_ADMITTED",
            "admit": admit, "verdict": "INFRA", "why": "not in the running load: X"}


class Fx(object):
    def __init__(self, rows, led=None, preflight=None):
        self.rows, self.led, self.pre = rows, led or {}, preflight or {}
        self.text = "live-proof A2: python3 prove.py\n"

    def game_rows(self):
        return self.rows

    def game_ledger(self, item):
        return self.led.get(item, {"state": "built", "built_sha": "aaaa11112222", "title": "a mod thing", "owed": {"A2": "L1"}})

    def proofs_at(self, item, sha, ext=".txt"):
        return self.text

    def game_preflight(self, item, lines, sites=None):
        return self.pre.get(item, [])


def names(fx, states=(), item="LEAD", now=0):
    return [o["item"] for o in G.stranded_riders(fx, {}, list(states), item, now)]


def riders():
    ok(names(Fx([gap_row("HOSTILE")])) == ["HOSTILE"], "a running_load gap rides")
    ok(names(Fx([gap_row("FLAME", "deploy_gap")])) == ["FLAME"], "a deploy gap rides (not enabled, stale companion)")
    o = G.stranded_riders(Fx([gap_row("HOSTILE")]), {}, [], "LEAD", 0)[0]
    ok(o["game"]["sha"] == "aaaa11112222" and o["stranded"], "in others' shape, on the ledger's built sha")
    ok(not names(Fx([gap_row("LEAD")])), "the lead does not ride itself")
    ok(not names(Fx([gap_row("X", "stale")])), "a stale build is no staging's to end")
    ok(not names(Fx([gap_row("X", "full_list")])), "nor is a full-list hold")
    for status in ("running", "game", "checking"):
        ok(not names(Fx([gap_row("X")]), [{"item": "X", "status": status}]), "a %s item is moving: it does not ride" % status)
    for status in ("queued", "held", "blocked", "done"):
        ok(names(Fx([gap_row("X")]), [{"item": "X", "status": status}]) == ["X"], "a %s item rides: no phase stages it" % status)
    moved = {"X": {"state": "built", "built_sha": "bbbb00000000", "title": "t", "owed": {"A2": "L1"}}}
    ok(not names(Fx([gap_row("X")], moved)), "the ledger moved past the row's sha: its gap no longer says anything")
    closed = {"X": {"state": "done", "built_sha": "aaaa11112222", "title": "t", "owed": {"A2": "L1"}}}
    ok(not names(Fx([gap_row("X")], closed)), "a closed item owes no load")
    gone = {"X": {"state": "built", "built_sha": "aaaa11112222", "title": "t", "owed": {"A9": "L1"}}}
    ok(not names(Fx([gap_row("X")], gone)), "an item with no proof line for what it owes cannot use the load")
    fly = {"X": {"state": "built", "built_sha": "aaaa11112222", "title": "the flyer's flight", "owed": {"A2": "L1"}}}
    ok(not names(Fx([gap_row("X")], fly)), "never a flyer's flight")
    ok(not names(Fx([gap_row("X")], preflight={"X": [{"kind": "stale"}]})), "a refused preflight stays off")
    later = [gap_row("X"), dict(gap_row("X"), outcome="PASS", verdict="PASS", admit=None)]
    ok(not names(Fx(later)), "a judged clause no longer rides")
    fresh = Fx([gap_row("X")])
    fresh.proofs_at = lambda item, sha, ext=".txt": ""      # the lines landed after the build (lightspeed_wire)
    fresh._mods_text = lambda item, sha: "live-proof A2: python3 prove.py\n"
    ok(names(fresh) == ["X"], "it reads the books' current proof file, as the live run does")
    menu = Fx([gap_row("X")])
    menu.text += "live-menu: python3 record.py\n"
    ok(not names(menu), "a live-menu proof measures only on a staging of its own")
    toggle = Fx([gap_row("X")])
    toggle.text += "live-toggle: some.mod\n"
    ok(not names(toggle), "and so does a live-toggle pair")
    many = [gap_row("I%02d" % n) for n in range(10)]
    a, b = names(Fx(many), now=0), names(Fx(many), now=4 * 3600)
    ok(len(a) == G.STRANDED_RIDERS == len(b), "bounded: %d a staging" % G.STRANDED_RIDERS)
    ok(a != b and set(names(Fx(many), now=8 * 3600)) - set(a), "rotating: one rider's gap starves no other")


def yields():
    def rows(n, verdict, outcome, h=24):
        return [{"at": "2026-11-0%dT%02d:00:00Z" % (7 + (k * h // n) // 24, (k * h // n) % 24), "verdict": verdict,
                 "outcome": outcome} for k in range(n)] + [{"at": "2026-11-08T00:00:01Z"}]
    v, o = (154, 285), (79, 286)
    ok(LR.proof_yield(rows(100, "PASS", "PASS"), 24, v, o)[0] == 0, "both fields above: HIGHER")
    ok(LR.proof_yield(rows(100, "FAIL", "UNMEASURED"), 24, v, o)[0] == 1, "an UNMEASURED read as a verdict FAIL does not pass")
    ok(LR.proof_yield(rows(100, "INFRA", "NOT_ADMITTED"), 24, v, o)[0] == 1, "rows that measured nothing do not pass")
    ok(LR.proof_yield(rows(100, "PASS", "PASS", h=10)[:-1], 24, v, o)[0] == 2, "10 h is not 24: UNMEASURED, never a pass")
    ok(LR.proof_yield(rows(10, "PASS", "PASS"), 24, v, o)[0] == 2, "ten rows are too few to say")
    ok(LR.proof_yield([], 24, v, o)[0] == 2, "no rows: UNMEASURED")
    with tempfile.TemporaryDirectory() as t:
        src, dst = os.path.join(t, "runs.jsonl"), os.path.join(t, "snap.jsonl")
        with open(src, "w", encoding="utf-8") as f:
            f.write("\n".join(json.dumps(r) for r in rows(100, "PASS", "PASS")) + "\nnot json\n")
            f.write(json.dumps({"at": 1.5}) + "\n")
        cli = [sys.executable, os.path.join(HERE, "relentless_live_round.py"), "yield", "--rows", dst]
        got = subprocess.run(cli + ["--take", src, "--since", "2026-11-07T00:00:00Z"], capture_output=True, text=True)
        ok(got.returncode == 0 and os.path.getsize(dst) > 0, "--take copies the rows: " + got.stdout.strip()[-60:])
        got = subprocess.run(cli, capture_output=True, text=True)
        ok(got.returncode == 0 and got.stdout.startswith("HIGHER"), "the CLI measures the copy: " + got.stdout.strip()[:60])
        got = subprocess.run(cli[:-1] + [os.path.join(t, "absent.jsonl")], capture_output=True, text=True)
        ok(got.returncode == 2 and "UNMEASURED" in got.stdout, "no snapshot: exit 2, UNMEASURED")


if __name__ == "__main__":
    riders()
    yields()
    print("%d failed" % len(FAILS))
    sys.exit(1 if FAILS else 0)
