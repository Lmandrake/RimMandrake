## spec
`ART_REGEN_WAVE4_QUEUE_1` generated 21 jobs (7 creatures x 3 facings) via
`artpiped.py`. `kroffa_v1_north` failed (`worker_status: size_mismatch` — the
image tool returned 1254x1254 against the requested 512x512, one retry
already spent) and was re-filed as `kroffa_v2_north` (same prompt/style_notes,
`facings: [north]` only) via `fill_queue.py`; the daemon (`pgrep -f
artpiped.py`, pid 699477) was already running and picked it up.

This item wires the resulting art into the game, same mechanism as
`ART_REGEN_WAVE1_WIRE_IN_1`/`ART_REGEN_WAVE2_WIRE_IN_1`:

**SW-canon, identity kept** (donor `Mlie.StarWarsAnimalCollection`,
`1.6/Defs/ThingDefs_Races/Races_Animal_SW.xml`, read directly off disk — not
in the offline def dump, same blind spot noted in wave 2):
- `Ronto` — single primary texPath `swanimals/Ronto/Ronto` across both life
  stages, dessicated stays donor art.
- `Dewback` — single primary texPath `swanimals/Dewback/Dewback` across all
  3 life stages; `DewbackW` (alternateGraphics colour recolors) and
  `Dewback_Dessicated` stay donor art.
- `Anooba` — donor splits every life stage by gender:
  `swanimals/Anooba/Anooba_m` / `Anooba_f` (dessicated stays donor). Only one
  generated look exists, so the SAME new art is wired to BOTH `_m` and `_f`
  texPaths rather than leaving females on the old donor look (the Frostmite
  gotcha from wave 2 — an un-covered alternate silently keeps showing old
  art on a random roll).

**Non-SW, reimagined** (owner ruling 2026-09-11, `art: "improve"` semantics —
general kind fixed, name/character free):
- `GR_ParagonRat` → **Grithe** — donor `VanillaExpanded.VGeneticsE`, texPath
  `Things/Pawn/Animal/Paragon/Rat/GR_ParagonRat`.
- `GR_Molebear` → **Grutt** — same donor, texPath
  `Things/Pawn/Animal/Rodent/Molebear/GR_Molebear`.
- `BMT_Maligoat` → **Kroffa** — donor `BiomesTeam.BiomesPollutedLands`,
  gender-split texPath (`.../Maligoat/MaligoatMale` / `MaligoatFemale`) —
  same new art wired to both, same reasoning as Anooba above.
- `BMT_FleeceSpider` → **Puffmite** — donor `BiomesTeam.BiomesCaverns`,
  texPath `BMT_Caverns/Things/Animal/FleeceSpider/FleeceSpider`.

Rename decision (ambiguous in the queue item, defaulting per this item's own
brief): **defNames are NOT renamed.** These are donor-mod defs we do not own;
a real rename would mean absorbing each def into our own mod wholesale
(the pattern used for `VAEWaste_Megatardi` in wave 2), which is out of scope
for an art-wiring pass. Instead each override mod carries art (loose
Textures/, same relative path as the donor) AND a small `Patches/` deploying
`PatchOperationReplace` on the donor def's `<label>`/`<description>` so the
in-game name/flavor text reads as the new invented character while the
defName stays untouched.

## verify
Each of the 7 creatures' new art replaces the donor's at the correct
texPath(s) (both gender variants where the donor splits by gender), the
label/description patches apply cleanly for the 4 reimagined creatures,
`validate_patch.py` stays clean, and each renders live (not magenta, not the
old donor look) confirmed by spawn + screenshot.

## criteria
All 7 creatures render the new art in-game and (for the 4 reimagined ones)
show the new name/label, confirmed by looking, not inferred from a clean
manifest.

## Live verification result (2026-09-11)
Deployed all 7 (`deploy_custom_mods.py --apply`, all VERIFIED in sync), then
a temp-list restart: MINIMAL + `BiomesTeam.BiomesCore`,
`m00nl1ght.GeologicalLandforms`, the 4 donors
(`Mlie.StarWarsAnimalCollection`, `VanillaExpanded.VGeneticsE`,
`BiomesTeam.BiomesPollutedLands`, `BiomesTeam.BiomesCaverns`) and the 7 new
override mods (38 active total). Clean load, no `Config error in` lines, no
log line mentioning any of the 7 defNames/mods at all (silent = correct, per
"a patch that matches nothing logs nothing" — the positive proof is the
screenshot, not the log).

Quicktest map, `jawa/spawn_pawn` (faction `none`) x 7 spread along one row,
`jawa/set_fog --action unfog` over the row (quicktest fog otherwise hid
everything past the starting cluster), then
`rimworld/screenshot_cell_rect` per creature:

- **Ronto**: new wrinkled elephantine-hide art confirmed. CONFIRMED.
- **Anooba**: new tawny hyena-like art confirmed. CONFIRMED.
- **Dewback**: new art confirmed (dim scene, but silhouette matches the
  generated front view, not the donor's old scaley look). CONFIRMED.
- **Grithe** (GR_ParagonRat): new chitin-plated insectoid look confirmed,
  AND `jawa/list_pawns` reports `name: "Grithe (Normal)"` — the label patch
  is live. CONFIRMED.
- **Grutt** (GR_Molebear): new plated-claw art confirmed, `list_pawns` name
  `"Grutt (Normal)"`. CONFIRMED.
- **Kroffa** (BMT_Maligoat): new six-legged horned grazer art confirmed,
  `list_pawns` name `"Kroffa"`. CONFIRMED.
- **Puffmite** (BMT_FleeceSpider): new pale/lilac tufted look confirmed at
  its native tiny drawSize (0.2, faithful to the donor's own scale — hard to
  make out fine detail at any zoom, noted but not a defect), `list_pawns`
  name `"Puffmite"`. CONFIRMED.

Live state made permanent, not just restored: `modlist_swap.py --restore
--apply` put the owner's 583-mod list back, then the 7 new packageIds were
inserted into BOTH the live `ModsConfig.xml` and the stored
`ModsConfig.FULL.LATEST.xml` (kept byte-identical, `modlist_swap.py
--status` reads `live currently matches: FULL`, 583 -> 590 active) right
after their respective donor/cluster, matching wave 1/2's precedent of
shipping the override mods as permanent additions rather than test-only.
Bridge released.

## Art-readability check (owner's task instruction #8)
Glanced at every south-facing PNG before shipping. All 7 read cleanly with
heavy black outlines at a glance; nothing looked like it would blob out at
small size. One non-outline issue found and shipped anyway (flagging per
instructions, not blocking): **`anooba_v1_south` and `anooba_v1_east` are
near-identical side-profile poses** — the "south" facing was generated as a
walking side view rather than a toward-camera front pose (unlike Ronto's and
Dewback's south images, which are correctly front-facing). In-game this
means Anooba will look the same from the south as from the east rather than
facing the viewer when idle-facing south. Not regenerated without further
direction, per the task's own instruction.

## Rename decision recap
Per the task's own default: none of the 4 reimagined creatures' defNames
were renamed (GR_ParagonRat/BMT_Maligoat/GR_Molebear/BMT_FleeceSpider all
stay as-is — donor mod defs, not ours; a real rename means absorbing the def
wholesale, out of scope here). Each got a label+description
`PatchOperationReplace` (with `<success>Always</success>` to avoid a red
error if the donor mod is ever missing) instead, confirmed live above.
