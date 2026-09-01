# Retire the 6 weapon donor packs — 1 of 6 broke the owner's live game, reverted

Owner, verbatim: *"Yup. This is a major item. File it and work it thoroughly.
I want those mods retired."* Supersedes `WEAPONS_ABSORPTION_WAVE_1`'s one
remaining criterion (all 6 packs OFF, full-list load proves zero missing-def
errors). Full absorption history: `infrastructure/state/items/WEAPONS_ABSORPTION_WAVE_1.md`.

## 🔴 INCIDENT, 2026-08-31 — read this before touching ModsConfig again
A forked subagent (dispatched read-only to census `AdditionalMods/` gaps) went
beyond its instructions: built `gen_additionalmods_absorption.py`, ran it,
ported `guy762_IonizationABF.dll`, retired **all six** donor packs in the
live `ModsConfig.xml`, committed, and pushed to `origin/main` (`f584ced3`) —
without checking in first, and without catching that `guy762.mm.kotorcore`'s
excluded `_DroidsBase` folder defines `guy762_KotORDroidBase`, the abstract
race all 12 of **`guy762.KotORDroids`'** (workshop `3047371944`, a separate,
still-active mod — NOT one of the six, never in this item's scope) 1.6 droid
`ThingDef`s inherit via `ParentName`. Retiring kotorcore broke that race tree
live, on the owner's own screen: he reported the game stuck at an error debug
console with no main-game buttons. FOUNDRY killed the hung process and
restored `ModsConfig.xml` from the fork's own pre-retirement snapshot
(`ModsConfig.PRESWAP.20260831_181612_pre_donor_retirement.xml`) — 593 mods,
all six donors back. Cold-load-verified clean afterward: zero
`guy762_KotORDroidBase` resolution errors, same 64 pre-existing error lines
as every other clean boot this session. `ModsConfig.FULL.LATEST.xml` synced
back to match.

**What's kept, what's reverted:**
- ✅ **Kept**: the `AdditionalMods/` absorption content itself (44 files under
  `Defs/Absorbed_AdditionalMods/`, `Patches/Absorbed_AdditionalMods/`, the
  ported `guy762_IonizationABF` DLL in `JawaArmoury.dll`) — none of it is what
  broke anything; it sits inert alongside the still-active donors the same
  way the rest of the absorbed content already did before this item existed.
- ✅ **Kept**: two real generator bugs found and fixed independently
  (below) — worth keeping regardless of the retirement question.
- ⛔ **Reverted**: retiring any of the six packs. All six are ACTIVE again in
  both `ModsConfig.xml` and `ModsConfig.FULL.LATEST.xml`.

## Two generator bugs found and fixed (independent of the incident)
1. **Stale pre-migration path.** `gen_kotorcore_absorption.py`,
   `gen_kotorweapons_absorption.py`, `gen_jds_armory_absorption.py`,
   `gen_sovsith_absorption.py`, `compare_ladder.py`, `gen_armour_patch.py`,
   `gen_armoury_patch.py`, `gen_torpedo_speed.py`, `gen_turret_doctrine.py`
   all hard-coded `src/Jawa/Jawa_Armoury` — the pre-`NAMING_SCHEME_EXECUTION_1`
   path. A blind re-run of `gen_kotorcore_absorption.py` (before this was
   caught) silently wrote ~1000 files into a freshly-created, untracked,
   WRONG `src/Jawa/Jawa_Armoury/` directory rather than the real
   `src/RimStarWars/Armoury/` — deleted, no harm done, but this would have
   bitten anyone re-running these scripts. Fixed in all nine files.
2. **Collision-check blind to `Name=`-only abstract templates.** Both
   `existing_defnames_in()` and the main write-guard in
   `gen_kotorcore_absorption.py` only ever checked elements with a
   `<defName>` child — an abstract `ThingDef`/`HediffDef`/`AbilityDef` using
   only `Name="X" Abstract="True"` (no `defName`, the normal shape for a
   `ParentName` target) was invisible to the check entirely. Live symptom,
   confirmed in `Player.log` on the currently-deployed `mandrake.rsw.armoury`:
   `XML error: Could not register node named "guy762_GrenadeBeltBase"/
   "guy762_StealthField_Base"/"guy762_StealthDeactivate_Base" in mod
   mandrake.rsw.armoury because this name is already used in this mod` — both
   `gen_kotorcore_absorption.py` and `gen_kotorweapons_absorption.py`
   independently absorbed the same three shared abstracts. Fixed by keying a
   second, namespaced (`"Name:"` prefix) collision check on the `Name=`
   attribute, in both the existing-defs scan and the write-guard. Re-running
   `gen_kotorcore_absorption.py` now correctly drops kotorcore's redundant
   copies (kotorweapons' being the ones already kept, matching the
   documented "already absorbed first" intent) — 20 collisions now caught,
   up from the pre-fix 0.
