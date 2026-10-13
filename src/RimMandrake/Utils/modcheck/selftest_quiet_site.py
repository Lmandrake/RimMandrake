"""Offline selftest for modcheck.quiet_site against rimdrive.fake.FakeWorld (+ the two companion/UI tools it adds).

Asserts what the WORLD looks like afterwards, with a negative control per check. Run: python3 selftest_quiet_site.py
"""
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
sys.path.insert(0, os.path.dirname(_HERE))

import quiet_site as Q                                 # noqa: E402
from rimdrive.fake import FakeWorld, pawn_row, hediff  # noqa: E402

_results = []


def check(name, cond, detail=""):
    _results.append((name, bool(cond)))
    print("%s %s%s" % ("ok  " if cond else "FAIL", name, ("  -- " + detail) if (detail and not cond) else ""))


class SiteFake(FakeWorld):
    """FakeWorld + jawa/quiet_site, a force-pause window stack and a clickable UI layout."""

    def __init__(self, **kw):
        FakeWorld.__init__(self, **kw)
        self.structs = [{"id": "Hive1", "def": "Hive", "dormant": True}, {"id": "GlowPod1", "def": "GlowPod"},
                        {"id": "Mast1", "def": "RM_AerialMast"}]
        self.letters = [{"id": "VoidMonolith1", "def": "VoidMonolith", "label": "Fallen monolith", "sent": False}]
        self.wins = []

    def _t_jawa_quiet_site(self, action="status", clearThreats=False, keepDefs=None, proximityLetters=False):
        keep = set((keepDefs or "").split(",")) - {""}
        removed = []
        if action == "apply" and clearThreats:
            removed = [t for t in self.structs if t["def"] not in keep]
            self.structs = [t for t in self.structs if t["def"] in keep]
        before = [dict(l) for l in self.letters]
        if action == "apply" and proximityLetters:
            for l in self.letters:
                l["sent"] = True
        threats = [dict(t, kept=t["def"] in keep) for t in self.structs]
        after = len([t for t in threats if not t["kept"]])
        return {"success": True, "threats": threats, "removed": removed, "errors": [], "threatsAfter": after,
                "kept": len(threats) - after,
                "letters": [{"def": b["def"], "label": b["label"], "sentBefore": b["sent"], "sentAfter": l["sent"]}
                            for b, l in zip(before, self.letters)],
                "lettersUnsentAfter": len([l for l in self.letters if not l["sent"]])}

    def _t_jawa_window_list_close(self, action="list", **_):
        return {"success": True, "windows": [{"type": w, "forcePause": True} for w in self.wins]}

    def _t_rimworld_get_ui_layout(self, **_):
        if not self.wins:
            return {"success": True, "surfaces": []}
        return {"success": True, "surfaces": [{"type": self.wins[0], "elements": [
            {"label": "Spawn faction", "targetId": "btn-spawn"}, {"label": "Do nothing", "targetId": "btn-nothing"}]}]}

    def _t_rimworld_click_ui_target(self, targetId=None, **_):
        if targetId == "btn-nothing" and self.wins:
            self.wins.pop(0)
            return {"success": True}
        return {"success": False, "message": "no such target"}


def world():
    w = SiteFake(pawns=[pawn_row("Col1"), pawn_row("Col2"),
                        pawn_row("Megapede1", kind="VFEI2_Megapede", faction="Insect", is_player=False, hostile=True,
                                 intelligence="Animal")])
    w.queue = [{"defName": "StrangerInBlackJoin", "fireTick": 180}, {"defName": "RM_TestOwnIncident", "fireTick": 500}]
    return w


def mutations(w):
    return [c for c in w.calls if c[0] in ("jawa/debug_settings",) and c[1].get("action") == "set"
            or c[0] in ("jawa/quiet_site",) and c[1].get("action") == "apply"]


