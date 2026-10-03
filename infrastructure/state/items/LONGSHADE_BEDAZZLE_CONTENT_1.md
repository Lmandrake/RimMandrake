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
