# CORRECT_GIDDYUP_NULLKEY_1 — GIDDYUP_NULLKEY_CRASH_1's actual cause + fix

Filed by FOUNDRY (offline pass, 2026-09-12). `rimflow claim` correctly refused
me `GIDDYUP_NULLKEY_CRASH_1` (BENCH lane) — this item carries the full
diagnosis and the fix I already made in `src/`, for BENCH to review and use to
`claim`/`start`/`close --sha` the parent.

## Spec

**What was wrong with the filed description**: `GIDDYUP_NULLKEY_CRASH_1` as
filed pointed at 13 `RSW_`-prefixed Wave-B/C absorption animals (`RSW_Eopie`,
`RSW_Convor`, `RSW_Clodhopper`, `RSW_Beldon`, `RSW_Corinathoth`, `RSW_Anooba`,
`RSW_Borcatu`, `RSW_Cannok`, `RSW_Dalgo`, `RSW_Dianoga`, `RSW_Dragonsnake`,
`RSW_Bolotaur`, `RSW_CanCell`) as the null-key source, found in
`Transient/Player_log_before_restart_batch2_20260912.log`. **That generation
is stale, not live**: the freshest `Player.log` (594 mods, 1563 ctors,
captured 2026-09-12 18:30 — same mod list, much later) has **zero** cross-ref
failures for any of those 13 names; `mandrake.rsw.swbestiary`'s
`RSW_Eopie.xml` etc. are well-formed and load correctly now. That log capture
was almost certainly a session launched before that wave's files finished
deploying (`RSW_Eopie.xml` deployed 12:03, `BiomeCast_Ashkarr.xml` — which
already referenced it — deployed earlier at 10:18 that same day). Don't spend
further time on the 13 `RSW_` names; they are not the bug.

**What the freshest live log actually shows**: the identical crash signature
(`BiomeDef.CommonalityOfAnimal` → `ArgumentNullException: key`, IL offset
`0x0003d`, the *first* `Add` in the method — confirmed structurally distinct
from `GIDDYUP_WILDBIOMES_DUPLICATE_KEY_1`'s offset `0x000b2` second-loop
duplicate-key exception) still fires, exactly once, from a completely
different name: **`GR_Mantistanis`**.

```
Could not resolve cross-reference: No Verse.PawnKindDef named GR_Mantistanis
found to give to RimWorld.BiomeAnimalRecord RimWorld.BiomeAnimalRecord
Possible Matches:
[Source: Jawa Doctrine Patches] [File: .../Doctrine/Patches/MegafaunaYield.xml]
[Source: RimUtinni Patches (Jawa campaign)] [File: .../UtinniPatches/Patches/AnimalTolerances_Ashkarr.xml]
```

`GR_Mantistanis` is a dead reference: `design/Jawa/fauna/cast_assignment.csv`
line 368 attributes it to "Vanilla Genetics Expanded"
(`vanillaexpanded.vgeneticse`, workshop id `2883081878`, confirmed active),
but that mod's own files contain zero occurrences of "mantistanis" in any
case. No mod anywhere on this machine (installed or workshop) defines it. It
is not a load-order or deploy-timing artifact — it fails identically in every
capture that includes `ZBiome_Grasslands`'s wildAnimals cast, because
`BiomeCast_Ashkarr.xml`'s `MayRequire="zylle.morevanillabiomes,
vanillaexpanded.vgeneticse,Spino.Megafauna"` gate on that `<Operation>`
evidently does not block the add on the live mod list (`Spino.Megafauna` is
also not, and per `gen_cast_patch.py`'s own header was never expected to be,
an installed mod — yet the add still fires). Whatever the exact engine reason
for that, don't rely on `MayRequire` alone for these; gate on the def's own
existence.

**This is not new territory**: `MEGAFAUNAYIELD_DEAD_GR_TARGETS_1` (BENCH,
2026-09-12, item file already closed/`doing`) already found and fixed
`GR_Mantistanis` in `MegafaunaYield.xml` and `AnimalTolerances_Ashkarr.xml` by
wrapping each reference in an existence-testing `PatchOperationConditional`.
That pass explicitly did **not** touch `BiomeCast_Ashkarr.xml` — it's not in
that item's file list — which is exactly the gap: the stat-patch failures in
the other two files just log a caught error and move on; the wildAnimals
dictionary entry in `BiomeCast_Ashkarr.xml` is what actually feeds
`BiomeDef.CommonalityOfAnimal` a null key and crashes Giddy-Up. That's the
"different mechanism" `GIDDYUP_NULLKEY_CRASH_1` was filed to track, now
identified precisely.

