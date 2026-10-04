"""In-memory Bacta for offline runs of validation.py (northstar_driver --mock, selftest_bacta_mock.py).

Models exactly the behaviours the suite asserts, from the mod's own source (CompBactaImmersion.cs, BactaHealingUtility.cs,
Building_BactaTank.cs, CompUseEffect_BactaHeal.cs). It is NOT evidence about the game: it proves the SCRIPT's logic and
that every check can go red. BACTA_MOCK_BREAK=<comma list> re-introduces one defect per mode:
  no_heal heal_when_off heals_brain regrows_part ignores_power no_drain no_eject no_needs_hold scar_when_off
  revival_when_off ignores_window droid_always field_ignores_toggle trader_missing recipes_missing
Dev tooling, never deployed.
"""
import os
import re

DEFAULTS = {"healingEnabled": "True", "scarErasureEnabled": "True", "infectionAssistEnabled": "True",
            "suspendNeedsEnabled": "True", "autoEjectEnabled": "True", "revivalEnabled": "False",
            "medicalDroidEnabled": "True", "fieldItemsEnabled": "True", "woundHealPerDay": "30",
            "scarHealPerDay": "2.4", "immunityGainPerDay": "0.3", "fluidCostPerDay": "5", "tendQuality": "0.85",
            "revivalWindowHours": "6", "medicalDroidHealMultiplier": "1.5", "fieldItemPotency": "1"}
BRAIN = "Brain"


def _breaks():
    return set(x for x in os.environ.get("BACTA_MOCK_BREAK", "").split(",") if x)


