#!/usr/bin/env python3
"""build_art_sheet.py — one command to (re)build the Lantern Deeps art review sheet.

Generates a review-sheets-format HTML page over every one of the 51 Lantern
Deeps texture slots named in ART_JOBS.md (measured against
infrastructure/artpipe/{done,failed} on 2026-09-18, not re-copied from that
doc): 48 with a facts-PASS render on disk, 1 that FAILED (LanternstoneMedium
variant A — the tool ignored the requested 256x256 and returned 1254x1254), and
2 with no artpipe job at all (the two 2048x2048 wall atlases).

Usage:
    python3 build_art_sheet.py                 # dry run: validates the plan, writes nothing
    python3 build_art_sheet.py --apply          # writes the sheet + thumbnails + decisions seed

Then review it: `python3 <review-sheets skill>/assets/serve_sheet.py --sheet <out> --decisions <decisions>`
Owner picks keep/regen per sprite; wire_art.py --apply then copies exactly the
"keep" rows into Textures/.
"""
import argparse
import json
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
ARTSRC = REPO_ROOT / "infrastructure" / "artpipe" / "_artsrc"
DONE = REPO_ROOT / "infrastructure" / "artpipe" / "done"
FAILED = REPO_ROOT / "infrastructure" / "artpipe" / "failed"
TEMPLATE = Path("/home/mandrake/.claude/skills/review-sheets/assets/sheet_template.html")

OUT_HTML = REPO_ROOT / "Transient" / "deeps_art_review_2026-09-18.html"
OUT_THUMBS_DIR = REPO_ROOT / "Transient" / "deeps_art_thumbs_2026-09-18"
OUT_DECISIONS = REPO_ROOT / "Transient" / "deeps_art_review_2026-09-18.decisions.json"

