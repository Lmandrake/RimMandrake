# gravship_flight_invariants.md — what a gravship must satisfy to fly

_CREATE, 2026-08-13. Assembled for BRIDGE's gravship-XML tooling and for the
eventual gravship-creation skill. **A tool that writes ships must enforce these,
because the game enforces most of them at LAUNCH — long after the point where a
mistake is cheap to fix.**_

---

## 🔴 Rule zero — three sources, and only one of them is the game

This document was nearly wrong because of this, so it goes first.

| source | tells you | trust for |
|---|---|---|
| **live `jawa/get_def` on the running game** | what the game actually holds after every mod's startup code | **everything. This wins.** |
| **`DefDump/*.json`** | what shipped in XML after patching | structure, names, and nothing that a mod's C# can restamp |
| **wiki / forums** | vanilla behaviour and the failure modes players hit | *symptoms* and *what to test*, never a number |

⚠️ **Measured today:** the def dump says `GravFieldExtender` carries
`SubstructureSupport 500`. **The live def has no such stat at all.** I reported
the 500 as "confirmed" off the dump and was wrong. The same trap had already bitten
another seat on three xenotypes the same morning. **Never quote a dump for a
runtime value.**

---

## 1. The launch refusal list — this IS the validator spec

Ludeon's own Odyssey keyed strings. Official, exact, complete:

```
CannotLaunchNoEngine        "no grav engine"
CannotLaunchNoSubstructure  "no substructure"
CannotLaunchDisconnected    "not connected to grav engine"
CannotLaunchNoThrusters     "no unblocked functioning thrusters"
CannotLaunchNotEnoughFuel   "not enough fuel"
CannotLaunchOnCooldown      "engine cooldown: {0}"
NoPathToPilotConsole        "No path to pilot console"
PilotConsoleInaccessible    "Pilot console is not accessible from gravship"
NoPathToGravship            "No path to gravship"
```

✅ **Doors: DONE and in the artifact.** Two cut into the **outer** hull — which
was the real risk, since a door in an interior partition photographs identically
and leaves the ship sealed. Both are in the exported layout, so every future
import carries them; a sealed hull was a defect in the design, not in one
instance.
⏳ **But the gate is still UNPROVEN.** A door existing is not a path. Nobody has
yet walked a pawn to the pilot console's interaction cell, and that — not the
door — is what `NoPathToPilotConsole` actually tests.

🔴 **The last three make PATHING a launch requirement.** A sealed hull does not
merely fail "boardable" — **it cannot fly**. A pilot must be able to walk from
outside, through a door, to the console's interaction tile. This is the single
invariant most likely to be missed by a tool that thinks in tiles rather than in
routes.

---

## 2. Required components — three, and the game names them

`GravshipComponentTypeDef` carries `requiredForLaunch`. Exactly **three** are
true in this modset:

| component type | true? | provided by |
|---|---|---|
| **Thruster** | ✅ | `SmallThruster`, `LargeThruster` |
| **FuelStorage** | ✅ | `ChemfuelTank`, `LargeChemfuelTank` |
| **Controls** | ✅ | `PilotConsole` (`maxSimultaneous` 1, `maxDistance` 200, links to `GravEngine` only) |
| SignalJammer, PowerCell | ❌ | optional |
| `VGE_OxygenGenerator`, `VGE_Heatsink`, `VGE_CopilotControls` | ❌ | all three VGE additions are optional |

⇒ **A hull with none of these builds, reports connected, photographs perfectly,
and refuses to lift.** That was exactly our state when this was written.

⚠️ **The engine's own `GravshipRange` is 0. ALL range comes from thrusters** —
+10 per small, +16 per large. So a thruster-less ship is not a short-range ship,
it is a ship that cannot go anywhere. Thrusters are the propulsion *and* the
map budget, not a formality.

⚠️ **Launch is an Ideology RITUAL, and the ritual needs a co-pilot interaction
cell** offset from the pilot's. One report has a statue on that cell stalling the
launch silently and forever. **Leave clearance on both sides of the console** —
a validator that only checks the console's own footprint will pass this.

---

## 3. The grav engine

- **One per ship. Two DISABLE each other** — measured live: spawning a second
  engine gave *"Grav engine disabled: Multiple grav engines present"* and two
  readouts, `4057/633` and `0/633`. Removing it restored the first. **Not
  additive — mutually destructive.**
