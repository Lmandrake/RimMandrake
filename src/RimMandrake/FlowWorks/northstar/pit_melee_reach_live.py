"""PIT MELEE REACH live check (RIMMANDRAKE_ENACT_PIT_MELEE_REACH_EQUALS_CLIMB_SIZE_DECIDES, owner 2026-11-23: "anything
that can't climb out also cannot melee attack out ... a very large creature can attack farther down a pit").

  python.exe src\\RimMandrake\\FlowWorks\\northstar\\pit_melee_reach_live.py [out.json] [--origin X,Z] [--fresh-map]

Bridge held, minimal list + FlowWorks. UNRUN when written (offline build run). Never a flyer.

Scenes (plot 14 x 12 from --origin, default 40,180; cleared, dug, read back). In each a fresh pair, one on the rim (dx, 3) and one
in a pit square (dx, 4) beside it, is ordered to AttackMelee: the striker first, then (a fresh pair) the other way round.
  REACH_3m_neither   a 1x1 of 3 m: colonist above, pirate below. Neither lands a hit in TICKS.
  REACH_half_m_both  a 1x1 of 0.5 m: both directions land hits (control: the orders and the damage recorder work).
  REACH_2m_one_way   a 1x1 of 2 m: a thrumbo above and a pirate below. The thrumbo lands a hit, the pirate never does.
  REACH_3m_switch_off  the 3 m scene, pirate below, with the Mod Settings switch off: the pirate's hit lands (the switch works
                       and the 3 m row could have seen one). The switch is put back and read back.
Each order also reads RM_NorthstarProofs.ProofClimb "melee:<attacker>;<target>" (strikes / depths / climb limit): a read that
disagrees with the scene (wrong depth, not adjacent) makes the row UNMEASURED, never PASS.
LIES: a hit is counted only when the damage recorder names the attacker as instigator; a refused recorder is UNMEASURED.
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
NSP = "RimMandrake.FlowWorks.RM_NorthstarProofs"
S_FW = "RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings"
FIELD = "pitLipMeleeDeniedEnabled"
ITEM = "RIMMANDRAKE_ENACT_PIT_MELEE_REACH_EQUALS_CLIMB_SIZE_DECIDES"
SETTLE, TICKS = 70, 600        # > RM_PocketGrid.RebuildMinTicks; about five melee cooldowns


def parse(text):
    """ProofClimb melee: line -> {key: value}, or {} when it refused."""
    t = str(text or "")
    return dict(p.split("=", 1) for p in t.split()[1:] if "=" in p) if t.startswith("MELEE ") else {}


def leg(kv, hits, deep, attacker_below):
    """One ordered attack -> 'hit' | 'none' | None (could not look). hits: instigator ids of the target's damage events, or None."""
    want = (deep, 0) if attacker_below else (0, deep)
    if hits is None or kv.get("adjacent") != "True" or (kv.get("aDepth"), kv.get("tDepth")) != tuple(str(d) for d in want):
        return None
    return "hit" if hits else "none"


