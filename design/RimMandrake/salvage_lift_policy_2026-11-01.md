# What Salvage may lift: the one list

Item `SALVAGE_MINIFY_DESIGN_HAULER_OR_SCRAP`. Decides what `convenience_replacements.md` §1.3 e left open now that
Minify Everything is gone: which buildings can be lifted, minify-and-reinstall against scrap-for-yield per category,
the hauler droid's role, and one list shared with battlefield capture. Design only; the build items are in the last
section.

## The answer

Ownership of the verdict: this is a delegated design call (`delegated: game design route per category`), recorded for
the daily digest; none of it is on the `delegation_policy.md` §2 short list. It keeps every owner ruling below.

- **Three outcomes, no new verb.** A building is *lifted* (the vanilla Uninstall designation, a crate, reinstall),
  *scrapped* (the Deconstruct designation, yield through the one salvage rule) or *left alone*. Every lifted category
  can also be scrapped; the route named below is the one the design adds. The only new orders are the droid's
  right-click (built) and the Jawa disarm-and-take on an armed trap (capture build).
- **The list is rules, not defs.** Owner, 2026-08-31 (`trap_renaissance_spec.md` §2b): *"no curation sheet is needed.
  The scope is a CATEGORY, not a list."* So `design/RimMandrake/salvage_lift_policy.json` holds ordered category
  rules, first match wins, and a modded turret lands in `TURRET` with no one touching the file.
- **It only adds.** A def that declares its own `minifiedDef` keeps it. The 76 files of ours that already do, and
  `RM_CrawlerRoad_Wrecks` with its deliberate `alwaysUninstallable`, stay as authored.
- **Enemy gear is earned.** Battlefield categories need a claim first, which vanilla already refuses while hostiles
  are about. Only the droid lifts from a live site, and it pays for that with a `TakingEvent`.
- **A route must be one the engine will run.** Most ancient defs are `claimable=false`, many `deconstructible=false`
  (census column `flags`), so "after claim" was empty for `AncientTankTrap` and razor wire. Each category's `grants`
  names the building fields the pass switches on, and the selftest fails a row whose route vanilla would refuse.

## The categories

Rows are in rule order. `salvage_lift_policy.py --summary` gives the counts; the row-by-row result for all 588 Core and
DLC buildings is `design/RimMandrake/salvage_lift_census_2026-11-01.csv`.

| category | route | who lifts | what it holds |
|---|---|---|---|
| `NATURAL` | none | nobody | rock and ore |
| `SHIP_FIXTURE` | minify | any colonist | the nine fixtures of §1.3 b2, own gear, never degraded |
| `WRECKED_TIER` | minify | droid only | WreckedMachines tier 1; a colonist still may not move it (`WreckedMachines/DESIGN.md` §1), but *"a stolen wreck is low heat"* (`wrecked_machines_resurrection.md`) |
| `WRECK` | **scrap** | colonist | our wreck families; strip per `jawa_scavenge_system_design_2026-10-03.md` §2c |
| `TRAP` | minify | colonist after claim; a Jawa also disarm-and-take | every `Building_Trap*`; lifted intact |
| `TURRET` | minify, **degraded** | colonist after claim | every `Building_Turret*` that really fires, mech-cluster and ancient included |
| `FORTIFICATION` | minify | colonist after claim | sandbags, barricades, fences, gate, tank traps, razor wire, ancient barriers, and any modded Security building |
| `HAZARD_NODE` | minify | colonist after claim | unstable fuel node, explosives crate, mining charge, unstable power cell; redeployed as our hazard |
| `KIT` | minify | colonist after claim | everything already minifiable: camp gear, beds, benches, lamps |
| `STRUCTURE` | none | nobody | walls, doors, conduits, vents, gravship and ship parts (§1.3 b, §4) |
| `LOOP_ANCHOR` | none | nobody | scanners and anything of 10+ cells; leaving it behind is the loop |
| `PLACE_NOT_THING` | none | nobody | spots, graves, fires, torches |
| `HEAVY_MACHINE` | minify | **droid only** | every other buildable of up to 9 cells: refinery, crematorium, gene and mech machines, altars, cryptosleep |
| `HULK` | **scrap** | colonist | ancient vehicles and war machines; vanilla forbids deconstructing them, the pass grants it |
| `RUIN_FIXED` | none | nobody | ancient set dressing: blast doors, hatches, vents, containers, cranes, grav reactors |
| `RUIN` | **scrap** | colonist | ruin furniture, broken ancient guns |
| `UNLISTED` | none | nobody | quest, entity, archotech and mech-cluster objects; the policy changes nothing |