- **It needs substructure UNDER ITSELF.** The #1 player-reported failure, ~5
  independent threads: every tile renders red and the counter reads `0/500` until
  the engine itself is on substructure. One report says all **9** tiles of the
  3×3 footprint are required — *unsettled, verify*.
- **Cannot be placed under rock or mountain roof** — `SubstructureUnderRockRoof`
  *"Under rock roof"*. Ludeon shipped a fix for engines destroyed by landing
  under mountain (1.6.4528).
- Can be **uninstalled and moved**, never deconstructed.
- ⚠️ **Substructure is not buildable until a colonist has physically INSPECTED
  the engine.** Research alone does not unlock it. This bites dev-spawned engines
  hardest — which is exactly how a tool-built ship arrives.

### 🔴 THE ENGINE IS THE SHIP'S POWER PLANT — wire the components to it
**Owner's correction, 2026-08-14, and the LIVE def confirms it exactly.**
`jawa/get_def GravEngine` returns a comp the **disk def does not show**:

```
CompProperties_Power   compClass = CompPowerPlantGravEngine
                       transmitsPower = true
                       idlePowerDraw  = -1.0        (negative draw = GENERATION)
```

⇒ **the grav engine both generates power and transmits it**, so a gravship needs
no separate generator — but its components **do** need to be on a conduit network
reaching the engine. Conduit is not decoration on a ship; it is how the engine's
output gets anywhere.

🔴 **This entry exists because BRIDGE got it backwards and said so out loud.** I
grepped `Buildings_Gravship.xml` **on disk**, found no `CompProperties_Power` on
`GravEngine`, `PilotConsole`, `ChemfuelTank` or `SmallThruster`, and reported that
none of them needed power and that conduit "would have been ~200 pointless cells".
**The live def has the comp; the disk def does not.** That is Rule Zero of this
very file — *the live `jawa/get_def` wins for everything* — violated by the seat
that wrote it. **A mod restamping a def at load is invisible to any amount of XML
grepping**, and the failure is silent because the disk answer is perfectly
well-formed.

### ⏳ "Not enough fuel" on a freshly authored ship is a TIMING artefact
**Owner's observation, 2026-08-14.** A `ChemfuelTank` filled on a **paused** map
still reads *"no fuel"* at the launch check, because **no ticks have passed for
the thrusters to register it.** Let time run briefly and it clears.
⇒ **Do not treat a launch refusal on a paused, just-built ship as a defect.**
Unpause for a moment, then re-read. 📌 Generalises past fuel: a tool-built ship
arrives in a state no *played* ship is ever in — every comp's cached state is
cold, and several only refresh on their own tick. **Assert after time has run,
not at tick 0.** ⚠️ `ticksGame 1` on every read-back in an authoring session is
the tell.

## 4. Substructure

- Occupies the **foundation layer** — above natural terrain, below floors, **the
  same layer as bridges**, so it cannot coexist with one.
- Three official reasons a tile is dropped at launch: `DisconnectedSubstructure`
  *"Disconnected from grav engine"*, `SubstructureUnderRockRoof`,
  `SubstructureOutsideFootprint` *"Out of range"*.
- Connectivity is reported as **orthogonal, not diagonal** — single anecdote,
  consistent with the flood-fill reason above. **Verify before relying on it**;
  a diagonal-only join would silently orphan a whole section.
- **Over-cap tiles are dropped, and nothing documents WHICH ones.** Players see
  `662/500` with red tiles. ⇒ **A tool must never emit more substructure than the
  live cap.** Do not rely on the game to choose sensibly.

## 5. Thrusters — the geometric trap

**A thruster must STAND on substructure while its exclusion zone must contain
NO substructure.** That conflict is the single most likely defect in any
auto-generated layout.

| | building | exclusion zone | offset |
|---|---|---|---|
| `SmallThruster` | 1×2 | **1×5** | behind, `z-5` |
| `LargeThruster` | 2×2 | **2×7** | behind, `z-7` |

In-game warning, verbatim: *"Warning: Small thruster will be blocked by gravship
substructure."* Reason strings: `BlockedBySubstructure`, `ThrusterBlockedBy`,
`MustBeOutside`, `ThrusterNotConnected`, `ThrusterNotFunctional`,
`WarningThrusterInside`.

