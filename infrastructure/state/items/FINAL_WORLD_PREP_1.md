## spec
🔴 **OWNER, 2026-08-21: "If B55 is trying to actually build the final savegame, we don't
seem ready for that yet. Abort and refile final worldprep."** B55 is blocked on this item.

**B55 assumed a finished planet and there isn't one yet.** Measured the same morning,
before the abort:

| save | size | `<maps>` | what it is |
|---|---|---|---|
| `WORLDMAP_gen.rws` | 4.0 MB | **no** | world-only — the KEEPER shape |
| `WORLDMAP_gen2.rws` | 12.6 MB | **yes** | a landed game, NOT the keeper |

🔑 `WORLD_REDRAFT_PROCEDURE_1` settles which is which: *"the keeper is 5.1 MB, not the
19.7 MB a map-carrying save weighs."* ⇒ **B55 was about to author six founders into a
landed game that is not the artifact v1 ships.** That alone justified the abort.

⚠️ **And the planet may not be the painted one.** Both saves read `seedString grasshopper`
where the world docs record `lada`, so it has been remade. ⛔ A naive grep of the save
CANNOT settle whether the paint is in it — world biomes are stored as indices into a
compressed grid, so counting defName occurrences measures a lookup table, not tiles. The
instrument is `jawa/world_stats`' biome histogram compared against
`world/ASHKARR_WORLDMAP_tiles.csv`, and that is bridge work.

### The gate — every row must be TRUE before B55 may start
Each is owned elsewhere; this item does not do them, it refuses to let the campaign start
begin until they are done.

| # | precondition | owner | state at filing |
|---|---|---|---|
| 1 | The 21,872-tile paint is imported and the owner has LOOKED at his planet — `W9` | CHECK | `doing` |
| 2 | The Scald counts as water — `THE_SCALD_LOST_ITS_WATER_1`, 312 tiles short | CHECK | `proposed` |
| 3 | Painting under a live colony is understood — `PAINT_UNDER_MAP_DESTROYS_GAME_1` | CHECK | `proposed` |
| 4 | `jawa/world_stats`' biome histogram matches the tiles CSV, on the save that will ship | CHECK | not filed |
| 5 | The keeper save is backed up into `world/` — it is gitignored by `*.rws` and needs `git add -f` | any | see procedure step 8 |
| 6 | The twelve dice-named factions are renamed | CHECK | procedure step 6 |

🔑 **Row 4 is the one nobody has an item for and it is the cheapest to get wrong.** If the
shipping save is an unpainted regeneration, every hour spent on the campaign start is spent
on the wrong planet, and nothing announces it — the world loads fine and looks like a world.

⛔ **Do not "prepare" by editing a save.** `PAINT_UNDER_MAP_DESTROYS_GAME_1` records that
painting under a live colony destroyed the game state, measured. The order is: finish the
world FIRST, land SECOND, build the start THIRD. B55 is the third step and it was reached
out of order.

✅ **What B55 already has, and none of it is wasted** — verified 2026-08-21 and reproducible:
- `Gravship_v1.xml`, 1,992,426 bytes
- `SCENARIO_SPEC.md`, 332 lines, carrying the six founders
- step (b)'s batch regenerates exactly: 88×135 grid, 4,057 populated cells →
  **303 foundation rect ops + 355 terrain rect ops**, engine expected at (45,92).
  ⚠️ foundation layer FIRST — `SetFoundation` is refused silently on any cell already
  carrying a floor, and there is no retrofit.

## verify
All six rows above are true, each against its own item's evidence, and row 4 has a pasted
`jawa/world_stats` histogram beside the CSV counts it is being compared to.

## criteria
The save that will ship is identified by name, carries the painted planet, has no map, and
is backed up in `world/`. Only then does B55 unblock.

## notes
Filed by BUILD on the owner's abort. B55 is blocked ON this item rather than dropped —
its spec, its inputs and its measured terrain batch are all still correct and still wanted;
they were simply reached before the world was ready.