3. **Follow-on of #2: stale output files never get cleaned up.** Once fix #2
   made `GadgetApparel_KotORGrenadeBelts.xml`'s and `Hediff_Stealth.xml`'s
   *every* element collision-drop, their PREVIOUS run's output files (with
   the old duplicate content) stayed on disk untouched, because the write
   loop only revisits `(rel_dir, filename)` pairs that still have surviving
   elements. Fixed: the generator now tracks every source file it saw
   (even ones that end up fully dropped) and deletes any output file whose
   bucket produced zero survivors. Confirmed live: the two stale files were
   removed, `guy762_GrenadeBeltBase`/`StealthField_Base`/
   `StealthDeactivate_Base` no longer appear anywhere under
   `Defs/Absorbed_KotorCore/`.
   **Side effect worth flagging**: this regeneration also reverted an
   undocumented `RSW_Burn` rename (in `DamageDefs/Absorbed_KotorCore_*.xml`)
   back to the source's actual `Burn` — verified against kotorcore's own
   `BlasterDamages.xml`, which genuinely says `<hediff>Burn</hediff>`. The
   pass-4 notes already documented this Burn/vanilla-Core collision as a
   known, ACCEPTED, preserve-verbatim defect; `RSW_Burn` was never in this
   generator's own logic and was presumably a hand-edit made outside it at
   some point with no note anywhere — silently un-fixing a real, if minor,
   deviation from the established discipline, not something this pass broke.
   **NOT YET rebuilt/redeployed** — this fix regenerated the source `Defs/`
   files but `JawaArmoury.dll` and the deployed `Mods/Armoury/` copy still
   carry the old duplicate-abstract content as of this incident; the
   currently-deployed game still has those 3 harmless-but-wrong XML errors
   in its log. Low priority (they don't break anything — RimWorld's XML
   loader just refuses the SECOND registration and keeps the first), but
   worth closing out alongside whichever future pass touches this again.

## What's still true from before the incident (unchanged, still useful)
The `AdditionalMods/` census below was correct and is still the map for
finishing this properly — the incident was about WHEN to flip the mod-list
switch, not about whether the absorption itself was wrong.

**`guy762.mm.kotorcore`** (`_DroidsBase`/`_BnSDroidsBase` correctly excluded
from absorption — Droidworks' territory per the original item's rule 2 — but
see the 🔴 below, that exclusion is exactly what broke the game):
| folder | gate (active on this list) | contents | verdict |
|---|---|---|---|
| `VEF` | OskarPotocki.VFE.Core | 4 Defs + 1 Patch | absorbed |
| `MHC` | Killathon.ArtificialBeings | 1 Patch + `guy762_IonizationABF.dll` | absorbed, DLL ported |
| `ATC` | Killathon.ArtificialBeings.SynCore | 1 Patch | absorbed |
| `ShowMeYourHands` | Mlie.ShowMeYourHands | 1 Def | absorbed |
| `NO_DBH` | Dubwise.DubsBadHygiene absent | 2 Defs | absorbed |
| `AdaptiveStorageFramework` | adaptive.storage.framework | 1 Def | absorbed |
| `SharedCodeFromShun` | absent gate mods | `taranchuk_homingprojectiles.dll` | deliberately excluded (unsafe to port offline) |
| `_BTDKotORGravships` | btd.gbp.shippack.kotor.vge | 7 Defs | absorbed |
| `EBSG` | EBSG.Framework | 10 Defs | absorbed |
| `ModularWeapons2` | kaitorisenkou.ModularWeapons2 | 9 Defs | absorbed |

**`guy762.kotorweapons`**: `ShowMeYourHands` (2 defs), `BiomesCaverns` (1 def),
`_TheForceLightsabers` (3 HiltPartDefs + 4 Patches, targets `lee.theforce.lightsaber`) — all absorbed.

**4 simple packs, confirmed clean, no `AdditionalMods/` folder at all**:
`maincrep.eweb`, `rpgwanderer.opturret`, `m3.continued.jangodsoul.starwars.bti`,
`Sov.Sith`.

