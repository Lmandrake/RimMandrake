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
