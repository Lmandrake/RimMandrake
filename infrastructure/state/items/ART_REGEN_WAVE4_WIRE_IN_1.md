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
