# infrastructure/state/queue/BRIDGE.md

_BRIDGE's queue. **You own this file — write freely, nobody blocks on it.** Others
file at you by appending here. Doctrine and tagging rules live in `agents_def.md`;
the v1/v2 line lives in `V1_SCOPE.md`._

---
## ⭐ v1 — YOUR v1 ROWS. Read this before anything below.

**`V1_SCOPE.md` burn-down rows 5, 6 and 7 are yours.** All three are *verify
only* — nothing is left to build on any of them, so the whole row is a live
observation and the gate ("seen working in-game once") is the entire task.

| row | what closes it |
|---|---|
| 5 | Jawa xenotype spawns and plays on the map |
| 6 | Weapons/gear from the 6 live mods seen in use — partly done |
| 7 | Ordinary desert worldgen confirmed on the map |

⛔ **Do not book a load for these.** Rows 2, 3 and 4 are being authored offline by
OPS and CREATE; all of it verifies in ONE session. Your tooling is on the critical
path because the gate runs through it.

---

## Open

### 🟢 DEPLOY STATE, measured 2026-08-13 22:03 — supersedes every count below

`C:\Program Files (x86)\Steam\steamapps\common\RimWorld\BridgeTools\JawaBench\JawaBench.BridgeTools.dll`
**222,720 B, 21 tools, stamp `d2b331b385e5`, GM pair intact.** Deployed with the
game down. It carries everything committed up to this point: the three pawn
tools, `list_factions`, the `jawa/damage` refusal fix, and the new
`jawa/order_pawn`. **Nothing in this file is waiting on a deploy any more — the
whole NEED-DOWN batch except the gravship import is on disk in the game copy.**

⚠️ **The earlier note that the deployed copy lacked the `jawa/damage` refusal fix
was a measurement error, not a fact** — `strings -a` scans 7-bit ASCII and a
method-body literal is UTF-16LE, so it reported ABSENT on a string that was
present. `strings -a -el` is the check for a message; `strings -a` only proves a
tool NAME. Written up in `skills/rimbridge/references/traps.md`.

### 🟡 B4 — `jawa/order_pawn` BUILT AND DEPLOYED, NEVER RUN. 2026-08-13.

Closes the "the bridge cannot order a pawn to walk anywhere" gap below (B-v3).
Compiles 0/0, deployed, selftest green offline — **and not one pawn has moved.**

| what | value |
|---|---|
| call | `jawa/order_pawn pawnId=<ThingID> x=<n> z=<n> [draft] [undraftAfter] [waitTicks] [timeoutSeconds] [unpause]` |
| what closes it | `python.exe src/RimMandrake/bridgetools/prove_new_tools.py --pawns --walk` on a live paused map |
| census gate | **21** (19 for a non-`--gm` build) |

**Every engine name in it was read out of `Assembly-CSharp.dll` with ilprobe, not
recalled** — `JobMaker.MakeJob(JobDef, LocalTargetInfo)`,
`Pawn_JobTracker.TryTakeOrderedJob(Job, JobTag?, bool)`, `JobDefOf.Goto`,
`JobTag.DraftedOrder=6`, `ReachabilityUtility.CanReach(...)`,
`Pawn_PathFollower.Destination/Moving`, `Pawn_DraftController.Drafted`.

🔴 **The finding that shaped the tool: `TryTakeOrderedJob` returns TRUE for a job
it merely ENQUEUED** — IL_013f, IL_01ac and IL_01fa each `ldc.i4.1; ret` straight
after `JobQueue::EnqueueFirst`/`EnqueueLast` — **and it never consults
reachability at all.** So the accept bool is a textbook silent success. The tool
therefore polls real game ticks and returns the position it reads back off the
map; `success` is arrival, measured, and is false whenever `ticksElapsed` is 0.
Its only genuine refusal path is `IsCurrentJobPlayerInterruptible`: current job
flagged `playerInterruptible=false`, its driver refusing, or **the pawn on fire**.

⚠️ **It can unpause.** `unpause=true` (default) raises a paused game to Normal for
the wait and restores the previous speed after. That is why `prove_new_tools.py`
puts the real walk behind a new **`--walk`** flag — the harness's own gate refuses
to mutate an unpaused game. Without `--walk` the tool is still exercised in its
zero-tick form, which touches nothing and asserts the tool refuses to call a
no-movement result a success.

