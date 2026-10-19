"""SUSPENSION BRIDGE live proof (SUSPENSION_BRIDGE_BUILD_POSTS_AT_BOTH_ENDS; design/RimMandrake/
suspension_bridge_construction_design_2026-10-18.md; the debug_process rule: the functional script ships with the build item
and grows with each later suspension item: underpass, grates, waters, jetty).

  python.exe src/RimMandrake/FlowWorks/northstar/suspension_bridge_proof.py [out.json] [--origin X,Z] [--fresh-map]
                                                                          [--only posts,grate,...]
  python3    src/RimMandrake/FlowWorks/northstar/suspension_bridge_proof.py --mock   # every path offline (FakeBridge);
             every row is written SKIP with the verdict it would have reached under "mock" (proves the script, never the game)

Run from the repo root with python.exe; the bridge must be held. Exit 0 = every MEASURED row PASS. NEVER RUN BY THE BUILD
ITEM: written offline 2026-10-18 while the game belonged to FOUNDRY; every row below is OWED to the first live run.

Owner rulings this proves (2026-10-18, by card unless quoted): name *"Suspension bridge"*; build = drag across like a wall,
1-3 wide, solid ground at both ends; a limit per type plus towers; railings an on/off switch per bridge; railings give no
cover; whole-span collapse with the load shown (parent Q3); vanilla bridges refused over dug ground (parent Q6).

Scenes (plot coords from --origin, default 140,140; dig by jawa/flowworks_excavation_drive, 8 notches = 4 m):
  T1 a 6-square trench (1..6, 0): timber bridge dragged (0,0)-(7,0), built at once (god)  -> rows BUILD, PATH, LOAD.
  T2 a 7-square trench (1..7, 4): timber drag (0,4)-(8,4), NOT god                        -> row REFUSED_LENGTH.
  T3 a 4-square trench (1..4, 8): timber bridge (0,8)-(5,8) god; railings off then on     -> rows RAILS_OFF / RAILS_ON.
  T4 a 4-square trench (1..4, 12): timber bridge (0,12)-(5,12) god; anchor (0,12) destroyed -> row SWING.
  T5 one dug square (10, 0)                                                              -> row VANILLA_REFUSED.
GRATE (SUSPENSION_GRATE_BUILD_LET_THE_FIRE_UP), plot from origin + (0, 20):
  G1 a 4-square 2 m pit (1..4, 20) of chemfuel under a grated steel bridge, 3 colonists on it, lit; 2,500 ticks; then the
     same with a solid steel bridge at (1..4, 24)                                           -> row GRATE_FIRE.
  G2 a 2 m canal (1..4, 28) holding water under a grated steel bridge; 50 L poured on (2, 28) -> row GRATE_POUR.
  G3 a Steel bar dropped on the grate at (3, 28)                                             -> row GRATE_ITEM_STAYS.
Every read is jawa/static_call RimMandrake.FlowWorks.Pits.RM_SuspensionProofs.<Proof*> (one line out; see that file).

ANTI-GUESSING NOTES
- A BUILD row reads things on the drag's own squares; a PATH row is the production path finder's answer for that pawn now.
- LOAD: colonists are spawned ON the deck until the span reads over 600 kg BEFORE any tick (ProofSpan state=Over), then
  120 ticks run (two load passes of 60); PASS needs every deck of the span gone AND each spawned pawn standing on a dug
  square AND an injury hediff added. A span that never read Over makes the row UNMEASURED, never PASS.
- GRATE_FIRE: PASS needs >= 1 Burn hediff among the grate's riders AND fewer on the solid deck's (both counts written);
  a run where neither pit was alight (ProofIgnite not LIT) is UNMEASURED.
- GRATE_POUR: the body read is the decilitres in every dug square within 12 (ProofPour, through RM_LiquidSpill.Spill, the
  production spill); PASS needs rise == 500 dL AND no new filth on the square.
- RAILS: 20 production TryKnockOff rolls at the stagger chance (25%); railings off must drop >= 1 (P(0 of 20) = 0.3%),
  railings on must drop 0.
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

PROOF = "RimMandrake.FlowWorks.Pits.RM_SuspensionProofs"
DEEP = 8   # notches: 4 m


def parse(txt):
    kv = {}
    for tok in txt.split():
        if "=" in tok:
            k, v = tok.split("=", 1)
            kv[k] = v
    return kv


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("out", nargs="?", default=None)
    ap.add_argument("--origin", default="140,140")
    ap.add_argument("--fresh-map", action="store_true")
    ap.add_argument("--only", default="", help="comma list of sections: " + ",".join(SECTIONS))
    ap.add_argument("--mock", action="store_true", help="run every path against FakeBridge; rows are SKIP (mock verdict kept)")
    a = ap.parse_args(argv)
    only = set(x for x in a.only.split(",") if x) or set(SECTIONS)
    if a.mock:
        B, V = FakeBridge(), None
    else:
        import proof_hose as PH           # noqa: E402  (bridge-side imports only on a live run)
        V = PH.V
        B = PH.PB()
    out = a.out or os.path.join(HERE, "suspension_bridge_result_%s.json" % time.strftime("%Y%m%dT%H%M%S"))
    rows = []
    res = {"script": "suspension_bridge_proof.py", "started": time.strftime("%Y-%m-%dT%H:%M:%S"), "rows": rows, "args": vars(a)}

    def save():
        with open(out + ".tmp", "w", encoding="utf-8") as f:
            json.dump(res, f, indent=1, default=str)
        os.replace(out + ".tmp", out)

    def row(rid, st, det):
        if a.mock:
            det = dict(det, mock=st)
            st = "SKIP"
        rows.append({"id": rid, "status": st, "detail": det})
        print("%-34s %-10s %s" % (rid, st, json.dumps(det, default=str)[:300]), flush=True)
        save()

    def proof(method, arg):
        r = B.call("jawa/static_call", type=PROOF, method=method, args=arg) or {}
        txt = str(r.get("result") or r.get("message") or r.get("error") or "")
        return (parse(txt) if r.get("success") is True and not txt.startswith("REFUSED") else {}), txt

    def dig(c, n=DEEP):
        return B.call("jawa/flowworks_excavation_drive", x=c[0], z=c[1], deepenLevels=n, setFill=-1) or {}

    def spawn(c, kind="Colonist", faction="player"):
        r = B.call("jawa/spawn_pawn", kindDef=kind, x=c[0], z=c[1], faction=faction, count=1) or {}
        return ((r.get("pawns") or [{}])[0]).get("id")

    def pawns_by_id():
        return {p.get("id"): p for p in (B.call("jawa/list_pawns", limit=300) or {}).get("pawns") or []}

    def ticks(n):
        return B.call("rimworld/step_game_ticks", ticks=n, pauseFirst=True, timeoutMs=max(60000, n * 40))

    ox, oz = (int(v) for v in a.origin.split(","))
    FakeBridge.ox, FakeBridge.floor_z = ox, oz
    P = lambda dx, dz: (ox + dx, oz + dz)                        # noqa: E731
    xz = lambda c: "%d,%d" % c                                   # noqa: E731
    if a.fresh_map and not a.mock:
        B.call("rimworld/go_to_main_menu")
        B.call("rimworld/start_debug_game_ready", readiness="mapData", pauseIfNeeded=True, timeoutMs=280000)
    ok = True if a.mock else V._wait_playing(B, leave_s=0)[0]
    if not ok:
        row("SB_game_playing", "UNMEASURED", {"why": "no game in Playing"})
        return 2
    ctx = dict(B=B, P=P, xz=xz, row=row, proof=proof, dig=dig, spawn=spawn, pawns_by_id=pawns_by_id, ticks=ticks, ox=ox, oz=oz)
    for name in SECTIONS:
        if name in only:
            print("== section %s" % name, flush=True)
            SECTIONS[name](ctx) if name != "posts" else posts(ctx)
    res["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    save()
    bad = [r for r in rows if r["status"] == "FAIL"]
    if a.mock:
        mock_bad = [r["id"] for r in rows if r["detail"].get("mock") != "PASS" and not r["detail"].get("owed")]
        print("MOCK: suspension bridge proof: %d rows, mock verdicts not PASS: %s -> %s" % (len(rows), mock_bad or "none", out))
        return 1 if mock_bad else 0
    print("suspension bridge proof: %d rows, %d FAIL -> %s" % (len(rows), len(bad), out))
    return 1 if bad else 0


def posts(ctx):
    """SUSPENSION_BRIDGE_BUILD_POSTS_AT_BOTH_ENDS rows (T1-T5)."""
    B, P, xz, row, proof, dig, spawn, pawns_by_id, ticks = (ctx[k] for k in ("B", "P", "xz", "row", "proof", "dig", "spawn",
                                                                            "pawns_by_id", "ticks"))
    ox, oz = ctx["ox"], ctx["oz"]
    for dz, n in ((0, 6), (4, 7), (8, 4), (12, 4)):
        for i in range(1, n + 1):
            dig(P(i, dz))
    dig(P(10, 0))

    # T1: build, path, load
    kv, txt = proof("ProofBuild", "%s;%s;timber;god" % (xz(P(0, 0)), xz(P(7, 0))))
    good = kv.get("ok") == "True" and kv.get("anchors") == "2" and kv.get("decks") == "6"
    row("SB_drag_6_timber_builds", "PASS" if good else ("FAIL" if kv else "UNMEASURED"), {"read": txt})
    walker = spawn(P(-1, 0))
    kv, txt = proof("ProofPath", "%s;%s" % (walker, xz(P(8, 0)))) if walker else ({}, "no pawn")
    good = kv.get("found") == "True" and int(kv.get("decked", "0")) >= 6
    row("SB_path_crosses_on_deck", "PASS" if good else ("FAIL" if kv else "UNMEASURED"), {"read": txt})

    riders = []
    for k in range(12):
        riders.append(spawn(P(1 + k % 6, 0)))
        kv, txt = proof("ProofSpan", xz(P(3, 0)))
        if kv.get("state") == "Over":
            break
    before = pawns_by_id()
    over = kv.get("state") == "Over"
    line = kv.get("line", "")
    ticks(120)
    kv2, txt2 = proof("ProofSpan", xz(P(3, 0)))
    after = pawns_by_id()
    fell, hurt = 0, 0
    for pid in riders:
        p0, p1 = before.get(pid) or {}, after.get(pid) or {}
        if not p1:
            continue
        if ox + 1 <= int(p1.get("x", -1)) <= ox + 6 and int(p1.get("z", -1)) == oz:
            fell += 1
        if len(p1.get("hediffs") or []) > len(p0.get("hediffs") or []):
            hurt += 1
    gone = txt2.startswith("SPAN none") or kv2.get("decks") == "0"
    st = "PASS" if over and gone and fell == len([r for r in riders if r]) and hurt >= 1 else "FAIL"
    if not over:
        st = "UNMEASURED"
    row("SB_load_over_rating_whole_span_falls", st,
        {"before": txt, "inspect_line": line, "after": txt2, "riders": len(riders), "fell": fell, "hurt": hurt})

    # T2: too long for timber
    kv, txt = proof("ProofBuild", "%s;%s;timber" % (xz(P(0, 4)), xz(P(8, 4))))
    good = kv.get("ok") == "False" and "at most 6" in txt and kv.get("blueprints") == "0" and kv.get("anchors") == "0"
    row("SB_drag_7_timber_refused", "PASS" if good else ("FAIL" if kv else "UNMEASURED"), {"read": txt})

    # T3: railings
    proof("ProofBuild", "%s;%s;timber;god" % (xz(P(0, 8)), xz(P(5, 8))))
    rider = spawn(P(2, 8))
    proof("ProofRails", "%s;off" % xz(P(2, 8)))
    kv, txt = proof("ProofKnock", "%s;20" % rider) if rider else ({}, "no pawn")
    row("SB_rails_off_some_fall", "PASS" if kv and int(kv.get("fell", "0")) >= 1 else ("FAIL" if kv else "UNMEASURED"), {"read": txt})
    rider2 = spawn(P(3, 8))
    kv0, txt0 = proof("ProofRails", "%s;on" % xz(P(2, 8)))
    kv, txt = proof("ProofKnock", "%s;20" % rider2) if rider2 else ({}, "no pawn")
    good = kv and kv.get("railed") == "True" and kv.get("fell") == "0"
    row("SB_rails_on_nobody_falls", "PASS" if good else ("FAIL" if kv else "UNMEASURED"), {"rails": txt0, "read": txt})

    # T4: lose an anchor -> swing-down from that end
    proof("ProofBuild", "%s;%s;timber;god" % (xz(P(0, 12)), xz(P(5, 12))))
    B.call("jawa/destroy_batch", cells=[{"x": P(0, 12)[0], "z": P(0, 12)[1]}], defName="RM_SuspensionAnchor_Timber")
    ticks(150)
    kv, txt = proof("ProofSwing", "")
    stamps = []
    for tok in txt.split()[1:]:
        c, t = tok.split("@")
        x, z = (int(v) for v in c.split(","))
        if z == oz + 12:
            stamps.append((x, int(t)))
    xs = [x for x, _ in stamps]
    ts = [t for _, t in stamps]
    good = len(stamps) == 4 and xs == sorted(xs) and ts == sorted(ts) and len(set(ts)) == 4
    row("SB_anchor_lost_swings_from_that_end", "PASS" if good else ("FAIL" if stamps else "UNMEASURED"), {"read": txt, "lane": stamps})

    # T5: vanilla bridge refused on a dug square
    kv, txt = proof("ProofVanillaBridge", xz(P(10, 0)))
    good = kv.get("accepted") == "False" and "Use a suspension bridge over dug ground" in txt
    row("SB_vanilla_bridge_refused_over_dug", "PASS" if good else ("FAIL" if kv else "UNMEASURED"), {"read": txt})

    row("SB_settings_off_no_button_never_breaks", "UNMEASURED",
        {"owed": True, "why": "OWED: toggle suspensionBridgesBuildable / suspensionWeightCollapse via jawa/mod_settings_field on "
                "RimMandrake.FlowWorks.Pits.RM_SuspensionSettings and re-run LOAD; not scripted yet"})


FIRE_TYPE = "RimMandrake.FlowWorks.RM_LiquidFireProof"
FLUIDID_TYPE = "RimMandrake.FlowWorks.RM_FluidIdentityProof"


def burns(p):
    return sum(1 for h in (p.get("hediffs") or []) if "Burn" in (h if isinstance(h, str) else str(h.get("def") or h.get("defName") or h)))


def grate(ctx):
    """SUSPENSION_GRATE_BUILD_LET_THE_FIRE_UP rows: verify L2 x3 (fire through a grate vs a solid deck; a pour drains to the
    body; an item stays on the grate)."""
    B, P, xz, row, proof, dig, spawn, pawns_by_id, ticks = (ctx[k] for k in ("B", "P", "xz", "row", "proof", "dig", "spawn",
                                                                            "pawns_by_id", "ticks"))
    for dz in (20, 24, 28):
        for i in range(1, 5):
            dig(P(i, dz), 4)                                     # 2 m
    counts = {}
    for dz, tier in ((20, "steelgrated"), (24, "steel")):
        for i in range(1, 5):
            B.call("jawa/static_call", type=FLUIDID_TYPE, method="ProofFillWithFluid",
                   args="%d,%d,%d,RM_Fluid_Chemfuel" % (P(i, dz)[0], P(i, dz)[1], 2))
        proof("ProofBuild", "%s;%s;%s;god" % (xz(P(0, dz)), xz(P(5, dz)), tier))
        riders = [spawn(P(k, dz)) for k in (2, 3, 4)]
        before = pawns_by_id()
        lit = B.call("jawa/static_call", type=FIRE_TYPE, method="ProofIgnite", args=xz(P(1, dz))) or {}
        lit_txt = str(lit.get("result") or "")
        ticks(2500)
        after = pawns_by_id()
        n = sum(max(0, burns(after.get(r) or {}) - burns(before.get(r) or {})) for r in riders if r)
        counts[tier] = (n, lit_txt[:60], proof("ProofGrate", xz(P(3, dz)))[1])
    g, s_ = counts["steelgrated"][0], counts["steel"][0]
    litboth = all(c[1].startswith("LIT") for c in counts.values())
    st = "PASS" if g >= 1 and g > s_ else "FAIL"
    row("GRATE_fire_burns_people_above", st if litboth else "UNMEASURED",
        {"grateBurns": g, "solidBurns": s_, "reads": counts})
    for i in range(1, 5):                                         # 1 m of water in the 2 m canal: room for the pour
        B.call("jawa/flowworks_excavation_drive", x=P(i, 28)[0], z=P(i, 28)[1], deepenLevels=0, setFill=2)
    proof("ProofBuild", "%s;%s;steelgrated;god" % (xz(P(0, 28)), xz(P(5, 28))))
    kv, txt = proof("ProofPour", "%s;50;RM_Liquid_FreshWater" % xz(P(2, 28)))
    good = kv.get("rise") == "500" and kv.get("filthAfter") == kv.get("filthBefore")
    row("GRATE_pour_drains_to_body", "PASS" if good else ("FAIL" if kv else "UNMEASURED"), {"read": txt})
    B.call("jawa/spawn_batch", ops="Steel:%d,%d" % P(3, 28))
    ticks(60)
    things = B.call("jawa/list_things", rect="%d,%d,1,1" % P(3, 28), limit=20, includePawns=False) or {}
    names = [t.get("def") or t.get("defName") for t in (things.get("things") or [])]
    row("GRATE_item_stays_on_deck", "PASS" if "Steel" in names else ("FAIL" if things.get("success") else "UNMEASURED"),
        {"things": names})


SECTIONS = {"posts": None, "grate": grate}


class FakeBridge(object):
    """Offline stand-in for the RimBridge client: every call answers in the shape the live mod would on a PASS, so --mock
    walks every path of this script. It knows nothing about the game; a mock verdict proves the script only."""

    def __init__(self):
        self.next_id, self.calls, self.reads, self.tags, self.last_tier, self.span = 1000, [], 0, {}, "", 0

    def call(self, tool, **kw):
        method = tool
        self.calls.append(method)
        if method == "jawa/static_call":
            return {"success": True, "result": self.static(kw.get("method"), kw.get("args") or "")}
        if method == "jawa/spawn_pawn":
            self.next_id += 1
            self.tags[self.next_id] = self.last_tier
            return {"pawns": [{"id": self.next_id}]}
        if method == "jawa/list_pawns":
            self.reads += 1
            late = self.reads % 2 == 0
            return {"pawns": [{"id": i, "x": FakeBridge.ox + 1 + (i % 6), "z": FakeBridge.floor_z,
                               "hediffs": ([] if not late else ["Burn", "Bruise"] if self.tags.get(i) == "steelgrated" else ["Bruise"])}
                              for i in range(1001, self.next_id + 1)]}
        if method == "jawa/list_things":
            return {"success": True, "things": [{"def": "Steel"}]}
        return {"success": True}

    ox, floor_z = 140, 140
    tier_decks = {"timber": 6}

    def static(self, m, arg):
        if m == "ProofBuild":
            self.last_tier = arg.split(";")[2]
            if arg.split(";")[2] == "timber" and "god" not in arg:
                return "BUILD ok=False anchors=0 decks=0 blueprints=0 reason=A timber suspension bridge spans at most 6 squares"
            return "BUILD ok=True anchors=2 decks=6 blueprints=0 reason=-"
        if m == "ProofPath":
            return "PATH found=True cells=9 decked=6"
        if m == "ProofSpan":
            self.span += 1
            return "SPAN none" if self.span % 2 == 0 else "SPAN tier=timber load=640.0 rating=600 state=Over decks=6 line=Load 640 / 600 kg"
        if m == "ProofRails":
            on = arg.endswith("on")
            return "RAILS on=%s railed=%d" % (on, 4 if on else 0)
        if m == "ProofKnock":
            self.knock = getattr(self, "knock", 0) + 1
            return "KNOCK trials=20 fell=%d railed=%s edge=True" % ((5, "False") if self.knock == 1 else (0, "True"))
        if m == "ProofSwing":
            z = FakeBridge.ox + 12
            return "SWING " + " ".join("%d,%d@%d" % (FakeBridge.ox + i, z, 100 + 20 * i) for i in range(1, 5))
        if m == "ProofVanillaBridge":
            return "VANILLA accepted=False reason=Use a suspension bridge over dug ground"
        if m == "ProofIgnite":
            return "LIT 1 cell"
        if m == "ProofGrate":
            return "GRATE grated=True deck=True fire=True attach=0.75 splash=0.50 scorches=3 drainedDl=500"
        if m == "ProofPour":
            return "POUR dl=500 bodyBefore=4000 bodyAfter=4500 rise=500 filthBefore=0 filthAfter=0"
        return "OK"


if __name__ == "__main__":
    sys.exit(main())
