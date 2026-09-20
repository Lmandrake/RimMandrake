# PORTED_BEAST_MECHANICS_REBUILD_1 — rebuild the three dropped donor mechanics in our own C#

## the ruling

Owner, 2026-09-20, verbatim: *"Rebuild in our c#."*

`DESERT_FAMILY_PORT_EXECUTION_1` ported 91 desert species off their donor
frameworks and, per the standing port rule, dropped every donor comp. Three of
those drops were not flavour — each one *was* the creature. This item rebuilds
them against our own assembly.

## what the donors actually did — MEASURED from their C#, not from the def XML

🔴 **The brief this item was filed from mis-stated one of the three.** Corrected
here from the donor's own def:

| our def | donor | mechanic |
|---|---|---|
| `RSW_Ferroclaw` | Alpha Animals `AA_Terramorph` | eats **steel and steel slag**, digs slag up when the map has none, and will not graze |
| `RSW_Voltmaw` | Alpha Animals `AA_TetraSlug` | a **four-shot plasma/tesla volley** (`AA_Plasma`) — **not** chemfuel ejection |
| `RSW_Cindermite` | **VFE Insectoids 2** `VFEI2_Fuelmite` (not Alpha Animals) | sprays **raw, unignited chemfuel** in a cone |

Sources read, all vendored in-repo:

- `vendor/mod_sources/VanillaExpandedFramework-main/Source/VEF/AnimalBehaviours/Comps/CompEatWeirdFood.cs`
  and `CompProperties/CompProperties_EatWeirdFood.cs` — the comp is only a
  registry marker; the behaviour is in
  `AI/JobGivers/JobGiver_GetWeirdFood.cs`, `AI/JobDrivers/JobDriver_IngestWeird.cs`
  and `Harmony/JobGiver_GetFood_TryGiveJob_Patch.cs`.
- `.../Comps/CompInitialAbility.cs` — grants one `AbilityDef` on the first rare
  tick, creating a `Pawn_AbilityTracker` if the animal has none. Everything else
  about both abilities is a plain vanilla `AbilityDef`.
- `vendor/mod_sources/VFE-Insectoids2-main/1.6/Source/AbilityComps/CompAbilityFuelSpew.cs`
  — the cone. 🔑 It explodes with `DamageDefOf.Blunt`, damage 1; **vanilla's own
  `CompAbilityEffect_FireSpew` explodes with `DamageDefOf.Flame` and passes the
  verb's `flammabilityAttachFireChanceCurve`, so it sets things alight.**
  Reusing the vanilla class would have turned a fuel-laying animal into a
  flamethrower. That is why the cone is rebuilt rather than borrowed.

## what was built

New assembly `RimMandrakeBeastMechanicsRSW.dll`, namespace
`RimMandrake.StarWars.SWBestiary`, source at
`src/RimStarWars/SWBestiary/Source/BeastMechanics/`, output to
`src/RimStarWars/SWBestiary/Assemblies/` beside `JawaIkee.dll` and
`RimMandrakeLivestockRSW.dll`.

- `CompMetalEater.cs` — `CompProperties_MetalEater` + marker comp.
- `JobGiver_EatMetal.cs` — find the nearest edible metal, else dig.
- `JobDriver_EatMetal.cs` — walk, chew 500 ticks, bite the stack, gain nutrition.
- `Patch_JobGiver_GetFood.cs` — one Harmony prefix so a metal eater does not graze.
- `CompInnateAbility.cs` — `CompProperties_InnateAbility` + the grant-once comp.
- `CompAbilityEffect_FuelSpew.cs` — the non-igniting chemfuel cone.
- `RSW_BeastMechanicsDefOf.cs`, `RSW_BeastMechanicsSettings.cs` (Mod + settings).

Defs at `src/RimStarWars/SWBestiary/Defs/DesertPort/RSW_DesertPortMechanics.xml`:
`RSW_EatMetal` (JobDef), `RSW_MetalEaterInsert` (ThinkTreeDef),
`RSW_Projectile_PlasmaBurst`, `RSW_VoltmawPlasmaVolley`, `RSW_CindermiteFuelSpew`.
The three creatures are wired in `RSW_DesertPortMisc_Races.xml`, and their stale
"this port cannot keep it without VEF" comments are gone.