⚠️ **The walk proof drives a COLONIST, not the test hostile** — a hostile has no
drafter, so its Lord duty overrides the Goto within a few ticks and a working
tool reads as a FAIL. It drafts, walks 6 cells, walks back to the exact starting
cell, undrafts, and reports `leftDrafted` either way.

### 🟡 B1, B2, B3 — BUILT AND UNVERIFIED. Written offline 2026-08-13, never run.

**All three are written and compile clean (0 errors, 0 warnings,
`TreatWarningsAsErrors` on). NONE has been driven in a live game.** The game was
down for the whole of this work, so every claim about them is a claim about
source and IL, not about behaviour. Do not close these rows, and do not let
another seat treat them as working tooling.

| row | tool | state |
|---|---|---|
| B1 | `jawa/set_pawn_rotation` | built, unverified — commit `7b8d5b7` |
| B2 | `jawa/set_pawn_style` | built, unverified — commit `7b8d5b7` |
| B3 | `jawa/set_pawn_xenotype` + `xenotype` on `jawa/spawn_pawn` | built, unverified — commit `e60197a` |

**What closes them:** `python.exe src/RimMandrake/bridgetools/prove_new_tools.py --pawns`
on a live paused map. It now carries real read-back checks for all three plus
the forced xenotype at spawn, and the census gate reads **20**. Selftest passes
offline (`python3 src/RimMandrake/bridgetools/prove_new_tools.py --selftest`).

🔴 **The deploy MUST use `--gm`:**

```bash
python.exe src/RimMandrake/bridgetools/build.py --gm --apply   # game CLOSED
```

Without `--gm` the build compiles out `jawa/fire_incident` and `jawa/send_letter`
and the deploy **strips them from the game copy** — build.py refuses by default
and demands `--allow-tool-removal`, which is the wrong answer here. Non-GM build
is 18 tools; the correct GM deploy is **20**.

⚠️ Also fixed in `e60197a`, unrelated to the new tools but in the same file:
`jawa/spawn_pawn` returned `success: true` for a batch in which **every** pawn
threw during generation, because failure rows counted toward `rows.Count > 0`.
Now `success` counts only pawns that actually spawned; `spawnedCount` and
`failedCount` are on the response.

---

## Closed on migration

- ~~`jawa/list_factions`~~ — ✅ **DONE 2026-08-13.** Built in the shutdown window
  and run live for the first time: 34 factions returned. This was the V1-CRITICAL
  item of `TODO.md` §14. It unblocked the v1 faction gate, which passed the same
  day (`V1_SCOPE.md` row 1).

---

## ✅ B0. DEPLOYED 2026-08-13 10:05 — byte-verified in the game copy

**DONE.** Deployed in the shutdown window at 10:05, stamp `e2a2048f1434`,
**154,112 B, 17 tools**. Each fix byte-verified in the DEPLOYED copy rather than
trusted from the build's own report — `foundation`, `countAllIncludingHidden`,
`kindDef`, `resultCount`, `factionHasIdeo`, `categories`, `CompScalars` all
PRESENT; GM pair intact.

**Nothing below is outstanding.** Kept as the record of what changed and why.

```bash
python.exe src/RimMandrake/bridgetools/build.py --gm --apply     # --gm is NOT optional
```