class Model(object):
    def __init__(self):
        self.n = 0
        self.things = {}       # id -> dict(id, def, x, z, stack, born)
        self.pawns = {}        # id -> dict
        self.settings = dict(DEFAULTS)
        self.power = {}        # thing id -> bool
        self.fuel = {}         # tank id -> float
        self.occ = {}          # tank id -> pawn id
        self.jobs = []
        self.phase = 0

    def nid(self, p):
        self.n += 1
        return "%s%d" % (p, self.n)

    def b(self, k):
        return self.settings[k].strip().lower() == "true"

    def f(self, k):
        return float(self.settings[k])

    # ---------------------------------------------------------------- tank logic
    def tank(self):
        for t in self.things.values():
            if t["def"] == "RSW_BactaTank":
                return t
        return None

    def droid_assists(self):
        d = [t for t in self.things.values() if t["def"] == "RSW_MedicalDroid"]
        if not d or not self.power.get(d[0]["id"]):
            return False
        return self.b("medicalDroidEnabled") or "droid_always" in _breaks()

    def powered(self, tid):
        return self.power.get(tid) or "ignores_power" in _breaks()

    def can_accept(self, tk):
        return (tk["id"] not in self.occ and self.powered(tk["id"]) and self.fuel.get(tk["id"], 0) > 0)

    def heal(self, pawn, brk):
        did = False
        wound = self.f("woundHealPerDay") * 250 / 60000.0
        scar = self.f("scarHealPerDay") * 250 / 60000.0
        for h in list(pawn["hediffs"]):
            if h["def"] == "MissingBodyPart":
                if "regrows_part" in brk:
                    pawn["hediffs"].remove(h)
                    did = True
                continue
            if h["part"] == BRAIN and "heals_brain" not in brk:
                continue
            if h.get("perm"):
                if not self.b("scarErasureEnabled") and "scar_when_off" not in brk:
                    continue
                h["severity"] -= scar
                did = True
            else:
                h["severity"] -= wound
                did = True
            if h["severity"] <= 0.001:
                pawn["hediffs"].remove(h)
        return did

    def eject(self, tk):
        pid = self.occ.pop(tk["id"], None)
        if pid:
            pw = self.pawns[pid]
            pw["in"] = None
            pw["x"], pw["z"] = tk["x"] + 1, tk["z"]

    def tank_pass(self):
        brk = _breaks()
        tk = self.tank()
        if not tk or tk["id"] not in self.occ:
            return
        tid = tk["id"]
        pawn = self.pawns[self.occ[tid]]
        if not self.powered(tid):
            return
        if self.fuel.get(tid, 0) <= 0:
            if self.b("autoEjectEnabled") and "no_eject" not in brk:
                self.eject(tk)
            return
        if not self.b("healingEnabled") and "heal_when_off" not in brk:
            return
        if "no_heal" in brk:
            did = False
        else:
            did = self.heal(pawn, brk)
        if did:
            if "no_drain" not in brk:
                self.fuel[tid] = max(0.0, self.fuel[tid] - self.f("fluidCostPerDay") * 250 / 60000.0)
        elif self.b("autoEjectEnabled") and "no_eject" not in brk:
            self.eject(tk)

    def advance(self, n, game):
        brk = _breaks()
        self.resolve_jobs(game, brk)
        for _ in range(int(n)):
            game.ticks += 1
            self.phase += 1
            if self.phase % 250 == 0:
                self.tank_pass()
            tk = self.tank()
            for pw in self.pawns.values():
                if pw.get("dead"):
                    continue
                held = tk and self.occ.get(tk["id"]) == pw["id"] and self.b("suspendNeedsEnabled") \
                    and "no_needs_hold" not in brk
                if not held:
                    pw["food"] = max(0.0, pw["food"] - 0.000027)

    def resolve_jobs(self, game, brk):
        jobs, self.jobs = self.jobs, []
        for j in jobs:
            pw = self.pawns.get(j["pawn"])
            if not pw or pw.get("dead"):
                continue
            tk = self.tank()
            if j["job"] == "Refuel" and tk:
                st = self.things.get(j["b"])
                if st:
                    amt = min(st["stack"], 30 - self.fuel.get(tk["id"], 0))
                    self.fuel[tk["id"]] = self.fuel.get(tk["id"], 0) + amt
                    st["stack"] -= amt
                    if st["stack"] <= 0:
                        del self.things[st["id"]]
            elif j["job"] == "EnterBuilding" and tk and self.can_accept(tk):
                pw["in"] = tk["id"]
                self.occ[tk["id"]] = pw["id"]
            elif j["job"] == "UseItem":
                it = self.things.get(j["a"])
                if it and (self.b("fieldItemsEnabled") or "field_ignores_toggle" in brk):
                    amt = 6 * self.f("fieldItemPotency")
                    for h in list(pw["hediffs"]):
                        if h["def"] != "MissingBodyPart" and h["part"] != BRAIN and not h.get("perm"):
                            h["severity"] -= amt
                            if h["severity"] <= 0.001:
                                pw["hediffs"].remove(h)
                    del self.things[it["id"]]
            elif j["job"] == "RSW_CarryCorpseToBactaTank" and tk:
                c = self.things.get(j["a"])
                if not c or c["def"] != "Corpse":
                    continue
                age = game.ticks - c["born"]
                window = self.f("revivalWindowHours") * 2500
                if (self.b("revivalEnabled") or "revival_when_off" in brk) \
                        and (age <= window or "ignores_window" in brk) and self.can_accept(tk):
                    victim = self.pawns[c["pawn"]]
                    victim["dead"] = False
                    victim["in"] = tk["id"]
                    self.occ[tk["id"]] = victim["id"]
                    del self.things[c["id"]]


# ---------------------------------------------------------------- tool dispatch

def _rect(s):
    return [int(v) for v in str(s).split(",")]


def _in(x, z, r):
    return r[0] <= x < r[0] + r[2] and r[1] <= z < r[1] + r[3]


def _snap(pw):
    return {"thingId": pw["id"], "position": None if pw["in"] or pw["x"] is None else {"x": pw["x"], "z": pw["z"]},
            "hediffs": [{"def": h["def"], "part": h["part"], "severity": h["severity"]} for h in pw["hediffs"]],
            "needs": [{"need": "Food", "level": pw["food"]}, {"need": "Rest", "level": 1.0}]}


