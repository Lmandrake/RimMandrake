#!/usr/bin/env python3
"""Graffiti's spree rows must not stop on their OWN forced spree (GRAFFITI_NORTHSTAR_GREEN_FULL_1, test pilot gen 11).

Live A2 run 2026-11-03T14:36Z (/home/mandrake/rm/relentless/live/GRAFFITI_NORTHSTAR_GREEN_FULL_1-A2-20261103T143618Z.log,
results books/Transient/northstar/Graffiti_small_20261103T143624Z.json): mental_break_spree.mental_break_assigns_paint_job
read UNMEASURED "surprise: safe_advance stopped after 60 of 900 tick(s): mental: mental state RM_GraffitiPaintingSpreeState".
The row forces that break itself (jawa/pawn_force_mental_break), then waits. The companion's vitals latch reports any new
mental state of a colonist as kind 'mental', severity 'threat' (JawaBenchVitalsCore.cs, KMental), and
clockgate.resumable_stop resumes it only inside a declared clockgate.expected_disturbance. validation.py declares none,
so the row can never be measured: a HARNESS defect, deterministic, on every list.

This test drives the real chain bodies (mental_break_spree, spree_wall) against a fake game. At every wait_ticks it asks
the REAL clockgate.resumable_stop about the stop the live run saw (the painter's own spree), and about two stops that
must still stop the clock (another pawn's Berserk; a painter's death). Green iff every painter's own spree stop is
resumable during the row's wait and neither control stop is. A control run declares the disturbance itself, so the
probe is shown able to go green.
"""
import contextlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
UTILS = os.path.join(ROOT, "src", "RimMandrake", "Utils")
for p in (UTILS, os.path.join(UTILS, "modcheck"), HERE):
    if p not in sys.path:
        sys.path.insert(0, p)

import clockgate                     # noqa: E402
import validation as V              # noqa: E402

SPREE = "RM_GraffitiPaintingSpreeState"


def _stop(trigs):
    return {"state": "stopped", "executed": 60, "stopBy": trigs[0], "triggers": list(trigs)}


def _mental(n, state=SPREE, sev="threat"):
    return {"kind": "mental", "severity": sev, "subjectId": n, "detail": "mental state %s" % state}


class FakeT:
    """Just enough of modcheck's suite object for the two chain bodies."""

    def __init__(self, wrap_wait=None):
        self.anchor = (100, 100)
        self.upstream_failed, self.upstream_reason = False, None
        self._current = type("C", (), {"detail": ""})()
        self.pre = object()
        self.painters = []          # thing numbers of pawns the chain spawned
        self.waits = []             # (n, own_resumable, berserk_resumable, death_resumable)
        self.wrap_wait = wrap_wait
        self._next = 5000

    def _guard(self):
        return True

    @contextlib.contextmanager
    def component(self, name, toggle=None, beyond_toggle=False, shows=None):
        try:
            yield
        except Exception:            # noqa: BLE001 - only the waits are under test
            pass

    def clear_area(self, size=40):
        return None

    def screenshot(self, *a, **k):
        return None

    def _pawn(self):
        self._next += 1
        self.painters.append(self._next)
        return "Human%d" % self._next

    def spawn_pawn(self, kindDef, hostile=False, beyond=None):
        return self._pawn()

    def bridge_call(self, tool, **kw):
        if tool == "jawa/spawn_pawn":
            return {"pawns": [{"id": self._pawn()}]}
        if tool == "jawa/pawn_force_mental_break":
            return {"started": True, "mentalStateAfter": SPREE}
        if tool == "jawa/list_things":
            return {"things": [], "isCompleteList": True}
        if tool == "jawa/list_pawns":
            return {"pawns": []}
        if tool == "jawa/running_mods":
            return {"packageIds": ["mandrake.rm.graffiti"]}
        return {"success": True}

    def _probe(self, n):
        own = all(clockgate.resumable_stop(_stop([_mental(p)])) for p in self.painters) and bool(self.painters)
        allown = bool(clockgate.resumable_stop(_stop([_mental(p) for p in self.painters]))) if self.painters else False
        berserk = bool(clockgate.resumable_stop(_stop([_mental(424242, "Berserk")])))
        death = bool(clockgate.resumable_stop(_stop([{"kind": "death", "severity": "damage",
                                                       "subjectId": self.painters[0] if self.painters else 1,
                                                       "detail": "died: Crush"}])))
        self.waits.append((n, own and allown, berserk, death))

    def wait_ticks(self, n):
        if self.wrap_wait:
            with self.wrap_wait(self):
                self._probe(n)
        else:
            self._probe(n)


def _chain(name):
    for nm, fn in V.suite.chains:
        if nm == name:
            return getattr(fn, "__wrapped__", fn)
    raise SystemExit("chain %s not in Graffiti's suite" % name)


def _declared(t):
    ids = set(t.painters)
    return clockgate.expected_disturbance(
        "control: painter's own forced spree",
        lambda tr: tr.get("kind") == "mental" and tr.get("subjectId") in ids
        and str(tr.get("detail", "")).endswith(SPREE))


def run(chain, wrap=None):
    t = FakeT(wrap)
    _chain(chain)(t)
    return t


def main():
    bad, lines = [], []
    for chain in ("mental_break_spree", "spree_wall"):
        # control: the probe CAN go green -- with the disturbance declared by the test itself
        c = run(chain, _declared)
        if not c.waits or not all(w[1] for w in c.waits):
            bad.append("%s control: even a declared expected_disturbance did not resume the own-spree stop "
                       "(probe blind): %s" % (chain, c.waits))
        if any(w[2] or w[3] for w in c.waits):
            bad.append("%s control: a Berserk/death stop was resumable under the control declaration" % chain)
        # the real code
        t = run(chain)
        if not t.waits:
            bad.append("%s: the chain never waited (probe saw nothing)" % chain)
        for n, own, berserk, death in t.waits:
            lines.append("%s wait_ticks(%d): own spree resumable=%s, other Berserk=%s, painter death=%s"
                         % (chain, n, own, berserk, death))
            if not own:
                bad.append("%s wait_ticks(%d): the painter's own %s stops safe_advance (no "
                           "clockgate.expected_disturbance declared) -> the row reads UNMEASURED on every run, as live "
                           "A2 2026-11-03T14:36Z" % (chain, n, SPREE))
            if berserk or death:
                bad.append("%s wait_ticks(%d): a stop that is NOT the row's own spree was resumable "
                           "(over-broad declaration): berserk=%s death=%s" % (chain, n, berserk, death))
    for ln in lines:
        print("  " + ln)
    for b in bad:
        print("FAIL " + b)
    print("selftest graffiti spree surprise: %s" % ("PASS" if not bad else "FAIL (%d)" % len(bad)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