Why these calls, where a call was close:

- **Ruins scrap, they do not lift.** §1.3 e floated ruin furniture as liftable. A crate of ancient oven gives a Jawa
  nothing a stripped one does not, and the owner's complaint is about things that pop out ready to use. Broken guns
  (`AncientAutocannonTurret`, `AncientSecurityTurret`) are props, not turrets, so they fall here too.
- **Hulks are the heart of it, and vanilla locks them.** Ancient trucks, warwalkers and dropships are the owner's *"big,
  nasty, complex pieces of tech"*, and they are `deconstructible=false`. `HULK` opens them to stripping. What stays
  shut, `RUIN_FIXED`, is what holds a ruin or a quest together.
- **The rest of the machines stay colonist-immovable.** Giving colonists all of them would rebuild Minify Everything by
  hand, which §1.3 e forbids (*"it must not grow into a blanket allowlist"*, our own design text).
- **Linked fortifications are in** despite §4's "linked structure is too hard". That refusal is about walls and
  conduits. See the graphic note below.

## The hauler droid's role

The droid is the only way to lift what colonists cannot, and the only way to lift from a site you do not hold.

1. **Reach.** `HEAVY_MACHINE` and `WRECKED_TIER` are droid-only, as the owner's heist was designed: *"a C# gate keyed
   to the droid's job, not a global minify unlock — players without the droid still can't"*
   (`wrecked_machines_resurrection.md`). It may also take anything a colonist may lift.
2. **Live targets.** No claim and no pacified map: it works under the owner's nose and fires
   `TakingEvent(Act=Strip)`, so the perception engine decides who saw. That is its price, and is built.
3. **Carrying.** Crates are ordinary items; any hauler brings them home. If the droid goes down, the crate drops and
   either side can recover it. A colonist may carry and install a stolen crate; only the lift is gated.
4. **Not the stripper.** Wrecks are stripped by the separate strip droid of `jawa_scavenge_system_design` §5b. Per-chassis
   carry weight stays the later pass `TheftHaulerExtension` already names.

**Defect this fixes.** `FloatMenuOptionProvider_TheftHaulUninstall` gates on `building.def.Minifiable`, which was true of
everything while Minify Everything loaded. With it gone the droid can reach only what a colonist can, and the
heist's whole point has silently vanished. The fix is to give the droid classes a `minifiedDef` and take the colonist's
Uninstall away from them, because `MakeMinified` itself refuses a non-minifiable def.

## One list, one pass

`salvage_lift_policy.json` is the source. A generator emits it as a def in `mandrake.rm.patches` (game-generic, loads
for everyone); nothing else states a membership.

- **When.** A Harmony prefix on `DefGenerator.GenerateImpliedDefs_PreResolve`. It has to run there:
  `ThingDefGenerator_Buildings.ImpliedBlueprintAndFrameDefs` makes the install blueprint only `if (def.Minifiable)`, so
  a `minifiedDef` set any later yields a crate that can never be placed. Cross-references are already resolved
  (silent pass, `PlayDataLoader` line 122), so `thingClass`, `designationCategory`, `comps` and `size` can be read, and
  inheritance is already applied, which an xpath patch could not see. `def.building` can be null: the one NRE that ever
  came out of this hook point was a null `costList` entry from a broken patch of ours, so the pass must skip and log,
  never throw (`FULL_LIST_LOAD_DIAGNOSE_MINIFY_SAYS_NO`).
