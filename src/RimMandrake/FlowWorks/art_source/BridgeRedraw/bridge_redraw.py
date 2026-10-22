#!/usr/bin/env python3
"""Bridge art redraw — candidates for all 12 items of GPT's ranked redraw list (BRIDGE_ART_REDRAW_CABINETS_GROW_SADDLES;
owner by card 2026-10-21 "Redraw all 12 now") plus the drawbridge renders that never arrived (image-service 429s).
Review: Transient/pile_2026-10-21/bridge_art_gpt_review.md. Nothing here installs anything.

    bridge_redraw.py list [--wave N]                  the job table
    bridge_redraw.py guides                           grey geometry guides (raised leaf: one span for all three views)
    bridge_redraw.py gen --wave N [--only ID..] [--workers 12] [--timeout 520]
                                                      codex $imagegen, one worker home per job, raw -> RAW (outside git)
    bridge_redraw.py finalize [--wave N]              conform to canvas, reference-free checks, register artpipe done jobs
    bridge_redraw.py manifest                         texture manifest for art_sheet.py --textures (finalized jobs only)

Raw renders live under the agent storage root (D:\\ClaudeWork\\rimmandrake\\bridge_redraw\\raw); conformed candidates in out/.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
R = HERE.parents[4]
TEX = R / "src/RimMandrake/FlowWorks/Textures"
SB = "RimMandrake/FlowWorks/SuspensionBridge"
BASE = "Things/Building/FlowWorks/SuspensionBridge"
DBT = "Things/Building/FlowWorks/Drawbridge"
GPT = R / "Transient/pile_2026-10-21/bridge_art_gpt"
STORE = Path(subprocess.run([sys.executable, str(Path.home() / "dev/Lodestar/bin/lib/agent_storage.py")],
                            capture_output=True, text=True, check=True).stdout.strip()) / "rimmandrake"
RAW = STORE / "bridge_redraw" / "raw"
AP = STORE / "artpipe"
ARTSRC = AP / "_artsrc"
OUT = HERE / "out"
GUIDES = HERE / "guides"
RESULTS = HERE / "results.json"
ITEM = "BRIDGE_ART_REDRAW_CABINETS_GROW_SADDLES"
CI = [sys.executable, str(R / "skills/generating-images/scripts/codex_image.py")]
HOMES = Path("/mnt/c/Users/Mandrake/.codex_workers")
LOOKS = ["Scrapper", "Industrial", "Modern", "Futuristic"]
# already-seeded worker homes (a NEW home cannot be seeded while the sandbox seed template lags the codex build)
WORKER_HOMES = ["bench_lad1", "bench_lad2", "bench_lad3", "bench_lad4", "bench_lad5", "bench_spk1", "bench_spk2",
                "bench_spk3", "bench_spk4"]  # dw1-4, pyr0-3: 401 unauthorized


def done_png(job):
    return AP / "_artsrc" / job / f"{job}.png"


# ------------------------------------------------------------------------------------------------ the shared language
LOOK = {
    "Scrapper": "SCRAPPER look: salvaged scavenger work - mismatched weathered warm-brown timber, a few LARGE rusty "
                "orange-brown scrap-steel sheets, chunky tan rope lashings; warm 1970s earth-brown palette",
    "Industrial": "INDUSTRIAL look: dark gunmetal-grey steel plate and heavy beams, a few LARGE bolts, yellow-and-black "
                  "hazard paint used only as one or two broad bands",
    "Modern": "MODERN look: clean light-grey galvanised steel and smooth grey panels framed by bold glossy RED painted "
              "steel channels, a few zinc fittings",
    "Futuristic": "FUTURISTIC look: matte off-white and pale-grey composite panels, dark charcoal recessed seams, at most "
                  "one or two thin teal accent strips - matte, never glowing",
    "Timber": "base TIMBER: weathered warm-brown timber with dark iron nail heads and broad iron strap plates",
    "Steel": "base STEEL: plain mid-grey riveted steel plate and dark iron fittings, regular engineered framing",
    "Base": "the base set: weathered warm-brown timber, mid-grey steel plate, dark iron fittings, tan hemp rope",
}
TIER = {
    "Heavy": "HEAVY tier: massive and over-built - a broad thick structural frame, chunky members, lots of mass",
    "Steel": "STEEL tier: lighter all-metal construction - a SLIM frame, thinner members, visibly less mass than heavy",
    "Timber": "TIMBER tier: the body is unmistakably WOOD - broad wooden boards or beams with visible grain, held by the "
              "look's metal fittings",
}
READ = ("It must read at 32 pixels per cell: a few big bold shapes and strong value contrast; no fine mesh, no rows of "
        "tiny rivets, no thin chains, no hairline detail. Clean painterly vanilla-RimWorld rendering, matte surfaces, "
        "soft overhead-front light, a thin dark edge line around each part.")
ALPHA = ("Fully transparent background with real alpha: nothing painted on the ground around it, no cast shadow, no "
         "backdrop.")
CAM = ("Orthographic RimWorld building camera, about 35 degrees above horizontal: top faces clearly visible and lit, "
       "the front face short and foreshortened, square-on to the viewer (never a diagonal three-quarter view).")
TOP = "Seen from straight above, flat like a floor, no perspective, no taper."


def tile_prompt(what, layout_img=True):
    lay = (" Same layout as image 1: the walking surface down the middle and a side band down each of the left and right "
           "edges (each about one ninth of the width)." if layout_img else "")
    return (f"Paint ONE seamless square tile of a suspension-bridge walkway deck for RimWorld, 1 cell. {TOP} The walking "
            f"surface runs top-to-bottom in the direction of travel and repeats seamlessly top to bottom.{lay} {what} "
            f"{READ} The tile fills the whole square edge to edge.")


# ------------------------------------------------------------------------------------------------------- the job table
JOBS: list[dict] = []
ROWS: dict[str, dict] = {}


def row(key, label, part, look, res, size, refs=(), section="Bridge redraw"):
    ROWS.setdefault(key, {"key": key, "label": label, "part": part, "look": look, "section": section,
                          "resources": [res] if res else [], "size": size, "render_match": None, "jobs": [],
                          "reference_textures": [str(p) for p in refs]})
    return key


def job(wave, rank, rkey, jid, kind, canvas, prompt, images=(), target_def=None, texpath=None, facing=None, gen=(1024, 1024)):
    full = f"{jid}_{facing}" if facing else jid
    JOBS.append({"id": full, "family": jid, "wave": wave, "rank": rank, "row": rkey, "kind": kind, "canvas": canvas,
                 "prompt": prompt, "images": [str(i) for i in images], "target_def": target_def,
                 "target_texpath": texpath, "facing": facing, "gen": gen})
    ROWS[rkey]["jobs"].append(full)


S1 = {"drawSize": [1, 1], "footprint": [1, 1], "source": "def graphicData (default drawSize 1)"}
S15 = {"drawSize": [1.5, 1.5], "footprint": [1, 1], "source": "flowworks_drawbridge_design_2026-10-20.md §R12"}
SG = {"drawSize": [1, 1.5], "footprint": [1, 1], "source": "flowworks_drawbridge_design_2026-10-20.md §R12"}
SL = {"drawSize": [1, 4], "footprint": [1, 1], "source": "flowworks_drawbridge_design_2026-10-20.md §R12"}


def rel(p):
    p = Path(p)
    return str(p.relative_to(R)) if p.is_relative_to(R) else str(p)


def build():
    # ---- rank 1: styled towers (two candidates each) -------------------------------------------------- wave 1
    for lk in LOOKS:
        k = row(f"RD_Tower_{lk}", f"tower — {lk} (rank 1: saddle top, short front, projecting base)", "Tower", lk,
                f"{SB}/{lk}/RM_SuspensionTower", S1, [TEX / f"{SB}/{lk}/RM_SuspensionTower.png"])
        base = ("Redraw the suspension-bridge TOWER for RimWorld, 1x1 cell, square image. A short sturdy tower that carries "
                "the bridge's two main cables over its top. Show the broad cable SADDLE on top as a clearly visible "
                "horizontal top plane with the two thick cables draped over it in grooves; the front face is SHORT and "
                "foreshortened (never a tall cabinet or locker panel); a short visible south face; a broad base plinth that "
                "projects outward beyond the legs into the ground.")
        imgs = [GPT / "sample_tower_industrial.png", TEX / f"{SB}/{lk}/RM_SuspensionTower.png"]
        job(1, 1, k, f"RM_SuspensionTower_{lk}_rd1a", "fit", (256, 256),
            f"{base} Composition and camera of image 1 (two stout legs joined at the saddle); materials and palette of "
            f"image 2 and the {LOOK[lk]}. {CAM} {READ} {ALPHA} Fills about 80% of the image, centred.", imgs,
            f"RM_SuspensionTower_{lk}", f"{SB}/{lk}/RM_SuspensionTower")
        job(1, 1, k, f"RM_SuspensionTower_{lk}_rd1b", "fit", (256, 256),
            f"{base} This one is a single squat tapered pylon block (wider at the base than the top) with a big grooved "
            f"saddle casting on top, the cables sweeping over it. Materials and palette of image 2 and the {LOOK[lk]}. "
            f"{CAM} {READ} {ALPHA} Fills about 80% of the image, centred.", imgs,
            f"RM_SuspensionTower_{lk}", f"{SB}/{lk}/RM_SuspensionTower")

    # ---- rank 2: drawbridge lowered deck / planks ------------------------------------------------------ wave 1
    pl = {"Timber": "broad weathered warm-brown timber boards with dark iron nail heads, two flat iron straps across",
          "Steel": "plain mid-grey steel tread plate in three long panels, a few large flush bolts",
          "Scrapper": "mismatched salvaged timber boards with one or two large rusty scrap-steel patches, flush and flat",
          "Industrial": "dark gunmetal steel plate in long panels, one broad yellow-black hazard band at each end",
          "Modern": "smooth light-grey steel panels with shallow seams and flush joints, a slim red edge channel each side",
          "Futuristic": "matte off-white composite deck plates, dark recessed seams, one thin teal strip down each edge"}
    for lk, mat in pl.items():
        tex = f"{DBT}/RM_DrawbridgePlanks_{lk}"
        cur = {"Steel": done_png("RM_DrawbridgePlanks_Steel"), "Modern": done_png("RM_DrawbridgePlanks_Modern")}.get(lk)
        k = row(f"RD_DBPlanks_{lk}", f"drawbridge lowered deck — {lk} (rank 2: flat parallel-sided tread)" +
                ("" if cur else " · never rendered before"), "DBPlanks", lk, tex, S1, [cur] if cur else [])
        job(1, 2, k, f"RM_DrawbridgePlanks_{lk}_rd1a", "fit", (256, 256),
            f"Paint the lowered DRAWBRIDGE DECK section for RimWorld, 1x1 cell, square image. {TOP} A flat, parallel-sided "
            f"walking deck covering about 90% of the square, its boards or plates running top to bottom in the direction "
            f"of travel, straight sides, flush seams, hardware only along the two side edges, nothing lying across the "
            f"tread, no stacked layers, no raised bands, no chain. {mat}. Like the flat deck in image 1. {READ} {ALPHA}",
            [GPT / "sample_drawbridge_planks_steel.png"], None, tex)

    # ---- rank 3: raid plank ---------------------------------------------------------------------------- wave 1
    k = row("RD_RaidPlank_Laid", "raid plank, laid (rank 3: continuous flat tread)", "RaidPlank", "Base",
            f"{DBT}/RM_RaidPlank_Laid", S1, [done_png("RM_RaidPlank_Laid")])
    job(1, 3, k, "RM_RaidPlank_Laid_rd1a", "fit", (256, 256),
        f"Paint a RAID PLANK laid across a gap as a walkway, RimWorld, 1x1 cell, square image. {TOP} Three or four rough "
        f"split timber planks lashed side by side into ONE flat continuous tread running top to bottom, straight-sided, "
        f"covering about 85% of the square; two shallow flat iron straps across; a single rope loop tucked along one side "
        f"margin; flat even lighting, no raised rings, no handles. Weathered warm-brown timber like image 1. {READ} {ALPHA}",
        [GPT / "sample_raidplank_laid.png"], "RM_RaidPlank_Laid", f"{DBT}/RM_RaidPlank_Laid")
    k = row("RD_RaidPlank_LaidEnd", "raid plank, laid end (rank 3)", "RaidPlank", "Base", f"{DBT}/RM_RaidPlank_LaidEnd", S1,
            [done_png("RM_RaidPlank_LaidEnd")])
    job(1, 3, k, "RM_RaidPlank_LaidEnd_rd1a", "fit", (256, 256),
        f"Paint the END piece of a RAID PLANK walkway, RimWorld, 1x1 cell, square image. {TOP} Three or four rough split "
        f"timber planks lashed side by side into one flat continuous tread running top to bottom; at the bottom the planks "
        f"end cut square on a flat iron lip that bites into the ground; the tread runs on to the top edge. Shallow flat iron "
        f"straps, the rope tucked along the side margin, flat lighting, no raised rings or handles. Same timber as image 1. "
        f"{READ} {ALPHA}", [GPT / "sample_raidplank_laid.png"], None, f"{DBT}/RM_RaidPlank_LaidEnd")
    k = row("RD_RaidPlank_Item", "raid plank, carried item (rank 3: a plank, not a log)", "RaidPlank", "Base",
            f"{DBT}/RM_RaidPlank", S1, [done_png("RM_RaidPlank")])
    job(1, 3, k, "RM_RaidPlank_Item_rd1a", "fit", (256, 256),
        f"Paint a carryable RAID PLANK item lying on the ground, RimWorld item sprite, square image, seen from above and "
        f"slightly in front: one long straight split-trunk plank, its flat sawn walking top facing up and clearly visible, "
        f"rough bark only along its two sides, a rope carry loop at one end, two flat iron straps; straight and even in "
        f"width (no taper, no branches, no foliage, no round log end), lying diagonally across the square. Weathered "
        f"warm-brown timber like image 1. {READ} {ALPHA} Fills about 85% of the diagonal.",
        [GPT / "sample_raidplank_laid.png"], "RM_RaidPlank", f"{DBT}/RM_RaidPlank")

    # ---- rank 4: timber decks in the three metal looks ---------------------------------------------------- wave 2
    tdk = {"Industrial": "broad timber boards in the middle; the side bands are dark gunmetal steel channels with a few big "
                         "bolts and riveted steel straps crossing the boards",
           "Modern": "broad clean pale timber boards in the middle; the side bands are glossy red painted steel channels",
           "Futuristic": "broad smooth honey-coloured timber boards in the middle; the side bands are matte off-white "
                         "composite rails with a dark seam and one thin teal strip"}
    for lk, w in tdk.items():
        k = row(f"RD_DeckTimber_{lk}", f"timber deck — {lk} (rank 4: show wood)", "DeckTimber", lk,
                f"{SB}/{lk}/RM_SuspensionDeck", S1, [TEX / f"{BASE}/RM_SuspensionDeck_Timber.png"])
        job(2, 4, k, f"RM_SuspensionDeck_Timber_{lk}_rd1a", "tile", (256, 256),
            tile_prompt(f"{TIER['Timber']}: {w}. The wood must dominate, like the timber deck in image 2. {LOOK[lk]}."),
            [TEX / f"{SB}/{lk}/RM_SuspensionDeck.png", TEX / f"{BASE}/RM_SuspensionDeck_Timber.png"],
            f"RM_SuspensionDeck_Timber_{lk}", f"{SB}/{lk}/RM_SuspensionDeck_Timber")

    # ---- rank 5: styled anchors, three tiers (south view) ------------------------------------------------- wave 2
    ank = {"Heavy": "a BROAD grounded mounting shoe bolted into the ground with oversized bolts, a big heavy housing, a "
                    "thick cable",
           "Steel": "a COMPACT light steel bracket on a narrow bolted shoe, exposed tensioning hardware, a slimmer cable",
           "Timber": "a big WOODEN SLEEPER - a thick squared timber beam with visible grain and end-grain faces - lying "
                     "in the ground, the tensioner clamped onto it"}
    for lk in LOOKS:
        for tr, w in ank.items():
            k = row(f"RD_Anchor_{tr}_{lk}", f"anchor {tr.lower()} — {lk} (rank 5: distinct tier silhouette)", f"Anchor{tr}",
                    lk, f"{SB}/{lk}/RM_SuspensionAnchor", S1,
                    [TEX / f"{SB}/{lk}/RM_SuspensionAnchor_south.png", TEX / f"{BASE}/RM_SuspensionAnchor_{tr}.png"])
            job(2, 5, k, f"RM_SuspensionAnchor_{tr}_{lk}_rd1a", "fit", (256, 256),
                f"Redraw the suspension-bridge cable ANCHOR for RimWorld, 1x1 cell, seen from the south, square image. "
                f"{TIER[tr]}: {w}. The construction and silhouette follow image 2 (the base {tr.lower()} anchor); the "
                f"position, size and the direction the cable leaves follow image 1. {LOOK[lk]}. {CAM} {READ} {ALPHA}",
                [TEX / f"{SB}/{lk}/RM_SuspensionAnchor_south.png", TEX / f"{BASE}/RM_SuspensionAnchor_{tr}.png"],
                f"RM_SuspensionAnchor_{tr}_{lk}", f"{SB}/{lk}/RM_SuspensionAnchor_{tr}", facing="south")

    # ---- rank 6: raised leaf, three views sharing one span (and the missing look leaves) ------------------- wave 3
    lmat = {"Timber": "weathered warm-brown timber planks with broad dark iron straps and a big iron hinge barrel",
            "Steel": "mid-grey steel plate deck in three big panels with a heavy dark steel frame and hinge barrel, a few "
                     "large bolts",
            **{lk: LOOK[lk] for lk in LOOKS}}
    view = {"Face": ("the TOP FACE (walking surface) of the raised leaf: its deck boards or plates run along its length, "
                     "a strong dark outline, a big hinge barrel across the bottom end", "guide_leaf_face.png"),
            "Underside": ("the UNDERSIDE of the raised leaf: two long stringers down its length with a few bold diagonal "
                          "braces between them, the same outline and the same hinge barrel across the bottom end",
                          "guide_leaf_face.png"),
            "Edge": ("the raised leaf seen EDGE-ON: a narrow vertical strip showing the leaf's thickness, a continuous dark "
                     "outline, a lighter thickness strip, a distinct hinge block at the bottom and one bold lifting rope "
                     "or cable from the top", "guide_leaf_edge.png")}
    for lk in ["Timber", "Steel", *LOOKS]:
        for v, (w, g) in view.items():
            tex = f"{DBT}/RM_DrawbridgeLeafUp_{lk}_{v}" if lk in ("Timber", "Steel") else f"{DBT}/RM_DrawbridgeLeafUp_{v}_{lk}"
            src = f"RM_DrawbridgeLeafUp_{lk}_{v}" if lk in ("Timber", "Steel") else f"RM_DrawbridgeLeafUp_{v}_{lk}"
            cur = done_png(src)
            k = row(f"RD_Leaf_{lk}_{v}", f"raised leaf {v.lower()} — {lk} (rank 6: one span, one hinge)" +
                    ("" if cur.is_file() else " · never rendered before"), f"Leaf{v}", lk, tex, SL,
                    [cur] if cur.is_file() else [])
            job(3, 6, k, f"{src}_rd1a", "leaf", (256, 1024),
                f"Repaint image 1 (a grey geometry guide) as {w}, for a RimWorld drawbridge, tall narrow image. The leaf "
                f"occupies EXACTLY the grey shape: same length from the hinge at the bottom to the tip at the top, same "
                f"width, same hinge position - every view of this leaf shares that span. Material: {lmat[lk]}. Painting "
                f"style of image 2. {READ} {ALPHA}", [GUIDES / g, done_png("RM_DrawbridgeLeafUp_Timber_Face")],
                None, tex, gen=(512, 2048))

    # ---- rank 7: futuristic decks and jetties --------------------------------------------------------- wave 4
    fd = {"Heavy": "broad matte off-white floor plates inside a HEAVY dark-grey frame band, dark recessed seams, a single "
                   "thin recessed teal strip - a matte walkable floor, never illuminated panels or a display",
          "Steel": "pale-grey metal floor plates with fewer, larger divisions inside a SLIM frame band, no light grid"}
    for tr, w in fd.items():
        k = row(f"RD_Deck{tr}_Futuristic", f"{tr.lower()} deck — Futuristic (rank 7: matte floor, sparse light)",
                f"Deck{tr}", "Futuristic", f"{SB}/Futuristic/RM_SuspensionDeck", S1)
        job(4, 7, k, f"RM_SuspensionDeck_{tr}_Futuristic_rd1a", "tile", (256, 256),
            tile_prompt(f"{TIER[tr]}: {w}. {LOOK['Futuristic']}."), [TEX / f"{SB}/Futuristic/RM_SuspensionDeck.png"],
            f"RM_SuspensionDeck_{tr}_Futuristic", f"{SB}/Futuristic/RM_SuspensionDeck_{tr}")
    jet = {"Heavy": "a substantial thick perimeter frame with chunky corner blocks",
           "Steel": "a SLIM perimeter frame with small corner fittings - visibly lighter than the heavy jetty"}

    def jetty(wave, rank, lk, tr, extra=""):
        k = row(f"RD_Jetty{tr}_{lk}", f"jetty {tr.lower()} — {lk} (rank {rank})", f"Jetty{tr}", lk,
                f"{SB}/{lk}/RM_SuspensionJetty", S1, [TEX / f"{SB}/{lk}/RM_SuspensionJetty_south.png"])
        job(wave, rank, k, f"RM_SuspensionJetty_{tr}_{lk}_rd1a", "fit", (256, 256),
            f"Redraw the suspension-bridge JETTY (the landing platform at the bridge end) for RimWorld, 1x1 cell, seen "
            f"from the south, square image: a flat clear walkable platform surface with {jet[tr]}. {TIER[tr]}. {extra} "
            f"Position and size of image 1; construction of image 2. {LOOK[lk]}. {CAM} {READ} {ALPHA}",
            [TEX / f"{SB}/{lk}/RM_SuspensionJetty_south.png", TEX / f"{BASE}/RM_SuspensionJetty_{tr}_south.png"],
            f"RM_SuspensionJetty_{tr}_{lk}", f"{SB}/{lk}/RM_SuspensionJetty_{tr}", facing="south")

    jetty(4, 7, "Futuristic", "Heavy", "Matte walking panels; at most a thin recessed seam light, no cross, no glazed lid.")
    jetty(4, 7, "Futuristic", "Steel", "Matte walking panels, simple markings.")

    # ---- rank 8: plank-lattice pit cover --------------------------------------------------------------- wave 4
    k = row("RD_PitCover_PlankLattice", "pit cover, plank lattice (rank 8: squared load-bearing lattice)", "PitCover", "Base",
            "Things/Building/FlowWorks/Canals/RM_PitCover_PlankLattice", S1,
            [TEX / "Things/Building/FlowWorks/Canals/RM_PitCover_PlankLattice.png"])
    job(4, 8, k, "RM_PitCover_PlankLattice_rd1a", "fit", (256, 256),
        f"Redraw image 1 as a deliberate PIT COVER for RimWorld, 1x1 cell, square image. {TOP} A square timber frame flush "
        f"with the cell edges, and inside it a load-bearing lattice of WIDE weathered planks laid in two crossing layers, "
        f"evenly spaced, nailed at every crossing with dark iron nails, small dark gaps between them - it reads as safe "
        f"footing, never a debris pile. Warm brown weathered timber like image 1. {READ} {ALPHA} Fills about 95% of the "
        f"square.", [TEX / "Things/Building/FlowWorks/Canals/RM_PitCover_PlankLattice.png"],
        "RM_PitCover_PlankLattice", "Things/Building/FlowWorks/Canals/RM_PitCover_PlankLattice")

    # ---- rank 9: timber winch, square-on, no house roof ------------------------------------------------- wave 4
    for lk in ["Timber", *LOOKS]:
        src = "RM_DrawbridgeWinch_Timber" if lk == "Timber" else f"RM_DrawbridgeWinch_Timber_{lk}"
        cur = done_png(f"{src}_south")
        tex = f"{DBT}/{src}"
        k = row(f"RD_WinchTimber_{lk}", f"winch, timber tier — {lk} (rank 9: exposed spool, no shed roof)" +
                ("" if cur.is_file() else " · never rendered before"), "WinchTimber", lk, tex, S15,
                [cur] if cur.is_file() else [])
        mat = LOOK["Timber"] if lk == "Timber" else f"{LOOK[lk]}, but the uprights and sill are clearly TIMBER"
        job(4, 9, k, f"{src}_rd1a", "fit", (384, 384),
            f"Paint a hand-cranked drawbridge WINCH for RimWorld, 1.5 cells, seen from the south, square image: two THICK "
            f"timber uprights standing on a broad timber sill, a LARGE exposed rope drum on an iron axle between them with "
            f"iron collars, a big crank handle on one side, a thick rope wound on the drum; at most a small flat plank cap "
            f"over the top, never a house roof or shed. {mat}. {CAM} {READ} {ALPHA} Fills about 80% of the image.",
            [done_png("RM_DrawbridgeGate_Timber_Closed_south")] if lk == "Timber" else [done_png("RM_DrawbridgeGate_Closed_Scrapper_south")],
            "RM_DrawbridgeWinch_Timber", tex, facing="south")

    # ---- rank 10: scrapper decks; rank 7 (industrial list): industrial decks + heavy jetty --------------- wave 5
    sd = {"Heavy": "broad salvaged planks in the middle with two or three LARGE flush repair plates, heavy scrap-beam side bands",
          "Steel": "broad flush scrap-STEEL sheets in the middle with a few welded seams and exposed steel edges - it reads "
                   "as metal, not wood; slim angle-iron side bands"}
    for tr, w in sd.items():
        k = row(f"RD_Deck{tr}_Scrapper", f"{tr.lower()} deck — Scrapper (rank 10: simplify, steel reads metal)",
                f"Deck{tr}", "Scrapper", f"{SB}/Scrapper/RM_SuspensionDeck", S1)
        job(5, 10, k, f"RM_SuspensionDeck_{tr}_Scrapper_rd1a", "tile", (256, 256),
            tile_prompt(f"{TIER[tr]}: {w}. {LOOK['Scrapper']}."), [TEX / f"{SB}/Scrapper/RM_SuspensionDeck.png"],
            f"RM_SuspensionDeck_{tr}_Scrapper", f"{SB}/Scrapper/RM_SuspensionDeck_{tr}")
    idk = {"Heavy": "a few LARGE dark steel plates with sparse tread marks inside a heavy frame band",
           "Steel": "broad steel sheets with clear seams and sparse tread marks inside a slim frame band"}
    for tr, w in idk.items():
        k = row(f"RD_Deck{tr}_Industrial", f"{tr.lower()} deck — Industrial (rank 7 of the suspension list: less tread sparkle)",
                f"Deck{tr}", "Industrial", f"{SB}/Industrial/RM_SuspensionDeck", S1)
        job(5, 7, k, f"RM_SuspensionDeck_{tr}_Industrial_rd1a", "tile", (256, 256),
            tile_prompt(f"{TIER[tr]}: {w}. {LOOK['Industrial']}."), [TEX / f"{SB}/Industrial/RM_SuspensionDeck.png"],
            f"RM_SuspensionDeck_{tr}_Industrial", f"{SB}/Industrial/RM_SuspensionDeck_{tr}")
    jetty(5, 7, "Industrial", "Heavy", "Large plates with sparse tread, the substantial edge kept.")

    # ---- rank 11: grated decks, base + four looks ------------------------------------------------------- wave 5
    gr = {"Heavy": "an open steel GRATING: a few THICK bearing bars running top to bottom with wide open gaps between them "
                   "(the gaps are fully transparent), a few bold crossbars, a HEAVY perimeter band down each side",
          "Steel": "an open steel GRATING: substantial bearing bars alternating with thinner crossbars, open transparent gaps, "
                   "a SLIM angle-iron perimeter band down each side"}
    for lk in ["Base", *LOOKS]:
        for tr, w in gr.items():
            if lk == "Base":
                res, cur = f"{BASE}/RM_SuspensionDeck_{tr}Grated", TEX / f"{BASE}/RM_SuspensionDeck_{tr}Grated.png"
                tdef, tex = f"RM_SuspensionDeck_{tr}Grated", f"{BASE}/RM_SuspensionDeck_{tr}Grated"
            else:
                res, cur = f"{SB}/{lk}/RM_SuspensionDeckGrated", TEX / f"{SB}/{lk}/RM_SuspensionDeckGrated.png"
                tdef, tex = f"RM_SuspensionDeck_{tr}Grated_{lk}", f"{SB}/{lk}/RM_SuspensionDeckGrated_{tr}"
            k = row(f"RD_Grated{tr}_{lk}", f"{tr.lower()} grated deck — {lk} (rank 11: readable bearing bars)",
                    f"Grated{tr}", lk, res, S1)
            job(5, 11, k, f"{tdef}_rd1a", "tile_alpha", (256, 256),
                tile_prompt(f"{TIER[tr]}: {w}. {LOOK[lk]}.") + " " + ALPHA.replace("Fully transparent background",
                                                                                  "The gaps between the bars are fully transparent"),
                [cur], tdef, tex)

    # ---- rank 12: steel/heavy girth, railings, modern wreck, gates, mesh/chain detail -------------------- wave 6
    for lk in ["Scrapper", "Industrial", "Modern"]:
        jetty(6, 12, lk, "Steel", "Visibly slimmer edges than the heavy jetty.")
    k = row("RD_DeckSteel_Modern", "steel deck — Modern (rank 12: thinner channels)", "DeckSteel", "Modern",
            f"{SB}/Modern/RM_SuspensionDeck", S1)
    job(6, 12, k, "RM_SuspensionDeck_Steel_Modern_rd1a", "tile", (256, 256),
        tile_prompt(f"{TIER['Steel']}: smaller clean light-grey steel panels in the middle, THIN red edge channels down "
                    f"each side. {LOOK['Modern']}."), [TEX / f"{SB}/Modern/RM_SuspensionDeck.png"],
        "RM_SuspensionDeck_Steel_Modern", f"{SB}/Modern/RM_SuspensionDeck_Steel")
    for lk in ["Base", *LOOKS]:
        res = f"{BASE}/RM_SuspensionRailing_Edge" if lk == "Base" else f"{SB}/{lk}/RM_SuspensionRailing_Edge"
        cur = TEX / f"{res}.png"
        k = row(f"RD_Railing_{lk}", f"railing — {lk} (rank 12: thick posts, one bold rail)", "Railing", lk, res, S1, [cur])
        job(6, 12, k, f"RM_SuspensionRailing_{lk}_rd1a", "rail", (256, 256),
            f"Paint a bridge RAILING section for RimWorld as a long horizontal strip, wide image: five THICK upright posts "
            f"with distinct caps and a short visible front face, joined by ONE bold handrail along their tops and one "
            f"lower rail; seen from the south at the RimWorld building camera (about 35 degrees above horizontal). "
            f"{LOOK[lk]}. {READ} {ALPHA} The strip spans the full width of the image.", [cur],
            "RM_SuspensionRailing" + ("" if lk == "Base" else f"_{lk}"), res, gen=(1536, 512))
    k = row("RD_Wreck_Modern", "wreck — Modern (rank 12: painted panels, not timber)", "Wreck", "Modern",
            f"{SB}/Modern/RM_SuspensionWreck", S1, [TEX / f"{SB}/Modern/RM_SuspensionWreck.png"])
    job(6, 12, k, "RM_SuspensionWreck_Modern_rd1a", "fit", (256, 256),
        f"Redraw image 1 as the WRECK of a Modern suspension-bridge section for RimWorld, 1x1 cell, square image: the same "
        f"layout of fallen pieces, but they are folded grey steel panel backs and broken glossy RED edge channels with "
        f"torn ends and a snapped cable - no timber planks. {CAM} {READ} {ALPHA}",
        [TEX / f"{SB}/Modern/RM_SuspensionWreck.png"], "RM_SuspensionWreck_Modern", f"{SB}/Modern/RM_SuspensionWreck")
    gref = done_png("RM_DrawbridgeGate_Timber_Closed_south")
    gmat = {"Timber": LOOK["Timber"], "Steel": "plain mid-grey steel plate posts and a steel-plate leaf, dark iron fittings",
            **{lk: LOOK[lk] for lk in LOOKS}}
    for lk in ["Timber", "Steel", *LOOKS]:
        for st in ("Closed", "Open"):
            if (lk, st) in (("Timber", "Closed"), ("Scrapper", "Closed")):
                continue                                            # GPT: ok
            src = f"RM_DrawbridgeGate_{lk}_{st}" if lk in ("Timber", "Steel") else f"RM_DrawbridgeGate_{st}_{lk}"
            cur = done_png(f"{src}_south")
            k = row(f"RD_Gate_{lk}_{st}", f"gate {st.lower()} — {lk} (rank 12: clear operation and passage)" +
                    ("" if cur.is_file() else " · never rendered before"), f"Gate{st}", lk, f"{DBT}/{src}", SG,
                    [cur] if cur.is_file() else [])
            leaf = ("a CLOSED gate leaf fills the passage between the posts, a readable hinge or roller block at the top "
                    "and a threshold sill at the bottom" if st == "Closed" else
                    "the gate leaf is drawn UP into the top beam so the passage between the posts is CLEAR and open, the "
                    "roller block at the top holding it, a threshold sill at the bottom")
            job(6, 12, k, f"{src}_rd1a", "fit", (256, 384),
                f"Paint a drawbridge GATE for RimWorld seen from the south, 1 cell wide and 1.5 cells tall, tall image: two "
                f"slim stout posts and a lintel beam, {leaf}; broad frame depth, panels clearly separated from the posts. "
                f"Same camera, size and post layout as image 1. Material: {gmat[lk]}. {READ} {ALPHA}", [gref],
                "RM_DrawbridgeGate", f"{DBT}/{src}", facing="south", gen=(1024, 1536))
    smat = {"Steel": "regular engineered mid-grey steel framing, restrained, no patchwork",
            "Industrial": LOOK["Industrial"], "Modern": LOOK["Modern"] + ", the red frame is its defining shape",
            "Futuristic": LOOK["Futuristic"]}
    for lk, m in smat.items():
        src = "RM_DrawbridgeWinch_Steel" if lk == "Steel" else f"RM_DrawbridgeWinch_Steel_{lk}"
        cur = done_png(f"{src}_south")
        k = row(f"RD_WinchSteel_{lk}", f"winch, steel tier — {lk} (rank 12: top surfaces, big drum, fewer bits)" +
                ("" if cur.is_file() else " · never rendered before"), "WinchSteel", lk, f"{DBT}/{src}", S15,
                [cur] if cur.is_file() else [])
        job(6, 12, k, f"{src}_rd1a", "fit", (384, 384),
            f"Paint a powered drawbridge WINCH for RimWorld, 1.5 cells, seen from the south, square image: a steel frame on "
            f"a broad ground base, one LARGE drum with clear rims and a dark wound-chain mass on it, a compact motor "
            f"housing whose TOP surfaces are visible; few, large parts. Same camera as image 1. {m}. {CAM} {READ} {ALPHA} "
            f"Fills about 80% of the image.", [done_png("RM_DrawbridgeWinch_Steel_Scrapper_south")],
            "RM_DrawbridgeWinch_Steel", f"{DBT}/{src}", facing="south")
    for ic, w in (("Lower", "the drawbridge leaf swinging DOWN to lie flat, with a curved arrow pointing down"),
                  ("HoldRaised", "the drawbridge leaf held UP with a bold iron pin or lock symbol at its hinge")):
        k = row(f"RD_Icon_{ic}", f"gizmo icon — {ic} · never rendered before", "Icon", "Base",
                f"UI/Commands/FlowWorks/RM_Drawbridge{ic}", S1, [done_png("RM_DrawbridgeRaise_Icon")])
        job(6, 12, k, f"RM_Drawbridge{ic}_Icon_rd1a", "fit", (256, 256),
            f"Paint a RimWorld command gizmo ICON in exactly the style, palette and framing of image 1 (the RAISE icon of "
            f"the same set): {w}. {ALPHA}", [done_png("RM_DrawbridgeRaise_Icon")], None,
            f"UI/Commands/FlowWorks/RM_Drawbridge{ic}")


build()


# ------------------------------------------------------------------------------------------------------------ guides
def guides():
    GUIDES.mkdir(parents=True, exist_ok=True)
    W, H = 512, 2048
    grey, dark = (150, 150, 150, 255), (90, 90, 90, 255)
    face = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(face)
    d.rectangle((48, 24, W - 48, H - 72), fill=grey)                 # leaf body: tip at the top, hinge at the bottom
    d.rectangle((32, H - 120, W - 32, H - 24), fill=dark)            # hinge barrel
    face.save(GUIDES / "guide_leaf_face.png")
    edge = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(edge)
    d.rectangle((W // 2 - 40, 24, W // 2 + 40, H - 72), fill=grey)    # thickness strip, same span
    d.rectangle((W // 2 - 72, H - 120, W // 2 + 72, H - 24), fill=dark)
    edge.save(GUIDES / "guide_leaf_edge.png")
    print("guides ->", rel(GUIDES))


# --------------------------------------------------------------------------------------------------------------- gen
def gen(wave, only, workers, timeout, budget=120):
    """Run every pending job of the wave on a pool of worker homes (one job per home at a time). A job not STARTED within
    `budget` seconds is deferred, so one call ends inside the 600 s silence limit; run again to continue."""
    import queue
    RAW.mkdir(parents=True, exist_ok=True)
    js = [j for j in JOBS if (wave is None or j["wave"] == wave) and (not only or j["id"] in only)]
    js = [j for j in js if not (RAW / f"{j['id']}.png").is_file()]
    homes = queue.Queue()
    for h in WORKER_HOMES[:workers]:
        homes.put(h)
    t0 = time.time()
    print(f"gen: {len(js)} job(s), {workers} workers, start budget {budget}s", flush=True)

    def one(j):
        h = homes.get()
        try:
            if time.time() - t0 > budget:
                return j["id"], "deferred"
            return _run_slot(j, h, timeout)
        finally:
            homes.put(h)

    left = 0
    with ThreadPoolExecutor(workers) as ex:
        for jid, st in ex.map(one, js):
            left += st == "deferred"
            if st != "deferred":
                print(jid, st, flush=True)
    print(f"gen: {left} deferred — run again" if left else "gen: wave complete", flush=True)


def _run_slot(j, home, timeout):
    out = RAW / f"{j['id']}.png"
    w, h = j["gen"]
    prompt = j["prompt"] + f" Output size {w}x{h} pixels."
    cmd = CI + (["edit"] if j["images"] else ["generate"]) + ["--model", "gpt-6.1-sol", "--timeout", str(timeout),
                                                             "--codex-home", str(HOMES / home), "--out", str(out),
                                                             "--prompt", prompt]
    missing = [i for i in j["images"] if not Path(i).is_file()]
    if missing:
        return j["id"], f"MISSING IMAGE {missing}"
    for i in j["images"]:
        cmd += ["--image", i]
    t1 = time.time()
    try:
        with open(RAW / f"{j['id']}.log", "w") as lf:
            rc = subprocess.run(cmd, stdout=lf, stderr=subprocess.STDOUT, timeout=timeout + 20).returncode
    except subprocess.TimeoutExpired:
        return j["id"], "TIMEOUT"
    ok = out.is_file() and out.stat().st_size > 0
    return j["id"], f"{'OK' if ok else 'FAIL rc=%d' % rc} {time.time() - t1:.0f}s ({home})"


# ---------------------------------------------------------------------------------------------------------- finalize
def premul_resize(im, size):
    a = np.asarray(im.convert("RGBA"), dtype=np.float64) / 255.0
    a[..., :3] *= a[..., 3:4]
    small = np.asarray(Image.fromarray((a * 255).round().astype(np.uint8)).resize(size, Image.BOX), dtype=np.float64)
    al = small[..., 3:4]
    rgb = np.where(al > 0, small[..., :3] * 255.0 / np.maximum(al, 1), 0)
    out = np.concatenate([np.clip(rgb, 0, 255), al], axis=-1)
    out[out[..., 3] < 32] = 0
    return Image.fromarray(out.round().astype(np.uint8), "RGBA")


def _bbox(im):
    a = np.asarray(im.convert("RGBA"))[..., 3]
    ys, xs = np.nonzero(a >= 32)
    return (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1) if len(xs) else None


def _scale_into(src, maxw, maxh):
    w, h = src.size
    s = min(maxw / w, maxh / h)
    return premul_resize(src, (max(1, round(w * s)), max(1, round(h * s))))


def conform(j, raw):
    W, H = j["canvas"]
    k = j["kind"]
    if k in ("tile", "tile_alpha"):
        w, h = raw.size
        e = min(w, h)
        sq = raw.crop(((w - e) // 2, (h - e) // 2, (w - e) // 2 + e, (h - e) // 2 + e))
        out = premul_resize(sq, (W, H))
        if k == "tile":
            a = np.asarray(out).copy()
            a[..., 3] = 255
            out = Image.fromarray(a, "RGBA")
        return out
    bb = _bbox(raw)
    if bb is None:
        raise ValueError("empty alpha")
    sub = raw.crop(bb)
    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if k == "leaf":                                   # one span for every view: the height is fixed, hinge at the bottom
        piece = _scale_into(sub, W - 8, H - 8)
        canvas.alpha_composite(piece, ((W - piece.width) // 2, H - 4 - piece.height))
    elif k == "rail":                                 # a strip along the top edge, like the shipped railing
        piece = _scale_into(sub, W, 48)
        canvas.alpha_composite(piece, ((W - piece.width) // 2, 2))
    else:
        m = round(min(W, H) * 0.05)
        piece = _scale_into(sub, W - 2 * m, H - 2 * m)
        canvas.alpha_composite(piece, ((W - piece.width) // 2, H - m - piece.height if H > W else (H - piece.height) // 2))
    return canvas


def checks(j, raw, im):
    """Reference-independent checks (generating-rimworld-sprites: canvas, real alpha, clean corners, fringe, coverage,
    not identical to the current art). REJECT blocks registration."""
    f = []
    W, H = j["canvas"]
    a = np.asarray(im)[..., 3]
    ra = np.asarray(raw.convert("RGBA"))[..., 3]
    if im.size != (W, H):
        f.append(("REJECT", f"canvas {im.size} != {W}x{H}"))
    if j["kind"] != "tile" and ra.min() == 255:
        f.append(("REJECT", "raw render has no alpha (opaque background)"))
    if j["kind"] not in ("tile", "tile_alpha") and max(a[0, 0], a[0, -1], a[-1, 0], a[-1, -1]) > 0:
        f.append(("REJECT", "corner not clear"))
    fr = float(((a > 0) & (a < 32)).mean())
    if fr > 0:
        f.append(("REJECT", f"faint fringe {fr:.4f}"))
    cov = float((a >= 32).mean())
    lo = 0.02 if j["kind"] == "rail" else (0.30 if j["kind"].startswith("tile") else 0.06)
    if cov < lo:
        f.append(("REJECT", f"coverage {cov:.2f} < {lo}"))
    if j["kind"] == "tile_alpha" and cov > 0.95:
        f.append(("WARN", f"grating coverage {cov:.2f}: gaps not transparent"))
    mid = float(((a >= 32) & (a < 224)).mean() / max(cov, 1e-6))
    if mid > 0.25:
        f.append(("WARN", f"mid-alpha mass {mid:.2f}"))
    return f, round(cov, 3)


def finalize(wave):
    OUT.mkdir(parents=True, exist_ok=True)
    res = json.loads(RESULTS.read_text()) if RESULTS.is_file() else {}
    for j in JOBS:
        if wave is not None and j["wave"] != wave:
            continue
        rp = RAW / f"{j['id']}.png"
        if not rp.is_file():
            continue
        raw = Image.open(rp).convert("RGBA")
        try:
            im = conform(j, raw)
        except ValueError as e:
            res[j["id"]] = {"status": "REJECT", "findings": [["REJECT", str(e)]]}
            print("REJECT", j["id"], e)
            continue
        fs, cov = checks(j, raw, im)
        rej = [x for x in fs if x[0] == "REJECT"]
        op = OUT / f"{j['id']}.png"
        im.save(op)
        res[j["id"]] = {"status": "REJECT" if rej else "PASS", "findings": fs, "coverage": cov, "raw_size": raw.size,
                        "row": j["row"], "out": rel(op)}
        if rej:
            print("REJECT", j["id"], rej)
            continue
        d = ARTSRC / j["id"]
        d.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(op, d / f"{j['id']}.png")
        spec = {"id": j["id"], "facing": j["facing"], "channel": "codex", "created": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "drawsize": ROWS[j["row"]]["size"]["drawSize"][0], "canvas": {"width": j["canvas"][0], "height": j["canvas"][1]},
                "background": "transparent" if j["kind"] != "tile" else "opaque",
                "prompt": j["prompt"], "images": [rel(i) for i in j["images"]], "rimflow_item_id": ITEM,
                "target_def": j["target_def"], "target_texpath": j["target_texpath"], "source_file": rel(op),
                "note": "BENCH bridge redraw candidate (bridge_redraw.py); NOT installed — awaiting his pick"}
        (AP / "done" / f"{j['id']}.json").write_text(json.dumps(spec, indent=2))
        print("PASS", j["id"], cov, [x for x in fs if x[0] == "WARN"])
    RESULTS.write_text(json.dumps(res, indent=1, sort_keys=True))


def manifest():
    res = json.loads(RESULTS.read_text()) if RESULTS.is_file() else {}
    rows = []
    for k, r in ROWS.items():
        jobs = [j for j in r["jobs"] if res.get(j, {}).get("status") == "PASS"]
        if not jobs:
            continue
        fams = sorted({next(x["family"] for x in JOBS if x["id"] == j) for j in jobs})
        # an artpipe column is labelled "render <family>" (art_sheet.name_render_cols) and a family carries no facing,
        # so the row names both the job ids and their families
        rows.append(dict(r, jobs=sorted(set(jobs) | set(fams)), render_match=r"\b(" + "|".join(fams) + r")\b",
                         reference_textures=[rel(p) for p in r["reference_textures"]]))
    m = {"schema": 1, "rows": rows,
         "lead_html": "<p><b>Bridge art — redraw of all 12</b> (owner by card 2026-10-21: <i>Redraw all 12 now</i>). Each row "
                      "is one piece GPT's review asked to redraw, or a drawbridge piece whose render never arrived. The "
                      "reference picture beside a row is today's art; the lettered columns are the new candidates. Pick a "
                      "letter, or note what to change. Nothing is installed until you pick.</p>"}
    p = HERE / "bridge_redraw_manifest.json"
    p.write_text(json.dumps(m, indent=1))
    print(f"manifest: {len(rows)} rows, {sum(len(r['jobs']) for r in rows)} candidates -> {rel(p)}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    a = sp.add_parser("list"); a.add_argument("--wave", type=int)
    sp.add_parser("guides")
    a = sp.add_parser("gen"); a.add_argument("--wave", type=int); a.add_argument("--only", nargs="*", default=[])
    a.add_argument("--workers", type=int, default=9); a.add_argument("--timeout", type=int, default=420)
    a = sp.add_parser("finalize"); a.add_argument("--wave", type=int)
    sp.add_parser("manifest")
    a = ap.parse_args()
    if a.cmd == "list":
        for j in JOBS:
            if a.wave is None or j["wave"] == a.wave:
                st = "raw" if (RAW / f"{j['id']}.png").is_file() else "-"
                print(j["wave"], j["rank"], j["id"], j["kind"], j["canvas"], st)
        print(len([j for j in JOBS if a.wave is None or j["wave"] == a.wave]), "jobs")
    elif a.cmd == "guides":
        guides()
    elif a.cmd == "gen":
        gen(a.wave, set(a.only), a.workers, a.timeout)
    elif a.cmd == "finalize":
        finalize(a.wave)
    else:
        manifest()


if __name__ == "__main__":
    main()
