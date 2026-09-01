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

## 🔴 2026-08-31/09-01, WAVE 1 DONE — and a bigger kotorweapons blocker found
Owner: *"wake agent foundry. Be brave! It's ok to change the mod list even
though there was a scare."* Proceeded per this item's own verify plan §3.

**Done, verified clean:**
- Backed up `ModsConfig.xml` (`ModsConfig.PRESWAP.20260831_202013_pre_4pack_retirement.xml`,
  591 mods — the doc's "593" above was already stale by 2 from unrelated
  concurrent work; not a discrepancy in this pass).
- Retired the 4 confirmed-clean packs: `maincrep.eweb`, `rpgwanderer.opturret`,
  `m3.continued.jangodsoul.starwars.bti`, `sov.sith` (Sov.Sith). 591 -> 587
  active mods, `ModsConfig.FULL.LATEST.xml` synced to match.
- Cold-loaded via Steam (never the bare exe) to confirm. `[JawaBench] context:
  modSet 587/d2806925` on the live bridge; `harvest_log.py` clean except two
  genuinely NEW `[Jawa Patches (local)] PatchOperationConditional ... failed`
  lines (below) — everything else at baseline (25 crossref, 1 Scribe/
  `Corpse_Titan` — pre-existing, confirmed present in `Player-prev.log` too,
  unrelated to this wave; 5 patchfail baseline unchanged).
- **Found and fixed**: `src/SPLIT_Phase3/Jawa_Patches/Patches/WeaponTags_Renormalise.xml`
  (generated, do-not-hand-edit) carried two dead entries whose target
  ThingDef no longer exists at all: `Gun_ArchotechChargeBlasterHeavyTurret`
  (owned by `rpgwanderer.opturret`, just retired — direct fallout of this
  wave) and `RBME_EpsilonAxe` (owned by `tug.Minotaur`, already inactive
  before this wave, unrelated but caught the same way). Hand-removed both
  entries (a real generator regenerate is unsafe right now — the only dump
  available is post-patch, see the file's own 2026-08-21 warning) and noted
  why inline. Deployed (`deploy_custom_mods.py --mod Jawa_Patches --apply`).
  **NOT yet re-verified with a second cold load** — low-risk, single-file,
  named-string change; ride it into whatever load closes this item next.

**🔴 FOLLOW-UP, same sitting — corrected.** The raw `guy762_` mention counts
above (102/288/52 in the three Armoury patch files) were a false alarm: I
counted mentions, not whether they sit inside a guard. Re-checked properly
(walk each file's top-level `PatchOperationFindMod` blocks, confirm every
`guy762_` line falls inside one) — **`Armour_Ratings.xml`, `Armour_Penetration.xml`
and `Armoury_MeleePower.xml` are ALL already correctly grouped** under their
own `<mods><li>Star Wars KotOR Weapons and Armor</li></mods>` /
`Star Wars KotOR Resources and Materials` FindMod blocks, zero orphans in
any of the three. Not a blocker; leave them alone. Filing this correction so
the false claim doesn't survive as the record — see [[dramatic-findings-need-a-second-look]].

**What WAS real, now fixed:** `WeaponTags_Renormalise.xml`'s 63 unguarded
`PatchOperationConditional` blocks for kotorweapons defNames (the same shape
as the opturret bug) — wrapped every one in
`<Operation Class="PatchOperationFindMod"><mods><li>Star Wars KotOR Weapons
and Armor</li></mods><match Class="PatchOperationConditional">…`, mechanically,
verified well-formed and `validate_patch.py --defs`: 0 errors (still
matches correctly with kotorweapons active). Deployed.

**Residual, accepted risk:** 3 `apparelRequired` entries hardcode
kotorweapons defNames directly in two PawnKindDef files with no possible
patch-level guard (Defs load unconditionally) —
`GamorreanPawnKinds.xml` → `guy762_HvyArmor_gamorrean` (1 of that kind's 2
required items; `guy762_Hat_gamorrean`/`guy762_Clothing_gamorrean` are a
*different*, still-active guy762 mod, not kotorweapons) and
`JawaFactionRoster.xml` (generated) → `guy762_MandoArmor_battle`,
`guy762_MandoHelmet_supercom`. Retiring kotorweapons turns these into
`Could not resolve cross-reference` lines (the def loader drops the
unresolvable list entry and keeps going — soft, not the def-discarding
`<li>`-in-a-dictionary-field failure mode) — accepted as a small, known,
non-fatal cost rather than surgery on 2 more files; watch `harvest_log.py`'s
crossref baseline (was 25) for confirmation it rises by exactly 3.

**Verdict, revised: retired `guy762.kotorweapons` this sitting** (586 mods)
after the WeaponTags fix — see cold-load verification below. `kotorcore`
remains blocked on `DROID_DONOR_PATCH_GATE_1`, unchanged.

**Also unblocked and deployed, same sitting**: `DEPLOY_HOLD.txt` was holding
7 `mandrake.rsw.armoury` files (the eweb/opturret absorption — `Absorbed_Eweb*`,
`Absorbed_OPTurret.xml`, `Turrets_DamageDoctrine.xml`, `Turrets_Renames.xml`)
specifically pending "eweb/opturret retirement not done yet" — now done, so
lifted the hold and deployed all 7 together (per the hold's own "lift
together, never separately" note). Deployed mid-relaunch — **confirmed via the live def dump (586 mods,
captured this boot) that the timing race was lost**: `RSW_Turret_AutoChargeBlaster_OP`,
`RSW_RN2SWGun_EWeb_MG`, `RSW_EWebShot` etc. are NOT in this boot's dump. Not
urgent (eweb/opturret are already off regardless, this is purely additive
content); will ride the next restart, whenever that happens.

## 🔴 2026-09-01, consolidated restart — kotorweapons fix verified, one unrelated finding
Bundled per the owner's three-assembly batching waiver (signatures written
to `infrastructure/state/EXPECTED_FAILURES_next_load.md` before launch):
kotorweapons re-verify (config, free) + bridgetools companion redeploy
(adds `jawa/harmony_patches`, unblocks `WILD_ANIMALS_PADDED_LISTS_1`) +
first load-time proof of two already-built assemblies
(`mandrake.rm.graffiti`, `mandrake.rm.ninefold`).

