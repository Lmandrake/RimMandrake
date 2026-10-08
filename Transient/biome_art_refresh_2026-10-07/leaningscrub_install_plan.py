"""Leaning Scrub sheet (leaningscrub_sheet_2026-10-05) — plan/apply the owner's 2026-10-08 picks through the art ledger.
Same method as longshade_install_plan.py: the pick's pictures replace the IN-GAME column's live slots of that graphic.
Extra per-graphic picks (juvenile, female, swimming …) are handled the same way against their own graphic.
Skips: a pick whose every picture is already live somewhere (already current); a slot whose live picture was put there
by ANOTHER sheet's ruling tonight (cross-sheet conflict -> a question, never overwritten).
Usage: python3 leaningscrub_install_plan.py [--apply] [--rows A,B]"""
import json, sys
from pathlib import Path
R = Path("/home/mandrake/rm/bench")
sys.path.insert(0, str(R / "src/RimMandrake/Utils/art"))
import artledger as L

DEC = R / "infrastructure/state/art_rulings/2026-10-08_leaningscrub_sheet_2026-10-05.decisions.json"
SNAP = R / "infrastructure/state/art/sheets/leaningscrub_sheet_2026-10-05.snapshot.json"
VIA = "leaningscrub_sheet_2026-10-05"
# a _byname pick that names a DIFFERENT column of the same graphic as the decision is a variant, not a second primary
VARIANT_NOT_PRIMARY = {("RSW_Scurrier", "E")}
# a primary pick that is east-only, completed by the owner's other column for north/south (derived N/S of that east)
COMPLETE = {("RSW_Strill", "C"): "D"}


def main(apply, only):
    d = json.loads(DEC.read_text())["decisions"]; s = json.loads(SNAP.read_text())["rows"]
    idx = L.Index()
    live_shas = {}
    for (m, r), ev in idx.live.items():
        live_shas.setdefault(ev.get("sha"), []).append((m, r, ev))
    rul = {}
    for e in idx.rulings:
        t = e.get("target") or {}
        if VIA in (e.get("via") or "") and t.get("column") and L.normalise_verdict(e.get("verdict")) == "keep":
            rul.setdefault((t["row"], t["column"]), e["id"])
    rul_via = {e["id"]: (e.get("via") or "", e.get("at") or "") for e in idx.rulings}
    out = []
    for row, v in sorted(d.items()):
        if not v.get("at", "").startswith("2026-10-08") or (only and row not in only):
            continue
        dec = (v.get("decision") or "").strip()
        if len(dec) != 1 or row not in s:
            continue
        sr = s[row]; cols, gof, lab = sr["columns"], sr["graphic_of"], sr["labels"]
        jobs = [(dec, gof[dec])] + [(pl, g) for g, pl in (v.get("picks") or {}).items() if pl != dec or g != gof[dec]]
        for col, g in jobs:
            if (row, col) in VARIANT_NOT_PRIMARY:
                out.append({"row": row, "col": col, "status": "variant (not a primary) -> follow-up"}); continue
            if col not in cols:
                out.append({"row": row, "col": col, "status": "NO COLUMN"}); continue
            gg = sr.get("res") if g == "_byname" else g
            new = dict(cols[col])
            if (row, col) in COMPLETE:
                for f, h in cols[COMPLETE[(row, col)]].items():
                    new.setdefault(f, h)
            if all(h in live_shas for h in new.values()):
                out.append({"row": row, "col": col, "graphic": gg, "status": "already live"}); continue
            ing = [c for c in cols if (lab[c].startswith("IN GAME") or lab[c].startswith("our deployed art")) and (gof[c] == gg)]
            if not ing:
                out.append({"row": row, "col": col, "graphic": gg, "status": "NO IN-GAME COLUMN"}); continue
            ic = ing[0]
            for facing, newsha in sorted(new.items()):
                old = cols[ic].get(facing)
                base = gg.split("/")[-1] + ("" if facing == "single" else "_" + facing) + ".png"
                slots = [(m, r, ev) for (m, r, ev) in live_shas.get(old, [])
                         if (r.endswith("/" + base) and r.startswith(gg.rsplit("/", 1)[0] + "/"))
                         or (facing == "single" and r.startswith(gg + "/"))]
                if not slots:
                    out.append({"row": row, "col": col, "facing": facing, "status": f"old {str(old)[:10]} has no live slot at {gg}"}); continue
                src_col = col if cols[col].get(facing) == newsha else COMPLETE.get((row, col), col)
                rid = rul.get((row, src_col))
                for m, r, ev in slots:
                    rec = {"row": row, "col": col, "mod": m, "rel": r, "sha": newsha[:12], "ruling": rid}
                    pv = rul_via.get(ev.get("ruling_id"), ("", ""))
                    if pv[0] and VIA not in pv[0] and pv[1].startswith("2026-10-08"):
                        rec["status"] = f"CONFLICT: live picture put there tonight by {Path(pv[0]).name}"
                        out.append(rec); continue
                    if apply:
                        try:
                            res = L.install(m, r, newsha, ruling_id=rid)
                            rec["status"] = res.get("status") if isinstance(res, dict) else str(res)
                        except L.Refused as e:
                            rec["status"] = "REFUSED " + str(e)
                    else:
                        rec["status"] = "plan"
                    out.append(rec)
    for o in out:
        print(json.dumps(o))


only = None
if "--rows" in sys.argv:
    only = set(sys.argv[sys.argv.index("--rows") + 1].split(","))
main("--apply" in sys.argv, only)
