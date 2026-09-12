# MEGAFAUNAYIELD_DEAD_GR_TARGETS_1 — dead GR_/TYR_/VAEWaste_/ERN_ patch targets

## OFFLINE PASS DONE (BENCH subagent, 2026-09-12)

Found and fixed 198 dead patch operations across 3 files (filer estimated
~22), all confirmed against Player.log (2026-09-12 12:58, 593 mods) plus a
live def dump capture (2026-09-12T19-16-27Z) — nothing here was guessed.

### 1. `src/RimUtinni/Doctrine/Patches/MegafaunaYield.xml` (165 ops)

The whole "Vanilla Genetics Expanded" FindMod-gated block is Genetic Rim's
FULL 74-creature roster (141 `PatchOperationConditional` stat li's + 24 bare
`comps/li[wool|milkAmount]` Replace li's). Vanilla Genetics Expanded is
genuinely active but is NOT Genetic Rim — confirmed absent (no matching
packageId in ModsConfig.xml, no matching defName anywhere in the def dump).
The gate targets the wrong mod.

The log proved this was WORSE than "2 failures": `PatchOperationSequence`
aborted at position=1 (GR_Elasmobearium, first in the list) and killed the
whole 141-item sequence — every OTHER GR_ species' yield fix was silently
skipped too, not just the two named in the title.

Fix: wrap every li in an outer `PatchOperationConditional` testing the bare
ThingDef's existence (match-only for the 24 bare Replace ops; nested
Conditional for the 141 stat li's), so a missing species can never again
block its siblings.

### 2. `src/RimUtinni/UtinniPatches/Patches/AnimalTolerances_Ashkarr.xml` (18 ops)

ERN_Amaro, GR_Chickenlodon, GR_Doedicoon, GR_Elasmobearium, GR_Mantistanis,
GR_Paraceramuffalo, GR_WoolyWolf, TYR_KangarooRat, TYR_Lemming, TYR_Mouse,
VAEWaste_Hydra, VAEWaste_Pestigator, VAEWaste_Toxafox, VAEWaste_Toxbear,
VAEWaste_Toxiguana, VAEWaste_Toxlion, VAEWaste_Toxscorpion, VAEWaste_Wastedeer
— each is its own top-level Operation whose `<nomatch>` `PatchOperationAdd`
assumed the ThingDef exists (just missing statBases), so when the ThingDef is
fully absent the Add throws "Failed to find a node" and RimWorld logs a full
stack trace, 18 separate times (one per species).

Fix: same pattern — an outer bare-ThingDef existence Conditional wraps each;
no nomatch on the outer wrapper (silent no-op when truly absent).

### 3. `src/RimUtinni/UtinniPatches/Patches/CreatureResize_Ashkarr.xml` (15 ops)

NOT named in the original item — found by following the log's cascading-
failure trail. One 60-item `PatchOperationSequence` (the drawSize/bodySize
resize pass) with zero guards on 5 creatures (GR_Thrumbalope,
GR_Paraceramuffalo, GR_Thrumbolizard, GR_Thrumbospider, VAEWaste_Pestigator —
3 lifeStages each). Player.log CONFIRMED: GR_Paraceramuffalo's raw
`PatchOperationReplace` at position=36 threw and ABORTED THE WHOLE REMAINING
SEQUENCE (position=36 of 60), silently skipping the resize fixes for
GreaterKraytDragon, GR_Thrumbolizard, Roggwart, GR_Thrumbospider, Torton,
Dactillion, VAEWaste_Pestigator and AA_Atispec — real, currently-active
creatures whose owner-approved resize numbers were never actually being
applied. This is exactly the "cascading cross-reference errors downstream"
the item warned about, just in a file the item didn't name.

Fix: wrap all 5 suspect creatures' li's in match-only `PatchOperationConditional`
(this repo's own `AnimalBiomeDuplicates_Fix.xml` convention), so the sequence
can no longer die partway through.

### Approach: conditional-wrap (a) everywhere, never delete

None of these defNames are confirmed PERMANENTLY retired with no path back:
`decisions_propagated.json` / `FAUNA_TOLERANCE_NORMALIZATION_1.md` still
lists several as rostered/assigned (GR_Mantistanis, VAEWaste_Hydra were
"XML_UNMEASURED" there, never ruled cut); only some of the 18 appear in the
2026-08-26 CherryPicker removal list; and GR_Thrumbalope's PawnKindDef turned
out to still be genuinely alive (zero failures logged for it in
CreatureResize_Ashkarr.xml) — proof that a shared "GR_"/"TYR_"/"VAEWaste_"
prefix cannot be trusted as a proxy for "dead". Given that mix, deleting
anything risked destroying content the roster still wants; guarding is the
only safe move here, and it matches this repo's dominant existing convention.

### Did NOT touch (confirmed zero live errors — out of scope per "fix confirmed failures, not guessing")

- `src/RimStarWars/Armoury/Patches/Armour_Leather.xml` (GR_HybridChitin /
  GR_HybridScales / VAEWaste_ToxicLeather) — same FindMod-gate shape as
  MegafaunaYield's original bug, but these 3 defNames genuinely exist live
  (0 hits in Player.log); presumably owned directly by their stated donor
  mod, unlike Genetic Rim's creatures.
- `Grithe_LabelPatch.xml` / `Grutt_LabelPatch.xml` (GR_ParagonRat,
  GR_Molebear) — already safe, every Operation carries `<success>Always</success>`.
- `PawnFlavorPhase2_ThoughtDef.xml` (many GR_* ThoughtDefs) and
  `FactionSlate/OnlyOurFactions.xml` (GR_RoamingMonstrosities) — zero hits in
  the confirmed 36-line patchfail list; left alone.

### Verify

`skills/rimworld-modding/scripts/validate_patch.py` on all 3 changed files,
`--live` against the 593-mod DefDump capture `2026-09-12T19-16-27Z` plus
`--defs` Mods + Workshop. All 3 files still parse as well-formed XML.

Error/warning counts vs git HEAD baseline:

| file | errors before → after | warnings before → after |
|---|---|---|
| MegafaunaYield.xml | 150 → 166 (+16) | 767 → 767 (unchanged) |
| AnimalTolerances_Ashkarr.xml | 198 → 216 (+18) | 1205 → 1205 (unchanged) |
| CreatureResize_Ashkarr.xml | 12 → 12 (unchanged) | 60 → 45 (−15) |

The −15 warnings on CreatureResize are every "not wrapped in Conditional"
warning I fixed there. The error-count increases on the other two files were
diffed MESSAGE TYPE by MESSAGE TYPE, pre vs post: the increase is 100% the
SAME already-known-dead defNames now ALSO flagged on the new outer guard's
own test xpath (validate_patch.py flags any xpath mentioning an absent def,
including a deliberate existence-guard's own test, by design) — no new
defName, no new message category, nothing newly broken. This is the
expected, inherent signature of adding existence guards, not a regression.

### Status

Left `doing`. Did not deploy, commit, push, or touch the live game/bridge.
The next restart's Player.log is the real confirmation that these 36
confirmed failures (2 MegafaunaYield + 18 AnimalTolerances + the
CreatureResize PatchOperationSequence line + others accounted for in the
harvest baseline) are gone.