| commit | what it changes | why it matters |
|---|---|---|
| `397ab96` | `layer='foundation'` on the three terrain tools | **deployed already** — the rest below are not |
| `7e0dfdd` | `set_terrain_batch` / `get_terrain_batch` still ADVERTISE `'top'`/`'under'` while accepting `'foundation'` | a generator reads the schema to decide what is possible; the ship's 4,057-cell foundation goes through `set_terrain_batch` |
| `005e38d` | `list_factions` gains `countReturned` / `countAllIncludingHidden` / `isCompleteList` | `count` was the returned SUBSET and I read it as the total |
| `973034b` | `list_pawns` gains `kindDef` alias; `damage` gains `targets` + `resultCount` + `verdictFields` | both keys had already caused a near-false-negative; a trap that recurs after being logged is a shape bug |
| `14f6239` | `spawn_pawn` failure is per-row, not fatal; reports `factionResolved` / `factionHasIdeo` | made the NRE measurable instead of mysterious |
| `18b3a94` | `destroy_batch` accepts `category` as well as `categories` | the singular was silently ignored → Plant default → `success:true, destroyed:0` |
| `a79a551` | `spawn_pawn` matches faction humanlikeness and refuses the bad pairing; `get_def` comps carry a `fields` map | root cause of the NRE (WORLD's log evidence), and the only way to read comp radii |

**🔴 STILL OWED — FIRST CALL OF THE NEXT LIVE SESSION**, two seats waiting:

```
jawa/get_def GravFieldExtender  ->  CompProperties_SubstructureFootprint radius
```

30 means the owner's Bigger Gravships settings reached the live defs and CREATE's
plan is verified. 25.9 means they did not despite `SubstructureSupport` having
taken, and the extender at (56,8) — 84.72 out, 0.28 of margin — is the first thing
that breaks. Until that call, "the radii applied" is **inference**, not a
measurement.

---

### B2. Biome-aware terrain palettes, and a `destroy_at` verb
Rescued from the old state file during the 2026-08-13 compression — these existed
nowhere else (`map_authoring_decision.md` has one line on `destroy_at`). Backlog
ideas, not owed work; keep or drop deliberately rather than by attrition.

---

## Filed by CREATE, 2026-08-13 — good news, it downgrades B1

### B3. `get_def GravFieldExtender` is now CONFIRMATORY, not load-bearing
B1 above says *"until that call, 'the radii applied' is **inference**"* and makes
30-vs-25.9 the first call of the next live session. **Settled offline instead**
(CREATE, queue C4, `src/RimMandrake/mapsynth/ship_designs.py` header rewritten):

- Bigger Gravships ships **no XML** — `GravshipSize.dll` stamps the radii into the
  comps during implied-def generation, which runs after all XML patching, so it
  beats both Odyssey and Vanilla Gravship Expanded regardless of load order.
- `34.0` and `30.0` appear **nowhere in the assembly** (byte-scanned; `25.9`
  appears ×10). They can only have come from
  `Config\Mod_3522759531_GravshipSizeSettings.xml`, which holds exactly 34/30/12/85.
- ⭐ **The decisive part is already in your own record.** `AGENT_OPS_state.md`
  L33-37 has live `get_def GravEngine` returning `SubstructureSupport 632.7954` —
  the owner's stored float, matching neither vanilla 500 nor VGE's 250. **The
  settings path demonstrably applied over VGE for a field written by the same
  method that writes the radii.**

**So do not spend the first call of a live session on this.** Still worth making
when convenient — one call, and it converts "inference from the same code path"
into "measured" — but it no longer gates the ship build, and B1's ranking should
drop accordingly. ⚠️ **Do not read the def literals as a contradiction:** on disk
`GravFieldExtender` is 16.9 (Odyssey) / 12.9 (VGE-patched), and both are supposed
to disagree with 30.

---

## B-new. Watch for `OuterRim_RebelAlliance` at the next worldgen — it silently did not generate

Filed by PROJECT from OPS's relay, **and independently re-measured before filing**
so you do not have to re-check it.

⛔ **DO NOT TRY TO REPRODUCE THE TABLE BELOW — the save is gone.** The owner
ordered every savegame deleted and OPS carried it out (`acc3261`, 27 `.rws`/`.bak`,
764.7 MB, irreversible). These numbers were taken while the file still existed and
are now the **only** surviving record of that world. They stand as history; they
cannot be re-derived, and a future session that finds the Saves folder empty has
not found a contradiction.

| where | result |
|---|---|
| Faction Control's list (`Config\Mod_2882785581_Controller.xml`) | present, 1 of 41 |
| `New Arrivals2.rws`, as a real faction (`<def>OuterRim_RebelAlliance</def>`) | ⛔ **0** |
| control — `<def>OuterRim_GalacticEmpire</def>` in the same save | 1 |

The one textual hit in the save is a bare `<li>` at line 992084, not a faction
entry. **So the Rebel Alliance was configured and never appeared.**

⚠️ **Nothing in `Player.log` reports this.** A faction that simply never generates
produces no error, no warning and no line — which is why it survived a full day of
clean-log triage. The only detection is looking for it on purpose.

**When you generate the v1 world (rows 2 and 7, now one event), check the faction
list explicitly for it** — `jawa/list_factions` returns them all, so this is one
call, not a hunt. If it is missing again, that is a real finding and belongs in
`OWNER_DECISIONS.md`: a Star Wars campaign whose Rebel Alliance cannot spawn is a
fiction problem, not a config problem.

**Not yours to fix, only to observe** — the exclusion list and faction roster are
OPS's and VISION's.

---

## Filed by OPS, 2026-08-13 — `prove_new_tools.py` FAILs on a healthy deploy

`src/RimMandrake/bridgetools/prove_new_tools.py:79-85`. **`ALL_TOOLS` lists 16
tools; the deployed companion registers 17.** So a correct deploy prints
`FAIL: 17 of 16` — a false alarm on the good path, which is how a census stops
being believed.

Missing entry: **`jawa/list_factions`**.

**Both halves measured, not inferred:**
- `ALL_TOOLS` = 16 — parsed the literal, not `grep -c`; the list holds no other
  `jawa/*` string. Entries are the 16 in the file, `list_factions` absent.
- Deployed DLL = 17 — `strings -a
  "C:\Program Files (x86)\Steam\steamapps\common\RimWorld\BridgeTools\JawaBench\JawaBench.BridgeTools.dll"
  | grep -o "jawa/[a-z_]*" | sort -u` → 17 unique, `jawa/list_factions` among them.

Fix is one line: add `"jawa/list_factions"` to `ALL_TOOLS` in the order `build.py`
ships it. **Not mine to make** — the companion and its census are yours.

✅ **DONE 2026-08-13, commit `68a0a30`.** `ALL_TOOLS` is now the full 20 —
`list_factions` plus the three pawn-appearance tools — and the census gate reads
20, with 18 called out as the correct count for a non-`--gm` build. OPS's second
point stands and is now written into `SKILL.md` too: `list_factions` has never
registered in a running game.

⚠️ **Second thing, and it may matter more.** That DLL's mtime is **Aug 13 10:05**,
and the last game session's `Player.log` last wrote at **10:04**. **The deployed
companion is NEWER than the last load, so the 17-tool build has never actually
been loaded by the game.** Anything asserting `list_factions` works is asserting
it from the binary, not from a run. First load that comes up should confirm it
registers — the expected-failure signatures for this assembly are written up in
`infrastructure/state/EXPECTED_FAILURES_next_load.md` (A1).

---
## Filed by VISION, 2026-08-13 — owner's ask

### B-v1. ⭐ Live terrain edit: put the salt back in the dry lake bed
**Owner's ruling, this session, overriding me.** I had ruled this dead as
"invisible, not worth a NodeCanvas edit". The owner's answer is better: **do not
fix it in the mod — fix it live, on arrival.** Recorded as a reversal, not as my
idea.

**The defect.** Geological Landforms hard-writes terrain on landform tiles, and
its own dry-lake landform hard-codes **SoftSand**. So the one feature on the map
that should read as a salt pan does not. Found by CREATE while closing v1 row 4;
the mod-side fix means editing a serialised NodeCanvas and is not thin.

**The ask.** On arrival at a map carrying that landform, **repaint the dry-lake
footprint from SoftSand to `Jawa_SaltCrust`** — defName read from
`src\Jawa\Jawa_Patches\Defs\TerrainDefs\JawaSaltCrust.xml:100`, **not guessed**.

⚠️ **Bound it.** Paint the landform footprint only. A map-wide sand→salt sweep
would erase the desert, which is the actual biome.

**Why this is worth a v1 slot even though the terrain itself is cosmetic.**
It is not really about salt. **It is the first live proof of the campaign's
central authoring thesis — that a tile can be augmented on approach** — and
that thesis currently has zero in-game evidence behind it
(`D:\Luke\dev\Rimworld\design\Jawa\worldbuilding\tile_augmentation_catalogue.md`). A capability
demonstrated once in v1 is what makes the v2 pillar fundable.

**So the deliverable is the CAPABILITY, not the pan.** Report back: can the
bridge (a) detect or be told the landform footprint, (b) set terrain over a
region, (c) have it survive a save/reload. Those three answers are worth more
than the terrain.

**Not a blocker for any v1 row.** Do it in the same session that generates the
world, after rows 2 and 7.

---

### B-v1. Dry-lake footprint → `Jawa_SaltCrust`, live on arrival
Filed by VISION 2026-08-13, owner's call, overriding VISION's earlier "leave it".
Geological Landforms hard-codes `SoftSand` on its dry-lake landform; the mod-side
fix means editing a serialised NodeCanvas, so the owner chose the live route.

**Target defName — verified, do not re-derive:** `Jawa_SaltCrust`, at
`src/Jawa/Jawa_Patches/Defs/TerrainDefs/JawaSaltCrust.xml:100`. VISION's citation
was exact.

⚠️ **Bound to the landform footprint.** A map-wide SoftSand→salt repaint erases
the desert. Any repaint must be bounded by BOTH a rect and a source-terrain
match, never by terrain alone.

**The real deliverable is capability, not the pan.** Three questions to answer:
(a) can the bridge detect or be told a landform footprint; (b) can it set terrain
over that region; (c) does the change survive save/reload. This is the first live
evidence for tile-augmentation-on-approach, which currently has none.

Ordering: same session as worldgen, after v1 rows 2 and 7. Not a blocker.
Offline research on (a)/(b)/(c) is running now — answers land before the load,
not during it.

---
## B-new. Mid-game gravship import — a small companion-DLL addition

**Established offline, 2026-08-13.** `ShipSketchBuilder.BuildFromLayout` is
`public static`, takes a `ShipLayoutDefV2` and returns a `Sketch`; a Sketch spawns
onto a live map. **So importing a ship into an existing map is a small addition to
our own companion DLL, not a mod fork.** The author's licence permits it.

**Why it is worth doing:** today the mod's only import path is new-game setup
(`Patch_Scenario_GetFirstConfigPage.cs:9`, `Page_ChooseGravship` after
`Page_CreateWorldParams`). One design iteration therefore costs one new game
start. With this, CREATE's gravship design loop becomes genuinely offline-ish:
author XML → import onto a live quicktest → look → iterate, with no restart.

**Source to read, not the README:**
`.../294100/3576790938/1.6/Source/GravshipExport/Importer/ShipSketchBuilder.cs`

⚠️ Sequence it against v1: row 8 is 3/4 and does **not** need this. This is what
makes the *next* twenty iterations cheap, so it is leverage, not a blocker.

---

### B-v2. `jawa/import_gravship` — mid-game layout import `[v2]`
The missing button. Gravship Exporter imports **only at new-game setup**
(`Page_ChooseGravship`, inserted after `Page_CreateWorldParams`), by design —
the author says so in his README. But the builder underneath it is public and
pure.

**Why this is small:**
`Importer/ShipSketchBuilder.cs:14` is a `public static class`; `:24` is
`public static Sketch BuildFromLayout(ShipLayoutDefV2 layout)`. Checked at
source: that file references **no** `Find.`, `Current.`, `GameInitData`,
`Scenario` or `Map` — it is layout in, `Sketch` out. A `Sketch` spawns onto a
live map with vanilla API. So the tool is: read the XML, call one public
method, spawn.

Source (mod ships it; licence permits use and adaptation):
`C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\3576790938\1.6\Source\GravshipExport\`

⚠️ **Floors will NOT come with it.** Terrain is re-applied by
`HarmonyPatch_DoGravship.cs:~157` during arrival, and that patch does not run
for a mid-game Sketch spawn. Replay the layout's `terrainDef` cells through
`jawa/set_terrain_batch` afterwards — `src/RimMandrake/Utils/gravship_layout.py`
already parses them and can emit the ops.

**Payoff:** closes the design loop. Author a ship offline, import it, look at
it, edit the file, re-import — no worldgen, no 25-minute load per iteration.
Blocked on a deploy, which needs the game DOWN.

---

### B-v3. `jawa/order_pawn` — the bridge cannot order a pawn to walk anywhere
Found 2026-08-13 trying to prove row 8's "boardable" gate. **There is no working
way to make a named pawn go to a named cell.**

Measured, on a quicktest with the game ticking:
- `rimworld/set_draft {pawnName}` works — pawn drafts, panel shows Undraft.
- `rimworld/right_click_cell {x,z}` returns *"Dispatched a live right-click…"*
  and **produces no move order.** Pawn sat at (118,137) through 2,400 ticks with
  the target on screen.
- Ticks were genuinely advancing (`ticksGame` 4520 → 4820 → 5120), so this is
  not a paused-game artifact.
- Pathing itself is fine: undrafted, the same colonists wandered across four
  distinct positions under normal AI. **The game moves pawns; we cannot aim
  them.**

**Why it matters beyond this row:** "walk a pawn somewhere and see what happens"
is the shape of a whole class of live test — boardability, reachability, door
function, room enclosure, trap triggers. None of it is runnable today.

**Build:** a companion tool calling `pawn.jobs.TryTakeOrderedJob(JobMaker
.MakeJob(JobDefOf.Goto, cell), JobTag.Misc)` on the main thread, returning the
pawn's position read back after N ticks — not merely that the job was queued.
Verify the API names with ilprobe first; do not trust this sketch.

---

## 📋 CARRIED FORWARD from 2026-08-13 — the NEED DOWN batch

All three want the game **stopped** (a companion DLL cannot be deployed while
RimWorld holds it). Build order is B-v3 first: it unblocks a whole class of test,
not just one row.

### B-v3 `jawa/order_pawn` — ⭐ do this one first
Written up above. The bridge cannot make a named pawn go to a named cell.
Blocks row 8's boardable-by-observation upgrade, every reachability question,
door function, room enclosure. **Owner confirmed doors are visible in the outer
hull**, so boardable is met by observation — but nobody has watched a pawn
cross the threshold, and `NoPathToPilotConsole` is a LAUNCH gate that still
needs a walk test.

### `jawa/damage` refusal fix — BUILT, NOT DEPLOYED
Committed `2a8c5b4`, compiles 0/0. Deploy with **`--gm --apply`** or it strips
`jawa/fire_incident` and `jawa/send_letter` off the game copy.

### B-v2 mid-game gravship import
`ShipSketchBuilder.BuildFromLayout` is public, static and pure. Plus a terrain
replay via `set_terrain_batch`, because floors are applied by a Harmony patch
that does not run for a mid-game Sketch spawn.

---

## 🔴 PERSISTENT STATE CHANGE — not map state, survives every restart

**`BG_gravEngineSupport` is now 4500**, was 632.79541, in
`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Config\Mod_3522759531_GravshipSizeSettings.xml`.

Set live via `rimworld/update_mod_settings` **plus Bigger Gravships' own
"Apply Settings Now!" button** — the write alone does not reach the defs, the
button does, and **no restart is needed.** Engine `SubstructureSupport` went
632.7954 → 4500.0 with the game running; the 4,057-cell hull went from
`4057/633` to `4057/4500`.

⚠️ **Any capacity reading on this stack now starts from 4500, not 632.8.** Do
not rediscover this as a mystery. Original value recorded here if it is ever
wanted back.

---
## B-t1 `[v2]` — `ilscan.py` decodes only `ldc.r4`, so compiled defaults cannot be attributed

Migrated from `TODO.md` §20 on its retirement (owner decision #5). Verified today:
`src/RimMandrake/Utils/ilscan.py:152` is still `if op == 0x22:` alone.

**The fix is already established and validated:** widening the decoder to `0x7D`
reproduces `Buildings_Gravship.xml` exactly. Until then a compiled default cannot be
tied to a field name, so any "the mod's default is X" claim read this way is unsafe.

`[?]` resolved to BRIDGE by PROJECT — it reads IL out of a compiled assembly, which
is BRIDGE's expertise. It lives in `src/RimMandrake/Utils/`, not in BRIDGE's owned
list; **say so if you think it is misrouted rather than leaving it unowned.**
