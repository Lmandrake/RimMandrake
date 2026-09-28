# PYRELANDS_BURROWER_GRAZER_1 — dedicated burrower-grazer for the Pyrelands' fire-web

## what

`the_pyrelands.md` §4 rules **three families** into the fire food-web, all owner-ruled
("all ruled"): fire-followers (flame-edge hunters), **burrowers** (grazers that let the
fire pass over and emerge into the fertilized ash), and ash-grazers (herds eating the
regrowth sprint). `rosters/the_pyrelands.json`'s own `new_defs` entry for this row is
explicit:

> *"burrower-grazer (dives under the burn, emerges into ash)"* — `mechanic_load`: **"C#:
> burrow-on-fire behaviour; no clean donor body (Earth-named moles/voles purged)"*

This is `COMMISSION_LEDGER_CLEANUP_1`'s `the_pyrelands:burrower-grazer-dives-under-the-
burn-emerges-into-ash` slug, re-filed as its own build item because it needs new C#
behaviour rather than a def+art commission.

## why re-filed rather than built inline

- **New mechanism, not a reskin.** No existing comp implements "detect an approaching
  fire front, path underground/into a burrow state, then re-emerge once the burn has
  passed" — confirmed by grep: no `burrow`-named JobDriver/comp exists in
  `src/RimMandrake/Pyrelands/` or `src/RimUtinni/PyrelandsMechanics/`.
- **A partial answer already exists and needs a ruling, not a guess.** `Orray` is
  already imported and wired into `RUT_Pyrelands`'s wildAnimals at commonality 0.25
  (`rosters/the_pyrelands.json` §4 register: *"burrowers — register special 'burrows
  underground when hungry' (MEASURED), the one live def with the fire-diving
  mechanic"*) — but the roster's own `new_defs` note says Orray is *"a predator hybrid,
  not a pure grazer"* and explicitly leaves *"this slot OPEN for a third commission if
  the owner wants a dedicated grazer distinct from Orray."* That is an open design
  question (does Orray already satisfy the "burrowers" family, or is a second, herbivore
  -only species still wanted), not something to invent an answer to inline — matches
  CLAUDE.md's "no rules systems" / review-sheet discipline: this is a concrete case for
  the Pyrelands' own sitting, not a blanket call.
- A dead end was already checked and corrected upstream: the roster's own note records
  that `FrogDog` (mlie.starwarsanimalcollection, homeless from `the_contagion.json`) was
  considered as a donor body — its eviction note claimed a "burrows-when-hungry" special,
  but the **live def carries no such comp or field** (it is a docile long-lived pet,
  petness 0.75, wildness 0.10 MEASURED) — that note was already corrected in
  `the_contagion.json`. No verified non-Earth burrower-grazer donor candidate exists in
  this repo's mod set as of this pass.

## work owed

1. Owner ruling (question card): is Orray's existing burrow-on-fire behaviour sufficient
   for the "burrowers" family, or is a dedicated pure-grazer species still wanted
   alongside it?
2. If a dedicated species is wanted: author a new PawnKindDef/ThingDef (herbivore,
   grazer diet, no predator flags) plus a genuinely new C# behaviour — detect an
   approaching fire front (the biome's existing burn-tracking, `PyrelandsFireFront.cs`,
   is the mechanism to hook rather than re-derive) and drive a burrow/submerge state
   until the front passes, then resurface. Reuses `FireEcologyHook.cs`'s existing fire-
   state plumbing where possible rather than a second fire-detection system.
3. Art commission (checked `infrastructure/artpipe/{done,pending}`/`registry.jsonl` for
   "burrower"/"pyrelands grazer" first — clean, nothing pre-existing).

## verify

- Owner ruling recorded (card or note) before any new species is authored.
- If built: the new creature's def loads, is wired into `RUT_Pyrelands`'s (or its
  standalone-mod successor's) wildAnimals, and its burrow-on-fire behaviour is
  confirmed against a live/quicktest fire event, not asserted from code alone.

## caused by

`COMMISSION_LEDGER_CLEANUP_1` — the_pyrelands sheet's one owed slug.