def main():
    # 1. integration suite: nothing applied, said so
    w = world()
    qs = Q.QuietSite(w, suite="integration", row="int")
    rc = qs.apply()
    check("integration applies no control", not mutations(w) and rc["controls"] == [], str(mutations(w)))
    try:
        Q.QuietSite(w, suite="integration", controls=["storyteller_off"])
        check("integration refuses controls", False)
    except ValueError:
        check("integration refuses controls", True)

    # 2. isolated: storyteller off, threats gone except keep_defs, letters sent, hostiles gone, every control declared
    w = world()
    qs = Q.QuietSite(w, suite="isolated", keep_defs=["RM_AerialMast"], row="iso")
    rc = qs.apply()
    check("storyteller read back off", w.debug["enableStoryteller"] is False)
    check("hive + glowpod removed, mod-under-test mast kept",
          [t["def"] for t in w.structs] == ["RM_AerialMast"], str(w.structs))
    check("monolith proximity letter marked sent", all(l["sent"] for l in w.letters))
    alive_hostile = [p for p in w.pawns.values() if p.get("hostile") and not p.get("dead")]
    check("megapede removed", not alive_hostile, str(alive_hostile))
    check("every control carries a hides column", all(c["hides"] for c in rc["controls"]) and len(rc["controls"]) == 8)
    check("queue cleared at apply incl. the stranger", not any(q["defName"] == "StrangerInBlackJoin" for q in w.queue))

    # 3. drain removes ONLY the declared queued incident, at every chunk
    w.queue = [{"defName": "StrangerInBlackJoin", "fireTick": 900}, {"defName": "RM_TestOwnIncident", "fireTick": 950}]
    acts = qs.drain(tick=720)
    check("drain removed StrangerInBlackJoin", [q["defName"] for q in w.queue] == ["RM_TestOwnIncident"], str(w.queue))
    check("drain recorded with its tick", any(a.get("control") == "queue_drain" and a["tick"] == 720 for a in acts))
    # negative control: a profile without queue_drain leaves it
    w2 = world()
    q2 = Q.QuietSite(w2, suite="isolated", controls=["random_events_off"])
    q2.apply()
    w2.queue = [{"defName": "StrangerInBlackJoin", "fireTick": 900}]
    q2.drain()
    check("negative: no queue_drain control leaves the stranger", len(w2.queue) == 1)

    # 4. modal broker: five VEF knocks answered 'Do nothing'; an unknown force-pause window blocks
    w.wins = ["VEF.Factions.Dialog_NewFactionSpawning"] * 5
    qs.sleep = lambda t: None
    m = qs.modals()
    check("five faction dialogs answered", len(m["handled"]) == 5 and not w.wins, str(m))
    lag = world()
    lq = Q.QuietSite(lag, suite="isolated", controls=["modal_broker"])
    lq.sleep = lambda t: None
    lag.wins = ["VEF.Factions.Dialog_NewFactionSpawning"] * 5
    pending = []
    real_click = lag._t_rimworld_click_ui_target
    real_list = lag._t_jawa_window_list_close

    def lag_click(targetId=None, **_):
        pending.append([targetId, 0])
        return {"success": True}

    def lag_list(action="list", **_):
        for p in pending:                              # a click is processed only on the SECOND read after it
            p[1] += 1
        while pending and pending[0][1] >= 2:
            real_click(targetId=pending.pop(0)[0])
        return real_list(action)
    lag._t_rimworld_click_ui_target = lag_click
    lag._t_jawa_window_list_close = lag_list
    lm = lq.modals()
    check("lagging clicks: five dialogs need exactly five clicks", len(lm["handled"]) == 5 and not lag.wins
          and not lq.problems, "%d clicks, left %s, %s" % (len(lm["handled"]), lag.wins, lq.problems))
    w.wins = ["Dialog_SomethingUnknown"]
    qs.problems = []
    m = qs.modals()
    check("unknown force-pause window is captured, not closed",
          w.wins == ["Dialog_SomethingUnknown"] and m["unknown"] and qs.problems, str(m))

    # 5. support guard: refused on a health row, records harm BEFORE repair on a liquids row
    try:
        Q.QuietSite(world(), suite="isolated", protect_support=True, topic="health")
        check("guard refused for topic health", False)
    except ValueError:
        check("guard refused for topic health", True)
    w = world()
    qs = Q.QuietSite(w, suite="isolated", protect_support=True, topic="liquids", support_ids=["Col1"])
    qs.apply()
    w.pawns["Col1"]["health"]["hediffs"].append(hediff("Heatstroke", None))
    acts = qs.drain(tick=3000)
    g = [a for a in acts if a.get("control") == "support_guard"]
    check("guard recorded harm before repair", g and g[0]["harmBeforeRepair"] == [("Col1", "Heatstroke/None")], str(acts))
    check("guard repaired heatstroke",
          not any(h["def"] == "Heatstroke" for h in w.pawns["Col1"]["health"]["hediffs"]))
    w.pawns["Col2"]["health"]["hediffs"].append(hediff("Heatstroke", None))
    qs.drain()
    check("negative: non-support colonist not repaired",
          any(h["def"] == "Heatstroke" for h in w.pawns["Col2"]["health"]["hediffs"]))

    # 6. verify reads the game
    w = world()
    qs = Q.QuietSite(w, suite="isolated")
    qs.apply()
    v = qs.verify()
    check("verify: quiet after apply", v["quiet"] and v["threatStructures"] == 0, str(v))
    w.structs.append({"id": "Hive2", "def": "Hive", "dormant": True})
    v = qs.verify()
    check("negative: a new dormant hive breaks quiet", not v["quiet"] and v["dormantThreats"] == 1, str(v))
    qs.restore()
    check("restore puts the storyteller back", w.debug["enableStoryteller"] is True)

    bad = [n for n, ok in _results if not ok]
    print("%d/%d passed" % (len(_results) - len(bad), len(_results)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
