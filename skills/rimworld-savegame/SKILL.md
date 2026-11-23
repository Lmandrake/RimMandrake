---
name: rimworld-savegame
description: Reading, grepping and editing a RimWorld `.rws` savegame — plain XML plus base64/raw-DEFLATE map grids of 2-byte def shortHashes. Covers src/RimMandrake/Utils/rimbench/savemap.py, why the shortHash table must come from a def dump of the SAME mod set, the fogGrid bitfield that silently corrupts on write, grepping with `<def>NAME</def>` instead of the bare defName, which regions are safe to hand-edit and which are the fragile thing-ID reference graph, backing up before any edit, and the difference between `Could not resolve cross-reference` (def loader, live mod set) and `Could not load reference to` (Scribe — the SAVE holds a dead name and no mod change fixes it). Use before reading, counting, editing or repairing a save, when a log error names a def no installed mod has, or when a bridge experiment needs undoing.
---

# Savegames (`.rws`)

A `.rws` file is plain, human-readable XML. `xml.etree.ElementTree` parses a 14 MB save in ~0.4 s. So **read a save with a
parser, not a regex**. A regex is fine only for a quick count. The map grids inside the save are binary. The danger is in
those grids.

**What you may write.** Owner, 2026-08-18: *"Please don't write to the savegame file anymore."* Nobody paints a world or a
map into a save. The live bridge is the route for that. `write()` in `src/RimMandrake/Utils/worldmap.py` raises for this
reason. On 2026-09-06 he ordered a small repair in two saves: *"You should remove the troublesome spots in
WORLDMAP_v1_original.rsw_(most recent letter available)."* Such a repair removes or corrects named entries, after a backup (§7).
For any other change of a pawn, a scenario or a faction, use the bridge, not the save file. Before you change or resave a
canonical save, read `infrastructure/state/CANONICAL_SAVE.md`. One file there is frozen, and only
the owner's word unfreezes it. A resave of any canonical save needs the owner, or the Conductor window (`CLAUDE.md` §Only
five acts stay his).

Older evidence, dates and corrected lines: [references/history.md](references/history.md).

## 1. The two error phrasings are two different systems

