---
name: rimworld-savegame
description: Reading, grepping and editing a RimWorld `.rws` savegame — plain XML plus base64/raw-DEFLATE map grids of 2-byte def shortHashes. Covers src/RimMandrake/Utils/rimbench/savemap.py, why the shortHash table must come from a def dump of the SAME mod set, the fogGrid bitfield that silently corrupts on write, grepping with `<def>NAME</def>` instead of the bare defName, which regions are safe to hand-edit and which are the fragile thing-ID reference graph, backing up before any edit, and the difference between `Could not resolve cross-reference` (def loader, live mod set) and `Could not load reference to` (Scribe — the SAVE holds a dead name and no mod change fixes it). Use before reading, counting, editing or repairing a save, when a log error names a def no installed mod has, or when a bridge experiment needs undoing.
---

# Savegames (`.rws`)

A `.rws` is plain, human-readable XML — `xml.etree.ElementTree` parses a 14 MB save
in ~0.4 s, so **read with a parser, not a regex**; regex is fine only for quick
counts. The map grids inside it are binary, and that is where the danger lives.

## 1. The two error phrasings are two different systems

| Phrasing | System | Means |
|---|---|---|
| `Could not **resolve** cross-reference: No X named Y` | **def loader** | a def in a mod's XML points at something absent. A **live mod-set** problem. |
| `Could not **load** reference to X named Y` | **Scribe** (the save/load serialiser) | a **saved file** holds a name that no longer exists. Nothing to do with the current mod set. |

The second is where *"errors from mods I deleted months ago"* comes from, and **no
mod change fixes it** — the dead name is inside the file.

**The audit surface is every file RimWorld deserialises at startup**, not just
saves: `Config/Mod_*.xml` plus `Xenotypes/`, `Ideos/`, `Scenarios/`,
`PrepareLanding/`. Measured: 16 stale Scribe lines traced to two `.xtp` xenotype
presets, one line per dead gene, forever. **Saves are exempt from the startup
pass** — they are read only on load.

## 2. Grep a save with `<def>NAME</def>`, never the bare defName

`grep -c OuterRim_RebelAlliance <save>.rws` returns **1 on a world that does not
contain that faction** — the hit is the def-name **registry** entry beside a
neighbouring def, not an instance.

```bash
grep -c '<def>OuterRim_RebelAlliance</def>' save.rws    # instantiated objects only
```

**Use named controls**: check defs you know are present *and* absent in the same
run, or an empty result is a claim about your query rather than about the world.

## 3. Anatomy — what is safe to edit, and what is not

| region | edit? |
|---|---|
| `<game><scenario>` — `<name>`, `<summary>`, `<parts>` (`ScenPart_*`) | ✅ legible, low-linkage |
| pawn `<story>` (backstories, traits, appearance) and `<skills>` (12 `<li>`: `<def>`/`<level>`/`<passion>`) | ✅ this is how you hand-tune a crew |
| faction custom `<name>` | ✅ flavour only |
| faction rosters and `goodwill` relations | ⚠️ ID-linked — keep the ID map consistent |
| the **thing-ID reference graph** and raw map cell/region data | 🔴 fragile — prefer an engine route (dev-mode spawn, RimBridge, Map Designer, quest generators) |
| `<meta>` — `<modIds>`/`<modSteamIds>`/`<modNames>` | a save degrades when loaded against a different mod set; keep it in sync |

A **Thing** is any element with BOTH a `<def>` and an `<id>` direct child; `<pos>`
is `(x, 0, z)` with **origin bottom-left** — flip z for image rows.

🔴 **A wrong defName in the reference graph is unforgiving** — it can silently
corrupt or hard-fail a load. Never guess one; confirm it against the installed mod
files or the live dump.

## 4. Map grids: base64 + raw DEFLATE arrays of 2-byte shortHashes

```
<terrainGrid><topGridDeflate>          what you walk on
             <underGridDeflate>        what is beneath a constructed floor
             <foundationGridDeflate>
<roofGrid><roofsDeflate>       <snowGrid><depthGridDeflate>
```

