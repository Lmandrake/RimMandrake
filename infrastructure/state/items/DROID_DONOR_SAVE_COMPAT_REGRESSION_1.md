# DROID_DONOR_SAVE_COMPAT_REGRESSION_1

Caused by `DROID_RETIRE_DEPOT_ASIMOV_1` (commit `f6116f97`), discovered live 2026-09-09 ~20:20Z.
Sibling regression to `DOORSEXPANDED_SAVE_COMPAT_REGRESSION_1` — same root cause class,
different donors.

## spec
`DROID_RETIRE_DEPOT_ASIMOV_1` retired `Neronix17.Asimov`, `Neronix17.OuterRim.DroidDepot`,
and our own `mandrake.rsw.msedroidfix` after a correct, thorough whole-active-modlist
dependency check (0 other mods depended on them). `CANONICAL_ASHKARR_2026-09-09.rws` still
holds placed droid Things built from at least one of these donors' ThingDefs — a
Scribe-level (save-content) reference invisible to that check, same failure shape as the
doorsexpanded regression discovered ~10 minutes earlier tonight.

`rimworld/load_game` on the canonical save refused (`missing_mods`, 589→587 active,
all three confirmed genuinely absent from ModsConfig and the whole Workshop/local Mods
tree). The agent that found this correctly declined to force-load past it (unlike the
doorsexpanded case, which did force-load and killed the whole RimWorld process) —
no crash was reproduced for this one.

**Reverted in full** (~20:20-20:25Z): `src/RimStarWars/MSEDroidFix/*`,
`DroidFemaleTexture_Fix.xml`, `NoDroidManufacture.xml`, and the `DroidsAreMachines.xml`
Asimov half restored via git and redeployed; all three packageIds restored to
`ModsConfig.xml`. A real restart (process kill + Steam relaunch) is in progress to pick
up both this fix and the doorsexpanded one together.

## verify
```
PROVE   grep the canonical save's XML (rimworld-savegame skill tooling) for any
        Asimov/DroidDepot/MSEDroidFix-authored defName actually placed on the
        map/world
EXPECT  either zero placed instances (safe to re-attempt retirement, this time
        also checking the save) or a nonzero list of thing IDs/positions
        needing a real migration
LIES    "the mod-dependency check passed" says nothing about the save; only
        reading the save's own Scribe data settles this
```

## criteria
Either (a) the placed droid content in the canonical save is migrated to a surviving
def (Droidworks' own races, per the repointing this item's own C1/C2 predecessor work
already did for most kinds) and these three donors are retired for real with a clean
load proof, or (b) the owner rules they stay permanently. Either way,
`DROID_RETIRE_DEPOT_ASIMOV_1`'s own record should stop implying the retirement is
standing until one of these actually happens.

## Broader pattern worth an owner ruling
Two donor retirements tonight, both independently checked clean against the whole mod
stack, both broke the same live canonical save because of placed-object references no
mod-stack check can see. Before any further "retire this donor" item executes against
a save that has ever been played (not just a quicktest), it needs a save-content check
added to the standard discipline, not just the modlist dependency sweep. See
`[[donor-retirement-mod-check-not-save-check]]` memory for the generalized lesson.

## findings (FOUNDRY, offline save read, 2026-09-09 — game left up/untouched, no bridge taken)

Read `CANONICAL_ASHKARR_2026-09-09.rws` directly (`xml.etree.ElementTree`, ~1s parse,
25.7 MB) per the `rimworld-savegame` skill. Built the full defName lists for
`Neronix17.OuterRim.DroidDepot` (234 defNames, workshop `3096501398`) and
`Neronix17.Asimov` (59 defNames, workshop `3096481956`) from the live Steam Workshop
content dirs; `mandrake.rsw.msedroidfix` has **zero defNames of its own** — it is a
texture-path-only fix, confirmed by reading its 4-file mod folder.

**Method**: for every element whose text matched a target defName, checked whether its
parent also carried a sibling `<id>` element — that pairing is RimWorld's actual
Thing/pawn instance shape (`<li><def>Human</def>...<id>Human913</id>...`), confirmed
against controls (`Human`: 33 instances, `Steel`: 24 instances, both found correctly).
Also did an unrestricted second pass matching target defNames under **any** tag name,
and a `Class="..."` scan for both `Asimov.*` and any Droid/OuterRim-namespaced Scribe
class, to catch custom-component save state a plain `<def>` walk would miss.

