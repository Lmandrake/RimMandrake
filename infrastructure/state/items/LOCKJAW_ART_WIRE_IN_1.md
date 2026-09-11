## spec
`infrastructure/artpipe/done/lockjaw_improve_a_r7.json` and `_b_r7.json` (plus
`.manifest.json`s) hold validated, generated art for AA_Lockjaw
(`sarg.alphaanimals`, defName `AA_Lockjaw` — both the `ThingDef` race and the
`PawnKindDef`, confirmed from `1.6/Defs/ThingDefs_Races/Races_Lockjaw.xml`),
never wired into any mod's `Textures/` tree. Investigated as the ART_REGEN
WAVE1 pattern (`ART_REGEN_WAVE1_WIRE_IN_1`) applied to a creature that
audit missed.

Owner authorization for touching this creature's art at all:
`design/Jawa/worldbuilding/review/round2/decisions_propagated.json` key
`fauna:the_miasma:AA_Lockjaw`: `"art": "improve"`, note *"Make it like a huge
whale with alligator-like skin sitting and staring... then SNAP."* — matches
`lockjaw_improve_a_r7.json`'s `style_notes` verbatim. This is a real, current
ruling (not the retired `creature_art_register.decisions.json`, which is
context only).

## What "a" and "b" actually are (confirmed from the files, not the
secondhand description)
`AA_Lockjaw`'s `PawnKindDef` has `alternateGraphicChance: 1` with THREE
alternate `texPath`s, each a full south/east/north `Graphic_Multi` set on
disk: `AA_Lockjaw` (bare), `AA_Lockjaw2`, `AA_Lockjaw3` (plus a
`AA_Dessicated_Lockjaw` corpse texture, east-only on the donor too — that one
IS a legitimate single-facing asset, unrelated to this item). Every wild
Lockjaw spawn rolls one of the three equally.

- `lockjaw_improve_a_r7` — `reference`: `.../AA_Lockjaw2_east.png`, prompt
  "muted swamp-grey palette" (matches the donor's variant-2 grey coloring).
- `lockjaw_improve_b_r7` — `reference`: `.../AA_Lockjaw3_east.png`, prompt
  "darker mud-brown variant" (matches the donor's variant-3 brown coloring).

So **"a" and "b" are NOT two rival candidates for one slot** — they target two
*different* existing texPaths (variant 2 and variant 3) and are not mutually
exclusive. But they are also not "two facings of the same design": both are
the SAME facing (east) of two DIFFERENT variant textures.

Both manifests carry `"facing": null, "facings": []` — no north/south job for
either was ever queued. The `failed/` directory shows 6+ prior rounds for
both `a` and `b` (`lockjaw_improve_a`, `_a_r2`, `_a_r6`, plus earlier
`codexcal_lockjaw_a`/`_a_r2`/`_a_r3` under a different channel) — every one of
them east-only. North and south were never attempted, not even as a failure.

## Why this is being blocked, not wired
1. The `PawnKindDef` declares no `visibleFacing` — it is a full three-facing
   `Graphic_Multi` for every one of the three variants. Per
   `generating-rimworld-sprites`: *"A missing direction is not a defect —
   `visibleFacing` lets a def ship three facings deliberately... read the
   def's own declaration before calling a facing broken."* Here the
   declaration says all three facings are real and distinct (confirmed:
   different file sizes for `_north`/`_south`/`_east` per variant) — so
   shipping east-only is not a legitimate partial-facing case, it is
   genuinely incomplete art.
2. The same skill also documents *"Prove one facing before attempting
   four... one facing is enough to learn whether the art direction survives
   downscaling"* as the RECOMMENDED workflow shape — which is exactly what
   `_r7`'s east-only, validator-PASS output looks like: a successful
   direction-proving step, not a finished production set. Nothing in the
   `done/` files marks it as a deliberate final scope.
3. Wiring only `AA_Lockjaw2_east.png` and `AA_Lockjaw3_east.png` while
   leaving `_north`/`_south` on donor art (mechanically safe — RimWorld's
   content-finder resolves the missing facings to whichever mod last
   supplies that exact relative path, so no crash/pink-texture risk) would
   still make each of those two variants visibly INCONSISTENT per rotation
   (new style facing east/west, old donor style facing north/south), and the
   bare `AA_Lockjaw` variant (1/3 of all spawns) would be untouched entirely.
   That reads as broken art in play, not an improvement.
4. No design doc anywhere rules that an east-only ship is the intended final
   state for an "improve" job — "improve" semantics are not defined in
   `infrastructure/artpipe/README.md` (only "redo" is), and this is the only
   "improve" job that has ever reached `done/`, so there is no precedent to
   lean on either way.

Per the owner's own instruction on this task: *"If genuinely unclear, block
the item rather than guessing."* This is that case.

## What would unblock it
Queue `lockjaw_improve_a`/`b` south and north facing jobs (anchored on the
approved east treatment, per the skill's word-anchoring method) so each of
the two touched variants ships a complete three-facing set, OR get an
explicit owner ruling that an east-only "improve" is intentionally
acceptable to ship as-is (and decide then whether the untouched bare
`AA_Lockjaw` variant is left alone or also queued).

## verify
N/A — blocked before any wiring, deploy, or live test was performed.

## criteria
Either: (a) south+north facings exist and validate for both variants and get
wired + verified live per the WAVE1 pattern, or (b) the owner explicitly
rules east-only is acceptable to ship, in which case wire exactly that and
verify live that the untouched facings/variant are not visually jarring
enough to reject.
