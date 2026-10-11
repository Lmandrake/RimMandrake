# Convenience/automation mods: what we keep by building it ourselves

_Owner ruling C10, typed 2026-10-10 (`design/RimMandrake/mod_audit/OWNER_RULINGS.md`): "Cut them all
then go back and add only the key functionality we need unless it is too hard. Do a design pass of
what we need from them. Much modification will be required." This is that design pass (FOUNDRY,
2026-10-10, offline: no bridge, no game). Nothing here unticks a mod or files a ticket; §6 lists the
tickets to file._

**Method.** Each mod was resolved to its on-disk root by parsing every `About/About.xml` under both
`…\common\RimWorld\Mods` and `…\workshop\content\294100` (1,377 About files; all nine found, all in
the workshop root). Defs and patches were read as XML. C# was read where the mod ships source
(Belt Extractors, Dedicated Turrets, Ship Wall Enhanced, WallStuff). Where it does not
(MinifyEverything, LightsOut, Shield Generators, the HMC DLLs), type, method and user-string tables
were listed with `dnfile`, so behaviour stated for those is **INFERRED from names** unless marked
otherwise. Engine facts come from RimSage (decompiled 1.6). Save facts come from parsing
`CANONICAL_ASHKARR_START_2026-09-12.rws` (sanity probe: `MinifiedThing` 12 hits, 1,406 distinct defs).

**The scenario test applied throughout** (`mod_audit/SCENARIO_BRIEF.md` §1–2): six fixed founders on
a cramped gravship. Hauling, reloading and **deciding what to leave behind** are meant to cost
something. There is no free fuel and no large-scale automation. There is one kind of heat
(vanilla). Fluids run through FlowWorks and the `LiquidDef` registry, with "never redundant
tanks". Danger is qualitative, never an arms race. Static killboxes are forbidden
(`design/Jawa/mods/forbidden_mods.md` line 65).

## 1. Per-mod findings

### 1.1 Belt Extractors (`groovytaco.beltextractors`, workshop 3694555789)
- **(a) What it does.** It is a pure Harmony patch of VFE Factory's `Building_Conveyor`, with 0
  defs. A belt whose back faces a `Building_Storage` pulls whole stacks out of it, with no power,
  rate limit or filter. The storage filter is not consulted (read from `Source/Harmony/*.cs`). It
  has no licence.
- **(b) Needed?** No. It automates hauling, and hauling being a real cost is a pillar.
- **(d) If cut.** 0 placed things in the save. 0 references in our `src/`. VFE Factory and its
  belts are unaffected.
- **(e)** Not applicable.

### 1.2 Reel's Turret Pipeline (`reel.turretpipeline`, 3424132769)
- **(a) What it does.** It is XML only, on the VEF PipeSystem framework, with no licence. It adds:
  - A net, `Reel_AmmoNet`, with pipes, a 3×2 explosive "ammunition hub" tank holding 1,000 units,
    an injector, a dispenser and a `ReelTurretAmmo` item (20 steel → 25 ammo at
    `TableMachining`).
  - Patches that replace the `CompRefuelable` fuel filter of `Turret_MiniTurret`,
    `Turret_Autocannon`, `Turret_Sniper` (and VFE Security, VGE, Rim-Effect and VFE Ancients
    turrets) with that ammo.
  - `linkToRefuelables`, which then refills those turrets from the net. That removes the walk to
    the turret.
- **(b) Needed?** No.
  - Its stated purpose is removing manual rearming, which is a cost the scenario wants.
  - It is also a second pipe/flow engine, against the FlowWorks ruling.
  - Vanilla already makes rearming a hauling job: the `RearmTurrets` work giver, with `Rearm`
    jobs fed by `CompRefuelable`.
    - Mini-turret: 60 steel.
    - Autocannon: 90 steel.
    - Sniper: 30 uranium.
    - Rocketswarm: 12 chemfuel.
    - Mortar: 20 barrels, manned.

    These figures are parsed from `Core/Defs/ThingDefs_Buildings/Buildings_Security_Turrets.xml`.
- **(d) If cut.** 0 placed things in the save. 0 references in our `src/`.
  - `hmc.wall.furniture` patches it, but that patch is also cut.
  - `biotechrace.yautja.alleyballey` lists it in `loadAfter`, which is harmless.
  - The VEF PipeSystem stays loaded for other mods.

