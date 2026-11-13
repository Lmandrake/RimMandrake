"""UNDERPASS RAID live check (SUSPENSION_UNDERPASS_BUILD_MIND_YOUR_HEAD A7: "raiders in a 4 m moat walk under a bridge";
suspension_bridge_proof's owed row UND_raiders_walk_under_moat; BENCH belt 2026-10-22).

  python.exe src/RimMandrake/FlowWorks/northstar/underpass_raid_live.py [out.json] [--origin X,Z] [--fresh-map] [--ticks N]

Scene (plot from --origin, default 40,180; 30 x 9 cleared + read back): a moat x = 0..25, z = 3..4 (2 wide) dug 8 notches
(4 m); a 1-wide steel suspension bridge across it at x = 12, (12,2)-(12,5) (RM_SuspensionProofs.ProofBuild god); two
Mercenary_Slasher (melee) of a hostile faction on the moat floor at (1..2, 3) in a LordJob_AssaultColony; one colonist,
drafted, on the moat floor at (24, 4) -- the only colonist on the map, so the raid's way to him runs along the floor
under the deck.
PROVE raider positions every 60 ticks for --ticks (default 2400).
EXPECT a raider sampled on a deck-covered floor square (12, 3..4) or east of it (x > 12) on the floor.
LIES  raiders that never move (the lord sat) -> UNMEASURED; a raider ON the deck is not under it: x,z alone cannot tell
      deck from floor, so every sample on a decked square reads the pawn's band (RM_SuspensionProofs.ProofBand) and counts
      as under only with under=True onDeck=False; onDeck=True there FAILS. Reaching the far side alone proves no route
      (it may have climbed out and crossed the deck), so a raider east of the bridge with no band-confirmed under sample
      is UNMEASURED (samples tighten to 15 ticks near the bridge). The moat's 8-notch depth is read back before the raid
      (FW_PROOF_TOOLS_HARDEN_READ_GAPS, GPT 6.4).
"""
import re
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
NSP = "RimMandrake.FlowWorks.RM_NorthstarProofs"
SPROOF = "RimMandrake.FlowWorks.Pits.RM_SuspensionProofs"
ITEM = "SUSPENSION_UNDERPASS_BUILD_MIND_YOUR_HEAD"
MOAT_NOTCHES = 8


def band_reading(text):
    """ProofBand's "BAND under=b onDeck=b ..." -> (under, onDeck), or None when the read refused or is unparseable."""
    m = re.search(r"under=(True|False)\b.*?onDeck=(True|False)\b", str(text or ""))
    return None if not m else (m.group(1) == "True", m.group(2) == "True")


def moat_depth_problems(rows, moat, want=MOAT_NOTCHES):
    """excavation_rect rows -> the moat squares shallower than `want` ([] = the 4 m moat really is there; shovels_live's
    moat reads the same `>= 8`)."""
    d = {(r.get("x"), r.get("z")): r.get("d") for r in rows or []}
    return sorted((c, d.get(c)) for c in moat if not isinstance(d.get(c), int) or d[c] < want)


