#!/usr/bin/env python3
"""selftest_trophycraft_validation_chains.py -- TROPHYCRAFT_VALIDATION_FIX_SKIPPED_ROWS: validation.py's chains must
record every row with its own verdict. Through modcheck's real TestContext on a fake bridge (no game):
  * crafting: when every read passes, all five rows are recorded (a `return` inside a `with` row left the whole chain,
    so a PASS on the products row dropped the layer and pendant rows from the record);
  * fang_drop: the fang is read from RM_Ollathrix, the patch's only target (the old chain read the deleted donor
    Wyyyschokk: a false FAIL); with Webwork absent the row is UNMEASURED and the unpatched control still runs;
  * defs_resolve: the absent donor is no FAIL;
  * social_thought: three declared UNMEASURED rows each carry their OWN reason, not the first row's.
Offline.

    python3 src/RimStarWars/TrophyCraft/selftest_trophycraft_validation_chains.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import validation as V  # noqa: E402
from modcheck.suite import TestContext  # noqa: E402

FAILS = []
ANIMAL = "RM_Ollathrix"    # the patch target, spelled here so the test also runs against a pre-fix validation.py


def check(name, cond, detail=""):
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, "" if cond else detail))
    if not cond:
        FAILS.append(name)


class Fake(object):
    """get_defs answered by def name; `animal` False hides RM_Ollathrix (Webwork not loaded); the donor never loads."""

    def __init__(self, animal=True, thought_gap=False):
        self.animal, self.thought_gap = animal, thought_gap

    def track(self, *a, **k):
        pass

    def call(self, tool, **p):
        if tool != "jawa/get_defs":
            return {"success": True}
        d = p.get("defs", "")
        absent = {"success": True, "foundCount": 0, "notFound": [d]}
        if d == V.CONTROL_ABSENT or d == "ThingDef/Wyyyschokk" or (d == "ThingDef/" + ANIMAL and not self.animal):
            return absent
        if ";" in d:
            return {"success": True, "foundCount": len(d.split(";"))}
        f = {}
        if d == "RecipeDef/" + V.RECIPE:
            f = {"workAmount": 400, "products": [V.PENDANT], "ingredients": [{"filter": {"thingDefs": [V.FANG]}}]}
        elif d == "RecipeDef/Make_Patchleather":
            f = {"workAmount": 1000}
        elif d == "ApparelLayerDef/" + V.LAYER:
            f = {"drawOrder": 150}
        elif d == "ThingDef/" + V.PENDANT:
            f = {"apparel": {"layers": [V.LAYER]}}
        elif d == "ThingDef/" + ANIMAL:
            f = {"butcherProducts": ["Hyperweave", V.FANG]}
        elif d == "ThingDef/Wolf_Timber":
            f = {"butcherProducts": []}
        elif d == "ThoughtDef/" + V.THOUGHT:
            f = ({"thoughtClass": "(no such field)", "workerClass": "(no such field)"} if self.thought_gap else
                 {"thoughtClass": V.NS + "RSW_Thought_ObserverBraveFang",
                  "workerClass": V.NS + "RSW_ThoughtWorker_ObserverFactionApparel"})
        return {"success": True, "foundCount": 1, "defs": [{"defName": d.split("/")[-1], "fields": f}]}


def run(chain, **kw):
    t = TestContext(Fake(**kw))
    dict(V.suite.chains)[chain](t)
    return [(c.name, c.verdict, c.detail) for c in t.components]


def main():
    if V.suite is None:
        check("modcheck importable", False)
        return 1
    v = run("crafting")
    check("crafting records all five rows", len(v) == 5, repr([x[0] for x in v]))
    check("crafting: every row PASSes on a good def set", [x[1] for x in v] == ["PASS"] * 5, repr(v))

    v = run("fang_drop")
    check("fang_drop records both rows", len(v) == 2, repr(v))
    check("fang_drop PASSes when RM_Ollathrix carries the fang", [x[1] for x in v] == ["PASS", "PASS"], repr(v))

    v = run("fang_drop", animal=False)
    check("Webwork absent: the fang row is UNMEASURED and says why",
          bool(v) and v[0][1] == "UNMEASURED" and "webwork" in str(v[0][2]).lower(), repr(v[:1]))
    check("Webwork absent: the unpatched control still runs and PASSes", len(v) == 2 and v[1][1] == "PASS", repr(v))

    v = run("defs_resolve")
    check("defs_resolve has no FAIL without the donor", v and all(x[1] == "PASS" for x in v), repr(v))

    v = run("social_thought", thought_gap=True)
    check("social_thought records three UNMEASURED rows", [x[1] for x in v] == ["UNMEASURED"] * 3, repr(v))
    if len(v) == 3:
        check("row 2 carries its own reason", "factionDefNames" in str(v[1][2]), str(v[1][2])[:160])
        check("row 3 carries its own reason", "opinion read" in str(v[2][2]), str(v[2][2])[:160])
    print("trophycraft validation chains: %d failure(s) -> %s" % (len(FAILS), "OK" if not FAILS else "FAILED"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
