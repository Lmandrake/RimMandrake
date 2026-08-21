## spec
_not recorded in the source queue_

## verify
_not recorded in the source queue_

## criteria
_not recorded in the source queue_

## notes
**Everything is committed, pushed and deployed. The game is DOWN and the companion in
`C:\Program Files (x86)\Steam\steamapps\common\RimWorld\BridgeTools\JawaBench\` is
byte-verified against the build (md5 `04cb0977e66af0cb58d9c6f6ecf40acc`).**

🔴 **YOUR FIRST COMMAND AFTER THE LOAD:**
```
python.exe src/RimMandrake/Utils/first_light.py
```
`python.exe`, not `python3` — the bridge is on Windows loopback and WSL cannot reach it.
It runs the whole census in about a minute, changes nothing, prints one line and writes
`infrastructure/output/first_light_<date>.md`.

**Six new tools, 112 in the assembly against 106 live last session. None has run in a
live game — treat every one as a hypothesis until this load exercises it.**

| tool | why it exists |
|---|---|
| `faction_relations_get` / `_set` | nothing could read or write a relation between two NON-player factions |
| `pawnkind_audit` | generalises last night's hand finding to every kind in the stack |
| `texture_audit` | finds dead texPaths the log only reports when something tries to draw them |
| `world_settlements_import` | W9 stage 5, your 72 holdings |
| `world_features_import` | W9 stage 7, the 23 named regions |

**Two things I got wrong yesterday and corrected:**
- `weaponMoney` is a **ceiling**, not a bracket. Only `max` can empty a weapon pool; `min`
  never excludes anything. The BUILD ticket is corrected.
- The GrimTerra animals do **not** render magenta as adults. All three bad texPaths are the
  juvenile lifeStage.

**The one real risk in tomorrow's run:** `world_links_import` could never read its own
documented format — it demanded a `tile` column from an edge-shaped CSV. Fixed, untested,
and it is stage 2 of 7. If it still refuses, debug that before going further.

**Still yours alone:** the Configure Factions hand-tick pass and the `ScenarioDef`, both of
which gate a world you intend to keep. Nothing I can do moves either.

---
