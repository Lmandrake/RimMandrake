#!/usr/bin/env python3
"""Offline selftest of the pit rescue live driver (pit_rescue_live.py) against a fake bridge.

PIT_RESCUE_FIX_LADDER_UP_NOBODY_COMES (bridge run 1, 2026-10-23): RESCUE_COLONIST_OUT failed 2/2 because a rescuer lay down
in the victim's plain bed and so owned it; vanilla then had no bed for the victim and never offered the rescue. The fake
models exactly that engine rule (a sleeper claims a free NON-medical bed; a downed colonist is carried only to a medical bed
or an unowned one) and a tired rescuer who lies down at tick 500. Proves: (1) the scene's beds are made medical and read
back, so the tired rescuer claims nothing and the victim is carried out (all PASS) -- the old plain-bed driver goes red here;
(2) a refused medical write makes every row UNMEASURED SITE; (3) if a bed is still claimed (an engine that lets a sleeper
own a medical bed), the not-out verdict is SITE with the bed census, not MOD; (4) a fake where nobody rescues despite a
free bed stays FAIL MOD (the row can fail). A mock verdict is evidence about the DRIVER only, never about the mod.
"""
import contextlib
import io
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import pit_rescue_live as PRL  # noqa: E402

FAILS = []
TMP = tempfile.mkdtemp(prefix="pit_rescue_selftest_")
ORIGIN = (30, 30)


def check(name, cond, detail=""):
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, "" if cond else str(detail)[:300]))
    if not cond:
        FAILS.append(name)


class FakeV:
    @staticmethod
    def _wait_playing(B, leave_s=0):
        return True, None

    @staticmethod
    def site_calm(B):
        return {"ok": True}

    @staticmethod
    def prepare_site(B, rect, rows, name):
        rows.append({"id": name, "status": "PASS"})