# (job_id or None, group/def name, effect line, status)
# status: "pass" (facts PASS, image on disk) | "failed" (job ran, no usable image)
#         | "unserved" (no artpipe job exists at all)
#         | "pending" (job filed in artpipe/pending, not yet rendered — DEEP_FLORA_RENAME_1 puffer set)
ROWS = [
    ("lanternstoneterrain_v1", "Terrain/Lanternstone", "Tiling cave floor, 1024x1024 opaque (no alpha needed). MEASURED: real facet texture, mean RGB (20,27,36) — not the flat opaque colour a stale handoff note warned about.", "pass"),
    (None, "WallAtlas/lanternstone_wall_atlas", "Rough natural lanternstone linked-wall atlas, 2048x2048. NO artpipe job exists for this texPath at all — nothing to review, needs a job filed first.", "unserved"),
    (None, "WallAtlas/smoothedlanternstone_wall_atlas", "Polished lanternstone linked-wall atlas, 2048x2048. NO artpipe job exists for this texPath at all.", "unserved"),
    ("lanternstonewallicon_v1", "WallAtlas/lanternstone_wall_icon", "Build-menu icon for the built wall, 64x64.", "pass"),
    ("lanternstonesmall_a_v1", "Crystals/LanternstoneSmall", "Ankle-high cluster, variant A of 3, 256x256, drawSize 1.0.", "pass"),
    ("lanternstonesmall_b_v1", "Crystals/LanternstoneSmall", "Ankle-high cluster, variant B of 3, 256x256.", "pass"),
    ("lanternstonesmall_c_v1", "Crystals/LanternstoneSmall", "Ankle-high cluster, variant C of 3, 256x256.", "pass"),
    ("lanternstonemedium_b_v1", "Crystals/LanternstoneMedium", "Waist-high fan, variant B of 3, 256x256, drawSize 3.0. Also reused as the sowable's GROWN stage.", "pass"),
    ("lanternstonemedium_c_v1", "Crystals/LanternstoneMedium", "Waist-high fan, variant C of 3, 256x256.", "pass"),
    (None, "Crystals/LanternstoneMedium", "Variant A FAILED twice: tool returned 1254x1254 opaque unrelated textures instead of the isolated 256x256 sprite. No usable image on disk — folder currently ships with only 2 of 3 variants.", "failed"),
    ("lanternstonelarge_a_v1", "Crystals/LanternstoneLarge", "Person-height spire group, variant A of 2, 384x384, drawSize 5.0.", "pass"),
    ("lanternstonelarge_b_v1", "Crystals/LanternstoneLarge", "Person-height spire group, variant B of 2, 384x384.", "pass"),
    ("lanternstonehuge_a_v1", "Crystals/LanternstoneHuge", "Building-sized mass, variant A of 2, 512x512, drawSize 7.0. Brief called for a detached blade at a cleave line.", "pass"),
    ("lanternstonehuge_b_v1", "Crystals/LanternstoneHuge", "Building-sized mass, variant B of 2, 512x512.", "pass"),
    ("lanternstonesowableimmature_v1", "Crystals/LanternstoneSowableImmature", "Immature sown stage: single low, barely faceted shoot, 256x256.", "pass"),
    ("lanternstoneitem_a_v1", "Item/Lanternstone", "Cut raw-material stack, variant A of 3 (Graphic_StackCount), 256x256.", "pass"),
    ("lanternstoneitem_b_v1", "Item/Lanternstone", "Cut raw-material stack, variant B of 3, 256x256.", "pass"),
    ("lanternstoneitem_c_v1", "Item/Lanternstone", "Cut raw-material stack, variant C of 3, 256x256.", "pass"),
    ("lanternstonechunk_a_v1", "Chunks/LanternstoneChunk", "Rubble chunk, variant a of 4, 256x256.", "pass"),
    ("lanternstonechunk_b_v1", "Chunks/LanternstoneChunk", "Rubble chunk, variant b of 4, 256x256.", "pass"),
    ("lanternstonechunk_c_v1", "Chunks/LanternstoneChunk", "Rubble chunk, variant c of 4, 256x256.", "pass"),
    ("lanternstonechunk_d_v1", "Chunks/LanternstoneChunk", "Rubble chunk, variant d of 4, 256x256.", "pass"),
    ("twitchingpuffer_tendrils_v1", "Item/Crops/PufferTendrils", "Harvested crop item: heap of cut puffer tentacles, 256x256 (DEEP_FLORA_RENAME_1; render pending).", "pending"),
    ("mycelium_a_v1", "Plant/Mycelium", "Ground-cover filament mat, variant A of 3, 512x512, mostly texture not silhouette.", "pass"),
    ("mycelium_b_v1", "Plant/Mycelium", "Ground-cover filament mat, variant B of 3, 512x512.", "pass"),
    ("mycelium_c_v1", "Plant/Mycelium", "Ground-cover filament mat, variant C of 3, 512x512.", "pass"),
    ("gleamtip_a_v1", "Plant/ZivvitTaper", "Narrow glow-tip mushroom, variant A of 2, 128x128, drawSize 2.0.", "pass"),
    ("gleamtip_b_v1", "Plant/ZivvitTaper", "Narrow glow-tip mushroom, variant B of 2, 128x128.", "pass"),
    ("fungusfern_a_v1", "Plant/QuorrFern", "Fern/fungus bush, variant A of 4, 128x128.", "pass"),
    ("fungusfern_b_v1", "Plant/QuorrFern", "Fern/fungus bush, variant B of 4, 128x128.", "pass"),
    ("fungusfern_c_v1", "Plant/QuorrFern", "Fern/fungus bush, variant C of 4, 128x128.", "pass"),
    ("fungusfern_d_v1", "Plant/QuorrFern", "Fern/fungus bush, variant D of 4, 128x128.", "pass"),
    ("crystaltipbrambles_a_v1", "Plant/OsskBramble", "Thorny shoots with crystal tips, variant A of 2, 128x128.", "pass"),
    ("crystaltipbrambles_b_v1", "Plant/OsskBramble", "Thorny shoots with crystal tips, variant B of 2, 128x128.", "pass"),
    ("yumbulbs_a_v1", "Plant/BrellikBulb", "Squat bulbs, warm-amber glow tip (not blue — deliberate), variant A of 2, 128x128.", "pass"),
    ("yumbulbs_b_v1", "Plant/BrellikBulb", "Squat bulbs, warm-amber glow tip, variant B of 2, 128x128.", "pass"),
    ("twitchingpuffer_grown_v1", "Plant/TwitchingPuffer/PufferGrown", "Grown swollen ball with twitching tentacle fringe, 256x256 (DEEP_FLORA_RENAME_1; render pending).", "pending"),
    ("twitchingpuffer_immature_v1", "Plant/TwitchingPuffer/PufferImmature", "Immature wrinkled ball, tentacle nubs, 256x256 (render pending).", "pending"),
    ("twitchingpuffer_harvested_v2", "Plant/TwitchingPuffer/PufferHarvested", "Harvested/leafless stage — ball sagging, tentacles cut to stubs, 256x256 (v1 rendered a wrapped cocoon: content miss; v2 pending).", "pending"),
    ("crystalcap_a_v1", "Plant/ThrakkCap", "Mushroom tree with crystal-plated cap, variant A of 2, 256x256.", "pass"),
    ("crystalcap_b_v1", "Plant/ThrakkCap", "Mushroom tree with crystal-plated cap, variant B of 2, 256x256.", "pass"),
    ("greyladygrown_a_v1", "Plant/PrennaLace/PrennaLaceGrown", "Grown stage with cloth-like lace (the harvest feature), variant A of 3, 256x256.", "pass"),
    ("greyladygrown_b_v1", "Plant/PrennaLace/PrennaLaceGrown", "Grown stage with lace, variant B of 3, 256x256.", "pass"),
    ("greyladygrown_c_v1", "Plant/PrennaLace/PrennaLaceGrown", "Grown stage with lace, variant C of 3, 256x256.", "pass"),
    ("greyladyimmature_a_v1", "Plant/PrennaLace/PrennaLaceImmature", "Immature stage, cap closed, no lace yet, 256x256.", "pass"),
    ("arpeau_a_v1", "Plant/VellokReed", "Tall aquatic fungus, cyan glow, variant A of 2, 256x256 (tree category).", "pass"),
    ("arpeau_b_v1", "Plant/VellokReed", "Tall aquatic fungus, cyan glow, variant B of 2, 256x256.", "pass"),
    ("luminousspout_a_v1", "Plant/KuvraSpout", "Upside-down glowing cone, shallow water, variant a of 2, 256x256.", "pass"),
    ("luminousspout_b_v1", "Plant/KuvraSpout", "Upside-down glowing cone, variant b of 2, 256x256.", "pass"),
    ("nuitae_a_v1", "Plant/NurrikGill", "Dark cap, glowing underside (bounce light, not a glower), variant A of 2, 256x256.", "pass"),
    ("nuitae_b_v1", "Plant/NurrikGill", "Dark cap, glowing underside, variant B of 2, 256x256.", "pass"),
]


