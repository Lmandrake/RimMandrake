#!/usr/bin/env python3
"""Side actions of the 66-row conflict sheet that are not a letter in a decisions file: install the replacement
pictures his B ("swap in a replacement first, then delete it") needs, retire orphaned slots holding a ✕'d
picture, release+purge ✕'d pictures that are only owner-kept, and fill the noslot/kept installs he chose.
Every write goes through artledger (install / retire / purge). Jobs are filed separately (fill_queue).

    python3 Transient/sheet_conflicts_enact_side_2026-10-09.py [--apply]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src/RimMandrake/Utils/art"))
import artledger as L          # noqa: E402
import enact as E              # noqa: E402

OWNER = ('I have just finished that sheet. Every choice was deliberated. Anything "not selected" is left as the '
         'default. Use them all and go now. Use your efficient sheet script.')
VIA = "Transient/sheet_conflicts_review_2026-10-09.decisions.json"
ART = E.artpipe_aux()["artsrc"]


def render(jid):
    p = ART / jid / f"{jid}.png"
    if not p.is_file():
        raise SystemExit(f"no render {p}")
    sha = L.sha256_file(p)
    if not L.store_has(sha):
        L.store_put_file(p)
    return sha


def full(prefix, decisions_rel, row):
    v = json.loads((ROOT / decisions_rel).read_text())["decisions"][row]
    hit = [s for s in v.get("purge") or [] if s.startswith(prefix)]
    if len(hit) != 1:
        raise SystemExit(f"{prefix} not unique in {row}: {hit}")
    return hit[0]


# (mod, rel, job id, auth) — auth: "owner" (displaces a kept picture / his choice) or "collect" (mechanical)
INSTALLS = [
    ("src/RimMandrake/AssailantSalvage", "Things/Building/Ancient/RUT_AncientShieldedTurret.png",
     "RUT_AncientShieldedTurret_v2", "collect"),                                   # replaces ✕ a25f92 (turret)
    *[("src/RimMandrake/TerminalBiomes", f"Things/Pawn/Animal/RM_Hollu/RM_Hollu_{f}.png",
       f"twilightsea_hollu_redo_v3_{f}", "collect") for f in ("east", "north", "south")],
    *[("src/RimMandrake/TerminalBiomes", f"Things/Pawn/Animal/RM_Lunoowa/RM_Lunoowa_{f}.png",
       f"twilightsea_lunoowa_redo_v1_{f}", "owner") for f in ("east", "north", "south")],
    *[("src/RimStarWars/HawkbatArtOverride", f"swanimals/Hawkbat/Hawkbat_j_{f}.png",
       f"regen_gt_canon_hawkbat_juv_v1_{f}", "owner") for f in ("east", "south")],
    ("src/RimMandrake/Abyss", "RM_Abyss/Things/Pawn/Animal/RM_Olumetha/RM_Olumetha_south.png",
     "abyss_olumetha_v4_south", "collect"),                                        # Night Ram pick's missing facing
    ("src/RimMandrake/FeverWood", "Things/Plant/RM_Halquin/RM_Halquin_a.png",
     "feverwood_plant_halquin", "owner"),                                          # Halquin kept:B -> column B
    ("src/RimMandrake/LeaningScrub", "Things/Plant/RM_HoardVenomvine/RM_HoardVenomvine_b.png",
     "0vv_hoard_venomvine_v2", "owner"),                                           # noslot:A pick J, new random slot
    # noslot:A pick E, donor override. The donor body is Graphic_Multi (AA_Mantrap_{east,north,south}.png on disk,
    # no plain AA_Mantrap.png), so the one-picture pick fills all three facings of our override slot.
    *[("src/RimUtinni/UtinniPatches", f"Things/Pawn/Animal/AA_Mantrap/AA_Mantrap_{f}.png",
       "mantrap_improve_a_r7", "owner") for f in ("east", "north", "south")],
]
# orphaned slots (no def names the texPath) holding a picture he ✕'d with B
RETIRE = [
    "src/RimMandrake/LongShade/Textures/Things/Pawn/Animal/RM_Ossik/RM_Ossik_north.png",
    "src/RimStarWars/SWBestiary/Textures/Things/Pawn/Animal/RSW_Ossik/RSW_Ossik_north.png",
    "src/RimMandrake/TerminalBiomes/Textures/Things/Pawn/Animal/RM_Sorruth/RM_Sorruth.png",
]
GT = "Transient/biome_ffar/greentide_sheet_2026-10-05.decisions.json"
PURGE = [(GT, "RSW_Fambaa", p) for p in ("7f0dd6333392", "105e206407cf", "c9a3a0d102da")] + \
        [(GT, "RSW_Gelagrub", p) for p in ("6abd2d80da8a", "80f34fa32f88", "06c241a95ee0")] + \
        [(GT, "RSW_Mott", p) for p in ("d6cc815ed757", "228ee4391696", "84f8df890d71")]


def main(argv):
    apply = "--apply" in argv
    mods = set()
    for mod, rel, jid, auth in INSTALLS:
        sha = render(jid)
        kw = {"owner_said": OWNER} if auth == "owner" else {"reason": "artpipe-collect"}
        try:
            r = L.install(mod, rel, sha, dry_run=not apply,
                          provenance={"kind": "conflict-sheet", "job": jid, "via": VIA}, **kw)
            print(f"install {r['status']:12} {mod}/{rel} <- {jid} {sha[:12]} (old {str(r.get('old'))[:12]})")
            mods.add(mod)
        except L.Refused as e:
            print(f"install REFUSED {mod}/{rel}: {e}")
    for p in RETIRE:
        if not apply:
            print(f"retire (dry) {p} exists={Path(ROOT / p).is_file()}")
            continue
        try:
            r = L.retire(ROOT / p, reason="conflict-sheet B", owner_said=OWNER)
            print(f"retire {r['status']} {p}")
            mods.add(E.mod_of(ROOT / p))
        except L.Refused as e:
            print(f"retire REFUSED {p}: {e}")
    for f, row, pre in PURGE:
        sha = full(pre, f, row)
        if not apply:
            print(f"purge (dry) {row} {sha[:12]} live={L.Index().live_anywhere(sha)}")
            continue
        try:
            L.purge(sha, owner_said=OWNER, via=VIA, release_keep=True)
            print(f"purged {row} {sha[:12]}")
        except L.Refused as e:
            print(f"purge REFUSED {row} {sha[:12]}: {e}")
    print("MODS", sorted(mods))


if __name__ == "__main__":
    main(sys.argv[1:])
