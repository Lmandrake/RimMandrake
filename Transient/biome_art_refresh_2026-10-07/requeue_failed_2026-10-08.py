#!/usr/bin/env python3
"""Requeue tonight's failed artpipe jobs (see failed_jobs.md). Priority -10 sorts ahead of the
520 priority-0 bulk jobs (artpiped sorts by (priority, name), lower first). Run once."""
import json, os, shutil, time
from pathlib import Path
S = Path("/mnt/d/Luke/dev/_artpipe"); F, P, K = S/"failed", S/"pending", S/"_requeued_manifests"
TS = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime()); URGENT = -10
def put(job, dest=P):
    t = dest/(job["id"]+".json.tmp"); t.write_text(json.dumps(job, indent=1)); os.replace(t, dest/(job["id"]+".json"))
def park(jid):
    shutil.move(F/f"{jid}.manifest.json", K/f"{jid}.manifest.{TS}.json"); (F/f"{jid}.json").unlink()

# 1. codex 'final schema before tool use' flake: same job, same id, priority bumped
FLAKES = {  # id: priority (None = keep)
 "miasma_canon_laajuv_v1_east": URGENT, "miasma_canon_laajuv_v2_north": URGENT,
 "miasma_canon_yobshrimpjuv_v1_north": URGENT, "miasma_nemreth_varb_v1": URGENT,
 "0vv_desert_venomvine_v4": URGENT, "0vv_rearing_venomvine_v1": URGENT, "0vv_shedding_venomvine_v2": URGENT,
 "wreck_nightsideexpeditionrig_a": None, "wreck_canyonwreckspeeder_a": None,
 "wreck_falllinewreckcarapace_a": None, "chill_item_hydrocarbonflesh_v1": None}
for jid, pr in FLAKES.items():
    j = json.loads((F/f"{jid}.json").read_text())
    if pr is not None: j["priority"] = pr
    put(j); park(jid); print("flake requeued", jid)

# 2. canon-gate failures on derived facings: v2 job, the failed lines baked into the prompt up front
FIX = {
 "miasma_canon_opeejuv_v1_north": ("miasma_canon_opeejuv_v2_north",
   "(1) The two or three antennae from the crown must be VERY LONG thin whips, each clearly LONGER THAN THE WHOLE BODY, arching up and out past the silhouette, each ending in a dark blue-purple lure bulb. (2) Under the rear body show THREE distinct pairs (six) of thin, jointed, crab-like walking legs, spindly like crab legs, not thick paddles."),
 "miasma_canon_opeejuv_v1_south": ("miasma_canon_opeejuv_v2_south",
   "(1) The antennae from the crown must be VERY LONG thin whips, each clearly LONGER THAN THE WHOLE BODY, arching up and out past the silhouette, each ending in a dark blue-purple lure bulb. (2) The walking legs must be THIN, JOINTED, CRAB-LIKE, three pairs, spindly with visible knee joints - NOT short thick paddle limbs. (3) The pink-mauve tongue must be long, smooth and prehensile, extending out of the mouth, not a short textured nub."),
 "miasma_canon_bogwing_flying_2_v1_north": ("miasma_canon_bogwing_flying_2_v2_north",
   "The spindly hind legs must end in LARGE, clearly SPLAYED three-toed talons, each toe spread wide apart and long, held down and forward, big enough to read at 256 px; not small gathered claws."),
 "miasma_canon_yobshrimpjuv_v1_south": ("miasma_canon_yobshrimpjuv_v2_south",
   "(1) The two arms end in HUGE, LONG, THIN SCISSOR claws: two long narrow straight blades each, like shears, not broad bulky curved jaws or hooks. (2) Two LONG thin whip antennae must trail straight back behind the head, longer than the carapace, not short curls."),
 "twilightsea_mee_canon_redo_v1_north": ("twilightsea_mee_canon_redo_v2_north",
   "The body surface must show a clear HEXAGONAL scale texture: a regular honeycomb net of small hexagon scales across the whole golden-yellow body between the broad dark brown diagonal bars; not mottled or granular."),
 "twilightsea_mee_canon_redo_v1_south": ("twilightsea_mee_canon_redo_v2_south",
   "(1) Exactly ONE very long thin dark needle spine on the centreline of the body, pointing straight away from the viewer along the midline (seen foreshortened, protruding past the tail fork) - never one or two needles sticking out sideways from the flanks. (2) Exactly TWO wispy blue-tipped streamers on the forked tail, no extra blue extensions at the front. (3) Clear hexagonal scale texture on the golden body. (4) Red-ringed yellow eyes."),
}
for old, (new, fix) in FIX.items():
    j = json.loads((F/f"{old}.json").read_text())
    j["id"] = new; j["priority"] = URGENT
    j["prompt"] += (" CANON MUST-PASS FOR THIS FACING (the previous render of this facing failed the daemon's canon check on these exact points; "
                    "get every one right and keep everything else): " + fix)
    put(j); park(old); print("canon v2", new)

# 3. tooke-trap: v3's prompt contradicted itself (fit inside 198x195 AND fill 210x207); the render came back 193x182 at (34,49)
j = json.loads((F/"webwork_tooketrap_redo_v3.json").read_text())
base = j["prompt"].split(" HARD FOOTPRINT LIMIT")[0]
j["id"] = "webwork_tooketrap_redo_v4"; j["priority"] = URGENT
j["prompt"] = base + (" FOOTPRINT (hard requirement, the validator rejects otherwise): the plant's tight bounding box must be EXACTLY 210 px wide by 207 px tall "
    "(+-3 px) with its top-left corner at x=22, y=25 on the 256x256 canvas, i.e. spanning x 22-232 and y 25-232: leaves touch the left and right edges of that box and the tallest stalk touches the top edge. "
    "Draw it, then crop tightly to the plant's alpha bounding box, scale it uniformly to 210x207, and paste it with its top-left at (22,25) on a transparent 256x256 canvas. Do not leave margin inside the box, do not centre it on the canvas.")
put(j); park("webwork_tooketrap_redo_v3"); print("tooke v4")