def src_png(job_id):
    return ARTSRC / job_id / f"{job_id}.png"


def build_items(thumbs_relpath):
    items = []
    counts = {"pass": 0, "failed": 0, "unserved": 0, "pending": 0}
    for job_id, group, effect, status in ROWS:
        counts[status] += 1
        rid = job_id or f"MISSING__{group}__{status}"
        thumb = f"{thumbs_relpath}/{job_id}.png" if job_id else None
        prefill = "keep" if status == "pass" else "regen"
        items.append({
            "id": rid,
            "label": group.split("/")[-1] + (f" [{job_id}]" if job_id else " — NO RENDER"),
            "group": group,
            "effect": effect,
            "thumb": thumb,
            "prefill": prefill,
            "inferred": False,
            "contested": status != "pass",
            "occurs": status not in ("unserved", "pending"),
        })
    return items, counts


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true", help="write the sheet, thumbnails and decisions seed (default: dry run)")
    args = ap.parse_args()

    if not TEMPLATE.exists():
        print(f"ERROR: sheet template not found at {TEMPLATE}", file=sys.stderr)
        return 1

    items, counts = build_items(OUT_THUMBS_DIR.name)
    print(f"# build_art_sheet.py plan — {len(items)} rows "
          f"({counts['pass']} pass, {counts['failed']} failed, {counts['unserved']} unserved, {counts['pending']} pending)")
    for it in items:
        print(f"  [{('OK ' if it['thumb'] else 'N/A')}] {it['group']:40s} {it['id']}")

    if not args.apply:
        print(f"\nDry run only. Re-run with --apply to write:\n  {OUT_HTML}\n  {OUT_THUMBS_DIR}/*.png\n  {OUT_DECISIONS}")
        return 0

    OUT_THUMBS_DIR.mkdir(parents=True, exist_ok=True)
    for job_id, group, effect, status in ROWS:
        if status != "pass":
            continue
        src = src_png(job_id)
        if not src.exists():
            print(f"WARNING: {job_id} marked pass but PNG missing at {src}", file=sys.stderr)
            continue
        shutil.copy2(src, OUT_THUMBS_DIR / f"{job_id}.png")

    cfg = {
        "sheetId": "deeps_art_review_2026-09-18",
        "title": "Lantern Deeps — art review",
        "subtitle": f"{len(items)} texture slots · CAVERNS_PARITY_BUILD_1",
        "briefHtml": (
            "<p>Every Lantern Deeps texture slot from "
            "<code>src/RimMandrake/LanternDeeps/ART_JOBS.md</code>, measured against "
            "<code>infrastructure/artpipe/{done,failed}</code> on 2026-09-18. "
            f"<b>{counts['pass']}</b> rendered and passed the facts gate, "
            f"<b>{counts['failed']}</b> FAILED (no usable image — LanternstoneMedium "
            "variant A), and <b>{u}</b> have no artpipe job at all (the two 2048x2048 "
            "wall atlases).</p>"
            "<p>Pick <b>Keep</b> to ship the render as-is, or <b>Regen</b> to send it back "
            "for another pass. Rows with no thumbnail have nothing to keep — Regen is the "
            "only real choice there, this just records that you looked.</p>"
            "<p>Nothing is copied into <code>Textures/</code> until you decide AND "
            "<code>wire_art.py --apply</code> is run afterward — that is a separate, "
            "one-command step.</p>"
        ).replace("{u}", str(counts["unserved"])),
        "criterion": "facts-gate PASS/FAIL from the artpipe manifest — this checks the render met its technical spec (size, alpha, corners transparent), not whether the art is good or on-brief. Judge the picture, not the badge.",
        "invented": [
            "Grouping is by the def's texPath folder name (e.g. Crystals/LanternstoneMedium), one group per Def/graphic slot, matching ART_JOBS.md's own row numbering.",
            "Prefill is 'keep' for every facts-PASS render and 'regen' for the failed/unserved rows — nobody has judged the art itself yet, this only reflects the technical gate.",
        ],
        "posture": {"mode": "whitelist", "explain": "Undecided rows are stripped by wire_art.py — for the 2 unserved rows and the 1 failed row that is correct (there is nothing to keep); for anything else it means you have not looked yet."},
        "options": [
            {"key": "keep", "label": "Keep", "hotkey": "1", "color": "#5ac37f", "counts": "in"},
            {"key": "regen", "label": "Regen", "hotkey": "2", "color": "#e06c6c", "counts": "out"},
        ],
        "groupLabel": "def",
        "media": True,
        "decisionsFile": OUT_DECISIONS.name,
        "decisionsPath": str(OUT_DECISIONS),
        "sheetPath": str(OUT_HTML),
    }

    # Swap the whole CONFIG and ITEMS script bodies by locating the two known
    # script tags rather than hand-matching the demo JSON verbatim.
    import re
    html = TEMPLATE.read_text()
    html = re.sub(
        r'(<script id="CONFIG" type="application/json">\n).*?(\n</script>)',
        lambda m: m.group(1) + json.dumps(cfg, indent=2) + m.group(2),
        html, count=1, flags=re.S,
    )
    html = re.sub(
        r'(<script id="ITEMS" type="application/json">\n).*?(\n</script>)',
        lambda m: m.group(1) + json.dumps(items, indent=2) + m.group(2),
        html, count=1, flags=re.S,
    )
    OUT_HTML.write_text(html)

    if not OUT_DECISIONS.exists():
        OUT_DECISIONS.write_text(json.dumps({
            "sheetId": cfg["sheetId"], "posture": "whitelist", "frozen": False,
            "writeCount": 0, "decisions": {},
        }, indent=2) + "\n")

    print(f"\nWrote {OUT_HTML}")
    print(f"Wrote {len(list(OUT_THUMBS_DIR.glob('*.png')))} thumbnail(s) to {OUT_THUMBS_DIR}")
    print(f"Decisions file: {OUT_DECISIONS}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