**Result — DroidDepot and MSEDroidFix: ZERO placed content, of any kind.**
None of the 234 DroidDepot defNames (or MSEDroidFix, which has none) appear as a
placed Thing, pawn, or custom Scribe-serialized component anywhere in the save. The
~110 distinct DroidDepot/OuterRim defNames that *do* appear (2-10 occurrences each)
are exclusively **mod-cache registry lists that enumerate every currently-loaded def
regardless of use** — e.g. `CaravanAdventures.InitGC`'s `packUpFilter/allowedDefs`
(a caravan-packing whitelist) and `WorkTab.PriorityManager`'s per-colonist Workgiver
priority table. These are reference-only residue exactly as CLAUDE.md's Scribe
distinction predicts, and retiring DroidDepot/MSEDroidFix should not touch a single
placed object.

**Result — Asimov: real, live save-content dependency, but NOT droid pawnkinds.**
`grep -c 'Class="Asimov\.'` (override: `MEASURE_ALLOW_SCAN=1`, this session) found:
- **78× `Asimov.Need_Energy`** — a custom `Need` C# class instance, live inside
  `game/world/worldPawns/pawnsAlive/<pawn>/needs/needs/`, i.e. attached to real,
  currently-loaded pawns. Checked the owning pawns' own `<def>`/`<kindDef>`: they are
  **not droids** — 27 Human (9 `Colonist`, plus Jawa faction leaders/elders), 7
  Bantha, 7 Eopie, 6 Megascarab, 5 `AA_Behemoth`, 3 each Qormot/Bolotaur/
  IridonianReek, assorted mechs (`Mech_Militor`, `Mech_CentipedeGunner`,
  `Mech_Pikeman`) and other wildlife/NPCs. Asimov's energy-need patch has clearly
  attached to the general pawn population, not just automatons.
- **1× `Asimov.WorldComp_EnergyNeed`** — a world-level GameComponent, also live.
- These are the exact same two Scribe-class names `DROID_ASIMOV_SAVE_SCRUB_1`
  (closed 2026-09-06) already scrubbed to 0 — **but on two different save files**,
  `Saves\WORLDMAP_V1_original_c.rws` (82→0) and `Saves\gravship_scratch_d.rws`
  (133→0). `CANONICAL_ASHKARR_2026-09-09.rws` did not exist yet, or was not the
  "latest letter," at scrub time — **it was never scrubbed, and still carries live
  Asimov Need/WorldComp data.** This is the actual gap, not the Empire KX kind
  repoint (that repoint is real and complete — checked `GalacticEmpire.xml`, still
  points at `RSW_DW_OuterRim_ImperialKXSecurityDroid`, no raw Depot kind live
  anywhere — it was never the blocker).

## Player.log cross-check
No crash trace exists for this item's own attempt, and none should be expected: per
the item's own account, `rimworld/load_game` refused with `missing_mods` at the
**pre-Scribe compatibility gate** (the save's `<meta><modIds>` list — confirmed by
reading it directly: it still names `neronix17.asimov`, `neronix17.outerrim.droiddepot`,
`mandrake.rsw.msedroidfix` among 590 entries) and the agent correctly declined to force
past it. That gate is a blunt "every mod recorded in the save must be active" check —
independent of whether the save actually uses the mod's content — which is why it
fired identically for DroidDepot/MSEDroidFix (zero content dependency) and Asimov
(real dependency): both read as `missing_mods` for the same reason, before content
is ever touched. The doorsexpanded sibling's crash-after-force-load is a different,
unverified case (not this item's scope) but is consistent with what a live
`Class="Asimov.Need_Energy"` deserialization failure would likely do here too, had
this item's agent forced the load instead of stopping.

## Real fix scoped (no porting needed)
No pawnkind, building, or def needs porting to Droidworks. The fix is a **save
scrub**, the same operation already proven safe by `DROID_ASIMOV_SAVE_SCRUB_1`,
applied to the one save that missed it:
1. Back up `CANONICAL_ASHKARR_2026-09-09.rws` (mandatory, per CHARTER's expensive-list
   item 4 and the `rimworld-savegame` skill).
2. Text-line-surgery the 78 `Asimov.Need_Energy` `<li>` blocks and the 1
   `Asimov.WorldComp_EnergyNeed` block to empty/absent (same technique as the 2026-09-06
   scrub: no XML re-serialization, grids untouched), verify `Class="Asimov\.` reads 0.
3. DroidDepot and MSEDroidFix need no save edit at all — confirmed zero placed
   content — only the `ModsConfig.xml`/`<meta>` removal.
4. Re-attempt retirement; this time `rimworld/load_game` should clear `missing_mods`
   once the save's own `<meta><modIds>` no longer lists the three packageIds (that
   list is separate from the game's live `ModsConfig.xml` and is part of what a
   real re-save after a clean load rewrites — confirm this on the actual reload
   rather than assuming).
5. Cold-load proof still owed, as R3's own item already noted.

Not done here (scoping/root-cause only, per this item's brief): the scrub itself,
any `ModsConfig.xml` edit, and any retirement re-attempt.
