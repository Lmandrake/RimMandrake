#!/usr/bin/env python3
"""LEANINGSCRUB_SWEETLINE_SHED_LIVE_1 offline proof: sweetline_shed_probe.py's verdict and its run against a fake bridge.

judge() must pass a healthy shed and fail each broken half the item names (0 felt, a timer still 'ready to fall', a tree
gone across the jump, a clock that did not move a Long tick, a new 'Exception ticking' line). main() is then run against
a fake bridge that models RM_CompSweetlineStation (shed woolCount felt on the first Long tick past the timer, reset the
timer) and once with the shed broken, so the probe's wiring (pad, jump, step, counts, log delta) is proven to see both.
Exit 0 when every case reads as expected."""
import os
import sys
import types

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sweetline_shed_probe as P  # noqa: E402

FAILS = []


def check(name, cond, detail=""):
    print("%s  %s %s" % ("PASS" if cond else "FAIL", name, detail))
    if not cond:
        FAILS.append(name)


GOOD = dict(before=0, after=5, moved=2100, standing=True, lines_after=["Loose sweetline felt falls in 5 days."],
            errors=[])


def j(**kw):
    a = dict(GOOD)
    a.update(kw)
    return P.judge(**a)


class FakeTree(object):
    def __init__(self, broken=False, throws=False, dies=False):
        self.ticks, self.felt, self.tree, self.next = 100000, 0, None, None
        self.broken, self.throws, self.dies, self.errors = broken, throws, dies, 3   # 3 old error lines in the buffer
        self.calls = []

    def _long_tick(self, a, b):
        for t in range(a + 1, b + 1):
            if t % 2000 == 0 and self.tree:
                if self.throws:
                    self.errors += 1
                    continue
                if t >= self.next:
                    self.next = t + 5 * 60000
                    if not self.broken:
                        self.felt += 5

    def call(self, tool, p):
        self.calls.append(tool)
        if tool == "jawa/get_terrain_batch":
            return {"success": True, "mapSize": {"x": 250, "z": 250}}
        if tool == "jawa/set_plants":
            self.tree = "Plant_RM_SweetlineTree1"
            self.next = self.ticks + 4 * 60000          # inside the first-shed stagger
            return {"success": True}
        if tool == "jawa/list_things":
            if p["defName"] == P.TREE:
                return {"success": True, "things": [{"id": self.tree}] if self.tree else []}
            return {"success": True, "things": [{"stackCount": self.felt}] if self.felt else []}
        if tool == "jawa/inspect_string":
            left = self.next - self.ticks
            line = "Loose sweetline felt ready to fall." if left <= 0 else "Loose sweetline felt falls in %d ticks." % left
            return {"success": True, "things": [{"inspect": [line]}]}
        if tool == "rimworld/get_game_info":
            return {"ticksGame": self.ticks}
        if tool == "jawa/time_set_ticks":
            self.ticks = p["ticks"]
            return {"success": True}
        if tool == "jawa/drain_log":
            return {"success": True, "messages": [{"text": "Exception ticking Plant_RM_SweetlineTree1", "repeats": self.errors}]}
        if tool in ("jawa/destroy_batch", "jawa/set_terrain_batch"):
            return {"success": True}
        raise AssertionError("unexpected tool %s" % tool)

    def advance(self, n):
        a = self.ticks
        self.ticks += n
        self._long_tick(a, self.ticks)
        if self.dies:
            self.tree = None


def run_main(fake):
    rb = types.ModuleType("rimbridge_client")
    rb.resolve_endpoint = lambda: ("h", 1, "t")

    class RB(object):
        def __init__(self, **k):
            pass

        def connect(self):
            pass

        def call(self, tool, p):
            return fake.call(tool, p)
    rb.RimBridge = RB
    cg = types.ModuleType("clockgate")
    cg.advance_chunk = lambda s, n, time_exception=False: fake.advance(n)
    saved = {k: sys.modules.get(k) for k in ("rimbridge_client", "clockgate", "helpers")}
    sys.modules.update({"rimbridge_client": rb, "clockgate": cg, "helpers": types.ModuleType("helpers")})
    try:
        return P.main()
    finally:
        for k, v in saved.items():
            if v is None:
                sys.modules.pop(k, None)
            else:
                sys.modules[k] = v


def main():
    check("judge: healthy shed passes", j()[0], j()[1])
    check("judge: 0 felt fails", not j(after=0)[0])
    check("judge: 4 felt fails", not j(after=4)[0])
    check("judge: timer still ready to fall fails", not j(lines_after=["Loose sweetline felt ready to fall."])[0])
    check("judge: no timer line fails", not j(lines_after=["Growth: 100%"])[0])
    check("judge: tree gone fails", not j(standing=False, lines_after=["<tree gone>"])[0])
    check("judge: short clock fails", not j(moved=600)[0])
    check("judge: unread clock fails", not j(moved=None)[0])
    check("judge: Exception ticking fails", not j(errors=["Exception ticking Plant_RM_SweetlineTree1"])[0])
    f = FakeTree()
    check("main: healthy fake tree exits 0", run_main(f) == 0)
    check("main: jumped the clock and destroyed its pad", "jawa/time_set_ticks" in f.calls
          and f.calls[-1] == "jawa/destroy_batch")
    check("main: broken shed exits 1", run_main(FakeTree(broken=True)) == 1)
    check("main: throwing tick exits 1 (old buffer lines alone do not)", run_main(FakeTree(throws=True)) == 1)
    check("main: tree dies across the jump exits 1", run_main(FakeTree(dies=True)) == 1)
    stall = FakeTree()
    stall.advance = lambda n: None
    check("main: a stalled clock exits 2 (UNMEASURED), never a verdict", run_main(stall) == 2)
    print("%d failure(s)" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