def mock_extension(game, tool, p):
    bm = getattr(game, "bm", None)
    if bm is None:
        bm = game.bm = Model()
    brk = _breaks()
    ok = {"success": True}

    if tool == "jawa/mod_settings_field":
        k = p["field"]
        if k not in bm.settings:
            return {"success": False, "message": "no field " + k}
        if p.get("action") == "set":
            bm.settings[k] = str(p["value"])
        return {"success": True, "value": bm.settings[k]}
    if tool == "jawa/get_defs":
        return _get_defs(p, brk)
    if tool == "jawa/get_def":
        return _get_def(p)
    if tool == "jawa/drain_log":
        return {"success": True, "messages": []}
    if tool == "jawa/destroy_batch":
        r = _rect(p["rects"])
        cats = str(p.get("categories") or "")
        for tid in [i for i, t in bm.things.items() if _in(t["x"], t["z"], r)]:
            if cats in ("All", "Item", "Building", "Filth"):
                del bm.things[tid]
        return ok
    if tool == "jawa/build_batch":
        n = 0
        for op in str(p["ops"]).split(";"):
            d, rest = op.split(":")
            x, z = [int(v) for v in rest.split(",")[:2]]
            tid = bm.nid("Thing")
            bm.things[tid] = {"id": tid, "def": d, "x": x, "z": z, "stack": 1, "born": game.ticks}
            n += 1
        return {"success": True, "placed": n, "survived": n}
    if tool == "rimworld/spawn_thing":
        tid = bm.nid("Thing")
        bm.things[tid] = {"id": tid, "def": p["defName"], "x": p["x"], "z": p["z"], "stack": int(p.get("stackCount", 1)),
                          "born": game.ticks}
        return {"success": True, "id": tid}
    if tool == "jawa/list_things":
        r = _rect(p["rect"])
        want = set(d.strip() for d in str(p.get("defName") or "").split(",") if d.strip())
        if p.get("group") == "Corpse":
            want = {"Corpse"}
        rows = [{"id": t["id"], "def": t["def"], "position": {"x": t["x"], "z": t["z"]}, "stackCount": t["stack"]}
                for t in bm.things.values() if _in(t["x"], t["z"], r) and (not want or t["def"] in want)]
        return {"success": True, "things": rows, "isCompleteList": True}
    if tool == "jawa/power_net":
        t = bm.things.get(p["thing"])
        if not t:
            return {"success": False}
        if p.get("forcePowerOn") is not None:
            bm.power[t["id"]] = bool(p["forcePowerOn"])
        return {"success": True, "powerOnAfter": bool(bm.power.get(t["id"]))}
    if tool == "jawa/spawn_pawn":
        pid = bm.nid("Human")
        bm.pawns[pid] = {"id": pid, "x": p["x"], "z": p["z"], "in": None, "hediffs": [], "food": 1.0, "dead": False}
        return {"success": True, "pawns": [{"id": pid}]}
    if tool == "jawa/list_pawns":
        rows = [{"id": q["id"], "dead": False} for q in bm.pawns.values() if not q["dead"] and not q["in"]]
        return {"success": True, "pawns": rows}
    if tool == "jawa/pawn_get":
        q = bm.pawns.get(p["pawn"])
        return {"success": True, "pawns": [_snap(q)]} if q else {"success": False, "message": "no pawn"}
    if tool == "jawa/pawn_need":
        q = bm.pawns.get(p["pawn"])
        if q and p.get("need") == "Food" and p.get("action") == "need":
            q["food"] = float(p["level"])
        return ok
    if tool == "jawa/comp_read":
        # companion tool the suite reads tank fuel with (CompRefuelable.fuel, exact)
        t = bm.things.get(p["thing"])
        if t and t["def"] == "RSW_BactaTank" and "Refuelable" in str(p.get("comp")):
            return {"success": True, "values": {"fuel": str(bm.fuel.get(t["id"], 0))}}
        return {"success": False, "message": "mock: no such comp"}
    if tool == "jawa/pawn_health":
        q = bm.pawns.get(p["pawn"])
        if not q:
            return {"success": False}
        if p.get("action") == "permanent":
            for h in q["hediffs"]:
                h["perm"] = True
            return {"success": True, "hediffs": []}
        sev = float(p.get("severity", -1))
        q["hediffs"].append({"def": p["hediff"], "part": p.get("bodyPart"), "severity": 0.5 if sev < 0 else sev})
        return {"success": True, "hediffs": []}
    if tool == "jawa/damage":
        q = bm.pawns.get(p.get("thingId"))
        if q and not q["dead"]:
            q["dead"] = True
            if q["x"] is not None and not q["in"]:
                cid = bm.nid("Thing")
                bm.things[cid] = {"id": cid, "def": "Corpse", "x": q["x"], "z": q["z"], "stack": 1,
                                  "born": game.ticks, "pawn": q["id"]}
        return ok
    if tool == "jawa/inspect_string":
        t = bm.things.get(p["thingIds"])
        lines = []
        if t and t["def"] == "RSW_BactaTank":
            tid = t["id"]
            lines.append("Bacta: %s / 30" % round(bm.fuel.get(tid, 0), 2))
            if tid in bm.occ:
                if not bm.powered(tid):
                    lines.append("Unpowered — not healing")
                elif bm.fuel.get(tid, 0) <= 0:
                    lines.append("Out of bacta")
                elif not bm.b("healingEnabled") and "heal_when_off" not in brk:
                    lines.append("Healing disabled in mod settings")
                else:
                    lines.append("Immersing: pawn")
                if bm.droid_assists():
                    lines.append("Medical droid assisting")
        return {"success": True, "things": [{"id": p["thingIds"], "inspect": lines}]}
    if tool == "jawa/ordered_job":
        bm.jobs.append({"pawn": p["pawnId"], "job": p["jobDef"], "a": p.get("targetAId"), "b": p.get("targetBId")})
        return {"success": True, "accepted": True, "nowRunningRequested": True}
    if tool == "rimworld/search_debug_actions":
        return {"success": True, "results": [{"path": "Pawns\\Make injuries permanent"}]}
    if tool == "rimworld/execute_debug_action":
        q = bm.pawns.get(p.get("pawnId"))
        if q:
            for h in q["hediffs"]:
                h["perm"] = True
        return ok
    if tool == "rimworld/step_game_ticks":
        bm.advance(int(p.get("ticks") or 0), game)
        return ok
    return None


