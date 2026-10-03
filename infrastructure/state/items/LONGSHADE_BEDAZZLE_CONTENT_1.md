# LONGSHADE_BEDAZZLE_CONTENT_1 — make the built Long Shade visible

From the Long Shade bedazzle review
(`design/Jawa/worldbuilding/biomes/longshade_bedazzle_review_2026-09-29.md`, "Art status per
cast member" and "Roster gaps"), plus the 2026-09-29 rulings. **Model: sonnet**: this is wiring
and defs whose outcome a screenshot or atlas proves.

## spec

1. **Wire the finished-but-unwired art.** `RM_Ossik`, `RM_Kudda`, `RM_Thurra`, `RM_Vosska`,
   `RM_Khorrak`, `RM_Ommok` and `RM_Ulgga` are magenta today. Their renders are done under the
   old port names (`rsw_sandstrider` / `spineroller` / `sandhorn` / `dunestalker` / `ferroclaw` /
   `sandmaw` / `tuskcoil`). The vorrel family's are done as `rutstaggerseed*`. Reconcile the
   khorrak's two jobs per `DESERT_FAMILY_PORT_EXECUTION_1`.
2. **Five filler defs** already ruled on the 09-27 art sheet: sollak, gennok, tebbra, dakkra
   and pirrik (use the owner-ruled `_b` redo sets where they exist). Dakkra is the free-tier bearer of
   the burst-grab-retreat predator.
3. **Rename the qorrax**: `JOE_Cephalope` → `RM_Qorrax`, with its own art (6 renders, KEEP).
4. **Dedupe the glitter-bird**: `RSW_GlitterBird` and pirrik are one creature, so make it one
   `RM_Pirrik` def carrying the built shadow-follower wiring and the pirrik art.
5. **Gloomcast art of its own**, replacing the copied Horax sprite; the movement-4 commission
   covers it.
6. **Remove the Alpha Animals texture dependencies** on `RM_GreatDevourer`, `RM_Groundrunner` and
   `RM_MatureFleshbeast`. Their art is owed and commissioned.
7. **Mirrak def and art**, paired with its mechanics in `LONGSHADE_BEDAZZLE_MECHANICS_1`.
8. **Maidenbloom** (the owner renamed it from "middenbloom"), plus the proposed fills skarrok,
   vrekka, sippra, tazzok, shadespire and pavecrust. These fills were **never ruled**, so their
   art goes to an owner review sheet first, and defs are built only for what he keeps. That is the 09-27
   filler precedent.

## criteria

- A Long Shade quicktest atlas shows no magenta and no donor texture on any free-tier def.
- There is one glitter-bird def.
- Fill defs exist only for the subjects the owner kept on the review sheet.

## Fills art ruled 2026-10-02 (owner, review sheet `Transient/longshade_fills_art.decisions.json`)

All seven kept: maidenbloom (`_b`), tazzok (`_b`), skarrok (`_b`), pavecrust, vrekka, sippra, and shadespire
pending a redo. Owner notes, typed: shadespire *"Keep the interesting husk-like fruits, but make it dull green
without all that wild color and frills."*; skarrok *"Keep art, redo description based on image."*; vrekka
*"Tint it a bit darker please."* Defs are owed for all seven (spec point 8).
Gloomcast (spec 5): owner, typed: *"accept colossus shade whale"*: wire its own finished 3-facing render in place of the Horax copy.

## Fills built (2026-10-02, spec point 8)

Landed (free Long Shade tier, `src/RimMandrake/LongShade`): animals `RM_Skarrok`, `RM_Vrekka`, `RM_Sippra`, `RM_Tazzok` in `Defs/ThingDefs_Races/RM_LongShade_Fills.xml`; plants `RM_Maidenbloom` (+ harvest `RM_MaidenbloomHeart`, icon cropped from its render), `RM_Pavecrust`, `RM_Shadespire` in `Defs/ThingDefs_Plants/RM_LongShade_FillPlants.xml`; all seven wired into `RM_LongShade` wildAnimals/wildPlants (first-value weights). Art: `_b` sets for tazzok/skarrok/maidenbloom, single sets for vrekka/sippra/pavecrust. Skarrok's description was rewritten from its image (crested, plated raptor-lizard, banded fan-tail, coral-edged wing vanes, hooked talons; the old "falls from the scarp" role is kept in the second sentence). Vrekka is darkened by a def tint (`bodyGraphicData color (185,175,165)`); the texture files are the originals.
Also landed on the owner's "accept colossus shade whale": `RM_Gloomcast` now has its own 3-facing render (downscaled 1024 to 512 at the old texPath) and the ochre body tint is dropped; its `Gloomcast_Dessicated.png` is still the Horax-derived copy.

- **Shadespire art is a PLACEHOLDER.** The def's texPath `Things/Plant/RM_Shadespire` currently holds the `_b` render. Redo queued as artpipe job **`RM_Shadespire_c`** (`Transient/longshade_shadespire_redo_job.json`, dull green, husk-like fruits kept, no reference=). When it finishes, copy `_artsrc/RM_Shadespire_c/RM_Shadespire_c.png` over `Textures/Things/Plant/RM_Shadespire/RM_Shadespire_a.png`.
- **Not built (owed):** mechanics the roles describe (skarrok scarp-drop strike, vrekka corpse-following, sippra shade-line gate, tazzok ash-keyed dormancy, maidenbloom dung-only germination, pavecrust hardpan gate). Stand-in harvests: shadespire yields vanilla `WoodLog` (unique pale wood owed), pavecrust vanilla `Chemfuel` (dye/fuel item owed). Shadespire casts shade already (ShadeGrid treats plants with visualSizeRange max >= 1.5 as casters). No flight animation frames for skarrok (flip-book owed, per the flyer law); no live flight test.
- **Needs deploy and a live look:** `deploy_custom_mods.py --compose biomes` (dry run shows the new files; not applied). Look: atlas of the seven (no magenta), skarrok draw size 0.5/0.85/1.2, vrekka tint, shadespire reading as a shade patch, gloomcast sprite at 6.4/8.8 draw size.
- Validation: `validate_patch.py` on the three new/edited files with `--defs` Core+Mods: 0 errors, 0 warnings; with `--live` the whole mod shows 14 errors, all pre-existing `RM_GreatDevourer` texPaths (spec point 6). Long Shade has no `validation.py`, so point 6 of this task was a no-op.
