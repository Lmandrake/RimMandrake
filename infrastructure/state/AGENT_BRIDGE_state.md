# AGENT_BRIDGE_state.md — where BRIDGE is

**Cross-session address:** recompute on resume, before anything else:

```bash
echo "**Cross-session address:** \`uds:/run/user/1000/cc-socks/$PPID.sock\`"
```

⚠️ **Peers must address this seat as `AGENT BRIDGE`, not `BRIDGE`.** A send to
the bare name bounces, and OPS lost a warning that way on 2026-08-13 — the
message was never delivered and a map was discarded without it.

Identity: `infrastructure/agents/BRIDGE.md`, injected automatically.
Queue: `infrastructure/state/queue/BRIDGE.md`.

---

## State of the world at handoff, 2026-08-13 ~21:00

| | |
|---|---|
| bridge | **RELEASED** — announced to PROJECT, OPS, CREATE |
| game | UP, but **the map I worked is GONE** — OPS regenerated a fresh quicktest on owner's instruction. Current map is stock, `ticksGame 1`, paused |
| left on the map | **nothing of mine survives.** The gravship, its doors, the salt-crust patch, the Jawa-converted Alex — all discarded with the old map. Nothing lost: the ship is exported and committed |
| camera zoom extension | **OFF** — I re-disabled it, `rootSize 14`. It was mine and it caused a false "graphics corrupted" alarm |
| 🔴 persistent, survives restarts | **`BG_gravEngineSupport` = 4500** (was 632.79541). See the queue file — do not rediscover this as a mystery |

## Owed

Nothing to any seat. All three peers had a release message with full state.

## Blocked

**Everything below wants the game DOWN** — a companion DLL cannot be deployed
while RimWorld holds it.

| item | what |
|---|---|
| **B-v3** `jawa/order_pawn` | ⭐ build first. The bridge cannot make a pawn walk anywhere; blocks reachability, doors, room enclosure, and the `NoPathToPilotConsole` launch gate |
| `jawa/damage` refusal fix | built, `2a8c5b4`, 0 errors. Deploy **`--gm --apply`** or two GM tools are stripped |
| **B-v2** mid-game import | `ShipSketchBuilder.BuildFromLayout` + a terrain replay |

## Closed today, with evidence

- v1 gravship **built, exported, doored, committed** — `6909ecb` `a12fe3a` `9684fb6`.
  31 steps, 4,057 foundation + 4,057 floor cells, ~1,052 things, ~1.4 s of calls.
- **`execute_ship_plan.py`** — `ship_bridge.json` had never been executed by anything.
- **`gravship-layout` skill + library** — a ship can now be authored as a FILE, no
  map, no game. Round-trips clean on three fixtures.
- Three pawn tools proven on first execution; `spawn_pawn` silent-success fixed.
- **Capacity is a live setting**, not a ceiling: 632.8 → 4500 with the game
  running, via BG's "Apply Settings Now!". Removes a ~25 min load from every
  future ship-size experiment.
- Extender zero explained: **BG rebuilds `CompProperties_GravshipFacility` and
  drops its `statOffsets`**, so extenders link and give nothing.
- `Jawa_SaltCrust` PASS. `ilprobe` repaired (`il.py`, `enumdump.py`) and extended
  (`xref.py` fixed to scan all six field opcodes, `sigdump.py` banked).

## Three corrections I made against myself — read these before trusting a negative

1. **A truncated print is not an absence.** Twice I reported "the field is not
   there" when my `[:260]` had cut it off, or when I had searched `statBases`
   and the value lives in `statOffsets`. Both conclusions happened to survive.
   That is luck, not method.
2. **A def dump is what shipped, not what the game holds.** Three claims died on
   this today — the three Jawa xenotypes, the extender's 500, the amplifier's
   200. For a runtime value, read the runtime.
3. **I diagnosed a zoom artifact as texture corruption** and told the owner to
   restart, wrongly implicating a peer's file prune. The discriminator was free:
   the red frame was 0.49 MB against 2.4–3.7 MB, and it healed on a legal zoom.

---

## Pre-flight corrections for `CREATE_TEST_PLAN.md` — verified offline, do not re-derive

Moved out of my queue 2026-08-14 during its 690→150 compaction. These change what
you TYPE at a live console; the plan itself is still the script.

- 🔴 **Part 3b's diagnostic string has NO BASIS.** `ShipChunk_Mech` needs **`Light`**
  (inherited from `BuildingBase`), not `Heavy`; and `BrokenSubstructure` supplies
  Light/Medium/Heavy/Walkable/Substructure — its `<affordances>` has no
  `Inherit="False"`, so it MERGES with `FloorBase`'s. Requirement and supply are met
  on either layer ⇒ if props are missing, look at prefab placement, blocked cells or
  `spotMustBeStandable` — **not** the affordance.
- ⚠️ **Scrapfields is NOT biome-gated.** `Patches\JawaResource_Scrapfields.xml:56-59`
  adds the GenStep to `MapGeneratorDef[Base_Player]` with no biome filter, contrary
  to the plan. A scrapfield on a non-desert quicktest is not a bug.
- 🔴 **`jawa/set_terrain` takes `terrainDef`, not `def`.** The plan's line 118 is
  wrong and the bridge drops unknown params silently — as written it costs live
  minutes for nothing.
- 🔴 **`ToolBelt` does not exist** (zero hits on disk). It is **`VAEA_Apparel_ToolBelt`**,
  `...\294100\2521176396\1.6\Defs\ThingDefs_Misc\Apparel_Utility.xml:531`. It and
  Survival Tools' rival are both labelled *"tool belt"* ⇒ **spawn by defName.**
- 🔴 **The four RR research kits are APPAREL.** The fix replaces `wornGraphicPath`
  (`Apparel_FieldKits.xml:62`); the ground `texPath` (`:51`) is one directionless
  PNG, so a kit on the ground exercises **none** of the fixed art — it must be
  **WORN by a pawn facing east**. There is no apparel tool on the bridge: the only
  route is `rimworld/select_pawn` then `Actions\Wear apparel (selected)…`, which
  works on **player colonists only** ⇒ spawn the wearer with `faction=player`.
- `AV_DogSled` is a `Vehicles.VehicleDef`, not a ThingDef, so `spawn_thing` may not
  construct it; its brown is a def patch (`DogSledTint_Brown.xml`, `graphicData/color`
  → `(99,65,24)`) ⇒ a grey sled means the patch, not the art.
- `VGE_Astronaut` has two lifeStages sharing one maskPath and only the double-r
  `Astrronaut` files were typo'd ⇒ **shoot an adult**, or you pass on art that was
  never broken.
- The plan's C12 double-ship warning is **stale and names the wrong mod** — the real
  overlap was `MissingArtFixes`, all seven pairs md5-identical, now inactive. **Load
  order is not the suspect if rows 4 or 7 look wrong.**
- **581 mods active as of 2026-08-13 23:18, ten art-fix mods live**; the plan's table
  covers eight. `phytokinbarkheadfix` and `kotorbandoliernorthfix` are active and
  deployed but untabled.