def _get_defs(p, brk):
    rows = []
    reqs = [r for r in str(p["defs"]).split(";") if r]
    for r in reqs:
        ty, dn = r.split("/")
        fields = {}
        if ty == "TraderKindDef":
            # the REAL deep shape (LIVE 2026-10-03): rows carry countRange but NO thingDef; the patch's rows are the tail
            import os, re
            import xml.etree.ElementTree as ET
            tail = []
            for op in ET.parse(os.path.join(os.path.dirname(os.path.abspath(__file__)), "Patches",
                                            "RSW_Bacta_TraderStock.xml")).getroot().iter("Operation"):
                m = re.search(r'defName="([^"]+)"', op.findtext("xpath") or "")
                if m and m.group(1) == dn:
                    for li in op.iter("li"):
                        lo, hi = (li.findtext("countRange") or "0~0").split("~")
                        tail.append({"countRange": {"min": int(lo), "max": int(hi)}})
            items = [{"trader": dn, "countRange": {"min": 5, "max": 9}}] + ([] if "trader_missing" in brk else tail)
            fields = {"stockGenerators": items}
        elif dn == "Human" or dn == "Muffalo":
            rec = ["AdministerMechSerumHealer"] + ([] if "recipes_missing" in brk else
                                                     ["RSW_AdministerBactaPatch", "RSW_AdministerBactaSpray"])
            fields = {"recipes": rec}
        else:
            fields = {"defName": dn}
        rows.append({"requested": r, "found": True, "defName": dn, "fields": fields})
    return {"success": True, "foundCount": len(rows), "notFound": [], "defs": rows}


def _get_def(p):
    dn = p["defName"]
    comps = []
    extra = {"tradeTags": ["ExoticMisc"], "tradeability": "All"}
    if dn == "RSW_BactaTank":
        extra.update(thingClass="Building_BactaTank", tickerType="Normal")
        comps = [{"compClass": c, "fields": {}} for c in ("CompBactaImmersion", "CompBactaShell", "CompPowerTrader",
                                                          "CompAffectedByFacilities")]
        comps.append({"compClass": "CompRefuelable", "fields": {"fuelCapacity": 30.0}})
    elif dn == "RSW_MedicalDroid":
        comps = [{"compClass": "CompFacility", "fields": {}}]
    return {"success": True, "defName": dn, "comps": comps, "extra": extra}
