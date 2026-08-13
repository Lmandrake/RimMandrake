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
(`design\Jawa\worldbuilding\tile_augmentation_catalogue.md`). A capability
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