def verdict(moved, seen_under, on_deck, past, band_blind=()):
    """(status, class) of UND_raiders_walk_under_moat. seen_under holds only band-confirmed under samples; a raider read
    ON the deck fails only when none was confirmed under it; a blind band read or a far-side arrival with no confirmed
    under sample measured nothing."""
    if not moved:
        return "UNMEASURED", "SITE"
    if seen_under:
        return "PASS", "MOD"
    if on_deck:
        return "FAIL", "MOD"
    if past or band_blind:
        return "UNMEASURED", "HARNESS"
    return "FAIL", "MOD"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out", nargs="?", default=None)
    ap.add_argument("--origin", default="40,180")
    ap.add_argument("--fresh-map", action="store_true")
    ap.add_argument("--ticks", type=int, default=2400)
    a = ap.parse_args()
    import proof_hose as PH  # noqa: E402
    V = PH.V
    B = PH.PB()
    out = a.out or os.path.join(HERE, "underpass_raid_result_%s.json" % time.strftime("%Y%m%dT%H%M%S"))
    rows = []
    res = {"script": "underpass_raid_live.py", "started": time.strftime("%Y-%m-%dT%H:%M:%S"), "rows": rows, "args": vars(a)}

    def save():
        with open(out + ".tmp", "w", encoding="utf-8") as f:
            json.dump(res, f, indent=1, default=str)
        os.replace(out + ".tmp", out)

    def row(st, cls, det):
        rows.append({"id": "UND_raiders_walk_under_moat", "status": st, "class": cls, "item": ITEM, "detail": det})
        print("%-28s %-10s %-6s %s" % ("UND_raiders_walk_under_moat", st, cls, json.dumps(det, default=str)[:600]), flush=True)
        save()

    def step(n):
        return B.call("rimworld/step_game_ticks", ticks=n, pauseFirst=True, timeoutMs=max(60000, n * 40)) or {}

    ox, oz = (int(v) for v in a.origin.split(","))
    P = lambda dx, dz: (ox + dx, oz + dz)  # noqa: E731
    xz = lambda c: "%d,%d" % c  # noqa: E731
    if a.fresh_map:
        B.call("rimworld/go_to_main_menu")
        B.call("rimworld/start_debug_game_ready", readiness="mapData", pauseIfNeeded=True, timeoutMs=280000)
    ok, _ = V._wait_playing(B, leave_s=0)
    if not ok:
        row("UNMEASURED", "HARNESS", {"why": "no game in Playing"})
        return 2
    res["site_calm"] = V.site_calm(B)
    B.call("jawa/kill_hostiles")
    rect = (ox - 1, oz, 30, 9)
    B.call("jawa/static_call", type=NSP, method="ProofResetRect", args="%d;%d;%d;%d" % rect)
    site_rows = []
    V.prepare_site(B, rect, site_rows, "underpass_site")
    if [r for r in site_rows if r.get("status") not in (None, "PASS")]:
        row("UNMEASURED", "SITE", {"why": "site not prepared", "site": site_rows[:2]})
        return 2
    moat = {P(x, z) for x in range(0, 26) for z in (3, 4)}
    for c in sorted(moat):
        B.call("jawa/flowworks_excavation_drive", x=c[0], z=c[1], deepenLevels=MOAT_NOTCHES, setBodyWaterM=-1)
    ex = B.call("jawa/flowworks_excavation_rect", x=P(0, 3)[0], z=P(0, 3)[1], w=26, h=2, includeTerrain=False) or {}
    shallow = moat_depth_problems(ex.get("rows"), moat)
    if not ex.get("success") or shallow:
        row("UNMEASURED", "SITE", {"why": "the moat is not %d notches deep" % MOAT_NOTCHES, "bad": shallow[:6],
                                   "read": ex.get("success")})
        return 2
    bt = str((B.call("jawa/static_call", type=SPROOF, method="ProofBuild", args="%s;%s;steel;god" % (xz(P(12, 2)), xz(P(12, 5))),
                     _answer=True) or {}).get("result"))
    if "ok=True" not in bt:
        row("UNMEASURED", "SITE", {"why": "the bridge did not build", "build": bt})
        return 2
    for p in (B.call("jawa/list_pawns", limit=400) or {}).get("pawns") or []:
        if not p.get("dead"):
            B.call("jawa/pawn_force_incapacitate", pawn=p.get("id"), action="vanish")
    r = B.call("jawa/spawn_pawn", kindDef="Colonist", x=P(24, 4)[0], z=P(24, 4)[1], faction="player", count=1) or {}
    col = ((r.get("pawns") or [{}])[0]).get("id")
    B.call("jawa/set_draft", pawnId=col, drafted=True)
    probe = B.call("jawa/spawn_pawn", kindDef="Mercenary_Slasher", x=0, z=0, faction="?", count=1, _answer=True) or {}
    fac = next((f["def"] for f in (probe.get("details") or {}).get("available") or []
                if f.get("hostile") and str(f.get("def")).startswith("Pirate")), None)
    if not fac:
        row("UNMEASURED", "SITE", {"why": "no hostile Pirate faction"})
        return 2
    raiders = []
    for k in range(2):
        r = B.call("jawa/spawn_pawn", kindDef="Mercenary_Slasher", x=P(1 + k, 3)[0], z=P(1 + k, 3)[1], faction=fac, count=1) or {}
        pid = ((r.get("pawns") or [{}])[0]).get("id")
        if pid:
            raiders.append(pid)
    B.call("jawa/lord_assault_spawn", pawns=",".join(raiders))
    under = {P(12, 3), P(12, 4)}
    t, trail, seen_under, on_deck, band_blind, past, moved = 0, [], [], [], [], [], False
    first, near = {}, False
    while t < a.ticks:
        dt = 15 if near else 60
        step(dt)
        t += dt
        near = False
        ps = {p.get("id"): p for p in (B.call("jawa/list_pawns", limit=400) or {}).get("pawns") or []}
        snap = []
        for pid in raiders:
            p = ps.get(pid) or {}
            c = (p.get("x"), p.get("z"))
            snap.append((pid, c))
            first.setdefault(pid, c)
            if c != first[pid]:
                moved = True
            if c[0] is not None and abs(c[0] - P(12, 0)[0]) <= 3:
                near = True
            if c in under:
                kb = (B.call("jawa/static_call", type=SPROOF, method="ProofBand", args=re.sub(r"\D", "", str(pid)),
                             _answer=True) or {}).get("result")
                band = band_reading(kb)
                if band is None:
                    band_blind.append((t, pid, c, str(kb)[:80]))
                elif band[0] and not band[1]:
                    seen_under.append((t, pid, c))
                elif band[1]:
                    on_deck.append((t, pid, c))
            if c in moat and c[0] is not None and c[0] > P(12, 0)[0]:
                past.append((t, pid, c))
        trail.append({"t": t, "raiders": snap})
        if seen_under and past:
            break
    res["trail"] = trail
    det = {"bridge": bt, "under": seen_under[:6], "onDeck": on_deck[:6], "bandBlind": band_blind[:4],
           "pastTheBridge": past[:6], "moved": moved, "ticks": t}
    st, cls = verdict(moved, seen_under, on_deck, past, band_blind)
    if st == "UNMEASURED":
        det["why"] = "the raiders never moved" if not moved else "no band-confirmed under sample (band read blind or crossed between samples)"
    row(st, cls, det)
    for pid in raiders + [col]:
        B.call("jawa/pawn_force_incapacitate", pawn=pid, action="vanish", _answer=True)
    res["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    save()
    return 0 if rows and rows[-1]["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