| Phrasing | System | Means |
|---|---|---|
| `Could not **resolve** cross-reference: No X named Y` | **def loader** | a def in the XML of a mod points at an absent def. A problem of the **live mod set**. |
| `Could not **load** reference to X named Y` | **Scribe** (RimWorld's own code that saves and loads) | a **saved file** holds a name that no longer exists. The file holds the dead name; the def that the name meant is gone. |

The second phrasing is the source of *"errors from mods I deleted months ago"*. **No mod change fixes it.** The dead name is
inside the file.

**Before you delete or rename a def that the planet uses (a BiomeDef above all), check the tiles of the live world.** Decode
the tiles; do not grep them. The `tileBiome` array of the world grid holds shortHashes (§5). So `grep -c <defName>` on the
`.rws` reads 0 while thousands of tiles point at that def. `WorldGrid(save).census()` in `src/RimMandrake/Utils/worldmap.py`
decodes the tiles of a save offline. Check each world save: the canonical saves in
`infrastructure/state/CANONICAL_SAVE.md` and the `ASHKARR_DEV_*` saves. Read the live game when the live game is newer than the save.
The dump must come from the mod set of the save (§5), and `WorldGrid(save).unresolved()` must be `[]`. An empty list alone
does not prove that the dump is right.

The paint-once rule is in `CLAUDE.md` §A biome with zero tiles is not a defect. That rule covers a tile on a wrong biome, when
the biome def exists. That rule does not cover a tile whose biome def has been deleted.

**Audit every file that RimWorld reads back at startup, not only saves.** Those files are `Config/Mod_*.xml` and the files in
`Xenotypes/`, `Ideos/`, `Scenarios/` and `PrepareLanding/`. In one measured case, two `.xtp` xenotype presets caused 16 stale
Scribe lines at each start. There was one line per dead gene. **The startup pass does not read saves.** RimWorld reads a save
only when it loads that save.

🔴 **Before you retire a mod, a dependency check of the whole active mod list is necessary but not sufficient.** The campaign
save can hold direct Scribe references. No mod-to-mod XML check sees those references. Two kinds are known:

- A `Class="Donor.SomeComp"` block on a live pawn or need.
- A bare `<meta><modIds>` entry. The `missing_mods` gate of the engine reads the entry at each load. In the game's
  own menu, that gate only warns. Through the bridge, that gate refuses the load. The option `ignoreModCompatibility: true`
  loads past that gate, for a read or a check only.

Two incidents each passed a thorough dependency census, and the save load still broke. **Check the save itself** before you
call a retirement safe.

🔴 **A mod can write its own future events into the save. Those events outlive a mod that looks inert.** In one known case,
the quest-chain framework of VEF (Vanilla
Expanded Framework) writes its future quests into `VEF.Storyteller.GameComponent_QuestChains.futureQuests`. A quest mod can
show no activity. Check that path in the `.rws` before you assume that the mod does nothing. If you retire the mod, remove
those entries when the save is written again.

## 2. Grep a save with `<def>NAME</def>`, never the bare defName

`grep -c OuterRim_RebelAlliance <save>.rws` returns **1 on a world that does not contain that faction**. The hit is the entry
in the **registry** of def names, beside a neighbouring def. The hit is not an instance of the faction.

```bash
MEASURE_ALLOW_SCAN=1 grep -c '<def>OuterRim_RebelAlliance</def>' save.rws   # instances only
```

**The blind-scan hook (`.claude/hooks/block_blind_scan.py`) refuses each `grep` of a `.rws` by default.** The override
`MEASURE_ALLOW_SCAN=1` is on that line for this reason. The override is legitimate in one case: you ask whether an exact
literal string occurs. Run that grep with `MEASURE_ALLOW_SCAN=1`. Say in your next message that you overrode the hook.

🔴 **The override does not make a count legitimate when the data is in a grid.** Biomes and terrain are 2-byte
shortHash **indices** in base64/raw-DEFLATE grids. So are the things that the game compresses
(`<compressedThingMapDeflate>`). The grids hold no text. So a grep for biome defNames returned **2** where the answer was 3 / 233 / 31. Read such data with one of these:

- the biomes of world tiles: `src/RimMandrake/Utils/worldmap.py`;
- terrain and roofs of a map: `rimbench/savemap.py` (§4);
- all of them: the live bridge.

`measure explain <save>.rws` says why a scan cannot read a save. That command is the `cli.py` of the skill
`measuring-large-artifacts`. Its `use` line names `savemap.py`. For world biomes, use `worldmap.py` instead.

**Use named controls.** In the same run, check defs that you know are present *and* defs that you know are absent. Without
the controls, an empty result tells you about your query and not about the world.

🔴 **A search without both tags also matches a LONGER defName that contains your defName.**
`guy762_ResearchKotOR_workbench` matched 9 times in a resave that no longer held that def. All 9 hits were the substring
inside `Techprint_guy762_ResearchKotOR_workbench`. That ThingDef is different and still valid. The full string
`<def>NAME</def>` cannot match a longer defName. **Always check what matched, not only whether something matched.**

More traps for this section: [references/traps.md](references/traps.md) § 2. Grep a save with `<def>NAME</def>`, never the bare defName.

## 3. Anatomy — what is safe to edit, and what is not

This table says how fragile each region is. The head of this skill says what you may write.

| region | edit? |
|---|---|
| `<game><scenario>` — `<name>`, `<summary>`, `<parts>` (`ScenPart_*`) | low risk: legible, few links to other regions |
| pawn `<story>` (backstories, traits, appearance) and `<skills>` (12 `<li>`: `<def>`/`<level>`/`<passion>`) | low risk: hand-tuning of a crew was done here |
| faction custom `<name>` | low risk: flavour only |
| faction rosters and `goodwill` relations | take care: linked by ID — keep the ID map consistent |
| the **thing-ID reference graph** and raw map cell/region data | 🔴 fragile — prefer an engine route (dev-mode spawn, RimBridge, Map Designer, quest generators) |
| `<meta>` — `<modIds>`/`<modSteamIds>`/`<modNames>` | a save degrades when a different mod set loads it; keep these lists in sync |

The **thing-ID reference graph** is every place in the save where one object names another object by its ID.

🔴 **The `loadID` of a gene is local to one save, exactly like `Faction_N`. A collision resolves silently to the wrong
object.** There is no error. When you splice a pawn into another save, its gene references resolve *successfully* to unrelated
genes of the destination. In one splice, 5 of 6 founders lost their `Wimp` trait this way. The `<sourceGene>` of the
trait pointed at a `loadID`. The destination save had used that `loadID` again for a different gene. `Player.log` said
nothing about it.

**Before you take the bridge for work on a save, check that the save can load.** That check is a 2-line `ElementTree` diff,
not a bridge call. Compare `<meta><modIds>` with `activeMods` in the live `ModsConfig.xml`. This free diff answers "can this
item be verified at all".

🔴 **`ModsConfig.xml` is not the mod set that is loaded now.** `ModsConfig.xml` names the next load. When the bridge is up,
read the loaded set with `jawa/running_mods`. Without the bridge, read `<meta><modIds>` of the newest autosave. A session from
before a reboot ran on 26 mods while `ModsConfig.xml` read 621. So "the mod is in the live list" does not prove that the
running game loaded the mod.

A **Thing** is any element with BOTH a `<def>` and an `<id>` as direct children. `<pos>` is `(x, 0, z)`, and the **origin is
bottom-left**. Flip z for the rows of an image.

🔴 **A wrong defName in the thing-ID reference graph can silently corrupt a load or make the load fail.** Never guess a
defName. Confirm it against the installed mod files or the live dump.

### 3a. Two parsing traps that produce a save that "has no data"

🔴 **The `<features>` element of the canonical save is NESTED** (`<features><features><li>…`). A non-greedy regex that stops
at the FIRST `</features>` close tag returns a fragment that does not parse. Use a real XML parser and no regex. With a
regex, take the LAST close tag.

🔴 **`ET.iterparse` with `el.clear()` on every element destroys the children of a node before the `end` event of that node.**
One such reader returned 71 features, and each name and size was None. That result reads as "the save has no data". The
reader had already cleared the children that hold the name and the size. Clear an element only when you have read it
whole. A child must stay until the handler of its parent has run.

More traps for this section: [references/traps.md](references/traps.md) § 3a. Two parsing traps that produce a save that "has no data".

## 4. Map grids: base64 + raw DEFLATE arrays of 2-byte shortHashes

```
<terrainGrid><topGridDeflate>          what you walk on
             <underGridDeflate>        what is beneath a constructed floor
             <foundationGridDeflate>   the foundation (for example gravship substructure)
<roofGrid><roofsDeflate>               roofs, as RoofDef shortHashes
```

`zlib.decompress(data, -15)` returns the array. On a 250×250 map the array is exactly **125,000 bytes = 62,500 cells × 2**.
`src/RimMandrake/Utils/rimbench/savemap.py` wraps the decoding:

```python
m = SaveMap(save_path, dump_dir)
m.census()                   # defName -> cell count; the fastest way to read a map
m.paint(cells, "Gravel")     # do not use (owner, 2026-08-18); clear_under=True by default
m.write(out_path)            # do not use for a painted map; NEVER in place -- refuses to overwrite the source
roundtrip_check(save, dump)  # run this FIRST on any new save or mod set
```

`<snowGrid><depthGridDeflate>` is also 2 bytes per cell, but it holds **no shortHash**. Each value is a snow depth. `savemap.py`
does not read that grid, on purpose.

**Use `SaveMap` to read.** Do not paint a map with it (the ruling at the head of this skill). The bridge paints things
and structures live. The bridge also paints terrain (`jawa/set_terrain_batch`) and roofs (`jawa/set_roof_batch`).

**`clear_under` in `SaveMap.paint`.** RimWorld keeps a built floor in `topGrid`. RimWorld keeps the natural terrain below that
floor in `underGrid`. If you paint natural terrain into `topGrid` alone, you **orphan** the buried terrain. The game never produces
that state. In `underGrid`, `0` means "nothing buried" (61,671/62,500 cells were `0` in one measured save). **Pass
`clear_under=False` when you paint a FLOOR.** There, the buried terrain must survive. The function cannot tell a floor from
natural terrain. So the caller says which one it is.

## 5. The shortHash table must come from a dump of the SAME mod set

A shortHash is a 2-byte number that stands for one def of one def type. RimWorld resolves hash collisions **at load time**. So
a hash from a 3-mod dump can mean a different def in a 570-mod game. `SaveMap` refuses to run without a dump. `SaveMap` does
not compare the mod set of the dump with the mod set of the save. You make that comparison.

To compute a hash offline, use `(ushort)(StableStringHash(name) % 65535)`. The divisor is **`% 65535`, not `65536`, and not a
mask**. C# `%` truncates toward zero. The floor `%` of Python is off by exactly 1 on a negative hash. After a collision, the game adds 1 until
the number is free. So a computed hash can differ from the true hash. The `shortHash` field of the
dump is the ground truth. Prefer that field to a computed hash.

⚠️ **The same mod SET is necessary, not sufficient. `modCount` says nothing about the CONTENT of the defs.**
`validate_save_artifact.py` resolves names against the newest DefDump capture. The `modCount` in the manifest of that capture
can match the live mod set. The capture can still hold defNames from before a rename. The game that wrote it had loaded its
defs before the edit. In one measured case, the tool reported 6 genes missing from a `.xtp` xenotype preset. The
genes were correct on disk. The capture was stale, not the preset. Before you trust the verdict of a validator, compare the
timestamp of the capture with the rename commit. The `modCount` alone is not enough.

More traps for this section: [references/traps.md](references/traps.md) § 5. The shortHash table must come from a dump of the SAME mod set.

## 6. 🔴 `fogGrid` — leave it untouched

**Do not add `fogGrid` to the `GRIDS` table of `savemap.py`.** Each other row of that table is 2-byte ushorts, unpacked as
`'<%dH'`. `fogGridDeflate` is a **bitfield**: 7,813 bytes for 62,500 cells, `ceil(62500/8) == 7813`, **one bit per cell**.

If you decode the fog at 16× the wrong width, the decode **still "succeeds"**, with no exception. Then the encode silently
corrupts the fog of a healthy save. When nobody touches the grid, nothing can go wrong: `write()` passes the grid through,
never decoded and never encoded again. The only cost is that explored ground stays revealed.

**The general rule:** before you add a row to a fixed-width table, divide the byte length by the cell count. Confirm the width
of one element. Confirm also what the element means: the snow grid (§4) has the right width and the wrong content.

⚠️ **This section is a prohibition, not an unfinished fix.** Sometimes the correct output of an investigation is a
**DO-NOT-DO-THIS**. Write the reason with the prohibition. Without the reason, the next person undoes it to be helpful. Twice,
the wish to tidy was itself the defect. One person added `fogGrid` "for completeness". Another put a stale line count back
into a doc that had removed the count on purpose.

⚠️ **Do not infer a rule from a grid that holds one value.** In the first save that we measured, all 62,500 cells
of `foundationGrid` held one value. **A rule from such a sample is how a wrong rule gets baked in.** Find a map where the grid varies first.
The canonical save `ASHKARR_DEV_START_2026-10-20_PARITY_QUIET_R3.rws` is such a map: 59,225 cells hold `0` and 3,275 hold `Substructure`. What an edit of `foundationGrid`
does is untested.

## 7. Back up first, and never write in place

**Make a timestamped backup → edit → parse the XML to validate it → reload the save in the game.** There are no exceptions. A
corrupted save costs a campaign *and* a cold load (`rimworld-load-round` has the times). `SaveMap.write()` enforces the last
words of the heading: it raises an error before it overwrites its source.

🔴 **Never open a `.rws` in Python TEXT mode (`"r"`/`"w"`) for a raw edit.** Text mode silently turns each CRLF into LF across
the WHOLE file. A planned 50-byte string replace on a 21 MB save made the file ~500 KB smaller. That save still parses and
still loads, because XML and Scribe do not read line endings. The only sign is a size change that is far too large for the edit. **Always open a savegame `"rb"`/`"wb"` and use `bytes.replace()`.** Before you trust the output, assert its size against
the size that the string lengths predict. (`SaveMap` itself reads and writes in text mode. So this size check does not hold
for a file that `SaveMap.write()` made.)

## 8. The save is the real undo for a bridge experiment

To restore terrain is **not** to undo the paint. `SetTerrain` destroys the plants on a cell when the new terrain cannot
support them. Measured: grass dies on Sand, PackedDirt, rock and water. Grass survives on Gravel. One capture and restore
recorded only terrain. That restore put 2,601 cells back to their original `TerrainDef`, **0 wrong**. The map still did not look as
before.

**On a colony that matters, save before the experiment, and reload that save to undo the experiment.** The reload restores the
terrain *and* everything that the terrain write destroyed. Content that the bridge added does survive a save and a reload.

## Census a save before removing a def or a donor

More traps for this section: [references/traps.md](references/traps.md) § Census a save before removing a def or a donor.