class FakeBridge:
    """Just enough RimWorld for the driver: pawns, beds with owners, a ladder that builds, a rescue that needs a bed."""

    def __init__(self, faults=()):
        self.faults = set(faults)
        self.t = 0
        self.calls = []
        self.beds = {}      # id -> {cell, medical, owners[], occupant}
        self.pawns = {}     # id -> {x, z, downed}
        self.n = 0
        self.ladder = None
        self.sleeper = None

    def _id(self, pre):
        self.n += 1
        return "%s%d" % (pre, self.n)

    def _bed_for_patient(self, who):
        for b in self.beds.values():
            if b["occupant"] is None and (b["medical"] or not b["owners"] or who in b["owners"]):
                return b
        return None

    def _tick(self):
        pit = {(ORIGIN[0] + x, ORIGIN[1] + z) for x in range(6, 9) for z in range(4, 7)}
        if self.t >= 250 and self.ladder is None:
            self.ladder = "Blueprint_RM_LadderPortable"
        if self.t >= 1000:
            self.ladder = "RM_LadderPortable"
        for pid, p in self.pawns.items():
            if not p["downed"] or p.get("inBed"):
                continue
            in_pit = (p["x"], p["z"]) in pit
            due = 250 if not in_pit else 3000
            blocked = in_pit and ("nobody_rescues" in self.faults or self.ladder != "RM_LadderPortable")
            if self.t >= due and not blocked:
                b = self._bed_for_patient(pid)
                if b is not None:
                    b["occupant"] = pid
                    p["x"], p["z"] = b["cell"]
                    p["inBed"] = True
        if self.t >= 500 and self.sleeper is None and self.rescuers:
            self.sleeper = self.rescuers[0]
            for b in self.beds.values():
                claimable = not b["medical"] or "sleeper_claims_medical" in self.faults
                rests = b["medical"] and "rescuer_rests_in_medical" in self.faults
                if b["occupant"] is None and not b["owners"] and (claimable or rests):
                    if claimable:
                        b["owners"].append(self.sleeper)
                    b["occupant"] = self.sleeper
                    self.pawns[self.sleeper]["x"], self.pawns[self.sleeper]["z"] = b["cell"]
                    self.pawns[self.sleeper]["lying"] = True
                    break

    @property
    def rescuers(self):
        return [pid for pid, p in self.pawns.items() if not p["downed"]]

    def call(self, tool, **kw):
        self.calls.append((tool, kw))
        if tool == "rimworld/step_game_ticks":
            for _ in range(kw["ticks"] // 250):
                self.t += 250
                self._tick()
            return {"ok": True}
        if tool == "jawa/spawn_pawn":
            pid = self._id("Human")
            self.pawns[pid] = {"x": kw["x"], "z": kw["z"], "downed": False}
            return {"pawns": [{"id": pid}]}
        if tool == "jawa/pawn_force_incapacitate":
            p = self.pawns.get(kw.get("pawn"))
            if p is not None and kw.get("action") == "downed":
                p["downed"] = True
            elif p is not None and kw.get("action") == "vanish":
                del self.pawns[kw["pawn"]]
            return {"success": True}
        if tool == "jawa/list_pawns":
            return {"pawns": [{"id": k, "x": p["x"], "z": p["z"], "downed": p["downed"], "dead": False, "spawned": True,
                               "isPlayer": True} for k, p in self.pawns.items()]}
        if tool == "jawa/build_batch":
            x, z = (int(v) for v in kw["ops"].split(":")[1].split(",")[:2])
            bid = self._id("Bed")
            self.beds[bid] = {"cell": (x, z), "medical": False, "owners": [], "occupant": None}
            return {"ok": True}
        if tool == "jawa/list_things":
            if kw.get("defName") == "Bed":
                x, z = (int(v) for v in kw["rect"].split(",")[:2])
                return {"things": [{"id": k} for k, b in self.beds.items() if b["cell"] == (x, z)]}
            if self.ladder:
                return {"things": [{"def": self.ladder, "x": ORIGIN[0] + 7, "z": ORIGIN[1] + 6}]}
            return {"things": []}
        if tool == "jawa/set_bed_owner_type":
            if kw.get("thing") is None:
                if "no_census" in self.faults:
                    return {}
                return {"mode": "census", "beds": [{"thingId": k, "medical": b["medical"], "owners": len(b["owners"]),
                                                    "sleepingSlots": 1, "pos": {"x": b["cell"][0], "z": b["cell"][1]}} for k, b in self.beds.items()]}
            b = self.beds[kw["thing"]]
            if kw.get("medical") == "true" and "medical_refused" not in self.faults:
                b["medical"] = True
                b["owners"] = []
            return {"mode": "set", "medicalAfter": b["medical"]}
        if tool == "jawa/attack_target_probe":
            p = self.pawns.get(kw["pawn"]) or {}
            return {"position": {"x": p.get("x"), "z": p.get("z")}, "curJob": "LayDown" if p.get("lying") else "Wait"}
        return {"ok": True}


def run(faults=()):
    B = FakeBridge(faults)
    out = os.path.join(TMP, "r_%d.json" % len(os.listdir(TMP)))
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = PRL.main([out, "--ticks", "6000"], bridge=B, validation=FakeV)
    res = json.load(open(out, encoding="utf-8"))
    return code, {r["id"]: (r["status"], r["class"]) for r in res["rows"]}, res, B


# (1) the run-1 scene: a tired rescuer lies down at 500; with medical beds the victim is still carried out
code, rows, res, B = run()
bed_writes = [kw for t, kw in B.calls if t == "jawa/set_bed_owner_type" and kw.get("thing")]
check("every scene bed is set medical", len(bed_writes) == 2 and all(kw.get("medical") == "true" for kw in bed_writes), bed_writes)
check("medical read back into the scene", [b.get("medicalAfter") for b in res["scene"]["beds"]] == [True, True], res["scene"])
check("tired rescuer claims no bed", all(not b["owners"] for b in B.beds.values()), B.beds)
IDS = ("RESCUE_LADDER_QUEUED", "RESCUE_LADDER_BUILT", "RESCUE_COLONIST_OUT")
check("clean run: all three rows PASS", rows == {k: ("PASS", "MOD") for k in IDS}, rows)
check("clean run exits 0", code == 0, code)
check("bed census in the result", len((res.get("beds") or {}).get("beds") or []) == 2, res.get("beds"))

# (2) the medical write is refused: nothing about the mod can be read
code, rows, res, B = run({"medical_refused"})
check("refused medical: every row UNMEASURED SITE", rows and all(v == ("UNMEASURED", "SITE") for v in rows.values())
      and len(rows) == 3, rows)

# (3) a sleeper still owns a bed: not out is the scene's (SITE), with the census as evidence
code, rows, res, B = run({"sleeper_claims_medical"})
check("claimed bed: COLONIST_OUT is UNMEASURED SITE", rows.get("RESCUE_COLONIST_OUT") == ("UNMEASURED", "SITE"), rows)
check("claimed bed: free patient beds < 2 recorded",
      res["rows"][-1]["detail"].get("freePatientBeds", 9) < 2, res["rows"][-1]["detail"])

# (4) beds free, nobody rescues: the row can still fail as the mod's
code, rows, res, B = run({"nobody_rescues"})
check("nobody rescues with beds free: COLONIST_OUT FAIL MOD", rows.get("RESCUE_COLONIST_OUT") == ("FAIL", "MOD"), rows)

# (5) an injured rescuer rests in an unowned medical bed: still no bed for the victim, so SITE, not MOD
code, rows, res, B = run({"rescuer_rests_in_medical"})
check("rescuer lying in a medical bed: COLONIST_OUT is UNMEASURED SITE",
      rows.get("RESCUE_COLONIST_OUT") == ("UNMEASURED", "SITE"), rows)

# (6) the census call returns nothing: the bed guard cannot see, so the verdict is the harness's, never FAIL MOD
code, rows, res, B = run({"nobody_rescues", "no_census"})
check("no bed census: COLONIST_OUT is UNMEASURED HARNESS",
      rows.get("RESCUE_COLONIST_OUT") == ("UNMEASURED", "HARNESS"), rows)

# free_patient_beds unit
check("free_patient_beds counts beds with an unowned slot only",
      PRL.free_patient_beds({"beds": [{"medical": True, "owners": 1, "sleepingSlots": 1},
                                      {"medical": True, "owners": 0, "sleepingSlots": 1},
                                      {"medical": False, "owners": 1, "sleepingSlots": 1},
                                      {"medical": False, "owners": 0, "sleepingSlots": 1}, {}]}) == 2)
check("free_patient_beds skips a bed a rescuer lies in",
      PRL.free_patient_beds({"beds": [{"owners": 0, "sleepingSlots": 1, "pos": {"x": 1, "z": 2}},
                                      {"owners": 0, "sleepingSlots": 1, "pos": {"x": 3, "z": 2}}]},
                            PRL.lying_cells({"rescuers": [["a", {"x": 1, "z": 2}, "LayDownResting"], ["b", None, "Wait"]]})) == 1)

print("%s %d fail" % ("FAIL" if FAILS else "OK", len(FAILS)))
sys.exit(1 if FAILS else 0)