def verdict(up, down, want_up, want_down):
    """(status, why) from the two legs ('hit'/'none'/None) and what the rule asks (None: the leg is not part of the row)."""
    got = [(g, w) for g, w in ((up, want_up), (down, want_down)) if w is not None]
    if any(g is not None and g != w for g, w in got):
        return "FAIL", "up=%s down=%s, want up=%s down=%s" % (up, down, want_up, want_down)
    if any(g is None for g, _w in got):
        return "UNMEASURED", "a leg was not read: up=%s down=%s" % (up, down)
    return "PASS", ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out", nargs="?", default=None)
    ap.add_argument("--origin", default="40,180")
    ap.add_argument("--fresh-map", action="store_true")
    a = ap.parse_args()
    import proof_hose as PH  # noqa: E402
    V, B = PH.V, PH.PB()
    out = a.out or os.path.join(HERE, "pit_melee_reach_result_%s.json" % time.strftime("%Y%m%dT%H%M%S"))
    rows, res = [], {"script": os.path.basename(__file__), "started": time.strftime("%Y-%m-%dT%H:%M:%S")}
    res["rows"] = rows

    def row(rid, st, cls, det):
        rows.append({"id": rid, "status": st, "class": cls, "item": ITEM, "detail": det})
        print("%-22s %-10s %s" % (rid, st, json.dumps(det, default=str)[:500]), flush=True)
        with open(out, "w", encoding="utf-8") as f:
            json.dump(res, f, indent=1, default=str)

    def step(n):
        return B.call("rimworld/step_game_ticks", ticks=n, pauseFirst=True, timeoutMs=max(60000, n * 40)) or {}

    def switch():
        return str((B.call("jawa/mod_settings_field", typeName=S_FW, action="get", field=FIELD) or {}).get("value"))

    def set_switch(v):
        B.call("jawa/mod_settings_field", typeName=S_FW, action="set", field=FIELD, value=str(v))
        return switch()

    ox, oz = (int(v) for v in a.origin.split(","))
    if a.fresh_map:
        B.call("rimworld/go_to_main_menu")
        B.call("rimworld/start_debug_game_ready", readiness="mapData", pauseIfNeeded=True, timeoutMs=280000)
    ok, _ = V._wait_playing(B, leave_s=0)
    if not ok:
        row("REACH_site", "UNMEASURED", "HARNESS", {"why": "no game in Playing"})
        return 2
    res["site_calm"] = V.site_calm(B)
    B.call("jawa/kill_hostiles")
    rect = (ox - 1, oz, 16, 12)
    B.call("jawa/static_call", type=NSP, method="ProofResetRect", args="%d;%d;%d;%d" % rect)
    site = []
    V.prepare_site(B, rect, site, "pit_melee_site")
    if [r for r in site if r.get("status") not in (None, "PASS")]:
        row("REACH_site", "UNMEASURED", "SITE", {"why": "site not prepared", "site": site[:2]})
        return 2
    pits = {6: (ox + 1, oz + 4), 1: (ox + 5, oz + 4), 4: (ox + 9, oz + 4)}       # notches -> the pit square
    for d, c in pits.items():
        B.call("jawa/flowworks_excavation_drive", x=c[0], z=c[1], deepenLevels=d, setBodyWaterM=-1)
    step(SETTLE)
    probe = B.call("jawa/spawn_pawn", kindDef="Pirate", x=0, z=0, faction="?", count=1, _answer=True) or {}
    fac = next((f["def"] for f in (probe.get("details") or {}).get("available") or []
                if f.get("hostile") and str(f.get("def")).startswith("Pirate")), None)
    if not fac:
        row("REACH_site", "UNMEASURED", "SITE", {"why": "no hostile Pirate faction"})
        return 2

    def spawn(kind, at, faction):
        kw = {"faction": faction} if faction else {}
        r = B.call("jawa/spawn_pawn", kindDef=kind, x=at[0], z=at[1], count=1, **kw) or {}
        return ((r.get("pawns") or [{}])[0]).get("id")

    def run(deep, above, attacker_below):
        """A fresh pair; the named one attacks; the other stands (Wait). -> the leg's result and its evidence."""
        pit = pits[deep]
        rim = (pit[0], pit[1] - 1)
        up, below = spawn(above[0], rim, above[1]), spawn("Pirate", pit, fac)
        att, tgt = (below, up) if attacker_below else (up, below)
        kv = parse((B.call("jawa/static_call", type=NSP, method="ProofClimb", args="melee:%s;%s" % (att, tgt), _answer=True)
                    or {}).get("result"))
        B.call("jawa/ordered_job", pawnId=tgt, jobDef="Wait", _answer=True)
        order = B.call("jawa/ordered_job", pawnId=att, jobDef="AttackMelee", targetAId=tgt, _answer=True) or {}
        hits = []
        for _ in range(TICKS // 60):
            step(60)
            r = B.call("jawa/damage_log", thingId=str(tgt), limit=12) or {}
            if not r.get("success"):
                hits = None
                break
            hits = [e.get("instigatorId") for e in r.get("events") or [] if e.get("instigatorId") == att]
            if hits:
                break
        for pid in (up, below):
            B.call("jawa/pawn_force_incapacitate", pawn=pid, action="vanish", _answer=True)
        step(1)
        got = leg(kv, hits, deep, attacker_below) if order.get("accepted") else None
        return got, {"attacker": att, "target": tgt, "proof": kv, "hits": hits, "accepted": order.get("accepted")}

    colonist, thrumbo = ("Colonist", "player"), ("Thrumbo", None)
    was = switch()
    try:
        if was != "True":
            set_switch("True")
        for rid, deep, above, want_up, want_down in (("REACH_3m_neither", 6, colonist, "none", "none"),
                                                     ("REACH_half_m_both", 1, colonist, "hit", "hit"),
                                                     ("REACH_2m_one_way", 4, thrumbo, "none", "hit")):
            (u, du), (d, dd) = run(deep, above, True), run(deep, above, False)
            st, why = verdict(u, d, want_up, want_down)
            row(rid, st, "MOD" if st == "FAIL" else "SITE" if st == "UNMEASURED" else "", {"why": why, "fromBelow": du, "fromAbove": dd})
        off = set_switch("False")
        u, du = run(6, colonist, True)
    finally:
        back = set_switch(was if was in ("True", "False") else "True")   # unreadable: the shipped default
    st, why = verdict(u, None, "hit", None) if off == "False" else ("UNMEASURED", "the switch did not go off: %s" % off)
    row("REACH_3m_switch_off", st, "MOD" if st == "FAIL" else "", {"why": why, "fromBelow": du, "switchBack": back, "switchWas": was})
    res["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    row("REACH_done", "PASS" if back == was else "FAIL", "HARNESS", {"switch": back, "switchWas": was})
    return 0 if all(r["status"] == "PASS" for r in rows) else 1


if __name__ == "__main__":
    sys.exit(main())
