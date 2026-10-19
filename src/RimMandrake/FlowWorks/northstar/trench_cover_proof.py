"""TRENCH COVER live proof (TRENCH_COVER_BUILD_SANDBAGS_MADE_OF_DIRT; design/RimMandrake/canal_cover_design_2026-10-17.md §10
step 7, the debug_process rule: the proof script ships with the build and grows with each live session).

  python.exe src/RimMandrake/FlowWorks/northstar/trench_cover_proof.py [out.json] [--origin X,Z] [--fresh-map]

Run from the repo root with python.exe; the bridge must be held. Exit 0 = every MEASURED row PASS (owed rows are UNMEASURED
and say why). NOT RUN BY THE BUILD ITEM: written offline 2026-10-18.

Owner rulings this proves (2026-10-18, design §11): Q1 "This updates/replaces the old ruling that digging does not change
shooting." · Q2 any dug hole with a wall, wet or dry · Q3 waist-deep a bit under sandbags, chest-deep a bit over ·
Q5 raiders use canals, never one they could not climb out of · Q7 no blast cover.

L1 (offline, not here): python3 src/RimMandrake/Utils/selftest_flowworks_trench_cover.py (the §4 table, enfilade, lip,
pit cover, natural water, stacking, the HitReportFor fold).

Scene (plot coords from --origin, default 120,120; 30 x 16, cleared + read back by validation_core.prepare_site):
  an east-west trench one square wide at z = 5, x = 2..12, dug 2 notches (1 m). Target: a Colonist at (7, 5).
  Shooters (player faction, a ranged pawnkind, so nobody fights): square-on 10 off (7, 15); along the axis (22, 5);
  on the lip (7, 6); one back from the lip (7, 7).
Every read is jawa/static_call RM_TrenchCover.ProofTrenchCover "targetId;shooterId":
  "TRENCH trench=t vanilla=v combined=c hit=h hitNoTrench=h0 cage=b target=x,z shooter=x,z".
hitNoTrench is the same report with trenchCoverEnabled off for that read: the open-ground control without moving anyone.

Rows (MEASURED): TRENCH_square_on_blocks_044, TRENCH_square_on_hit_falls, TRENCH_enfilade_zero, TRENCH_lip_shooter_zero,
TRENCH_one_back_third, TRENCH_wet_same_as_dry (0.5 m of water poured in, square-on read again).
OWED (always UNMEASURED): see OWED.

ANTI-GUESSING NOTES
- A REFUSED read (no ranged verb on the spawned kind, no pawn) is UNMEASURED, never FAIL.
- trench is the mod's own BlockFor; the hit rows compare HitReportFor with the setting on and off for the SAME pair, so
  weather, lighting and skill cancel out.
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

PROOF_TYPE = "RimMandrake.FlowWorks.RM_TrenchCover"
S_FW = "RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings"
SHOOTER_KIND = "Mercenary_Gunner"
SETTLE = 70

OWED = {
    "TRENCH_raiders_cast_from_canal": "needs a raid against a colony with a 1 m canal line (design §10 step 7 row 3)",
    "TRENCH_raiders_skip_sheer_cage": "needs a raid beside a 1.5 m sheer canal; trusts PIT_CLIMB_PROVE_RAIDERS_VS_SHEER_TRENCH",
    "TRENCH_no_blast_cover": "needs a frag grenade on a pawn in the trench vs an open-ground control (damage read)",
    "TRENCH_cast_search_cost": "CastPositionFinder timing on a 500-dug-square map, on vs off",
}


# ============================================================================ verdicts (pure)
def parse(txt):
    kv = {}
    for tok in str(txt).split():
        if "=" in tok:
            k, v = tok.split("=", 1)
            kv[k] = v
    return kv


def num(kv, k):
    try:
        return float(kv.get(k))
    except (TypeError, ValueError):
        return None


def near_verdict(kv, key, want, tol):
    v = num(kv, key)
    if v is None:
        return "UNMEASURED"
    return "PASS" if abs(v - want) <= tol else "FAIL"


def hit_falls_verdict(kv, block, tol=0.03):
    """hit should be about hitNoTrench x (1 - block)."""
    h, h0 = num(kv, "hit"), num(kv, "hitNoTrench")
    if h is None or h0 is None or h0 <= 0.05:
        return "UNMEASURED"
    return "PASS" if abs(h - h0 * (1 - block)) <= tol else "FAIL"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out", nargs="?", default=None)
    ap.add_argument("--origin", default="120,120")
    ap.add_argument("--fresh-map", action="store_true")
    a = ap.parse_args()
    import proof_hose as PH           # noqa: E402  (bridge-side imports only on a live run)
    V = PH.V
    B = PH.PB()
    out = a.out or os.path.join(HERE, "trench_cover_proof_result_%s.json" % time.strftime("%Y%m%dT%H%M%S"))
    rows = []
    res = {"script": "trench_cover_proof.py", "started": time.strftime("%Y-%m-%dT%H:%M:%S"), "rows": rows, "args": vars(a)}

    def save():
        with open(out + ".tmp", "w", encoding="utf-8") as f:
            json.dump(res, f, indent=1, default=str)
        os.replace(out + ".tmp", out)

    def row(rid, st, cls, det):
        rows.append({"id": rid, "status": st, "class": cls, "detail": det})
        print("%-36s %-10s %-6s %s" % (rid, st, cls, json.dumps(det, default=str)[:300]), flush=True)
        save()

    def read(tid, sid):
        r = B.call("jawa/static_call", type=PROOF_TYPE, method="ProofTrenchCover", args="%s;%s" % (tid, sid)) or {}
        txt = str(r.get("result") or r.get("message") or r.get("error") or "")
        return (parse(txt) if r.get("success") is True and txt.startswith("TRENCH") else {}), txt

    def sget(f):
        return B.call("jawa/mod_settings_field", typeName=S_FW, action="get", field=f).get("value")

    def sset(f, v):
        return B.call("jawa/mod_settings_field", typeName=S_FW, action="set", field=f, value=str(v))

    def dig(c, n, fill=-1):
        return B.call("jawa/flowworks_excavation_drive", x=c[0], z=c[1], deepenLevels=n, setFill=fill) or {}

    def spawn(kind, c):
        r = B.call("jawa/spawn_pawn", kindDef=kind, x=c[0], z=c[1], faction="player", count=1) or {}
        return ((r.get("pawns") or [{}])[0]).get("id")

    ox, oz = (int(v) for v in a.origin.split(","))
    P = lambda dx, dz: (ox + dx, oz + dz)                        # noqa: E731
    if a.fresh_map:
        B.call("rimworld/go_to_main_menu")
        B.call("rimworld/start_debug_game_ready", readiness="mapData", pauseIfNeeded=True, timeoutMs=280000)
    ok, _ = V._wait_playing(B, leave_s=0)
    FIELDS = ("trenchCoverEnabled", "trenchCoverStrength", "trenchCoverCap")
    before = {f: sget(f) for f in FIELDS}
    res["settings_before"] = before
    try:
        if not ok or not V.prepare_site(B, (ox, oz, 30, 16), rows, "TRENCH_site_ready"):
            row("TRENCH_site", "UNMEASURED", "SITE", {"why": "site not ready / not playing"})
            return 2
        sset("trenchCoverEnabled", True)
        sset("trenchCoverStrength", 1.0)
        sset("trenchCoverCap", 0.9)
        for x in range(2, 13):
            dig(P(x, 5), 2)
        B.ticks(SETTLE)
        target = spawn("Colonist", P(7, 5))
        shooters = {name: spawn(SHOOTER_KIND, P(*xz)) for name, xz in
                    (("on", (7, 15)), ("axis", (22, 5)), ("lip", (7, 6)), ("back", (7, 7)))}
        res["pawns"] = {"target": target, "shooters": shooters}

        kv, txt = read(target, shooters["on"])
        row("TRENCH_square_on_blocks_044", near_verdict(kv, "trench", 0.441, 0.02) if kv else "UNMEASURED", "MOD",
            {"kv": kv, "txt": txt})
        row("TRENCH_square_on_hit_falls", hit_falls_verdict(kv, num(kv, "trench") or 0.441) if kv else "UNMEASURED", "MOD",
            {"kv": kv})
        kv, txt = read(target, shooters["axis"])
        row("TRENCH_enfilade_zero", near_verdict(kv, "trench", 0.0, 1e-3) if kv else "UNMEASURED", "MOD", {"kv": kv, "txt": txt})
        kv, txt = read(target, shooters["lip"])
        row("TRENCH_lip_shooter_zero", near_verdict(kv, "trench", 0.0, 1e-3) if kv else "UNMEASURED", "MOD", {"kv": kv, "txt": txt})
        kv, txt = read(target, shooters["back"])
        row("TRENCH_one_back_third", near_verdict(kv, "trench", 0.147, 0.01) if kv else "UNMEASURED", "MOD", {"kv": kv, "txt": txt})

        for x in range(2, 13):
            dig(P(x, 5), 0, fill=1)
        B.ticks(SETTLE)
        kv, txt = read(target, shooters["on"])
        row("TRENCH_wet_same_as_dry", near_verdict(kv, "trench", 0.441, 0.02) if kv else "UNMEASURED", "MOD",
            {"kv": kv, "txt": txt})
        for rid, why in OWED.items():
            row(rid, "UNMEASURED", "OWED", {"why": why})
    finally:
        for f, v in before.items():
            if v is not None:
                sset(f, v)
        res["settings_restored"] = {f: sget(f) for f in FIELDS}
        save()
    measured = [r for r in rows if r["class"] != "OWED" and r["id"] != "TRENCH_site_ready"]
    return 0 if measured and all(r["status"] == "PASS" for r in measured) else 1


if __name__ == "__main__":
    sys.exit(main())