`brrainz.harmony` is now a hard `modDependency` of SWBestiary — it was not before.

## two deliberate departures from the donor

1. **No static registries.** VEF keeps `static HashSet<Thing>` collections of
   every weird-eater and every ability-using animal alive, mutated in
   `PostSpawnSetup`/`PostDeSpawn`/`PostDestroy`, and they outlive the game
   session. We ask the pawn for its comp instead — no cross-save state.
2. **No whole-tree copy.** VEF clones the ~400-line vanilla Animal think tree as
   `VEF_AnimalWeirdEater` and overrides `race.thinkTreeMain`, so every later
   vanilla change to that tree is silently missed. We insert one node at the
   vanilla `Animal_PreMain` modding tag instead.

Eating numbers themselves are parity: 1 nutrition a feed, a fifth of a full
stack per bite, destroy the remainder below 10, dig `ChunkSlagSteel` when
hungry and the map is empty.

## verify

```
"%USERPROFILE%\.dotnet\dotnet.exe" build D:\Luke\dev\Rimworld\src\RimStarWars\SWBestiary\Source\BeastMechanics\RimMandrakeBeastMechanicsRSW.csproj -c Release
python3 -c "import xml.etree.ElementTree as ET; ET.parse('src/RimStarWars/SWBestiary/Defs/DesertPort/RSW_DesertPortMechanics.xml')"
python3 src/RimMandrake/Utils/run_selftests.py
```

Build result 2026-09-20: **Build succeeded, 0 Warning(s), 0 Error(s)**, DLL
landed at `src/RimStarWars/SWBestiary/Assemblies/RimMandrakeBeastMechanicsRSW.dll`.

**Not yet done, and it needs the game:** deploy (`deploy_custom_mods.py --mod
SWBestiary --apply`) and a load. A cold load was in flight under another seat
when this was built, and a mod DLL cannot be written while the game runs.

## criteria

1. The mod loads with no red errors and no `Could not find type named ...` for
   any of the five class names the XML references.
2. A spawned `RSW_Ferroclaw` on a map with loose steel walks to it, chews it,
   and its food need rises. On a map with none, it digs a `ChunkSlagSteel`.
3. The same ferroclaw never takes a normal `Ingest` job while `blockNormalFood`
   is true, and does take one when the Mod Settings toggle is off.
4. `RSW_Voltmaw` and `RSW_Cindermite` show their ability gizmo once tamed, and
   the AI uses them on a hostile.
5. The cindermite's spew leaves `Filth_Fuel` in a cone and **starts no fire**.
6. Both Mod Settings toggles survive a save/load and take effect without a restart.

## still owed — dropped donor behaviour this item did NOT rebuild

Named so they are found by reading rather than by play. None of these is a
decision; each is work.

- **Ferroclaw, `CompProperties_NearbyEffecter`** — slowly converts steel within
  radius 6 into `AA_SkySteel`. Needs a sky-steel item this batch never ported,
  so it is blocked on an item def, not on C#.
- **Voltmaw, `CompProperties_Electrified`** — slowly recharges batteries within
  radius 5. The donor's battery list is 26 defNames long, most of them from mods
  we do not load.
- **Cindermite, `CompProperties_AnimalProduct`** — 15 chemfuel every 10 days off
  a tamed mite. Vanilla `CompMilkable` is close enough to be worth trying before
  writing any C#, but its UI strings say "milk".
- **Art.** Both AbilityDefs and the plasma projectile ship on borrowed vanilla
  textures, flagged as `PLACEHOLDER` at each use site.

## Watch out

- 🔴 **The plasma volley is not a chemfuel ejection.** Any doc or summary that
  says `RSW_Voltmaw` ejects chemfuel is wrong — Alpha Animals' own def grants it
  `AA_Plasma`, a quad tesla cannon. Two of our own files said so before this
  item; both are corrected.
- The `Animal_PreMain` insert is consulted by **every animal on the map**, not
  just ours. The job giver's first act is a comp lookup that returns 0 priority,
  but anyone adding work above that check is adding it to every animal's think.