`zlib.decompress(data, -15)` — on a 250×250 map that is exactly **125,000 bytes =
62,500 cells × 2**. `src/RimMandrake/Utils/rimbench/savemap.py` wraps it:

```python
m = SaveMap(save_path, dump_dir)
m.census()                   # defName -> cell count; the fastest way to read a map
m.paint(cells, "Gravel")     # clear_under=True by default
m.write(out_path)            # NEVER in place -- refuses to overwrite the source
roundtrip_check(save, dump)  # run this FIRST on any new save or mod set
```

**RimBridge and save-editing are complements**: the bridge does things and
structures, live; the save does the substrate — terrain, rock, water, roofs.

**`clear_under`.** RimWorld keeps a built floor in `topGrid` and the natural terrain
it was laid over in `underGrid`, so painting natural terrain into `topGrid` alone
**orphans** the buried terrain — a state the game never produces. Measured:
61,671/62,500 underGrid cells are `0`, so `0` means "nothing buried". **Pass
`clear_under=False` when painting a FLOOR** — there the buried terrain is meant to
survive, and the function cannot tell the two apart, so the caller says.

## 5. The shortHash table must come from a dump of the SAME mod set

RimWorld resolves hash collisions **at load time**, so a hash from a 3-mod dump is
not guaranteed to mean the same thing in a 570-mod game. `SaveMap` refuses to run
without a dump rather than guessing.

Offline reversal is `(ushort)(StableStringHash(name) % 65535)` — **`% 65535`, not
`65536`, not a mask**, with C#'s truncate-toward-zero `%`; Python's floor-`%` is off
by exactly 1 on negative hashes. Verified against the live dump: BiomeDef 66/66,
RoofDef 6/6, TerrainDef 1,227/1,238 (the 11 misses all +1, collision-bumped). The
dump's own `shortHash` field is ground truth — prefer it to computing.

## 6. 🔴 `fogGrid` — leave it untouched

**Do not add `fogGrid` to `savemap.py`'s `GRIDS` table.** Every other row is 2-byte
ushorts, unpacked as `'<%dH'`. `fogGridDeflate` is a **bitfield**: 7,813 bytes for
62,500 cells, `ceil(62500/8) == 7813`, **one bit per cell**.

Decoding it at 16× the wrong width **still "succeeds"** — no exception — and
re-encoding silently corrupts the fog of an otherwise healthy save. Leaving it alone
is safe by construction: never decoded, never re-encoded, passed through `write()`
untouched. The only cost is that already-explored ground stays revealed.

**Generalises:** before adding a row to a fixed-width table, divide the byte length
by the cell count and confirm the element width.

⚠️ **This section is a prohibition, not an unfinished fix, and it says why on
purpose.** Sometimes the correct output of an investigation is a
**DO-NOT-DO-THIS** — and unless the prohibition carries its reason, the next
person helpfully undoes it. Twice now the maintenance instinct has been the
defect: adding `fogGrid` "for completeness", and putting a stale line count back
into a doc that had deliberately removed it.

⚠️ **`foundationGrid` is UNIFORM across all 62,500 cells** on the map measured —
every cell the same value. Untested beyond that, and flagged for exactly that
reason: **a rule inferred from a uniform sample is how a wrong rule gets baked
in.** Do not generalise its encoding or its meaning from that sample; find a map
where it varies first.

## 7. Back up first, and never write in place

**Timestamped backup → edit → parse-validate the XML → reload-test in game.** No
exceptions. A corrupted save costs a campaign *and* a ~23–30 minute reload.
`SaveMap.write()` enforces the last part: it raises rather than overwrite its source.

## 8. The save is the real undo for a bridge experiment

Restoring terrain is **not** undoing the paint. `SetTerrain` destroys plants on a
cell whenever the new terrain cannot support them — measured: grass dies on Sand,
PackedDirt, rock and water, survives Gravel. A capture/restore that recorded only
terrain put 2,601 cells back to their original `TerrainDef`, **0 wrong**, and the
map still did not look as before.

**On a colony that matters, save before the experiment and reload to undo it** —
that restores terrain *and* everything the terrain write destroyed. Bridge-injected
content does survive the save/reload round trip.