### 1.3 MinifyEverything (`erdelf.minifyeverything`, 872762753, **MIT**)
- **(a) What it does.**
  - A postfix on implied-def generation gives *every* building def a `minifiedDef`, so they all
    become uninstallable.
  - Transpilers on the install job and the blueprint designator make reinstalling work for things
    vanilla never expected to move: walls, doors, conduits, generators.
  - A `get_Graphic` postfix lets minified linked graphics draw.
  - Optional ticking of minified things (`tickMinified`).
  - A per-def disable list in Mod Settings.
  - All of this is INFERRED from method names and strings.
- **(b) Needed?** Two narrow parts of it are needed. The blanket rule is not.
  1. **Battlefield capture.** Owner, 2026-08-31, `design/Jawa/trap_renaissance_spec.md` §2b, typed:
     *"We can steal their traps rather than setting them off... maybe also their sandbags,
     anti-tank traps, fences, etc. Yes to turrets"*, ruled **REDEPLOY, DEGRADED** by card.
     - The spec names this "the light minify — steal the unstealable, bounded".
     - It is **not built and has no open item** (searched `src/`, `design/`,
       `infrastructure/state/items/`).
     - Vanilla leaves `Turret_Autocannon`, `Turret_Sniper`, `Turret_RocketswarmLauncher`,
       `Barricade`, `Sandbags`, `Fence` and `FenceGate` non-minifiable (measured: 100 of 249
       player-buildable vanilla buildings carry no `minifiedDef`). MinifyEverything is what
       currently makes them liftable.
  2. **A few ship and camp fixtures that must move.** Anything standing on the substructure
     already flies with the ship (Odyssey). So minify matters only for:
     - re-laying a cramped deck;
     - carrying camp gear back aboard.

     The vanilla non-minifiable list that bites on a gravship is short:
     - `Cooler`
     - `HydroponicsBasin`
     - `CommsConsole`
     - `HiTechResearchBench`
     - `FabricationBench`
     - `ChemfuelPoweredGenerator`
     - `WoodFiredGenerator`
     - `MoisturePump`
     - Odyssey `ChemfuelTank`

     Everything else ships minifiable already: 149 of 249, including beds, workbenches,
     batteries, mini-turret, lamps and heaters.
  - **NOT needed:**
    - Minifiable walls, doors, conduits and vents. They are structure; the ship's hull moves
      with it.
    - Large generators and scanners (`SolarGenerator` 4×4, `WindTurbine`, `GeothermalGenerator`,
      scanners). Leaving them behind is the decision the loop is built on.
    - Ticking minified buildings.
- **(d) If cut.**
  - **The canonical save holds 11 `MinifiedThing` wrapping `Wall` (stuff `BlocksSlate`)** lying at
    map cells (39–54, 0, 41–46). Only MinifyEverything can have made them.
    - After the cut, `Wall` has no `minifiedDef`. The items should still load, because
      `MinifiedThing` is vanilla, but they cannot be reinstalled.
    - Without its `get_Graphic` postfix, a minified linked wall graphic may draw wrongly or log
      errors. **UNMEASURED.**
    - Purge them before or at the cut (§6, `SAVE_WALLS_EXCISE_MINIFIED`). The 12th
      `MinifiedThing`, `RM_Graffiti_Vandal`, is ours and natively minifiable.
  - Our own defs: no reference in `src/` (0 hits). Our buildings that need to move already set
    `minifiedDef` explicitly (177 hits across 76 files, for example WreckedMachines' mobile
    machines and `RUT_ShieldGenerator`).

### 1.4 Dedicated Turrets (`clown.dedicatedturrets`, 3739213606, **"All rights reserved"**)
- **(a) What it does.** Four 2×2 powered (90 W) autonomous `Building_TurretGun`s with **no
  ammunition** (no `CompRefuelable`), behind research `DedicatedDefenceSystems` (1,800 points):
  - **Atomiser:** a ramping lock-on beam.
  - **Vaporiser:** a piercing line beam with a 180-pulse burst.
  - **Sludger:** a 48° slowing cone; hediff `SludgerSludge`, move speed ×0.2 for 900 ticks.
  - **Zapper:** chain lightning that stuns up to 5 targets.
