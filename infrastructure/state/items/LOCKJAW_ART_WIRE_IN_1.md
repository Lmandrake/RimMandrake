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

## 2026-09-11 update — `AA_Lockjaw3` (brown) DONE and shipped; `AA_Lockjaw2` (grey) still blocked on one facing

Queued the missing south+north facings (`lockjaw_improve_a_r9`..`_r12`,
`lockjaw_improve_b_r9`..`_r10`) via `fill_queue.py`, channel `gemini` matching
`_r7` (not `codex` — `codexcal_lockjaw_a`/`_b` had already failed 6 times on
`codex` with `worker_error, image_present=False`, a reproducible failure for
this asset, not the documented "hangs 1 in 4" transient; `gemini` is what
`_r7` actually used and passed on).

**Root cause of the south/north failures found and fixed**: the r8 batch
(first attempt at the missing facings) copied `_r7`'s prompt text verbatim
except for adding a `facing` field — but `_r7`'s prompt itself says *"side
view facing east"*, and `artpiped.py:build_job_prompt` ALSO appends `Facing:
south.`/`Facing: north.` from the job's `facing` field. That produced a
prompt telling the model two contradictory things at once, and it obeyed the
explicit "side view" text: all 4 r8 jobs failed with the same signature — a
wide, ~1.7-1.9 aspect (broadside) subject against references that are ~0.73-0.74
aspect (narrow, front/back-on). Fix: drop "side view" from the prompt
entirely for south/north jobs and state the front-on/back-on framing
explicitly instead (`r9` on).

**Results after the fix** (retries per facing in parens):
- `AA_Lockjaw2` (grey, "a") north — PASS on `r9` (2nd attempt).
- `AA_Lockjaw3` (brown, "b") south — PASS on `r9` (2nd attempt).
- `AA_Lockjaw3` (brown, "b") north — PASS on `r10` (3rd attempt; r9 missed by
  only 5.9% of canvas on height).
- `AA_Lockjaw2` (grey, "a") south — **FAILED all 5 attempts** (`r8`-`r12`).
  Once the broadside-pose bug was fixed, this facing specifically kept
  overshooting width/height against the reference's narrow aspect (0.739) —
  aspect readings of 0.944, 0.985, 1.244, 0.901 across 4 fixed-prompt retries,
  never converging inside tolerance, while the sibling brown variant's south
  facing (near-identical prompt, different reference image) passed on its
  2nd try. This reads as generation variance on this specific reference
  image, not a reproducible prompt defect — stopped at 5 attempts per the
  "don't loop forever" guidance rather than continuing indefinitely.

**Shipped**: `src/RimStarWars/LockjawArtOverride/` (packageId
`mandrake.rsw.lockjawartoverride`, `loadAfter sarg.alphaanimals`) ships
`AA_Lockjaw3` (brown) COMPLETE — east (from `_r7`, already validated),
south (`_r9`), north (`_r10`), all offline-`PASS`. Deployed
(`deploy_custom_mods.py --apply`), added to the live `ModsConfig.xml` and
`ModsConfig.FULL.LATEST.xml`, and verified live: 6 `AA_Lockjaw` pawns spawned
on a quicktest map, screenshots (`Transient/lockjaw_closeup_*.png`,
`Transient/lockjaw_verify_row1.png`) show the new alligator-plated
whale-beast art rendering correctly on the brown-variant spawns (not a
magenta/missing-texture placeholder, not the donor's smooth pale look).

**Deliberately NOT shipped**: `AA_Lockjaw2` (grey, "a") — its `_east` and
`_north` are validated and sitting in `infrastructure/artpipe/done/`
(`lockjaw_improve_a_r7`, `lockjaw_improve_a_r9_north`) but `_south` is not,
so wiring the other two would reproduce exactly the per-rotation
inconsistency this item was originally blocked over (just for one facing on
one variant instead of two facings on two variants). `AA_Lockjaw2` is left
entirely on donor art — unchanged, still internally consistent — until
`_south` resolves. The bare `AA_Lockjaw` variant remains out of scope, as
before.

## What would unblock it now
Get `AA_Lockjaw2_south` past the validator (a `r13`+ attempt, or a different
approach — e.g. a still-image contact-sheet-style visual QA pass before
resubmitting rather than another blind text-prompt retry) and wire it
alongside the already-validated `_east`/`_north` into `LockjawArtOverride`,
OR get an explicit owner ruling that `AA_Lockjaw2` may ship on donor art
indefinitely while `AA_Lockjaw3` ships improved (an intentional two-tier
outcome, not a defect).

## verify
Live, 2026-09-11: quicktest map, 6x `AA_Lockjaw` spawned (`jawa/list_pawns`
confirmed `AA_Lockjaw40360`..`40365`), `rimworld/screenshot_cell_rect`
close-ups on each — brown-plated new art visible on multiple spawns,
donor pale/smooth look visible on the untouched bare variant, no magenta/
missing-texture. `ModsConfig.xml` round-tripped through a real restart
(rev590→rev591) with `mandrake.rsw.lockjawartoverride` active and no
recovery-reset to 6 mods, i.e. the mod loads cleanly. Full canonical
modlist restored afterward (`modlist_swap.py --restore --apply`,
confirmed `mandrake.rsw.lockjawartoverride` present in the restored live
config).

## criteria
`AA_Lockjaw3` criterion (a) is MET and closed out below. `AA_Lockjaw2`
remains open on the same two options as before: (a) get its `_south` facing
validated and wire the complete set, or (b) an explicit owner ruling that
grey stays on donor art rather than an agent deciding that alone.