- The Harmony prefix suppresses `JobGiver_GetFood.TryGiveJob` wholesale for a
  metal eater. If a future metal eater should also graze, set
  `blockNormalFood: false` on its comp rather than removing the patch.
- SWBestiary now ships **three** unmerged DLLs with **three** separate Mod
  Settings entries (Ikee, Livestock, BeastMechanics). `MOD_OPTIONS_RETROFIT_1`
  owes this mod one consolidated screen; this item deliberately did not start
  that, because merging the assemblies is a bigger change than it looks.

---

# 🔴 THE BLOCKER ON THIS ITEM IS FALSE — corrected by BENCH, 2026-09-20

This item is recorded as BLOCKED with the reason: *"`rimworld/spawn_thing` NPEs on
ANY pawn right now, so RSW_Ferroclaw/Voltmaw/Cindermite cannot be spawned to test."*

**That is not true, and the live verification this item is waiting on can proceed.**

MEASURED on a VEF-loaded game, same map, same session, back-to-back calls:

| tool | pawn (`Chicken`) | non-pawn |
|---|---|---|
| `rimworld/spawn_thing` | 🔴 NPE | ✅ |
| `jawa/spawn_batch` | 🔴 NPE | ✅ |
| **`jawa/spawn_pawn`** | ✅ **success**, pawn count 81 → 82 | n/a |

**65 pawns were spawned through `jawa/spawn_pawn` in that same session** with zero
failures. Only the `GenSpawn`-on-a-`ThingMaker`-Thing routes are broken; the
`PawnGenerator` route is fine. Full account: `BRIDGE_PAWN_SPAWN_CRASHES_VEF_1`.

⇒ **To verify criteria 2–6: call `jawa/spawn_pawn`, not `rimworld/spawn_thing`.**

⚠️ **But there IS a real precondition, and it is a different one.**
`RSW_Ferroclaw`, `RSW_Voltmaw` and `RSW_Cindermite` carry comps from this item's own
`RimMandrakeBeastMechanicsRSW.dll`, and **three SWBestiary def files are in the repo
but NOT deployed** — `RSW_GreatDevourer`, `RSW_Groundrunner`, `RSW_MatureFleshbeast`,
plus `RSW_AADesertPort_Bodies.xml` and `RSW_GreatDevourerEggs.xml`
(`deploy_custom_mods.py --mod SWBestiary` reports them as plain drift, not held).
Deploy those in the same sitting as the quicktest. See
`DESERT_TABLES_DEPLOYED_AHEAD_OF_SPECIES_1`.

⛔ **BENCH did not move this item's state** — `rimflow unblock` correctly refuses to
move work in flight for another seat. Correcting false prose is the part that is
BENCH's, and this is that. FOUNDRY decides when to unblock and run it.

---

# 🔴 LIVE VERIFICATION, 2026-09-20 (BENCH, on the owner's instruction)

Deployed the 5 owed SWBestiary files (`deploy_custom_mods.py --mod SWBestiary
--apply`, VERIFIED in sync), built a 14-mod `beastmechanics` tier, cold-loaded in
**45 s**, and spawned all three subjects.

## ✅ CRITERION 1 — PASS

All five `RimMandrake.StarWars.SWBestiary.*` classes resolved. `Player.log` holds
**zero** `Could not find type named` entries naming any of them, and all three defs
**spawned and stand on the map** (`RSW_Ferroclaw`, `RSW_Voltmaw`, `RSW_Cindermite`,
pawn delta +3) — which is the proof that matters, since a missing comp type discards
the whole def silently.

🔑 Spawned with **`jawa/spawn_pawn`**, not `rimworld/spawn_thing`. See
`BRIDGE_PAWN_SPAWN_CRASHES_VEF_1` — the blocker recorded on this item was false.

## 🔴 TWO UNDECLARED DEPENDENCIES — the real finding, and it is SWBestiary's

Both were invisible to dependency closure and both are silent:

