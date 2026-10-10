"""The Rot sheet, 2026-10-10 second ruling: enact ONLY the changed rows (new columns + changed values).

Why not `art.py enact --apply`: its plan (a) installs MortalMorel C/D and PaleTree B/C, letters unchanged since the
first enact (out of scope); (b) skips every row with ✕ but no re-clicked pick (purgeTouched without decidedAt is
"undecided"), so AgelessCap/Nuitae/RegenerantVeil/FruitingBodies/Flakespire ticked variants never install;
(c) swallows CrimsonCap's pick G behind its --mark-done; (d) cannot place Blastpod E/F (by-name renders on a
two-graphic row; the jobs target BoomshroomGrown); (e) would move 21 open notes. This applies the changed actions only.
Usage: python3 therot_newcols_2026-10-10.py [--apply]
"""
import sys
from pathlib import Path

ART = Path(__file__).resolve().parents[2] / "src/RimMandrake/Utils/art"
sys.path.insert(0, str(ART))
import artledger as L  # noqa: E402
import enact as E  # noqa: E402
import ingest as I  # noqa: E402

APPLY = "--apply" in sys.argv
DEC = Path(__file__).resolve().parent / "therot_sheet_2026-10-05.decisions.json"
P = "RotSporeKit/Things/Plant/"
CHANGED = ["AA_AngelMoth", "AB_GlowingAgarilux", "AB_Glowstool", "AB_LilacBeacon", "AB_SlimyPholiota",
           "AB_WitchesOyster", "RM_AgelessCap", "RM_BlastpodShroom", "RM_BleedingTooth", "RM_Brightbell",
           "RM_CrimsonCap", "RM_FalseFruit", "RM_FlakespireFungus", "RM_FruitingBodies", "RM_GreyLady",
           "RM_MortalMorelPlant", "RM_Nuitae", "RM_PaleTree", "RM_Pusmelon", "RM_RegenerantVeil", "RM_Sagecrust",
           "RM_VioletWimple", "RM_Wrinklecap"]
# (row, letter, folder graphic) — new ticks/picks of renders, one file each beside the folder's pictures
INSTALL = [("AB_GlowingAgarilux", l, None) for l in "BC"] + [("AB_Glowstool", l, None) for l in "BC"] + \
    [("AB_LilacBeacon", l, None) for l in "BC"] + [("AB_SlimyPholiota", l, None) for l in "BC"] + \
    [("RM_AgelessCap", l, None) for l in "DE"] + [("RM_Brightbell", l, None) for l in "DE"] + \
    [("RM_CrimsonCap", l, None) for l in "GH"] + [("RM_FalseFruit", l, None) for l in "CD"] + \
    [("RM_FlakespireFungus", l, None) for l in "CD"] + [("RM_FruitingBodies", l, None) for l in "EF"] + \
    [("RM_BlastpodShroom", l, P + "Boomshroom/BoomshroomGrown") for l in "EF"] + \
    [("RM_MortalMorelPlant", l, None) for l in "FG"] + [("RM_Nuitae", l, None) for l in "FG"] + \
    [("RM_PaleTree", l, None) for l in "DE"] + [("RM_Pusmelon", l, None) for l in "CD"] + \
    [("RM_RegenerantVeil", l, None) for l in "DE"] + [("RM_Sagecrust", "D", None)]
# ✕'d folder pictures that leave the folder (never a folder's last picture: checked below)
RETIRE_ROWS = ["RM_CrimsonCap", "RM_BlastpodShroom", "RM_FruitingBodies", "RM_FlakespireFungus", "RM_RegenerantVeil"]