⚠️ **Unresolved and it is invariant #1 for the validator:** the wiki says
thrusters work even enclosed by walls; Ludeon's strings include `MustBeOutside`
and `WarningThrusterInside`, and players report *"all thrusters say they're
indoors"*. **The official strings are the better evidence.** Working assumption:
the exclusion zone must be an **outdoor** run, not merely an empty one. Settle in
code before shipping a validator that passes enclosed thrusters.

Exclusion zones may overlap **each other**; no thruster *building* may sit in
another's zone. Vanilla caps are 4 small / 6 large; **ours are 20 small and 10
large, read live.** ⚠️ *Engines Unlimited* patches every thruster to
`maxSimultaneous 9000` on a defName-less xpath — **and it does not survive.**
Bigger Gravships stamps 20/10 after all XML patching. Exceeding the real cap
**silently disconnects the surplus**; nothing errors.

⭐ **A second `Controls` provider is live and it is on-brand:**
`guy762_SWGravshipPilotConsole_YT1300transport` (BTD KotOR gravships, gated on
`btd.gbp.shippack.kotor.vge`, active). Same `componentTypeDef: Controls`,
`maxSimultaneous 1`, `maxDistance 200`. **Either console satisfies the launch
requirement** — so a Jawa ship can fly on a Star Wars console rather than the
vanilla one, for free.

⚠️ **`PilotConsole maxDistance` is 200, and it is the tightest link after the
extender's 34.** Our 88×135 grid has a worst-case engine-to-corner of ~102, so it
clears — **a bigger hull would not.**

## 6. Capacity, in OUR modset — measured, not vanilla

| | value | source |
|---|---|---|
| engine `SubstructureSupport` | 🔴 **4500 — the baseline CHANGED 2026-08-13** | live. Was `632.79541`; raised through Bigger Gravships' settings dial + its **"Apply Settings Now!"** button **with the game running**, no restart. **It persists.** Any future capacity reading on this stack starts from 4500, not 632.8 — a doc or a memory quoting 632.8 is now stale. |
| extender `SubstructureSupport` | **none — the stat is absent** | **live def** |
| `VGE_GravFieldAmplifier` support | **none — the stat is absent** | **live def**; the dump's +200 is a ghost |
| extender `maxDistance` | **34** | live; the settings key `BG_gravExtenderMaxDistanceFromEngine 85` reaches no def |
| extenders max | 12 | live |

🔴 **CORRECTED 2026-08-13 — the mechanism above is right about the OBSERVATION
and was wrong about the CAUSE, and the ceiling IS raisable.**

**What the compiled game does:** the cap is
`engine.GetStatValue(SubstructureSupport)` = **`statBases` PLUS
`CompAffectedByFacilities::GetStatOffset`**, which sums `CompFacility.StatOffsets`
over linked facilities that are active. **The extender's support was never in
`statBases`** — vanilla declares 250 inside `CompProperties_GravshipFacility.statOffsets`
(`Odyssey/.../Buildings_Gravship.xml`), and Bigger Gravships' live offset is
**500**. Two seats searched `statBases`, found nothing, and agreed with each
other. ⚠️ **And the live probe returns NO COMPS AT ALL for that def, so "absent
live" was a blind spot in the probe, not a fact about the game.** Nothing was
measured that could have distinguished the two.