- **Verdict first, writes after.** The pass classifies every def as authored, keeps the verdicts, then writes. Otherwise
  its own `minifiedDef` would turn a `HEAVY_MACHINE` into `KIT` and its own loot comp a `RUIN` into `WRECK`. The game
  tests `thingClass_base` by assignability, so an oddly named subclass still lands; the census approximates by name.
- **What it writes,** for each def in a category with `adds_minified`: `minifiedDef` from `DefDatabase` (`ThingDefOf` is
  not bound yet); `thingCategories`, picked from the Buildings category matching its designation, never
  `BuildingsFurniture`, the one traders stock; `tradeability = Sellable` so that a stolen crate sells but no trader or
  reward roll creates one (`Minifiable` opens both `ThingSetMakerUtility.CanGenerate` and `TradeUtility`).
- **What consumers read.** Every def in a lift category gets the building tag `RM_Lift_<CATEGORY>` in
  `building.buildingTags`. That is the whole interface: `mandrake.rm.property` and `mandrake.rm.wreckedmachines` test a
  string, with no compile-time reference to each other or to the pass.
- **Grants.** `grants` fields are set on the def, for that category only.
- **Settings.** One toggle per lift category, defaults on. A toggle gates new lifting; it never removes the def fields,
  so turning one off cannot strand a saved crate with no install blueprint. `SHIP_FIXTURE` keeps the per-def toggle of §2.

| reader | reads | does |
|---|---|---|
| Colonist Uninstall | `RM_Lift_HEAVY_MACHINE`, `RM_Lift_WRECKED_TIER`, and any toggled-off category | refused at `Designator_Uninstall.CanDesignateThing`, the `Building.GetGizmos` reinstall button, and `WorkGiver_Uninstall`, so a leftover designation cannot run |
| `RM_TheftHaulUninstall` | `Minifiable` | unchanged; the widened set is now its reach |
| Capture comp (WreckedMachines) | `RM_Lift_TURRET` | marks and degrades, below |
| Jawa disarm-and-take | `RM_Lift_TRAP` | the verb, on armed enemy traps |
| Scrap yield | `RM_Lift_RUIN`, `RM_Lift_WRECK`, `RM_Lift_HULK` | one salvage rule, below |

## Capture, degraded

Follow `convenience_replacements.md` §7 route (i): claim, then uninstall. Vanilla `Designator_Uninstall.CanDesignateThing`
refuses any other faction's building and `DesignateThing` flips the faction, so by the time a crate exists the fact
"this was theirs" has been erased. It must therefore be recorded at the moment of the change:

- The pass adds one comp to `TURRET` defs. When such a building's faction becomes the player's from anything else,
  including none, the comp marks it **captured**, for good. `JobDriver_TheftHaulUninstall` sets the same mark before it
  minifies, because the droid never claims. A building we built never goes through that change: a finished
  Frame uses `SetFactionDirect` (`Frame.cs`, read), which the hook on `Building.SetFaction` does not see.
- The mark lives on the comp, so it survives inside `MinifiedThing.InnerThing`.
- **HP alone would be no degrade at all**: a colonist repairs it back. So the comp uses `ThingComp.GetStatFactor`
  (`StatWorker` reads it), which caps it for good: `MaxHitPoints` × 0.6 and `ShootingAccuracyTurret` × 0.8 as defaults
  (`ShotReport` reads that stat from the caster, so the building is the right target), on the WreckedMachines settings
  page, expressing the Kludged rung (§4: vanilla turrets carry no quality). HP is clamped when the mark lands.
  `MarketValue` takes the same factor.