def main():
    doc = I.json.loads(DEC.read_text()) if hasattr(I, "json") else __import__("json").loads(DEC.read_text())
    snap = __import__("json").loads((L.REPO_ROOT / doc["snapshot"]).read_text())["rows"]
    decs = doc["decisions"]
    skip = [r for r in decs if r not in CHANGED]
    ing = I.ingest(DEC, dry_run=not APPLY, defer_redo_jobs=True, purge=False, skip_rows=skip)
    print("ingest:", {k: ing.get(k) for k in ("ok", "rulings", "rejected", "error", "stale_rows")})
    idx = L.Index()
    out = {"keeps_recorded": [], "installed": [], "retired": [], "purged": [], "kept_last": [], "problems": []}
    # 0 ingest skips ticked variants on a row whose last touch included a ✕ and no pick re-click (purgeTouched,
    # no decidedAt) — but a tick stamps variantsAt, a real click. Record those keeps exactly as ingest would.
    via = I.rel_via(DEC)
    w = L.Writer({e["id"] for e in idx.events})
    for row, letter, _g in INSTALL:
        v, srow = decs[row], snap[row]
        if letter not in (v.get("variants") or []) or not v.get("variantsAt"):
            continue
        sha = srow["columns"][letter]["single"]
        if sha in (v.get("purge") or []) or E.keep_ruling(idx, row, letter, sha):
            continue
        ev = {"type": "ruling", "id": L.det_id("ruling-sheet", via, row, letter, v["variantsAt"]),
              "target": {"shas": [sha], "column": letter, "row": row, "variant_of": v.get("decision")},
              "verdict": "keep", "by": "owner", "said": v.get("note") or "", "note": v.get("note") or "",
              "at": v["variantsAt"], "trust": "ruled", "via": via, "subject_key": srow.get("subject_key", ""),
              "source_file": via, "evidence": "sidecar savedBy/writeCount; variant tick (variantsAt) on a "
                                              "purge-touched row, which ingest leaves unrecorded"}
        if APPLY:
            w.add(ev)
        out["keeps_recorded"].append(f"{row} {letter} {sha[:8]}")
    if APPLY:
        w.flush()
        idx = L.Index()
    # 1 install
    for row, letter, g in INSTALL:
        srow = snap[row]
        sha = srow["columns"][letter]["single"]
        g = g or E.gof_resolved(srow, letter)
        if sha in (decs[row].get("purge") or []):
            out["problems"].append(f"{row} {letter}: ✕'d, not installed")
            continue
        if idx.live_anywhere(sha):
            out["installed"].append(f"{row} {letter}: already live {idx.live_anywhere(sha)[0]}")
            continue
        fs = E.folder_slots(idx, g)
        if not fs:
            out["problems"].append(f"{row} {letter}: {g} is not a folder of ours")
            continue
        rel = f"{g}/{g.rsplit('/', 1)[-1]}_{letter.lower()}.png"
        rul = E.keep_ruling(idx, row, letter, sha)
        if not rul:
            out["problems"].append(f"{row} {letter}: no keep ruling for {sha[:12]}")
            continue
        if APPLY:
            r = L.install(fs[0][0], rel, sha, ruling_id=rul["id"])
            out["installed"].append(f"{row} {letter}: {rel} {r['status']}")
        else:
            out["installed"].append(f"{row} {letter}: WOULD install {rel} ({sha[:8]}, ruling {rul['id'][:12]})")
    idx = L.Index()
    # 2 retire ✕'d folder pictures, never a folder's last
    for row in RETIRE_ROWS:
        xed = set(decs[row].get("purge") or [])
        for g in sorted({x for x in snap[row]["graphic_of"].values() if x != "_byname"}):
            slots = E.folder_slots(idx, g)
            keep = [s for s in slots if s[2] not in xed]
            for m, r, sha in slots:
                if sha not in xed:
                    continue
                if not keep:
                    out["kept_last"].append(f"{row}: {r} (✕ but the folder's last picture)")
                    continue
                prot = idx.protected(sha)
                if any(not ((k.get("target") or {}).get("row") == row and k.get("via") == via) for k in prot):
                    out["problems"].append(f"{row}: {r} owner-kept by another ruling — not retired")
                    continue
                if APPLY:
                    # his only keep on it is this row's earlier pick in this same file, superseded by his ✕ here
                    L.retire(L.src_root().parent / m / "Textures" / r, reason=E.WRITER_TAG,
                             owner_said=f"reject+purge on sheet {doc['sheetId']}" if prot else None)
                out["retired"].append(f"{row}: {r}")
    # GreyLadyImmature_a: ✕ but the immature folder's only picture
    out["kept_last"].append("RM_GreyLady: GreyLady/GreyLadyImmature/GreyLadyImmature_a.png (✕ but the folder's only picture)")
    idx = L.Index()
    # 3 purge every new ✕ that is no longer live and not protected
    for row in CHANGED:
        for sha in decs[row].get("purge") or []:
            if idx.is_purged(sha):
                continue
            live = idx.live_anywhere(sha)
            if live and not (not APPLY and all(any(x.endswith(r.split("Textures/")[-1]) for x in out["retired"])
                                               for r in live)):
                out["problems"].append(f"{row}: ✕ {sha[:12]} stays live at {live[0]} — not purged")
                continue
            kept = [k for k in idx.protected(sha) if not ((k.get("target") or {}).get("row") == row
                                                           and k.get("via") == I.rel_via(DEC))]
            if kept:
                out["problems"].append(f"{row}: ✕ {sha[:12]} owner-kept elsewhere ({kept[0].get('via')}) — not purged")
                continue
            if APPLY:
                L.purge(sha, owner_said=I.open_note(decs[row]) or f"reject+purge on sheet {doc['sheetId']}",
                        via=I.rel_via(DEC), release_keep=bool(idx.protected(sha)))
            out["purged"].append(f"{row}: {sha[:12]}")
    for k, v in out.items():
        print(f"{k} ({len(v)})")
        for x in v:
            print("  ", x)


if __name__ == "__main__":
    main()
