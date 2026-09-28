# PYRELANDS_DEDICATED_GRAZER_1 — a dedicated pure-grazer burrower, distinct from Orray

## what
`the_pyrelands.md` §4 rules three families into the fire food-web (owner-ruled, "all
ruled"): fire-followers, **burrowers** (grazers that let the fire pass over and emerge
into the fertilized ash), and ash-grazers. `Orray` already ships as a live burrow-on-fire
creature (`rosters/the_pyrelands.json` §4 register, commonality 0.25 in `RUT_Pyrelands`'s
wildAnimals) but is a **predator hybrid**, not a pure grazer — the roster's own `new_defs`
note left this slot open for "a third commission if the owner wants a dedicated grazer
distinct from Orray."

Superseded item `PYRELANDS_BURROWER_GRAZER_1` was wrongly dropped 2026-09-27 on a
misread of the owner's "Already ruled" reply. Re-asked directly; the real ruling is:
**build the dedicated grazer.** (Owner ruling recorded via question card, 2026-09-28.)

## why re-filed rather than built inline
Same reasoning `PYRELANDS_BURROWER_GRAZER_1` gave, still true: this needs genuinely new
C# behaviour, not a def+art commission — no existing comp implements "detect an
approaching fire front, path underground/into a burrow state, then re-emerge once the
burn has passed." Grep confirmed no `burrow`-named JobDriver/comp exists in
`src/RimMandrake/Pyrelands/` or `src/RimUtinni/PyrelandsMechanics/` as of the original
filing (re-check before building — this repo keeps having already built things,
[[read-the-mechanism-before-filing-the-fix]]).

**Check first whether the shade-follow-family mechanism work landed anything reusable**
(`DESERT_GLITTER_BIRDS_COMMENSALS_1`, a same-session sibling problem — different
behaviour, moving-shadow-follow rather than fire-front-detect-and-burrow, but check its
final shape in case any shared "detect environmental event, drive a state machine"
scaffolding is worth reusing rather than re-deriving).

## work owed
1. Author a new herbivore-only PawnKindDef/ThingDef — grazer diet, no predator flags,
   distinct in body/behaviour from Orray. Check `cast_assignment.csv`/`animal_census.csv`
   for an existing small-grazer candidate before authoring from scratch.
2. New C# burrow-on-fire behaviour: hook the biome's existing burn-tracking
   (`PyrelandsFireFront.cs`) rather than re-deriving fire-front detection; reuse
   `FireEcologyHook.cs`'s existing fire-state plumbing where possible.
3. Wire into `RM_Pyrelands`'s (or its standalone-mod successor's) wildAnimals — check
   which file is currently live/canonical before choosing a target, same discipline as
   the Fever Swarm rename this session ([[decay-sweep-closes-cross-seats]] family: don't
   wire into a frozen twin that isn't the shipping target).
4. Art commission — checked `infrastructure/artpipe/{done,pending}/registry.jsonl` for
   "burrower"/"pyrelands grazer" as of the original item's filing: clean, nothing
   pre-existing. Re-check before queuing (this session found real unused art for a
   different creature under a stale name — always re-check,
   [[loose-png-beats-assetbundle-donor-art]] neighbourhood).

## spec
`design/Jawa/worldbuilding/biomes/the_pyrelands.md` §4 (three-families fire-web ruling);
`rosters/the_pyrelands.json`'s `new_defs` entry for this row.

## verify
- New creature's def loads, is wired into the live Pyrelands wildAnimals list.
- Its burrow-on-fire behaviour is observed live (or at minimum reasoned through against
  the actual fire-front hook code, if a live test isn't practical in one pass) —
  distinct in body/role from Orray, genuinely a pure grazer.

## criteria
A second, herbivore-only burrower-family creature ships, distinct from Orray, with real
burrow-on-fire behaviour, not a reskin of Orray and not a design document entry alone.

## Watch out
- Don't re-litigate whether Orray "counts" — that question is closed, this item's whole
  premise is that it doesn't, on the owner's explicit word.
- If this item's own question-card history ever looks ambiguous again, re-ask in words
  rather than inferring from a short reply — that is exactly the mistake that caused the
  wrongful drop this item corrects.