- **(b) Needed?** The mod is not needed.
  - Ammo-free power turrets delete the reload cost.
  - Ramping and piercing beams are arms-race tools.
  - The one idea worth keeping is a **non-lethal disable turret**. It fits Ozzik's "disable-and-
    take" and the prisoner pipeline (`trap_renaissance_spec.md` §1), and the setting's ion
    physics (`design/Jawa/worldbuilding/setting_physics.md`: ion is decisive against droids,
    vehicles and turrets).
  - The licence forbids reusing its code, XML or textures, so any version of ours must be written
    clean.
- **(d) If cut.** 0 placed things in the save. Our references are all inert:
  - `src/RimStarWars/Armoury/Patches/Turrets_Renames.xml` line 44 and `Turrets_DamageDoctrine.xml`
    line 184 are `PatchOperationFindMod "Dedicated Turrets"` and become no-ops. The second is
    generated by `src/RimStarWars/Armoury/Source/gen_turret_doctrine.py`.
  - The Armoury `About.xml` `loadAfter` (line 124).
  - ResearchRetag `About.xml` (line 48), and `RUT_ResearchTabAssign.xml` (around line 3370, a
    Conditional on `DedicatedDefenceSystems`).
  - They should be pruned, not left (owner 2026-09-09: inaccurate material is deleted).

### 1.5 Shield Generators (`neronix17.shieldgenerators`, 2540563802, no licence found)
- **(a) What it does.** Every def is `MayRequire` Royalty; it needs VEF and Tabula Rasa. Three
  research projects of 4,000–10,000 points. The buildings:

  | Building | Size | Radius | Power | Intercepts | Notes |
  |---|---|---|---|---|---|
  | Astroglide | 1×1 | 5 | self-powered | ground only | minifiable |
  | Durex | 4×4 | 20 | 1,000–3,500 W | ground and air | needs the plasma loop |
  | Trojan | 6×6 | 40 | 4,000–12,000 W | ground and air, `podBlocker` | blocks drop pods and shuttles |

  - **Plasma loop (Durex, Trojan):** a VEF pipe net, `ShieldGen_PlasmaNetwork`, plus venting
    cooling plugs. EMP collapse blast radius is 75 for the Durex and 200 for the Trojan.
  - **Shield walls:** commented out, so there are none.