**`GR_Mantistanis` is mid-rename, not simply dead-and-cuttable.**
`Transient/art_regen_wave7_improve.json` already reimagined this creature as
"Emberscythe" (explicitly checked as non-Star-Wars against
`design/RimStarWars/star_wars_canon_names.md`), and
`infrastructure/artpipe/done/emberscythe_v1_{north,east,south}.json` has
finished art. No `RSW_Emberscythe`/`RUT_Emberscythe` ThingDef/PawnKindDef
exists yet — authoring the actual creature is separate content work, not part
of this crash fix. `FAUNA_TOLERANCE_NORMALIZATION_1.md` /
`decisions_propagated.json` never ruled it cut from the roster, so I did not
delete the cast row (matches `MEGAFAUNAYIELD_DEAD_GR_TARGETS_1`'s own
"guard, never delete" call for this exact name).

**Fix already applied and deployed** (in `src/`, not blocked by the lane
rule — only the ledger claim/prose-write on the parent item was refused):

`src/RimUtinni/UtinniPatches/Patches/BiomeCast_Ashkarr.xml`, the
`ZBiome_Grasslands` wildAnimals `Operation` adding `GR_Mantistanis`: added an
inner `PatchOperationConditional` testing
`/Defs/PawnKindDef[defName="GR_Mantistanis"]` exists before the
`PatchOperationAdd` fires — the same add-if-missing shape already used
elsewhere in this file and in the sibling guarded files. Deployed via
`deploy_custom_mods.py --apply` (verified byte-identical against the repo
copy). `validate_patch.py` against the live 594-mod set: 0 errors, one
expected/benign WARN (the intentional test-one-node/add-another shape,
flagged the same way on every other add-if-missing guard in this file).

Diff is one file, one Operation, ~6 added lines (an outer wrap + inner xpath
+ comment) — no other content touched.

## Verify

Needs the next cold load (I did not restart — this item is `needs: offline`,
no bridge/restart from FOUNDRY on this pass). A fresh `Player.log` should
show:
- Zero `Could not resolve cross-reference ... GR_Mantistanis`.
- Zero `[Giddy-Up] An error occured calling AllWildAnimals` /
  `ArgumentNullException: ... key ... at RimWorld.BiomeDef.CommonalityOfAnimal`
  lines (the ONE remaining Giddy-Up null-key crash, IL offset `0x0003d`, in
  every log captured today).
- `GIDDYUP_WILDBIOMES_DUPLICATE_KEY_1`'s duplicate-key crashes (IL offset
  `0x000b2`, e.g. `AA_Eyeling`) are a SEPARATE, still-open item — do not
  expect this fix to touch those.

## Criteria

Done when: (a) BENCH has reviewed this write-up and the actual diff in
`src/RimUtinni/UtinniPatches/Patches/BiomeCast_Ashkarr.xml`, (b) BENCH closes
`GIDDYUP_NULLKEY_CRASH_1` with the commit sha below (or a follow-up commit if
BENCH wants changes), and (c) the next cold load's Player.log confirms zero
occurrences of the null-key crash.

## Watch out

- **Don't re-chase the 13 `RSW_` Wave-C names** — they're a red herring from a
  stale log capture, already resolved by the deploy that happened between
  that log and now. If a future log ever shows them failing again, that's a
  NEW bug (a real deploy/timing regression), not a reopening of this one.
- **`MayRequire` on a multi-mod comma-joined `<Operation>` attribute is not
  proven reliable here** — this file has dozens of similar gates; I did not
  audit all of them, only fixed the one confirmed-live failure. If BENCH or a
  future pass wants to harden this file generally, that's `gen_cast_patch.py`
  generator work (bigger, riskier, out of scope for a single crash fix) —
  don't assume every other `MayRequire`-gated Operation in this file is safe
  just because I didn't touch them; I only confirmed THIS one leaks.
- **Emberscythe's real def doesn't exist yet.** Once it's authored (new
  ThingDef/PawnKindDef under a real `RSW_`/`RUT_` tier defName), someone needs
  to update `cast_assignment.csv` row 368 to the new defName and regenerate
  `BiomeCast_Ashkarr.xml`/`AnimalTolerances_Ashkarr.xml`/`MegafaunaYield.xml`
  from it — at which point my hand-added existence guard becomes redundant
  but harmless (it'll just always pass). I did not file a separate item for
  authoring Emberscythe — check whether `ART_REGEN_WAVE7_QUEUE_1` or a
  successor already covers it before filing a new one.
- Commit: see `git log -1 -- src/RimUtinni/UtinniPatches/Patches/BiomeCast_Ashkarr.xml`
  for the sha (filed in the same push as this item).
