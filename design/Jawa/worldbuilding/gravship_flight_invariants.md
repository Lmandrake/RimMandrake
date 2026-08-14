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
| engine `SubstructureSupport` | **632.8** | live; `BG_gravEngineSupport 632.79541` |
| extender `SubstructureSupport` | **none — the stat is absent** | **live def** |
| `VGE_GravFieldAmplifier` support | **none — the stat is absent** | **live def**; the dump's +200 is a ghost |
| extender `maxDistance` | **34** | live; the settings key `BG_gravExtenderMaxDistanceFromEngine 85` reaches no def |
| extenders max | 12 | live |

⇒ **Ceiling is 632.8 and nothing in this modset raises it.** Extenders buy
**reach** (footprint radius 30), never **budget**. Reach and capacity are
different axes and only the engine carries the second.

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