- `[JawaBench] ready: 306 tools, build e91f6b7c5763` — matches HEAD exactly.
- `[JawaBench] context: modSet 586/e1489e27` — confirmed.
- **`WeaponTags_Renormalise.xml` fix CONFIRMED working**: `Jawa_Patches ops`
  check reads **0** (was 4-above-baseline before the fix). The 63-guard fix
  holds.
- No DEAD MOD / TYPE LOAD errors naming Graffiti or Ninefold — clean at
  load time (no live pawn/save exercise this pass, that's still owed).
- `stale saved data (Scribe)`: still just `Corpse_Titan`, pre-existing,
  confirmed present in `Player-prev.log` too — unrelated.
- `cross-reference (def loader)`: still exactly baseline 25, not the +3 I
  expected from the 3 dangling kotorweapons `apparelRequired` refs — those
  apparently resolve lazily at pawn-generation time, not at def-load /
  main-menu time, so a main-menu-only check can't see them. Still an
  accepted, tracked risk, just not one this kind of check will ever catch;
  would need an actual pawn of `Jawa_Gamorrean_Enforcer` or the Mandalorian
  NPC kind generated to prove either way.
- **NEW, unrelated finding, filed separately**: `patch operations failed`
  reads 7 (baseline 5), but the 2 above baseline are `[Jawa Armoury
  Rebalance] PatchOperationFindMod(Star Wars : The Force - Lightsaber)
  failed` in `Armoury_MeleePower.xml` — confirmed present in `Player-prev.log`
  too (pre-existing, not caused by tonight's work, unrelated donor/file).
  Filed as `LIGHTSABER_MELEE_PATCH_FAIL_1`.

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
- [x] Stale-abstract fix rebuilt + redeployed — confirmed 2026-09-01: zero
      `already used in this mod` / `GrenadeBeltBase`/`StealthField_Base`/
      `StealthDeactivate_Base` lines in `Player.log` on tonight's consolidated
      restart (picked up by one of the session's several `deploy_custom_mods.py`
      passes; source and deployed copy both confirmed "in sync" tonight).
- [x] 4 clean packs OFF, full-list cold load clean, as their own verified wave
      (591 -> 587, 2026-08-31/09-01; one fallout bug found in
      `WeaponTags_Renormalise.xml` and fixed, not yet re-verified with a
      second load).
- [x] `guy762.kotorweapons` retirement, separately verified — done: 63
      unguarded `WeaponTags_Renormalise.xml` blocks gated, retired (586
      mods), cold-load confirms the gate fix holds (`Jawa_Patches ops` 0).
      Residual accepted risk: 3 dangling `apparelRequired` refs, un-provable
      from a main-menu-only load (see 2026-09-01 note).
- [ ] `guy762.mm.kotorcore` retirement — blocked on `DROID_DONOR_PATCH_GATE_1`
      (itself entangled with the parked `DROID_SYSTEM_BUILD_1` — not
      something to force through solo while the owner is AFK).
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
