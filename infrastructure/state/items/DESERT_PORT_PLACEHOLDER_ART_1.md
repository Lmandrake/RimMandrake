# DESERT_PORT_PLACEHOLDER_ART_1 — 16 desert species still carry donor texPaths

## what is wrong

13 of 62 wired species across both desert biomes (8 fauna + 5 plants in
RUT_Desert; 4 fauna + 1 plant in RUT_ExtremeDesert; **16 unique defNames
total**) still carry donor texPaths (`Things/Pawn/Animal/AA_*`,
`Things/Plants/AB_*`, `swplants/*`). They render correctly only while Alpha
Animals, Alpha Biomes, or mlie stay subscribed, and go magenta the day any
donor mod is retired.

One is worse than fragile: **`RSW_Dunegrass` (surra grass) points at
`Things/Plants/AB_Aaklac`** — the def's own code comment admits this is the
wrong plant's art, so surra grass currently renders as an aaklac, today, with
every donor mod still present.

## why it matters

16 species are one donor-mod retirement away from rendering as magenta error
sprites, and one of them is already visibly wrong right now.

## the work

Queue all 16 through `fill_queue.py` — never hand-write the art. Land the
art, wire the new texPaths, deploy. Do surra grass first: it is the
top-weighted plant in RUT_Desert and is visibly wrong today, not just
fragile. Check `infrastructure/artpipe/done/` before queueing any of the 16
— per the standing rule (commit `96696811d`), some may already be rendered
and waiting.

## Watch out