- **(b) Needed?** No; the function is already ours.
  - `mandrake.rut.shipshields` (`src/RimUtinni/ShipShields`, 1,570 lines of C#) ships one 3×3
    `RUT_ShieldGenerator` on Substructure, minifiable, 400 W. It has four module-switched fields:
    - bubble: radius 14.9, ground and air, slow projectiles pass through, collapse warning;
    - thermal veil;
    - cryo envelope;
    - particulate screen.
  - It covers every ruled row of `design/Jawa/proposals/ship_shields_deep_design.md`
    (`SHIELD_MODS_LEVERAGE_1`).
  - Vanilla Odyssey also ships `GravshipShieldGenerator`: 3×3, radius 24.9, 200 W, ground and air,
    a gravship facility capped at 2.
  - **Explicitly not needed:**
    - **Pod blocking.** The Empire is an orbital pursuer, and a bubble that bans drop pods
      deletes that pressure.
    - **The plasma pipe net.** It is a second flow engine.
    - **Radius-40 base domes.** They are static-base defence on a ship that is meant to keep
      moving.
- **(d) If cut.** 0 placed things in the save. `RUT_ResearchTabAssign.xml` carries 19
  Conditional-guarded `ShieldGen_*` rows (around line 4618) that become no-ops; prune them.
  - `neronix17.toolbox` (Tabula Rasa) stays: Outer Rim and others need it.
  - The registry lists `neronix17.outerrim.core` among its dependents, but **no installed
    About.xml names `neronix17.shieldgenerators`** in a dependency or `loadAfter` (all 1,377
    parsed). So that edge is a patch or registry inference, not a load requirement.
  - `SHIELD_MODS_LEVERAGE_1`'s original "leverage the existing shield mods" brief is moot for this
    mod.

### 1.6 LightsOut (`juanlopez2008.lightsout`, 2584269293; upstream repo has no licence)
- **(a) What it does.** The 1.6 load folder is the root `Assemblies/` plus `Patches/`. Behaviour is
  INFERRED from names, corroborated by our own decompile notes in
  `src/RimMandrake/LuminousPigment/Source/DeepfireLightsOutCompat.cs`.
  - **Lights:** any `CompGlower` thing whose defName contains "light", "lamp" or "illuminated"
    goes dark when its room is empty, or when everyone in it is asleep.
  - **Standby:** workbenches, TVs, research benches and enterables (Biotech vats and the like)
    drop to standby power (default 0%) until a pawn is at them.
  - **Opt-out:** a per-building "Keep On" gizmo, added to vanilla `BuildingBase` by patch.
  - **Settings:** delay, standby rate, night lights, and animals triggering lights.
- **(b) Needed?** The *effect* is needed: fuel is life, so a light burning in an empty hold is real
  waste. The *mechanism* is not.
  - It writes glow state behind our back, which fights LIGHT_LEDGER and the Atmospheric compositor
    (`design/RimMandrake/atmospheric_base_hook_ecosystem.md` §7: "two mods writing the same field
    on the same tick").
  - It matches lights by **defName substring**, so it doused our Deepfire proxies and needed
    reflection compat code.
  - **Not needed:** bench standby for the Biotech mechanitor and gene buildings (those systems are
    out), TV handling, and animals triggering lights.
- **(d) If cut.**
  - 0 placed things (it adds no defs).
  - `DeepfireLightsOutCompat.cs` is reflection-soft and simply never patches. It becomes dead code,
    to delete along with its csproj `<Compile>` line and its references:
    - `src/RimMandrake/bridgetools/prove_deepfire_god_deltas.py` (21 hits);
    - `DeepfireGodDeltaDebugActions.cs` (15);
    - the `LightsOut:` bar in `src/RimMandrake/LuminousPigment/validation.py` and in
      `design/validation_walks/RimMandrake/LuminousPigment.md` line 72;
    - `deepfire_luminous_pigment_spec.md` §8;
    - two strings in `src/RimMandrake/Utils/modset_builder.py` (lines 115–116).
  - Editing the walk is prose outside a hashed `## north star` section; check before editing.

### 1.7 [HMC]Wall Furniture (`hmc.wall.furniture`, 3533512691, no licence)
- **(a) What it does.** About 41 buildings, all 1×1, using **vanilla
  `Placeworker_AttachedToWall`**. Each sits on the *floor cell in front of* a wall,
  `isEdifice=false`, Standable, with its sprite offset onto the wall face:
  - 8 wall turrets with power, ammo and flick;
  - a wall foam turret, comms console, trade beacon, fermenting barrel (custom C#),
    multi-analyzer, vitals monitor, tool cabinet, TV and tritium lamp;
  - 9 floor turret variants.
- **(b) Needed?** No. The mechanism is vanilla (Core `WallLamp`, `TorchWallLamp`; Odyssey
  `LifeSupportUnit`, `OxygenPump` and `AncientEmergencyLightBase` use the same placeworker), so we
  can give any of our own fixtures that look with no mod. Because the attachment **still occupies
  the floor cell** (walk-through, but not buildable over), it saves no deck footprint. It is a
  look, not a cheat.
- **(d) If cut.** 0 placed things. `src/RimStarWars/Armoury/Patches/Armoury_RangedDamage.xml`
  line 383 is a `PatchOperationFindMod "[HMC]Wall Furniture"` on 5 HMC projectiles and becomes a
  no-op. The file is generated by `src/RimStarWars/Armoury/Source/gen_armoury_patch.py`, so prune
  it in the generator, not by hand. Also drop the Armoury `About.xml` `loadAfter` (line 128).

### 1.8 [kyzy] Ship Wall Enhanced (`kyzy.shipwallenhanced`, 3537799933, no licence)
- **(a) What it does.**
  - **2×1 "cabins"** that *replace wall cells*: edifice, impassable, joined to walls by a Harmony
    postfix on `Graphic_Linked.ShouldLinkWith`. Cabin types:
    - **Free-production cabins:** chemfuel from power alone (50 per 10 days, or 75 per 5);
      synthetic meat for 1 wood a day; starch from nothing.
    - Batteries, a uranium generator (+4,200 W), a gravcore cell (+2,800 W) and a chemfuel
      generator.
    - A grav-fuel tank and a gravship shield, both added as `GravEngine` facilities.
    - Storage and fridge cabins.
  - **Wall mounts:** a mini solar panel, battery, mini-turret and a wall bed.
  - **Other patches:** an ammo-search patch that pulls mortar shells out of containers, and storage
    search patches for medicine and surgery.
- **(b) Needed?** No.
  - Its own stated aim is reclaiming ship interior space. Its producers are free fuel and free
    food: the chemreactor spawns chemfuel from power alone (`SW_SpawnerAdjustable.cs`).
  - Wall-cell storage multiplies a deck that is meant to be cramped.
- **(d) If cut.** 0 placed things. 0 references in `src/` outside northstar JSON snapshots, which
  are records and stay.

### 1.9 WallStuff (`arcjc007.wallstuff`, 1994340640, **Unlicense**; has 1.6 content)
- **(a) What it does.** A custom `PlaceWorker_WallObject` that places *on the wall cell itself*.
  This is the only one of the three wall mods that truly costs zero floor. It adds:
  - a wall heater, cooler and climate controller (`Building_MediumCooler`, **no exhaust side**);
  - a vent, TVs, a hi-fi, a blackboard and a tool board;
  - a multi-analyzer, trade beacon, comms console, ground-penetrating and mineral scanners;
  - mech chargers, a neural supercharger, a sleep accelerator, a mech booster, a firefoam popper,
    a battery, a power switch;
  - a room-wide repair "nano cloud";
  - a **Replicator** that spawns a configured item every day from power.
- **(b) Needed?** No.
  - Zero-footprint climate control with no exhaust breaks heat physics. Only vanilla heat is
    ruled, and a cooler must dump heat somewhere.
  - The Replicator is free goods.
  - Mech chargers serve the mechanitor ladder, which is out.
  - Zero-floor facilities defeat the cramped deck.
  - Being public domain, it is the only one we *could* copy from. Nothing in it is wanted, though.
- **(d) If cut.** 0 placed things. `frozensnowfox.frozensnowfoxtweaks` lists it in `loadAfter`,
  which is harmless.

## 2. Function table

| function (source mod) | needed? | provide how | where | effort | risk |
|---|---|---|---|---|---|
| Pull items from storage onto belts (Belt Extractors) | **no**: hauling is a cost | — | — | — | — |
| Pipe ammo into turrets (Turret Pipeline) | **no**: removes rearm cost; second flow engine | vanilla `RearmTurrets`/`CompRefuelable` stays as is | — | 0 | none |
| Manual turret rearming as a hauling job | **yes** | **vanilla**: keep every turret of ours on `CompRefuelable` with a real item | Armoury doctrine check only | 0 | a future turret def without ammo silently deletes the cost (lint, §5 step 6) |
| Uninstall enemy turrets, sandbags, barricades, fences and traps; reinstall **degraded** (MinifyEverything, ruled feature) | **yes** (owner 2026-08-31) | XML: `minifiedDef`+`thingCategories` on a fixed category list. C#: one comp that marks a building *captured* when it is uninstalled while not built by us, and on reinstall knocks it down a WreckedMachines grade (HP fraction + quality step) | `mandrake.rm.wreckedmachines` (the grade ladder already exists: WRECKED/KLUDGED/REFURBISHED) | M | enemy buildings need claiming first (`Designator_Uninstall` refuses non-player faction unless `alwaysUninstallable`), which matches "unseen/pacified map"; minified multi-cell turret graphics |
| Move a short list of ship/camp fixtures (MinifyEverything) | **yes**, narrow | XML patch adding `minifiedDef` to: Cooler, HydroponicsBasin, CommsConsole, HiTechResearchBench, FabricationBench, ChemfuelPoweredGenerator, WoodFiredGenerator, MoisturePump, Odyssey ChemfuelTank. Per-def Mod Settings toggle. Plus an audit of our own `src/` buildings that should move | `mandrake.rm.patches` (game-generic) | S | Cooler is a wall-slot building (`canPlaceOverWall`); minifying it must not leave a hole in a hull. Test install over a wall |
| Minify walls, doors, conduits, vents, large generators (MinifyEverything) | **no**: hull moves with the ship; leaving big kit behind is the loop | — | — | — | — |
| Lights and benches off when nobody is there (LightsOut) | **yes**: fuel is life | small comp `RM_CompIdlePowerDown`: rare-tick room check (no awake humanlike in the room, after a delay) → implements `IThingGlower.ShouldBeLitNow` = false (vanilla `CompGlower` honours it) + `CompGlower.UpdateLit`, and sets `CompPowerTrader.PowerOutput` to standby (the vanilla `GrowthVat` idiom). Added by patch to vanilla lamps and our fixtures by **explicit def list, never name match**; a Keep-On gizmo | game-generic. Recommended: a new tiny RM mod or `mandrake.rm.luminouspigment`'s sibling; it must link `_Shared/LightLedger` so it coexists with the compositor | S–M | double-writer with Atmospheric: resolve by making the comp *only* a LightLedger modifier owner (`cap:idle` = 0) if the compositor is live; `PowerOn` must stay true or flick logic breaks |
| Bench standby power, TV, Biotech vats (LightsOut) | **no**: mechanitor/genes out; benches are few | — | — | — | — |
| Bubble shield over ship/camp (Shield Generators) | **yes**, already built | `RUT_ShieldGenerator` (ShipShields) + vanilla `GravshipShieldGenerator` | ShipShields | 0 | none |
| Drop-pod blocking, radius-40 domes, plasma cooling (Shield Generators) | **no**: deletes Empire pressure; second flow engine | — | — | — | — |
| Portable 1×1 shield (Astroglide) | **no**: Royalty broadshield packs and wearable shields exist | — | — | — | — |
| Ammo-free beam turrets (Dedicated Turrets) | **no**: arms race; no reload cost; licence ARR | — | — | — | — |
| Non-lethal disable/ion turret (Dedicated's Zapper/Sludger idea) | **optional** | XML turret on vanilla `Building_TurretGun` firing our existing ion projectile/damage (`src/RimStarWars/JawaIonWeapons/Defs/DamageDefs_JawaIon.xml`, `HediffDefs_JawaIonStun.xml`), `CompRefuelable` on an ion cell item, single target, no chain | `mandrake.rsw.jawaionweapons` | S | art; balance against turret doctrine; owner must want a player turret at all |
| Wall-hung look for small fixtures (HMC) | **optional** | vanilla `Placeworker_AttachedToWall` on our own lamp/fixture defs | per owning mod | S | none: still uses the floor cell |
| On-wall-cell facilities, wall cabins, wall coolers, replicators, free chemfuel/food (WallStuff, kyzy) | **no**: free goods, zero-footprint, heat physics | — | — | — | — |
| Pull mortar shells out of containers (kyzy) | **no**: manning and hauling stay costs | — | — | — | — |

## 3. What breaks if cut with nothing added

| Item | Measured | Action |
|---|---|---|
| Placed Things from any of the nine mods in the canonical save | **0** (def sets parsed from each mod's 1.6 Defs, matched against `<def>` in the save) | none |
| `MinifiedThing(Wall, BlocksSlate)` × **11** at cells (39–54, 0, 41–46) | MEASURED | purge (`SAVE_WALLS_EXCISE_MINIFIED`); load effect without MinifyEverything is UNMEASURED |
| Save `modIds` lists all nine | MEASURED (616 ids) | "missing mod" notice on load, harmless |
| Armoury FindMod patches (HMC 5 projectiles; Dedicated renames + doctrine) and two `loadAfter` lines | read | no-op; prune in the generators |
| ResearchRetag rows: `DedicatedDefenceSystems`, 19 `ShieldGen_*`, `About.xml` line 48 | read | no-op; prune |
| `DeepfireLightsOutCompat.cs` + its prove script, debug action, validation bar, spec row | read | dead code; delete |
| `explosiveknockback` shield rule ("a pawn whose shield absorbed the blast is not thrown") | `mod_audit/records/batch_12.md` (Shield Generators) | still served by ShipShields/vanilla interceptors; no action |
| VEF PipeSystem, Tabula Rasa, VFE Factory | — | stay; other mods need them |
| Battlefield-capture feature | not built | the ruled feature loses its stopgap (MinifyEverything lifted turrets today); build `BATTLEFIELD_CAPTURE_BUILD_REDEPLOY` |

## 4. Too hard (or not worth it)

- **Faithful LightsOut parity** (every modded bench and enterable on standby, per-mod compat
  shims for about 20 third-party mods): **too hard** for its value. Our comp covers lights plus an
  explicit list of power-hungry fixtures. Anything not on the list stays as vanilla.
- **Chain-lightning multi-target stun (Zapper)**: needs a custom verb (the donor's
  `Verb_Zapper`, which cannot be reused under its licence). That is **not worth it**: single-target
  ion fire from existing defs gives the disable-and-take beat.
- **Minifying linked structure (walls, doors, conduits)**: needs MinifyEverything's install and
  graphic transpilers. **Too hard and unwanted.**
- **Degraded redeploy as true quality loss on turrets without `CompQuality`**: vanilla turrets
  have no quality. "Degraded" must be expressed as max-HP fraction plus the WreckedMachines grade
  (stat factors), not a quality tier. This is a design constraint, not a blocker.

## 5. Build order

1. **`CONVENIENCE_CUT_PRUNE_LEFTOVERS`** (S): delete the dead compat, patch rows and loadAfters in
   §3 so the cut leaves no false text. Do it first; it costs nothing at runtime.
2. **`SAVE_WALLS_EXCISE_MINIFIED`** (S): remove the 11 minified walls from the canonical save while
   MinifyEverything is still loaded. Back up first; use a bridge destroy or a binary-mode save edit
   with a size check.
3. **`SHIP_FIXTURES_WIDEN_MINIFY`** (S): XML allowlist plus settings toggle. This is the cheapest
   win, and the owner can strike items from the list.
4. **`IDLE_LIGHTS_BUILD_POWERDOWN`** (S–M): the comp, wired through LightLedger; ships with its
   first validation script per the debug-process rule.
5. **`BATTLEFIELD_CAPTURE_BUILD_REDEPLOY`** (M): the category minify plus the captured→degraded
   comp in WreckedMachines. This is the largest piece and the only one with owner-ruled gameplay.
6. **Turret ammo lint** (fold into 5): a selftest asserting every player-buildable turret in our
   tiers carries `CompRefuelable` with a real fuel item.
7. **`ION_TURRET_BUILD_STUNNER`** (S, optional): only after the owner says yes to a player turret.

## 6. Tickets to file (not filed; names pass `rimflow namecheck`)

| Name | Seat | Scope |
|---|---|---|
| `CONVENIENCE_CUT_PRUNE_LEFTOVERS` | FOUNDRY | §3 rows: Armoury generators (`gen_armoury_patch.py`, `gen_turret_doctrine.py`) and `About.xml` loadAfters; ResearchRetag rows; LuminousPigment LightsOut compat + prove script + validation bar + spec §8 row; `modset_builder.py` strings |
| `SAVE_WALLS_EXCISE_MINIFIED` | FOUNDRY (bridge) | 11 `MinifiedThing(Wall)` in `CANONICAL_ASHKARR_START_2026-09-12.rws` |
| `SHIP_FIXTURES_WIDEN_MINIFY` | FOUNDRY | allowlist patch in `mandrake.rm.patches` + settings; audit our own `src/` buildables lacking `minifiedDef` |
| `IDLE_LIGHTS_BUILD_POWERDOWN` | FOUNDRY | `RM_CompIdlePowerDown` per §2; explicit def list; LightLedger link |
| `BATTLEFIELD_CAPTURE_BUILD_REDEPLOY` | FOUNDRY | trap_renaissance §2b: category list, claim→uninstall path, degraded reinstall via the WreckedMachines grade |
| `ION_TURRET_BUILD_STUNNER` | BENCH (owner question first) | optional single-target ion turret in JawaIonWeapons |

## 7. GPT review disposition

(pending — GPT-6.1-sol consult, `Transient/foundry_convenience_gpt_20261010.md`)