**Tested and closed:** the leading explanation was that a dev-spawned engine
might be factionless — facilities find the engine through
`ListerBuildings::AllBuildingsColonistOfClass`, which files a building only when
`Faction == Faction.OfPlayer`. **Refuted:** the engine is already player faction
(its `Claim` gizmo is disabled, and the Claim designator refuses it as *"not
abandoned"*).

✅ **SOLVED 2026-08-13 — and it is an upstream bug with a name.**

**Bigger Gravships rebuilds `CompProperties_GravshipFacility` on the extender —
and in rebuilding it, DROPS the `statOffsets` block.** Read from the live def,
in full: the comp is present and carries `maxDistance 34.0`,
`maxSimultaneous 12`, `onlyRequiresLooseConnection true` — BG's own values,
written over vanilla's 18.9 and 6 — **and no `statOffsets` field at all**, where
vanilla `Data/Odyssey/.../Buildings_Gravship.xml` declares
`<statOffsets><SubstructureSupport>250</SubstructureSupport></statOffsets>`.

⇒ **The extender still LINKS. It simply offers nothing.** That is exactly
`4057 / 633`, and it is not a faction problem, not a range problem, and not a
probe artefact. **Reportable upstream as: "re-stamping
`CompProperties_GravshipFacility` discards `statOffsets`."**

⚠️ **How this was nearly missed twice, and it is the lesson worth keeping:** the
first two live reads reported *"no comps at all"* and *"no `SubstructureSupport`
in `statBases`"*. Both were **truncated or wrongly-scoped output reported as
absence** — one print cut at 260 characters, one search of the wrong field. **An
absence is only evidence if you can show the probe would have displayed a
presence.** The discriminator that cracked it was comparing the *shape* of a
healthy def's response against the suspect one, rather than reading either alone.

<details><summary>the observation as it stood before the cause was known</summary>

⏳ **The observation stands and is UNEXPLAINED:** 8 extenders, 4 of them
inside `maxDistance` 34, engine player-faction — capacity still read exactly the
engine's own 632.8. **Recorded as an open question, not a conclusion.**

</details>

✅ **It stopped mattering, and the fix needs no load.** `gravEngineSupport`
raised **632.8 → 4500** through the mod's settings plus its **"Apply Settings
Now!"** button, **with the game running**: the live def changed and the panel
went to **4057 / 4500**. No restart, no reload, no hull shrink.
⇒ **The ceiling is a slider, and it is adjustable live.** That is the lever,
and it is cheaper than either the XML route (dead) or a Harmony postfix.

⚠️ **Edge case from the IL, easy to trip over:** a support value of **0 or
negative means UNLIMITED**, not zero — `FloodFiller` compares the running count
with `beq`, not `>=`.

⇒ Extenders demonstrably buy **reach** (footprint radius 30). Whether they buy
**budget** is open here, whatever the vanilla IL says.

🔴 **This is almost certainly a Bigger Gravships bug, not a design fact.** Vanilla
is documented as **500 base + 250 per extender, max 6 → 2,000**, so vanilla
extenders *do* carry support. BG raises the engine and the extender count, and
its settings file has **no extender-support key at all**. Every engine-side
setting reached the live def; every extender-side one failed to.

⇒ **The practical lever is `BG_gravEngineSupport` in
`Config\Mod_3522759531_GravshipSizeSettings.xml`** — a slider. Its value,
`632.79541`, alongside `1140.60999` and `29.9015255`, is plainly a drag position
and not a chosen number.

## 7. Carried vs left behind

- Official: *"Your current map, as well as anything not on gravship substructure,
  will be permanently lost."* Destructive, no return, unless a **grav anchor**
  preserves the map.
- 🔴 `BuildingsWillBeLeftBehind` — a multi-tile building must be **entirely** on
  connected valid substructure or it is dropped **whole**. Our 3×2 console and
  2×2 thrusters are exactly that shape.
- **Floors on substructure ARE carried** — confirmed both ways: Gravship
  Exporter captures non-substructure terrain (`GravshipExporter.cs:182-184`) and
  re-applies it on arrival via `terrainGrid.SetTerrain`. The exporter README's
  "you can't save floors" is **stale**.
- Roofs are carried. Pawns left behind are listed; other-faction pawns aboard
  cost goodwill. No weight limit.

## 8. Writing the XML rather than building in-game — the sharp edges

1. **Rotation of modded content is a known defect area.** Ludeon shipped
   *"modded things with non-North default rotations not being placed incorrectly
   on gravships and prefabs"* (1.6.4566) and *"gravship rotation code not
   respecting default placing rotation of modded content"* (1.6.4528). Test one
   modded non-North-default building deliberately.
2. **Placement-time checks are bypassed.** *"Fix: Could place the gravship hull
   off of substructure"* (4535) tells you the on-substructure rule is enforced
   **when you place**. Writing XML skips that, so the tool must enforce it.
3. **Launch can HANG rather than refuse** — ~10 threads describe the ship
   half-vanishing with a dead HUD when a building cannot be despawned or
   serialised. Chain named: `WorldComponent_GravshipController.TakeoffEnded` →
   `GravshipUtility.AbandonMap`. **With several hundred mods this is our most
   likely exotic failure, and it throws rather than reporting.**
4. Missing defs in an imported ship mean the thing does not spawn, and may throw.

## 9. Open questions — settle in code before the validator ships

1. Thruster `MustBeOutside`: an outdoor-room check, or only exclusion-zone-clear?
   ⚠️ **Still open at the engine level, but NO LONGER EXPENSIVE — see §11.** Either
   answer costs one `GravshipHull` cell per small thruster, because `ThrusterBase`
   is `holdsRoof true` + `fillPercent 1` and seals the room exactly as the wall it
   replaces. This used to be written up as deciding whether the exported hull
   needed a stern re-lay. It does not.
2. Does the engine need all 9 footprint tiles on substructure, or just overlap?
3. Substructure connectivity: orthogonal only, or 8-way?
4. Over-cap: which tiles get dropped, in what order?
5. Does the exclusion rectangle include the thruster's own tiles?
6. Map-edge exclusion distance on landing (`GravshipInNoBuildArea`).
7. Does the launch-time radius check use *current* engine position? The
   "uninstall the engine to build substructure anywhere" exploit implies
   build-time and launch-time checks differ.
8. **Is the extender's `maxSimultaneous` a hard cap or display-only?** A tested
   player report flies an 8-extender ship and says the extra support counts,
   against a documented cap of 6. Moot for us — ours contribute nothing either
   way — but it decides the vanilla ceiling.
9. **The scenario-spawn path may not carry floors even though export does.** Our
   verified finding covers export → `DoGravship` arrival, where the Postfix
   restores terrain. The exporter author's "you can't save floors" is a claim
   about the **base-game initial-gravship spawner**, a different path. If a
   generated ship is ever spawned as a scenario start rather than through the
   mod's arrival patch, re-verify.

---

## 10. Why the live def is the only source — the mechanism, not just the rule

**Bigger Gravships stamps its numbers during implied-def generation, which runs
AFTER all XML patching.** It is therefore the last writer on every gravship value
in this stack. Two independent confirmations today: the radii (34/30/12) and the
thruster caps (20/10, beating Engines Unlimited's 9000 patch).

⇒ **The XML on disk is never final here, and the dump is only sometimes final.**
Read the running game.

🔴 **Therefore the XML route to changing any gravship number is DEAD.** Proven,
no load required: *Engines Unlimited* patches every thruster to
`maxSimultaneous 9000` in XML and the live def reads BG's **20 / 10**. A
`statOffsets` patch restoring the extender's lost `SubstructureSupport 250` dies
the same way — **and it is worse than a no-op, because it looks applied in every
offline check and is absent only in the live def.**

**The two routes that can work:**
1. **`BG_gravEngineSupport` in `Config\Mod_3522759531_GravshipSizeSettings.xml`** —
   a slider. Every engine-side BG setting demonstrably reaches the live def
   (632.8 and 34 are both there). No patch, no C#, nothing to validate.
2. **Our own Harmony postfix ordered after BG's prefix**, in the companion DLL.
   Changes another mod's numbers, so it needs the owner's say-so, not a seat's.

⚠️ **Three separate times in one day, offline evidence disagreed with the running
game**: three Jawa xenotypes, the extender's phantom 500, and Engines Unlimited's
9000. **For any value a mod might rewrite at startup, the XML and the dump answer
"what shipped", never "what the game holds."**

---

## 11. 🔴 THE FLIGHT RULING — CREATE, 2026-08-14. Ships UNBUILT, and that is the design.

VISION and CREATE were handed one question: *is flight v1-adjacent or
v2?* VISION is down; this is BUILD's half, measured offline, and it is
answerable without the game.

**Ruling: the flight CAPABILITY is v1. The flight HARDWARE is not, and must not
be.** The exported hull ships with no thruster, no tank and no console — and that
is correct, not an omission. The design docs already made this call and nobody
had noticed they had: `ship_deck_plan.md:224` gates it as **"Phase 4 — Fly …
Mobility earned, not given"**, and `ship_build.md:148-149` reserves zones `S`
(stern thrusters) and `U` (fuel bunkerage) by name. **Flight was designed IN and
deliberately deferred.** Building it now would spend the campaign's best
mid-game goal to satisfy a checklist.

⇒ **v1 owes the hull nothing.** What v1 owes is proof that the route the player
walks in Phase 4 is not blocked by something the hull already got wrong.

### Why this is cheap when the player does reach for it — measured

| | minimum flying config | cells | cost |
|---|---|---|---|
| Controls | **`VGE_PilotCockpit` 1×2** (not `PilotConsole` 3×2) | 2 | Steel 70, Comp 3 |
| Thruster | `SmallThruster` 1×2 | 2 | Steel 180, Comp 4 |
| Fuel | `ChemfuelTank` 2×2 | 4 | Steel 120 |
| | **total** | **8 of 4,057** | **Steel 370, Comp 7** |

⭐ **The cockpit route needs only `BasicGravtech` — 50 points, prerequisites
deleted by VGE.** The vanilla `PilotConsole` was *moved* to `StandardGravtech`
(200 pts, HiTechResearchBench) by `VanillaGravshipExpanded/1.6/Patches/PilotConsole.xml`.
**Do not write "the console gates flight" into any doc** — the cheap Controls
provider is a different building on a cheaper research.

**Range is entirely thrusters.** `GravEngine`'s `GravshipRange` statBase is **0**;
each small thruster is **+10** world tiles, each large **+16**. Ship size does not
change any required COUNT — all three requirements are "≥1".

**Fuel is not the constraint.** VGE replaces both tanks' `CompProperties_Refuelable`
with a PipeSystem resource store: **250 astrofuel** small, **750** large, burned at
**5/tile, minimum 25 a launch**. One small tank carries 50 tiles of fuel against one
thruster's 10 tiles of reach. ⚠️ Therefore `BG_chemFuelTankSize 1140.61` in the BG
settings file **targets a comp VGE deleted** — unverified whether it lands on
anything. Do not quote it.

### 🔴 CORRECTED 2026-08-15 — the old branch pair was wrong BOTH WAYS

This subsection used to pose open question **§9.1** — *must a thruster's exclusion
run be OUTDOOR, or merely substructure-free?* — as a live question with two
branches, and to call it the one flight question worth spending a live minute on.
**Both branches were wrong, and the question does not need a live minute.**

**What the export actually holds:** zero thrusters, zero tanks, zero consoles.
That part was right and stands.

**The format has NO roof field.** Roofs are not stored and were never exported.
🔴 **They are DERIVED — regenerated at import by the mod's own algorithm**,
`Patch_Sketch_GetSuggestedRoofCells_Postfix.cs:45-85`: a flood-fill from every
non-roof-holding cell, discarding any region that touches the hull's edge and
roofing everything that does not. Re-running that algorithm over the exported
hull yields **4,049 of 4,057 substructure cells roofed — every standable cell
indoors.**

⚠️ **That figure is DERIVED, not OBSERVED.** It is the mod's own code re-run
offline, not a roof map read out of a running game. It is exactly as right as the
algorithm is, and no righter. Do not quote it as a live measurement.

⇒ **Why the old "substructure-free: fine, nothing to change" branch was wrong.**
Every standable cell being indoors means OUTDOOR is not satisfiable anywhere on
this deck by doing nothing. "Nothing to change" could never have been the answer.

⇒ **Why the old "must be outdoor: re-lay the stern" branch was wrong, and this is
the expensive error.** There is **NO stern re-lay**. `ThrusterBase` is
`holdsRoof true` · `fillPercent 1` · `passability Impassable` — read from
`Data\Odyssey\Defs\ThingDefs_Buildings\Buildings_Gravship.xml` — so a thruster
**seals the room exactly as the wall it replaces did**. The cost is
**ONE `GravshipHull` cell per small thruster, two per large.** You swap a wall
cell for a thruster and the enclosure is unchanged.

**Nine sites exist at x41–49, z131/132.** The aft strip at (x,133) is off-deck.

⇒ **The hull is NOT wrong, and it was never at risk.** Nothing about Phase 4 is
blocked, and no deck change is owed now. What this section previously called a
deadline was an artefact of believing roofs were absent because the file has no
field for them.

### Not determinable offline — do not let these be quoted as known

`Building_GravEngine.FuelPerTile`'s own getter (C#, read live) · whether BG's tank
dial survives VGE's comp replacement · `BG_maxThrustersLarge` (absent from the
settings file; 10 is from the DLL default) · whether the two `Door` things in 780
hull segments actually give a pawn a path to the console's interaction cell —
which is the standing `NoPathToPilotConsole` item, and **a door is not a path**.