- **Ammo-free guns.** Six vanilla turrets carry no `CompRefuelable`: `Turret_AutoMiniTurret`, `Turret_AutoChargeBlaster`,
  `Turret_AutoInferno`, `Turret_AutoMortar`, `Turret_TacticalTurret`, `Turret_AncientArmoredTurret`. Lifted as they are,
  they would delete the rearm cost (§2). A captured one holds a finite magazine, 60 shots by default, counted per shot
  on a successful `TryCastShot` (a burst is several) and saved on the comp; spent, it holds fire, sells at a tenth
  through the same factor, and is only scrap. The turret lint (§5 step 6) must cover this.

## Scrap, and the rust that pays nothing

Scrap uses Deconstruct, through the one yield function of `SALVAGE_YIELD_UNIFY_THREE_RULES_TODAY`. Nearly every `RUIN`
and `HULK` def carries no cost at all (`hasCost` in the census), so a plain deconstruct gives nothing. Each needs a
loot source. `RM_CompProperties_SalvageLoot` already does exactly that, and already has the salvager context; patch it
onto `RUIN` at a low tier and `HULK` at a high one, and when the salvage pieces of the scavenging design land, the tier
swaps to pieces with no change to this list. It pays once, on the Deconstruct destroy, and neither category can be
lifted and rebuilt, so there is no farming loop; the §2d provenance flag stands for pieces.

## The linked graphic

Sandbags, barricades and fences are linked. `MinifiedThing.Graphic` only calls `GetCopy` on a multi-cell thing, and
`Graphic_Linked` has its own `MatSingle`, so a 1×1 crate may simply draw one atlas tile. That revises §7's inference
that it may error each frame, but nobody has looked. The pass item proves it on a quicktest, spawning each of the three
minified; if it is wrong, the fix is a small postfix on `GraphicUtility.ExtractInnerGraphicFor` returning
`Graphic_Linked.SubGraphic`, which is a public property.

## Review

Naive judge: GPT, 2026-11-01, ten findings. Taken: droid path marks capture; toggles gate lifting; verdicts before
writes; assignability and precedence; eligibility grants (the census confirmed it); refusal at the WorkGiver; a named
accuracy stat and an HP clamp; per-shot magazine; spent-turret price. Declined: its claim that salvage provenance
launders through a claim, which holds for pieces and not for this list, since nothing on a scrap route reinstalls.

## What this does not decide

- Live proofs: reinstall of a non-buildable def rests on one vanilla precedent (`WaspDroneTrap`: no designation, has
  `minifiedDef`). The pass item's first validation script must install an `AncientTankTrap` and an `AncientFuelNode`.
- Our own `src/` buildings: the same rules run on them, in the audit `SHIP_FIXTURES_WIDEN_MINIFY` owes. This census
  is vanilla only, because a modded row needs the load order.

## Build order

| item | scope |
|---|---|
| `LIFT_PASS_BUILD_ONE_LIST` | generator, the def, the pass, tags, tradeability, settings, the linked-graphic quicktest, the colonist refusal for droid classes |
| `SHIP_FIXTURES_WIDEN_MINIFY` | `SHIP_FIXTURE` through that pass, in-wall test for `Cooler`, audit of our own buildables |
| `BATTLEFIELD_CAPTURE_BUILD_REDEPLOY` | capture comp, Kludged factors, finite magazine, Jawa disarm-and-take, turret lint |
| `THEFT_HAULER_WIDEN_MINIFY_GONE` | prove the droid reaches `HEAVY_MACHINE` and `WRECKED_TIER`, colonists do not, and the walk still passes |
| `RUIN_SCRAP_BUILD_RUST_PAYS` | loot tiers on `RUIN` and `HULK`, through the one yield rule |

`src/RimMandrake/Utils/salvage_lift_policy.py` is the reference evaluator: the pass's first validation row compares the game's tags with its `classify`.
