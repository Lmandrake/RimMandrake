# Machine dig: colonists 2 m, machines deeper (2026-10-21)

Item: `DEEP_DIG_BUILD_DROIDS_TAKE_THE_SHOVEL` (merged: the digging machine, the self-digging droid and droids that
operate the machine are one item). Code: `src/RimMandrake/FlowWorks/Source/`. Prior design:
`natural_bodies_as_canals_design_2026-10-11.md` §9 (deep beds), PIT_DEPTH_WIDEN_TWO_METRES_TO_EIGHT (the 8 m colonist
cap this reverses for colonists).

## 1. Rulings

- Owner card 2026-10-21: *"Merge them. Droid labor / ridable machines allow digging past 2 meters."*
- Owner card 2026-10-21, clarified (decided by card): *Colonists 2 m, machines deeper.* Colonists go back to a 2 m
  dig limit; droid / mechanoid labour and ridable machines dig deeper. Reverses PIT_DEPTH_WIDEN_TWO_METRES_TO_EIGHT
  **for colonists only**: the 20 m ceiling, the dig-to order, the 3,200 × notch cost curve and lake floors are unchanged.
- Standing: every DLC is assumed (Biotech mechs are always present); every mod ships superb Mod Settings.

## 2. Who digs past 2 m

The dig job is `RM_DigCanalWorkGiver`, work type **Mining**, required capacity Manipulation (the same as vanilla's
`Mine`). So the question "who may dig deeper" only matters for pawns that can take Mining work at all. Verified from
defs on disk 2026-10-21 (Data/*/Defs and src/, not guessed):

| digger | defName (race / kind) | source | takes Mining? | machine labour? |
|---|---|---|---|---|
| Tunneler (heavy mining mech) | `Mech_Tunneler` / `Mech_Tunneler` | Biotech `Races_Mechanoids_Heavy.xml` | yes (`mechEnabledWorkTypes` Mining; vanilla's Mine work giver already accepts its power claws) | **yes**, `RaceProps.IsMechanoid` |
| other Biotech labour mechs | `Mech_Lifter`, `Mech_Constructoid`, `Mech_Fabricor`, `Mech_Agrihand`, `Mech_Cleansweeper`, `Mech_Paramedic` | Biotech | no (no Mining in `mechEnabledWorkTypes`) | would be, but never get the job |
| ancient servitor | `RM_AncientServitor` | our Scarlands | yes (Hauling, Construction, Mining, Cleaning) | **yes**, mechanoid |
| Droidworks droids (all) | e.g. `RSW_DW_Race_guy762_DroidRace_KM1MD` (KM1 mining droid) | our RimStarWars Droidworks | yes when their work tab allows it (Humanlike intelligence, `ParentName="Human"`) | **yes**, by fleshType `RSW_DW_FleshType_Droid` |
| Odyssey | no work-capable mech or ridable digger found in Odyssey defs (no `mechEnabledWorkTypes` there) | Odyssey | — | — |
| ridable machines | none that work: Vehicle Framework vehicles (DesertVehicleReskin) are `VehiclePawn`s and take no work | — | — | owed, §7 |

**Rule (one function, `RM_DigLabor.IsMachineLabour(pawn)`):** a pawn is machine labour when
1. `pawn.RaceProps.IsMechanoid` (every colony mech, vanilla or ours), or
2. its race ThingDef **or** its FleshTypeDef carries the `RimMandrake.FlowWorks.RM_MachineDigger` DefModExtension.

FlowWorks (RimMandrake tier) names no franchise def. Droidworks (RimStarWars tier) opts its droid fleshType in with a
patch guarded by `PatchOperationFindMod` on FlowWorks — an unguarded modExtension whose type is missing discards the
whole def (project trap). A future digger droid or rig pawn opts in the same way.

Not machine labour: humans, xenotypes, animals, a colonist with bionics (a bionic arm is not a machine), mechanitors
themselves.

## 3. How the cap is expressed

Three caps, all in notches (0.5 m), all Verse-free in `RM_DigDepthMath`:

| cap | default | range | meaning |
|---|---|---|---|
| colonist cap (`maxDigDepth`, kept name) | **4 = 2 m** (was 16) | 4..40 | how deep anyone who is not machine labour may cut |
| machine cap (`maxMachineDigDepth`, new) | **40 = 20 m** | 4..40 | how deep machine labour may cut; effective value is never below the colonist cap |
| ceiling `MaxDigCeiling` | 40 = 20 m | const | the deepest any dug square may hold; the load repair's clamp (unchanged) |

- `CapFor(isMachine, colonistCap, machineOn, machineCap)` = `isMachine && machineOn ? max(colonistCap, machineCap) : colonistCap`.
- `DesignationCap(colonistCap, machineOn, machineCap)` = the deepest ANYONE may dig now = `CapFor(true, …)`.
  The designator, dig-to targets, `DigToOwesWork`, `FirstCutDepthAt` and the work-giver's *stale* test read this:
  a 2 m square ordered to 6 m is valid work, only not for a colonist.
- Lowering any cap never shallows a dug square (unchanged law).
- The field name `maxDigDepth` is kept: the bridge stagers (`validation_v2.py` phase S, `site_spec.py`) set it by name,
  and RimWorld's `Scribe_Values` writes a value only when it differs from the default, so an install that never moved
  the slider simply gets the new 2 m default. An install that explicitly saved a non-default colonist cap keeps it.

## 4. Job and work-giver changes

- `RM_DigLabor` (new, Verse side): `IsMachineLabour(Pawn)`, `CapFor(Pawn)`, `DesignationCap`. The cell is not an input
  yet; the rig of §7 adds `CapFor(Pawn, IntVec3)` when it exists.
- `WorkGiver_DigCanal.HasJobOnCell`: the designation is **stale (deleted)** only against the designation cap, as
  today. New, after it: if this pawn's cap stops it (`!MayDeepen(depth, CapFor(pawn))`, or a pond-bed first cut deeper
  than its cap) → `return false` **without deleting** — a machine may still take it. `JobFailReason.Is("needs a
  machine to dig deeper than 2 m")` so the colonist's right-click explains.
- `JobDriver_DigCanal.DoEffect`: `excavation.Deepen(c, RM_DigLabor.CapFor(pawn))` — the cut itself refuses past the
  digger's cap (belt and braces: a job taken before a setting change cannot overshoot).
- `RM_MapComponent_Excavation.Deepen(c)` keeps its signature (debug action, bridge) and means the designation cap;
  `Deepen(c, cap)` is the new overload.
- Designator "Dig to": the float menu runs to the designation cap; options past the colonist cap say
  "(machines only)". Refusal text names which cap stops the square.
- No new JobDef, no new work type: a colony Tunneler already has Mining; droids have the work tab.

## 5. Mod Settings

In "Excavation and flow", under "Dig deeper" (greys with it):
- **Deepest colonist dig** — slider 2..20 m, **shipped 2 m**. Tooltip: machine labour (mechanoids, droids) may go
  deeper, see below.
- **Machines dig deeper** (`machineDigEnabled`, shipped on). Off: machines dig like colonists.
- **Deepest machine dig** — slider 2..20 m, shipped 20 m; greys with the checkbox.
All-off degrades gracefully: everyone stops at the colonist cap.

## 6. What breaks

| what | assumption | fix |
|---|---|---|
| `SelfTest/DeepDigChecks.cs` | `DefaultMaxDigDepth == 16`, settings text "shipped 8 m", source regexes for `MayDeepen(…, MaxDigDepth)` | default 4, new regexes, new CapFor/DesignationCap rows (can-fail: a colonist at 2 m is refused, a mech is not) |
| `SelfTest/DeepBedChecks.cs:260` | `FirstCutDepth(12, true, DefaultMaxDigDepth) == 13` (a 6 m bed dug by a colonist) | use the machine cap constant |
| `northstar/site_spec.py` SETTINGS | `maxDigDepth 16.0` shipped | 4.0, plus the two new settings |
| `northstar/validation_v2.py` phase S | sets 4.0 then **restores 16.0** | restore to the shipped value (4.0) |
| `northstar/live_session.py` `g_dig_depth` (B4) | a square *dug* to 8 m by bridge `dig` | the bridge dig is not a pawn: it reads the designation cap, so the 8 m readout row stands; its "a colonist digs it" note becomes "a machine digs it" |
| `review_map_coverage.py`, `review/map/COVERAGE.md` | "8 m shipped" | "2 m for colonists, 20 m for machines" |
| `scenarios/c04_wet_quarry.py` | "2 m dig refusal" DEFERRED because the code cap was 8 m | becomes a staged poke once built; "machine digging past 2 m" stays DEFERRED until a live proof (a mech must be staged) — or becomes staged if a Tunneler can be spawned by the stager |
| `scenarios/common.py` `dig2m` note | "machine dig not built" | "machine dig built; live proof owed" |
| 8 m proof holes and trap heights | staged by bridge dig, not by colonists | unaffected (bridge dig is not a colonist); any proof that waits for a **colonist** to dig past 2 m must spawn a Tunneler or set the colonist cap |

## 7. Owed (not built here)

- **A ridable digging machine.** None exists that works (Vehicle Framework vehicles take no jobs). Recommended shape,
  RimWorld-native: a buildable rig (`RM_PitExcavator`, winch-and-bucket over a pit, powered) whose operator counts
  as machine labour for cells within its reach — extension point `CapFor(Pawn, IntVec3)`. The alternative, a Vehicle
  Framework vehicle with a dig verb, is heavier and couples FlowWorks to VF. Owner's call; art owed either way.
- **A self-digging digger droid** in the franchise-free tier, if wanted beyond Tunnelers and Droidworks droids.
- **Droidworks opt-in patch** (`src/RimStarWars/Droidworks/Patches/`), guarded by FindMod; Droidworks is not FlowWorks'
  seat and this helper does not deploy.

## 8. Live proof rows owed

1. A colonist ordered "Dig to 4 m" on soil stops at 2 m; the designation stays; right-click says it needs a machine.
2. A colony Tunneler (`Mech_Tunneler`, mechanitor-controlled, Mining on) takes the same square from 2 m to 4 m.
3. A Droidworks droid (once the opt-in patch is deployed) does the same.
4. Settings: machines-off → the Tunneler stops at 2 m too; colonist cap raised to 4 m → the colonist finishes it.
5. Mod Settings page text reads "shipped 2 m" / "shipped 20 m".

## 9. GPT critique, folded in

`gpt_consult.py` (gpt-6.1-sol, 2026-10-21, 12 points). Taken:
- **(1) Scribe migration is conditional** — true: a slider moved away and back to 16 is also omitted, and one left at
  any other value keeps it. Accepted: the shipped default changes; an explicit non-default colonist cap is the player's
  choice and stands. Proof row 5 reads the live value.
- **(2) Lowering a cap cancels orders** — the stale test deletes a designation no one may dig any more (machines off,
  machine cap lowered). That is today's behaviour for a lowered cap and stays: an order nobody can fill is cancelled,
  not parked. Re-enabling does not resurrect it.
- **(3) A refused cut must not lose the order** — vanilla `JobDriver_AffectFloor` deletes the designation after every
  cut, and the finish action re-adds only after a landed cut. Built: a cut refused at the pawn's cap (setting changed
  mid-job) re-adds the designation when someone may still dig it, so a machine can finish.
- **(7) Refusal text from the effective limits** — built: "needs machine labour to dig past <colonist cap>" only when
  the machine cap is deeper; otherwise the plain cap text.
- **(8/9) IsMechanoid is flesh, not ownership; Mining needs a staging recipe** — ownership is the work scanner's
  (only colony pawns scan work); `RM_MachineDigger` covers custom mechanical races. Proof row 2 stages a Tunneler
  under a mechanitor, in Work mode, Mining enabled.
- **(11) Machine slider shows a false limit** — built: the label shows the effective value (never below the colonist cap).
- **(12) Evidence** — §8 rows are pawn-driven; the bridge-dig 8 m readout row (B4) is a readout check, not machine-dig
  evidence, and is not cited as such.
Not taken / owed:
- **(6) HasJobOnCell deletes** — already guarded: `PotentialWorkCellsGlobal` returns a copy (the comment there records
  the "collection modified" fix). Left as is.
- **(10) An order awaiting a machine is invisible** — owed: an inspect-string line "awaiting machine labour" on the
  designated cell (`MACHINE_DIG_SHOW_AWAITING_MACHINE`, not filed here; folded into the live proof row 1).
- **(4/5) Targets and pond beds** — already covered: `ClampTarget`/`DigToOwesWork` stop at the target, and the
  designator rejects a bed whose first cut passes the designation cap; the work giver now also checks the first cut
  against the pawn's cap.
