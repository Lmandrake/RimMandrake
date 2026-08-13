# Gravship Exporter round-trip — spec and success criteria

_CREATE, 2026-08-13. Written **before** the live test, per `V1_SCOPE.md`: the deep
gravship build is gated on this answer, and BRIDGE drives the session._

Mod: **Gravship Exporter**, `Arcjc007.GravshipExporter`, active at load 165.
Source: `https://github.com/JohnCannon87/RimworldCustomShipStart`
Workshop tree: `3576790938` (it ships its own `.git` and `README.md`).

---

## The question this answers

> Can the exporter round-trip a built ship into a file we keep in the repo?

**Yes → build the ship ONCE as a reusable artifact; the deep build is affordable.**
**No → rebuild per world; v1 scope shrinks.**

## Answered OFFLINE already — do not spend a bridge session on these

Read out of the shipped example `1.6/Defs/Advanced_Starter_Ship.xml` (4,816 lines)
and the assembly's own symbols. These are settled; the live test is only for what
follows in the next section.

| Question | Answer | Evidence |
|---|---|---|
| Is there a serialisable file format? | **Yes** — `GravshipExport.ShipLayoutDefV2`, a grid of cells | the def type in the example |
| What is in a cell? | `foundationDef`, `foundationStuff`, `terrainDef`, `terrainStuff`, and a `things` list of `defName` / `stuffDef` / `rotInteger` | ibid |
| Can it become a standalone mod we keep? | **Yes** — `ExportShipAsMod`, `Dialog_ExportModName`, and it writes `About.xml` itself | assembly symbols, README "Features" |
| Can a new game start on it? | **Yes** — `Page_ChooseGravship`, `ScenarioUsesGravshipStart` | assembly symbols |
| Are pawns or items included? | **No.** Zero pawn/item entries in the example | `grep -c "Pawn\|<items>"` = 0 |

⭐ **So the answer to the gating question is YES, established without a game.**
The reusable-artifact approach is the right one. What the live test does is
confirm it survives *this* stack and settle the one contradiction below.

---

## ⚠️ The contradiction the live test MUST settle

**The README says floors cannot be saved. The exported data says otherwise.**

> README, "Known Issues": *"You can't save floors :( The way base game RimWorlds
> spawning works for the initial Gravship you can only place one TerrainDef and
> that has to be the Substructure"*

But its own shipped example carries **204 non-null `terrainDef` cells**:

```
128  MetalTile
 38  SterileTile
 22  WoodPlankFloor
 16  CarpetMarine      <- the author's own carpets, in the file he says cannot hold them
354  foundationDef     all Substructure, with 150 terrainDef IsNull
```

Both statements can be true at once, and that is the likely reading: **terrain is
written on EXPORT and ignored on SPAWN.** The two halves are separate code paths
and the README is describing the spawn half.

**This is not a curiosity — it decides the deck plan.** If floors do not survive,
every material call in `design/Jawa/worldbuilding/ship_deck_plan.md` is decoration that will
never render, and the ship must be designed to read correctly on bare
Substructure.

---

## Success criteria — what BRIDGE must SHOW, not assert

Per `V1_SCOPE.md`'s gate: **seen**, not "the log was clean". Each row is
independently decidable; report them separately.

| # | Step | PASS looks like | FAIL looks like |
|---|---|---|---|
| 1 | Build a small test ship: gravship engine, hull, **≥1 Shelf**, an Autodoor, and **≥2 distinct floors, one of them a carpet** | it builds | — |
| 2 | Export it in-game | a named export appears; no red errors | export dialog errors, or nothing written |
| 3 | Locate the written file | ⭐ **report the ABSOLUTE PATH** — this is what tells us what to commit | nothing findable |
| 4 | Export further **as a mod** | an `About.xml` is generated beside the ship def | no mod tree |
| 5 | Start a new game choosing that ship | the ship spawns, recognisably the one built | absent, or spawns vanilla |
| 6 | 🎯 **Look at the floors** | the carpet and the second floor are **on the map** | everything is bare Substructure — README correct, spawn ignores terrain |
| 7 | Look at the Shelf | present | absent — then the "items need shelves" hint is load-bearing |

⚠️ **Item 6 is the one that changes my work.** Items 1–5 confirm the approach;
6 rewrites the deck plan if it fails. If the session is cut short, do 6.

⚠️ **Item 3 is the deliverable for the repo.** Without the path there is no
artifact to keep, and "it exported fine" is not a round-trip.

---

## Constraints already known — design to these regardless of the outcome

From the README's own "Known Issues" and "Features", all of which shape the build:

- **Pawns and items are not exported.** Confirmed against the data, not just the
  blurb. The ship ships empty.
- **Include Shelves**, possibly vanilla ones, or starting items may not spawn.
- **Rooms with no pawn in them spawn as unexplored fog.** A large authored ship
  will open half-fogged; that is cosmetic but it will look like a bug in a demo.
- **Any mod used in the ship is a hard dependency of the exported mod.** Ours is
  one stack, so this is free for us and a landmine only if we ever share it.
- **Preview screenshots must be placed by hand**; the author could not automate
  them.
- The starting platform extends around the ship, so large ships are supported
  "obviously with a limit" — **map edge is the bound, and it is untested by us.**
