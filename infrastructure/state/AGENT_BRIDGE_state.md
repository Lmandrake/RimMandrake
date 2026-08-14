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

## State of the world at handoff, 2026-08-14 — SECOND session, post-load

**This section replaces the pre-load handoff. That one was written with the game
DOWN and none of it survives: the game came up, a map existed, and the bridge was
driven.**

| | |
|---|---|
| bridge | **taken, worked, RELEASED.** Free at handoff. Released with a one-line broadcast per the owner's new ruling |
| game | **PLAYABLE** at handoff — a *quicktest* map, not a campaign. `programState: Playing`, **PAUSED** |
| 🔴 left on the map | quest **"The Claim" NotYetAccepted** · **HOSTILE KotOR droid at (0,0) — KEEP PAUSED** · `SmallThruster` (45,131) · `AV_DogSled` (60,120) · roof (40,126) 4×4 already restored to `None` |
| companion — GAME COPY | **26 tools, md5 `55b2362`.** Unchanged; no deploy was possible with the game up |
| companion — REPO BUILD | 🔴 **30 tools, md5 `d7e7c6c1`, UNDEPLOYED.** This is S8 and it is the whole next down-window — exact command in `queue/BRIDGE.md` |
| repo | clean of my paths, `origin/main` 0 ahead |
| 🔴 persistent | **`BG_gravEngineSupport` = 4500.** Unchanged. Do not rediscover this as a mystery |

## 🔴 The first three things the next BRIDGE must know

1. **RUN S8 FIRST when the game is down** — `build.py --gm --apply`. **`--gm` is not
   optional**; without it two working tools are stripped. Full command, verification
   and what each tool unblocks: `queue/BRIDGE.md`, top entry.
2. **The four "deployed and uncalled" tools from the last handoff have now RUN.**
   `list_things`, `clear_ui`, `get_defs`, `fire_quest` and the `spawn_batch`
   vehicle route are all live-proven. That warning is retired — do not re-issue it.
3. **The game-state doctrine changed mid-session.** `agents_def.md` rules 1a/1b and
   the TAKEN/RELEASED pair are **deleted**; state is measured and stamped with
   `src/RimMandrake/Utils/gamestate.py`, and the word "live" is retired.
   ⚠️ **Releasing still requires a one-line broadcast to the seats** — the owner
   ruled this after a release that only wrote a state file went unnoticed.

## Owed

- **CREATE**: the sealed-room thruster test (L8) once `inspect_string` deploys.
  **Send raw inspect lines, not a verdict.**
- **VISION**: 3 remaining sea seeds, and the `OuterRim_GalacticEmpire`
  `permanentEnemy` check that may deflate their V7 upgrade. Both in the queue.

## Blocked — wants the game DOWN

**S8, and nothing else.** Every live item that could be collected on a bare
quicktest was collected. What remains needs either the deploy (L3, L8, sea reqs
3+4) or a map with the gravship on it (L1/L2 as measurements).

## Closed this session, with evidence

- **Companion 22 → 26 tools**, three deploys, game verified down each time.
  `jawa/list_things` (a ThingID for a non-pawn — nothing could produce one),
  `jawa/clear_ui`, `jawa/get_defs`, `jawa/fire_quest`.
- **`spawn_batch` can spawn a `Vehicles.VehicleDef`** via `VehicleSpawner` by
  reflection. `AV_DogSled`'s NRE was this tool, not the art: `VehiclePawn`'s ctor
  leaves `vehiclePather`/`ignition`/`drawTracker` null and `SpawnSetup` calls all
  three. Read from `Vehicles.dll` with ilprobe.
- **The harness bug that killed two live rows** — `ok()`/`absent()` were called
  and never defined. Both now exist, `absent()` refuses to score a failed call as
  a missing def, and `load_session --selftest` runs real items against a scripted
  session instead of testing only the ledger plumbing.
- **The census gate stopped being a literal** — derived from `EXPECTED_TOOLS`,
  and `prove_new_tools` reads the deployed DLL. Three files disagreed about that
  number on 08-13.

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
- `AV_DogSled` is a `Vehicles.VehicleDef`, not a ThingDef. ✅ **Answered 2026-08-14:**
  `spawn_thing`/`ThingMaker` genuinely cannot construct it, and `spawn_batch` now
  routes vehicles through `Vehicles.VehicleSpawner.SpawnVehicleRandomized` by
  reflection. Its brown is a def patch (`DogSledTint_Brown.xml`,
  `graphicData/color` → `(99,65,24)`) ⇒ a grey sled means the patch, not the art.
- `VGE_Astronaut` has two lifeStages sharing one maskPath and only the double-r
  `Astrronaut` files were typo'd ⇒ **shoot an adult**, or you pass on art that was
  never broken.
- The plan's C12 double-ship warning is **stale and names the wrong mod** — the real
  overlap was `MissingArtFixes`, all seven pairs md5-identical, now inactive. **Load
  order is not the suspect if rows 4 or 7 look wrong.**
- **581 mods active as of 2026-08-13 23:18, ten art-fix mods live**; the plan's table
  covers eight. `phytokinbarkheadfix` and `kotorbandoliernorthfix` are active and
  deployed but untabled.