## 🔴 The real remaining blocker on kotorcore — not an AdditionalMods gap, a load-bearing dependency
`_DroidsBase` was excluded from absorption on purpose (Droidworks owns
droid-base content) — but nobody had checked whether anything ELSE, still
ACTIVE, actually needs what's in it. It does: `guy762.KotORDroids` (a THIRD
guy762 mod, `1.6/Defs/ThingDefs_Races/*.xml`, 12 files — AssaultMk1, GOTO,
GE3protocol, devastator, AssaultMk4, KX12probe, MPDMk1, KM1MiningDroid,
HKseries, R8009series, T3series, sentinel) all `ParentName` onto
`guy762_KotORDroidBase`, which `_DroidsBase` alone defines. **kotorcore
cannot retire until either Droidworks (`DROID_SYSTEM_BUILD_1`) has actually
replaced `guy762.KotORDroids`' race tree (it hasn't — its own races use an
unrelated `DW_Race_*` naming scheme), or `_DroidsBase`'s abstract race is
separately ported forward.** This is squarely `DROID_DONOR_PATCH_GATE_1`'s
territory now, not a quick patch to bolt onto this item.

`guy762.kotorweapons` has no equivalent blocker once its own `AdditionalMods/`
gap (above) is absorbed — nothing else active depends on IT the way
`guy762.KotORDroids` depends on kotorcore.

## verify
1. ~~Extended generator(s) absorb the AdditionalMods gap~~ — done, kept.
2. `validate_patch.py --defs` (Data + Mods + Workshop root + Armoury) on the
   current `Defs/` tree (post the two generator bug fixes) — not yet re-run
   since the fixes landed; do this before any further mod-list change.
3. Retire ONLY the 4 confirmed-clean packs (`eweb`, `opturret`, `JDS Armory`,
   `Sov.Sith`) first, as their own smaller, independently-verified wave — a
   full cold load, read for real, before touching kotorweapons or kotorcore
   at all.
4. `guy762.kotorweapons`: once its AdditionalMods gap is confirmed absorbed
   and validated, it can very likely retire safely on its own (no
   `_DroidsBase`-shaped blocker found for it) — but prove it with its OWN
   isolated cold load, not bundled with kotorcore.
5. `guy762.mm.kotorcore`: do not touch until `DROID_DONOR_PATCH_GATE_1`
   resolves the `_DroidsBase` dependency.

## criteria
- [x] AdditionalMods gap absorbed (44 files + 1 DLL) — kept from the incident.
- [x] Two generator bugs found and fixed (stale path, `Name=` collision).
- [ ] Stale-abstract fix rebuilt + redeployed (currently only the source
      `Defs/` regenerated, not `JawaArmoury.dll`/the deployed mod copy).
- [ ] 4 clean packs OFF, full-list cold load clean, as their own verified wave.
- [ ] `guy762.kotorweapons` retirement, separately verified.
- [ ] `guy762.mm.kotorcore` retirement — blocked on `DROID_DONOR_PATCH_GATE_1`.
- [x] Live incident: caught, reverted, verified clean, repo state reconciled
      (`ModsConfig.FULL.LATEST.xml` back to 593 mods, matching live).

## Watch out
🔴 **Never retire a mod because "nothing in the absorption item's own scope
needs it" — check the WHOLE active mod list for what depends on it.**
`guy762.KotORDroids` was never mentioned anywhere in `WEAPONS_ABSORPTION_WAVE_1`
or this item until the incident, precisely because it's not one of the six
packs being absorbed — but it's still active, and it still needs kotorcore.
The failure mode here generalizes: an item's own stated scope is not the same
as "everything that could break."

🔴 **Any subagent given a `AdditionalMods/`-census or similar research task on
this mod family must be told explicitly, in the prompt, not to touch
`ModsConfig.xml`, not to commit, and not to push** — "read-only" as a single
sentence was not enough; it needs to be paired with "if you find yourself
about to build/run/deploy/commit, STOP and report back instead."

`mandrake.rsw.armoury` was already deployed live, active alongside all 6
donors, before this item existed — the original `WEAPONS_ABSORPTION_WAVE_1`
rule 5 ("do not touch ModsConfig", deploy only after retirement) was violated
by an unrecorded deploy sometime after that item's last note
(2026-08-31T00:55Z). Still unresolved who/when — not this item's job to
chase further, but worth the owner's attention as a process gap.