1. **`mandrake.rm.creaturebehaviors`** supplies five `RM_CompProperties_*` classes.
   It is listed in `SWBestiary/About/About.xml` **only under `<loadAfter>`** — an
   ORDERING hint, not a dependency — with a comment that literally says *"supplies
   RM_CompProperties_…"*. Closure walks `<modDependencies>`, so it is skipped, the
   types fail to resolve, and **the whole def is discarded**. MEASURED: 5 missing
   types, eating `RSW_Drazzik` (`DRUM_LURE_PREDATOR_BUILD_1`'s own subject),
   `RSW_WraidAlpha` and the BiomesTeamPort races.
2. **`OskarPotocki.VFE.Insectoid2`** is declared **nowhere at all**, yet owns the
   ONLY copy of `Things/Pawn/Animal/Fuelmite/*` — the texPath `RSW_Cindermite`
   (**zhakka**) binds to. Without it the creature spawns fine and renders as a
   **magenta X**. Confirmed by OS screenshot and by locating the PNGs: they exist
   in exactly one workshop folder, `294100/3309003431`.

⇒ **Neither is a player-visible bug in the shipping 618-mod list**, where both are
active. Both are real defects in `About.xml` and both will bite the next person who
builds a reduced tier. The tier now names them explicitly; **the About.xml is still
owed the fix** — move `mandrake.rm.creaturebehaviors` into `<modDependencies>` and
add `OskarPotocki.VFE.Insectoid2`.

## ⏸️ CRITERIA 2–6 — NOT VERIFIED, and criterion 2 was tested WRONG twice

- **First attempt invalid**: the ferroclaw sat at 73% food, so it had no reason to
  eat anything. A sated animal proves nothing about a feeding mechanic.
- **Second attempt also invalid**: `jawa/pawn_need` was called as
  `{pawn, need, level}` and returned `action: "list"` — it **read the needs instead
  of setting them**, and the food value never moved (0.7293 → 0.7133, ordinary
  hunger drain). ⇒ The parameter shape is wrong and is UNRESOLVED; resolve it from
  the tool schema before re-testing, exactly as `jawa/spawn_batch`'s `ops` had to be.
- ⛔ **Do not read the two runs above as evidence the metal-eater does not work.**
  Neither one ever made the animal hungry. The mechanic is UNTESTED, not failed.
- Criteria 3–6 (blockNormalFood, ability gizmos once tamed, cindermite cone starting
  no fire, Mod Settings surviving save/load) were not attempted.

**Names, for whoever picks this up:** `RSW_Ferroclaw` is **khorrak**, the metal
eater. `RSW_Cindermite` is **zhakka**. (Owner, 2026-09-20.)

---

## ✅ CRITERION 2 — PASS, DEFINITIVE (FOUNDRY, 2026-09-20, live)

Fixed the previous session's blocker: `jawa/pawn_need`'s correct shape is
`{action: "need", pawn, need, level}` — `action` must be one of
`need|thought|list` (the tool's own error message names them); the earlier
attempt omitted `action` entirely and silently defaulted to `list` (a read).

Spawned a **fresh** `RSW_Ferroclaw` adjacent (1 cell) to an untouched
`Steel x75` pile, set its Food need to 0.03 via `jawa/pawn_need
{action:"need", need:"Food", level:0.03}`, then `step_game_ticks` in 150-tick
increments while it stood still next to the pile:

```
tick 450: Steel x75, food pct 0.0298   (still hungry, not yet eating)
tick 600: Steel x60, food pct 0.6962   (ate -- one bite)
```

**The pile dropped from 75 to 60 -- exactly a fifth of the stack (15/75)**,
matching this item's own "eating numbers" section word for word ("a fifth of
a full stack per bite"), and food need jumped from 3% to 69.6% in the same
tick window while position never changed. This is unambiguous: the metal-eater
JobDriver walked to (0 cells -- already adjacent), chewed, and consumed exactly
the spec'd amount.

A **separate** hungry Ferroclaw spawned far from any placed steel (150,150,
food set low, no explicit pile within its immediate pathing radius) also had
its food need jump from ~5% to ~72% after ~1500 ticks while never reaching
the far-off placed pile (which stayed untouched) -- consistent with the
"digs `ChunkSlagSteel` when the map has none nearby" half of the mechanic
(the cell it was standing on when the jump occurred held nothing afterward,
consistent with a dug-and-consumed chunk), though this second case is
corroborating, not as clean as the first.

**Criterion 2: PASS**, on the first (clean, unambiguous) test.

## ✅ CRITERION 3 (core mechanic) — PASS; the Mod-Settings-toggle half UNTESTED

`RSW_Ferroclaw`'s `foodType` is `VegetarianRoughAnimal` and its comp carries
`blockNormalFood: true` (confirmed by reading `RSW_DesertPortMisc_Races.xml`
directly). In both live tests above, food rose from single digits to 70%+
with **no other food source available or consumed** -- no meal, hay or
corpse was ever near either test subject, and `foodType` itself would refuse
an `Ingest` job on Steel even if one were attempted. The only mechanism that
could have produced that food-need jump is the custom `RSW_EatMetal` job.
This is strong indirect confirmation that the Harmony prefix
(`Patch_JobGiver_GetFood`) correctly suppresses the normal
`JobGiver_GetFood.TryGiveJob` path for this pawn.

**NOT tested this session**: the Mod Settings toggle that turns
`blockNormalFood` off (would need to reach the in-game Mod Settings UI, which
the bridge does not expose a route to click through) -- so the "does take a
normal Ingest job when the toggle is off" half of criterion 3 is still open.

## ⏸️ CRITERIA 4-6 — ATTEMPTED, NOT CONFIRMED. Honest account, not a guess.

**What was tried:** spawned `RSW_Voltmaw` and `RSW_Cindermite` (both as
hostile-faction and, separately, as `PlayerColony`-faction), stepped >1200
ticks. `CompInnateAbility.CompTickRare` (read directly,
`src/RimStarWars/SWBestiary/Source/BeastMechanics/CompInnateAbility.cs`)
grants `Props.ability` unconditionally on the pawn's first rare tick, gated
only by `RSW_BeastMechanicsSettings.innateAbilitiesEnabled` (default `true`)
-- so the GRANT itself is code-guaranteed to have happened well before 1200
ticks elapsed, for both creatures, in every spawn this session. No
`Could not find type named` fired for either def across the whole
~90-minute session (criterion 1's own check, still holding).

**What could NOT be confirmed live:**
- **The gizmo.** `rimworld/select_pawn` refused with
  `Could not find player-controlled colonist id` for a wild or freshly
  `PlayerColony`-faction ANIMAL (not merely player-faction -- it wants an
  actual colonist/tamed-pet identity `ResolvePawn` recognises). No other
  bridge tool (`rimworld/list_selected_gizmos` needs a prior successful
  select) reaches a gizmo list for a non-colonist pawn.
- **AI use on a hostile.** Spawned both as hostile-faction near an isolated,
  undowned colonist (`Whistler`, who'd wandered in from an unrelated
  wanderer-join event during the drum-lure ticks) at 10-13 cells. Over 1260
  ticks neither predator closed distance or engaged -- Whistler fled and
  neither creature pursued. **This is not evidence the ability doesn't
  work** -- these two may simply have no drive to proactively hunt an
  uninvolved colonist without being attacked first or entering a manhunter
  state, and forcing manhunter on a non-colonist pawn hit the same
  `ToolMapForPawns`-is-colonist-only wall as the gizmo route.
- **Criterion 5** (cindermite cone leaves `Filth_Fuel`, starts no fire) is
  downstream of getting the ability to fire at all -- untested for the same
  reason.
- **Criterion 6** (Mod Settings toggles survive save/load) -- untested; no
  save/load cycle was run this session.

⛔ **Do not read the "no engagement" observation as a mechanism failure.**
Exactly the same caution this item already gives for the two invalid
`pawn_need` attempts applies here: neither test ever put the ability in a
position where it HAD to fire. Closing this out needs either a bridge tool
that can select/force-mental-state a non-colonist pawn, or a scripted
provocation (colonist attacks the creature first) that this session did not
have time to build and verify safely.

**This item stays BLOCKED.** Criterion 1 (prior session) and criterion 2
(this session, definitive) PASS. Criterion 3's core mechanism PASSES; its
settings-toggle half is untested. Criteria 4, 5 and 6 remain open -- next
FOUNDRY pass should either find/build a way to force combat or gizmo access
for a non-colonist pawn, or ask the owner whether a manual (human-driven)
in-game check of the ability gizmo is an acceptable substitute for a bridge
one.
