## spec
The Lua structure template engine (`src/RimMandrake/Utils/rimplace/`, spec
`design/Jawa/bridge/STRUCTURE_TEMPLATE_ENGINE_SPEC.md` §10) has **never placed a single
cell in a live game.** Everything proven so far is offline and stops at the bridge call
boundary:

MEASURED 2026-08-23 by CHECK, all offline:
- `rimplace selftest` — 23/23 pass (sandbox escapes refused, out-of-footprint refused,
  undersized footprint REFUSED rather than silently shrunk)
- `rimplace lint dwelling` at 1, 2 and 3 rooms — 0 findings
- `rimplace verify dwelling` vs the live def dump — 11 distinct defNames, 11 found, 0 missing
- `rimplace calls dwelling --rect 0,0,18,10` — 11 bridge calls / 67 build ops:
  `jawa/set_terrain_batch` x2, `jawa/build_batch` x7, `jawa/set_roof_batch`, `jawa/map_commit` last
- all four tools are declared in `JawaBenchMapTools.cs` / `JawaBenchTerrainTools.cs` and the
  deployed companion `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\BridgeTools\JawaBench\JawaBench.BridgeTools.dll`
  is dated 2026-08-22 21:49, NEWER than both sources ⇒ present in the running binary

⛔ **None of that is evidence about the game.** A compiled call list is not a placed wall.

⚠️ The dwelling template's palette is INVENTED PLACEHOLDER — it builds Jawa huts from
`WoodLog`. That is open decision #1 in the spec (§11) and is NOT this item's problem: this
item asks whether the mechanism works, not whether the materials are right. Do not stop the
run over the palette; report it and continue.

## verify
Game UP with a map, bridge held by CHECK. Build the shipped dwelling at a clear rect and
read every result back OUT OF THE ENGINE — never from the call's own `success`.

```
cd /mnt/d/Luke/dev/Rimworld/src/RimMandrake/Utils
P=~/.local/venvs/rimlua/bin/python
$P -m rimplace verify dwelling            # cheap, FIRST: a wrong defName costs a load
$P -m rimplace calls  dwelling --rect <x>,<y>,18,10 --rooms 3 --occupants 4
```
Then issue those calls in order, `jawa/map_commit` LAST, and read back.

## criteria
🔴 The four in `STRUCTURE_TEMPLATE_ENGINE_SPEC.md` §10. Report each with its number, not a verdict:

1. **The rooms classify.** Build 3 rooms, read `Room.Role` back per room. Expect
   `Bedroom`/`Barracks`, `DiningRoom`, `Storeroom` ⇒ the game agrees it is a house.
2. **The shell holds temperature.** Build the nursery variant on a hot tile, run time forward,
   read room temperature. **Must be <= 32 C.** No offline check can ever prove this.
3. **Nothing was silently refused.** `placed == cellsRequested`, `refused[]` empty or explained.
   🪤 This is the one that has burned us: a 6x6 stockpile took 11 of 36 cells and reported success.
4. **The plan and the map agree.** Re-read EVERY placed cell and diff against the BuildPlan.
   `success: true` from `build_batch` is not evidence; the read-back is.

✅ A FAIL on any of the four is a full result — it is what tells BUILD which call lies.
⚠️ If the game goes down mid-run, record what was measured and mark the rest UNMEASURED.
Rounding an unrun check to "pass" is the worst outcome available here.
