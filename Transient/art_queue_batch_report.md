# Art queue batch report — 2026-09-29

Items: BLURRG_CANON_REGEN_1, RM_RAWVENOM_ART_1, FORGE_MISSING_ART_1, JOSSUR_FLIGHT_FRAMES_1, FLOATSTONE_WALL_ATLAS_1

Status: DONE

Worktree artpipe directories (`pending/`, `active/`, `done/`, `failed/`) in this
checkout are a STALE SNAPSHOT — several subjects with pending job JSONs here
(`RM_Jossur_*`, `RM_Floatstone*`, `rsw_blurrg_v1_*`) already have finished PNGs
wired on disk in `src/`, meaning the daemon's live tree on `origin`/the main
checkout has already moved/cleaned those jobs while this worktree's copy never
saw the update. Duplicate-id checks were run against this (stale) tree anyway
since that's what `fill_queue.py` can see; the new v2/new-subject ids chosen
don't collide with anything live either way.

## 1. BLURRG_CANON_REGEN_1
QUEUED: `rsw_blurrg_v2_east` (master) + `rsw_blurrg_v2_north`/`_south` (derived).
Root cause of the regen: the wired v1 render (`rsw_blurrg_v1_*`,
`BLURRG_ART_JOB_FIX_1`) omitted the canon two-short-clawed-forelimbs anatomy
entirely and was filed at drawsize 1.0 against the def's real adult drawSize
2.4. v2 prompt states the forelimbs explicitly per
`design/RimStarWars/canon_references/blurrg/description.md`'s Must-show list,
canvas corrected to 512x512 (drawsize 2.4), no `reference=` used (fresh regen,
not a reskin).

## 2. RM_RAWVENOM_ART_1
QUEUED: `RM_RawVenom` (item icon, 256x256). No existing art/queue/decision
found for this subject (checked done/, _artsrc/, registry.jsonl, pending/,
active/, failed/, Transient/*.decisions.json — zero hits before this run).
Palette anchor amber-venom, keyed to `RM_DrippingVenomvine`'s bead-string
description (the plant it's harvested from) and the item's own def text.

## 3. FORGE_MISSING_ART_1
QUEUED: `RUT_TibannaGas` (item icon 256x256, cool vapor-blue counter-note),
`RUT_FoundryTowerEntrance` (building 512x512, drawsize 3.0), `RUT_FoundrySalvageCache`
(building 256x256, drawsize 1.0). All three read from their own def files
(`src/RimUtinni/UtinniPatches/Defs/...`), all three DEPLOY_HOLD'd pending art
per their own headers.
SKIPPED: `RM_CinderCrust` — no def, no reference, no mention anywhere in
`src/` or `design/` under that exact name; identity genuinely unwritten, not
queued as instructed.

## 4. JOSSUR_FLIGHT_FRAMES_1
SKIPPED — not filed. `fill_queue.py`/`common.py`/`artpiped.py` have no concept
of a multi-frame animation sequence: a job is exactly one image per facing (the
only structured multi-part concept is `derive_facings` deriving north/south
from an east master — nothing analogous exists for N sequential animation
frames). Grepped the whole artpipe package for "frame" — the only hit is an
unrelated Python signal-handler parameter. Building flip-book coherence (N
frames × 3 facings, each consistent with its neighbours) through this
single-image-per-job contract would mean hand-authoring ~24 independent
one-off jobs with no daemon-level guarantee they cohere — that's the "hack
around missing support" this task told me not to do. Not filed. This needs
either new pipeline machinery (a frame-sequence job type) or a differently-scoped
approach, which is a design/build decision for BENCH/FOUNDRY, not something to
improvise here. Note: RM_Jossur's grounded master art (`RM_Jossur_{east,north,south}.png`)
already exists on disk in `src/RimMandrake/TheForge/Textures/...`, so a real
master to derive frames from does exist once frame-sequence support is built.

## 5. FLOATSTONE_WALL_ATLAS_1
QUEUED NOTHING — closes the item. `RM_Floatstone`
(`src/RimMandrake/TheForge/Defs/ThingDefs_Items/RM_TheForgeItems.xml`) is
`ParentName="StoneBlocksBase"` with a plain `<stuffProps><color>` block, same
mechanism as vanilla Granite/Sandstone/etc — walls built from it use the
shared vanilla wall atlas tinted by that stuff color, no per-stuff wall
texture exists or is needed anywhere in vanilla RimWorld's own stone walls.
The item's own icon (`RM_Floatstone.png`) already exists on disk. No atlas
job filed.

## Git
Filed 7 job JSONs to `infrastructure/artpipe/pending/` via
`fill_queue.py` (dry-run first, clean). `registry.jsonl` updated by
`fill_queue`'s own `artreg` side-effect. Commit + push follow.