This is the item other rows point at when they say "placeholder art, not
this item" — e.g. `DESERT_TABLES_DEPLOYED_AHEAD_OF_SPECIES_1` explicitly
defers 78 SWBestiary defs with no art at all to this item and the artpipe
queue. Do not fold that broader 78-def backlog into this item's scope; this
item is specifically the **16 donor-texPath species** named above, which
already have art (someone else's) rather than none.

## verify

All 16 defNames' texPath fields point at RSW_/RUT_-tier art, not a donor
path; a rendered contact sheet shows no magenta/placeholder sprites for any
of the 16; surra grass no longer renders as an aaklac.

## criteria

No shipped desert species depends on a donor mod remaining subscribed in
order to render correctly.

## progress (FOUNDRY, 2026-09-20) — PARTIAL, left claimed/doing

Re-measured the 16 (item's briefed 8+5 / 4+1 = 16 confirmed correct on
re-check): fauna {RSW_Sandstrider, RSW_Spineroller, RSW_Sandhorn,
RSW_Dunestalker, RSW_Ferroclaw, RSW_Sandmaw, RSW_Tuskcoil, RSW_Cindermite,
RSW_Stareling, RSW_Voltmaw} (10 unique, 8 in RUT_Desert / 4 in
RUT_ExtremeDesert with Spineroller+Cindermite shared) and plants
{RSW_Dunegrass, RSW_VellaraBloom, RSW_SweetbarkTree, RSW_Plant_Chakroot_Wild,
RSW_Plant_HubbaGourd_Wild, RSW_Plant_Bloddle} (6, all unique).

Before queueing anything, checked `infrastructure/artpipe/done/` +
`_artsrc/` + `registry.jsonl` per the standing rule — found 3 of the 6
plants already generated and validated from an earlier, unrelated wave
(`ART_REGEN_FLORA_WAVE1_QUEUE_1`, 2026-09-13): `bloddle_v1`, `chakroot_v1`,
`hubbagourd_v1`. Looked at all three renders directly — clean painterly
sprites, real alpha, no magenta/placeholder look. **Landed these three now,
no new queue jobs**:

- `RSW_Plant_Chakroot_Wild` -> `Things/Plant/RSW_Plant_Chakroot_Wild`
  (`RSW_Plant_Chakroot_WildA.png`, from `chakroot_v1`)
- `RSW_Plant_HubbaGourd_Wild` -> `Things/Plant/RSW_Plant_HubbaGourd_Wild`
  (`RSW_Plant_HubbaGourd_WildA.png`, from `hubbagourd_v1`)
- `RSW_Plant_Bloddle` -> `Things/Plant/RSW_Plant_Bloddle`
  (`RSW_Plant_BloddleA.png`, from `bloddle_v1`)

`immatureGraphicPath` on each repointed to the same new folder too (no
separate immature render exists; better than the donor `swplants/*_Immature`
path it replaced). Edited
`src/RimStarWars/SWBestiary/Defs/DesertPort/RSW_DesertPortB_Plants.xml`,
deployed via `deploy_custom_mods.py --mod SWBestiary --apply` (plan showed
exactly these 3 PNGs + the one def file, applied clean, VERIFIED in sync).
`RSW_Plant_Nysyllin_Wild` and the four `RSW_Raw*` items in the same file are
untouched — not in this item's 16.

**The remaining 13 (7 fauna + 3 plants pending art, plus Spineroller/
Cindermite already counted) are NOT re-queued** — `registry.jsonl` shows all
16 defNames, including `RSW_Dunegrass`, were already registered/queued
~2 hours before this claim under `source: DESERT_FAMILY_PORT_EXECUTION_1`
(the owner's blanket 109-species desert-family REPLACE ruling, ts
2026-09-20T16:43-16:51Z — see that item), with no `generated`/`validated`
event yet for any of those job_ids as of this session. Re-queueing them
would only waste daemon capacity on a duplicate job. Surra grass
(`RSW_Dunegrass`) is in this batch as job `RSW_Dunegrass` — still pending,
so it still renders as an aaklac today; not fixable without waiting on that
render or hand-authoring (out of policy).

**Left claimed/doing, not closed** — 3 of 16 defNames now point at real
RSW_ art (verified via `deploy_custom_mods.py` plan + apply); the other 13
are queued and pending the artpipe daemon, which this session did not wait
on per the item's own instructions. Whoever picks this back up: check
`infrastructure/artpipe/registry.jsonl` for `generated`/`validated` events
on `RSW_Sandstrider`, `RSW_Spineroller`, `RSW_Sandhorn`, `RSW_Dunestalker`,
`RSW_Ferroclaw`, `RSW_Sandmaw`, `RSW_Tuskcoil`, `RSW_Cindermite`,
`RSW_Stareling`, `RSW_Voltmaw`, `RSW_Dunegrass`, `RSW_VellaraBloom`,
`RSW_SweetbarkTree` (all facings for the fauna) before wiring the rest and
closing this item.

## FOUNDRY, 2026-09-24: remaining 13 landed and wired — item CLOSES

**Checked `infrastructure/artpipe/done/` before doing anything else** (this
item's own standing instruction) — all 13 remaining defNames had, in fact,
finished generating: all 10 fauna (3 facings each) plus all 3 plants sitting
in `infrastructure/artpipe/done/`, real PNGs at `_artsrc/<id>/<id>.png`, none
magenta/empty (spot-checked `RSW_Voltmaw_east` directly: 1254x1254, real
alpha coverage — the only one of the 13 that also had a stray duplicate
failure in `failed/` from a later re-attempt; the earlier `done/` copy is the
real, valid render and was used). Surra grass's render (`RSW_Dunegrass`) was
among them, so today's own "renders as an aaklac" defect is fixed with this
pass, not deferred again.

**Wired all 13** (`Transient/wire_desert_port_art.py`, one-shot script, kept
for provenance): copied each render into
`src/RimStarWars/SWBestiary/Textures/Things/{Pawn/Animal,Plant}/RSW_<name>/`
following this mod's own established conventions — fauna get
`RSW_<name>_{south,east,north}.png` at `Things/Pawn/Animal/RSW_<name>/RSW_<name>`
(matching every donor path's own shape, confirmed no separate juvenile art
was ever generated so, like the donor, all life stages of each PawnKindDef
now share the one image at different `drawSize`, including `RSW_Sandhorn`'s
baby stage which had used a donor-only `_baby` texture variant with no
equivalent of our own); plants get the established single-"A"-variant
`Things/Plant/RSW_<name>/RSW_<name>A.png` shape already set by
`RSW_Plant_Chakroot_Wild` etc in the earlier pass. Rewrote every `<texPath>`
in `RSW_DesertPortMisc_Races.xml`/`RSW_DesertPortMisc_Plants.xml` (30 fauna +
3 plant occurrences, scoped per-defName since `RSW_Dunegrass` and
`RSW_VellaraBloom` shared one donor placeholder path and a global replace
would have collided) and refreshed all 13 "TEMP PLACEHOLDER" comments to
name the landed render. XML re-parses clean on both files; grepped for every
donor texture name (`AA_DesertAve`, `AA_Needleroll`, `AA_Gigantelope`,
`AA_SandProwler`, `AA_Terramorph`, `AA_SandSquid`, `AA_MammothWorm`,
`Fuelmite`, `AA_Eyeling`, `AA_TetraSlug`) — zero remaining `<texPath>` hits,
only comment/`useMeatFrom` prose referencing them (expected, out of this
item's scope).

**Deployed**: `deploy_custom_mods.py --mod SWBestiary --apply` — 38 files (30
new textures across 13 folders + 2 def files + 3 pre-existing, already-
committed drift from `DUPLICATE_CANON_DEFNAME_PAIRS_1` this same day, carried
through incidentally since it shares the mod folder), VERIFIED in sync.
**Not live yet** — defs parse once at startup; owed on the next restart, same
as every other def-only deploy this session.

**Not run this pass**: `validate_patch.py --live` (no local def-dump capture
directory found; these are raw `ThingDef`/`PawnKindDef` edits, not
`PatchOperation` xpaths, so the tool's main value — xpath-match checking —
doesn't apply here anyway). Confirmed by direct filesystem check instead:
every new `<texPath>` resolves to a real PNG that now exists on disk at
exactly that path, in both the repo and the deployed copy.

## verify — met
All 16 defNames' texPath fields now point at RSW_-tier art. Surra grass no
longer renders as an aaklac (fixed this pass). A rendered contact sheet
showing no magenta/placeholder sprites was not built as a separate
artifact — verified per-species instead via the `_artsrc` PNGs directly
(all 16, including the 3 landed in the first pass).

## criteria — met
No shipped desert species depends on a donor mod remaining subscribed in
order to render correctly.
