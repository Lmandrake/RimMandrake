> 🧹 **PRUNED 2026-08-24 01:4x on the owner's order — "clean out all stale NEXT_RELOAD files
> immediately".** Every block whose only item IDs had already closed, dropped or been superseded
> was removed; blocks naming still-live work were kept verbatim. **Nothing is lost — the full
> previous text is the parent of commit `ec0b5a61` in git.** ⚠️ A block here is a DUPLICATE of a ledger
> item; when the two disagree, the ledger is right. Live IDs kept in this file: `ANCIENT_SCATTERBOW_TAG_SEVER_1`.
> ⚠️ **RE-AUDITED 2026-08-26 by CHECK against the ledger.** `C40` closed that day, so this line was
> already stale. §5 BATCH B is **deleted** — all eight of its IDs (C37 C38 C39 C40 C41 C42
> VEHICLE_IDENTITY_TEXT_PASS_1 VEHICLE_SPRITE_ARTEFACT_CLEANUP_1) are closed or dropped and none is
> live. §20 keeps its block, but `ORDERS_DESIGNATORS_ENUMERATE_ZERO_1` inside it is closed.
> ⚠️ `W3` `W4` `W5` appear nowhere in the ledger at all — pre-ledger legacy, unverifiable from here.

## 🔄 HANDOFF — CHECK, 2026-08-26 16:3x, agent rebooting. ⏳ TRANSIENT: delete this block once read.

**Game is UP and MEASURED** (`./game` reads RUNNING, ledger UP). **Bridge RELEASED by CHECK** — take
it before driving. Companion is live at **166 tools**, `build 70b3b117`, `modSet 582/317a3860`.

⚠️ **The loaded map is a THROWAWAY quicktest and it has been used hard.** A `Crashlanded` colony on
world tile **18393**, and by me: ~60 spawned pawns, a `rimplace` dwelling at `100,200,18,10`, two
growing zones, three allowed areas, and **most of its wildlife killed** by a −66 °C tile edit that
has since been restored (tile is back at 14.7229729 °C, committed). ⛔ Nothing on it is kept and no
population count on it means anything. Discard it freely.

**The first five minutes below are SPENT** — steps 1–6 all ran. Their results are in
`infrastructure/state/evidence/`: `live_test_2026-08-26_postload_CHECK.md`,
`template_rooms_…`, `jawa_farming_…`, `temperature_tolerance_…`, `tool_shakedown_…`,
`religion_test_…`. §24's hood reading passed (131/136 wearing both pieces).

🔴 **Still owed, in the order I would take them:**
1. **The ideology import trial — the owner's hands.** `IDEOLOGY_REBUILD_TRIAL.md`. ⚠️ Phase A
   (`vivify_world.py --live`) must happen while **Ash'karr** is loaded, BEFORE anyone touches New
   Colony. The religion half is already proven: all twelve ideoligions generate and the leader titles
   come out right on a non-classic world.
2. **`defs.sqlite` is still built from the 2026-08-23 / 581-mod capture** while a fresh
   `2026-08-26T14-20-04Z` / 582 capture sits unused in `DefDump/captures/`. Rebuild it —
   `measure build` — then **delete `dump_request.txt`** or every load pays ~27 s and 1.2 GB again.
3. `refresh.py --offline` printed the same staleness after running; its artefacts are still stale.
4. `G3` needs a HorrorWastes map; `T3`'s hypothermia hediff was never seen; `J4`'s behavioural half
   needs a route that can set `plantDefToSow` (`ORDERED_JOB_CANNOT_SOW_1`).

🔑 **Read `skills/rimbridge/references/traps.md` and `silent-failures.md` before driving** — five new
entries went in today, including one that affects every tool: **the bridge silently drops any
parameter a tool's schema does not declare.**

---

## ▶️ THE FIRST FIVE MINUTES — 2026-08-26 load, in this order

🔴 **Signatures were written BEFORE launch: `EXPECTED_FAILURES_next_load.md` §25.** Read them, do
not invent new ones from the log.

| # | do | why it is in this position |
|---|---|---|
| **0** | 🔴 **If Ash'karr is the world that loads and you intend the ideology trial: `vivify_world.py --live --out world\ASHKARR_PREREBUILD_2026-08-26` BEFORE touching the main menu.** | The `_final` bundle predates the hilliness pass and the Wither rebuild. Once you leave Ash'karr for New Colony, the chance to take a current one is gone until it is loaded again. ~1 min. `IDEOLOGY_REBUILD_TRIAL.md` Phase A |
| **1** | `prove_stat_and_room.py --census` | 2 seconds, and **everything else depends on it**: 165 jawa tools or the 44-tool deploy did not land. Baseline 121 |
| **2** | `harvest_log.py` | The whole log while it exists. Baselines in §25 D. ⚠️ It is destroyed at the NEXT launch |
| **3** | Grep the log for `required apparel can't be worn together` | Baseline **3**. Expect **0**. The cheapest reading of the day and it decides §24 |
| **4** | Spawn 8 each of the four Jawa kinds, read apparel back | §24. Absence of the errors is necessary, not sufficient — the pawn wearing the hood is the evidence |
| **5** | `prove_stat_and_room.py` (full), then `--rect` if a dwelling is built | §23. Produces the temperature table the **owner asked to see before ruling** on T2 vs N1 |
| **6** | Rebuild `defs.sqlite` from the fresh capture, then **delete `dump_request.txt`** | §25 C. The marker is not consumed and was already armed when I found it — that is how every load ends up paying 27 s and 1.2 GB |

⚠️ **`refresh.py --offline` printed the same staleness after running** (inventory CSVs, contact
sheets). Not a load blocker — its own verdict is "no game load needed" — but it did not do what it
said, so treat those artefacts as still stale and chase it offline.

---

## 📇 INDEX — every block, and whether it is spent

⚠️ **A block with no ✅ has not been scored. Add the row when you add the block, and mark it
the moment you score it** — an unmarked block is how this file rotted twice.

✅ **NO LONGER ONLY DISCIPLINE, as of `RUN_SHEET_STALE_BLOCK_CHECK_1`, 2026-08-27.** `rimflow next`
now reads this table on every call and warns on stderr about any row whose `deployed` date
precedes the last `game UP` event and is still ⏳ — it either was scored and nobody moved
it, or rode a load and nobody looked. `_stale_run_sheet()` in `src/RimMandrake/rimflow/cli.py`.
⚠️ **A row with no date in `deployed` is invisible to it** — the check cannot tell a block that
never shipped from one nobody dated, so date the cell or the row is only discipline again.

| block | deployed | status |
|---|---|---|
| §4 BATCH A — three never-run pawn tools | — | ⏳ PENDING |
| §6 BATCH C — the cheapest launch gate | — | ⏳ PENDING |
| §10 INHABITED — baseline, gated on `[Inhabited] ready: 294` | — | ⏳ PENDING |
| 🌱 BIOME FLORA + 🏷️ PLANT NAMES | 2026-08-23 | ⏳ PENDING |
| 🌡️ TOLERANCES + 🏹 ANCIENT ARSENAL + 🦴 CAST SUBSTITUTIONS | 2026-08-23 (cast NOT yet) | ⏳ PENDING |
| 🔧 §19 TWO DLLs WAITING ON THE DOWN WINDOW | ✅ **BOTH DEPLOYED 2026-08-24 01:3x** | ⏳ readings pending |
| 🎨 §22-ART CREATURE ART ON THE ADULT PATHS — needs only eyes on it | 2026-08-24 | ⏳ PENDING |
| 🎯 §20 RE-ROLL THE ROSTER — the 2026-08-24 harvest is the BEFORE | 2026-08-24 | ⏳ PENDING |
| 🏷️ §21 WORLD LABELS LIFTED — ✅ **DEPLOYED** 2026-08-24 07:3x | 2026-08-24 | ⏳ READING PENDING |
| 🌍 §21 THE WORLD ROUND TRIP — `check_world_reload.py`, 6 predictions | 2026-08-24 | ⏳ PENDING |
| 🔧 §22 FORTY-FOUR UNDEPLOYED BRIDGE TOOLS | ✅ **DEPLOYED 2026-08-26 06:36; REDEPLOYED at 166 tools ~07:0x** | ⏳ readings pending |
| 🔬 §23 THE ROWS THAT UNBLOCK ON `jawa/pawn_stats` + `jawa/room_get` + `jawa/thing_stats` | 2026-08-26 | ⏳ PENDING — **run its census FIRST** |
| 🐛 §26 DUPLICATE ANIMALS + FOUR DISCARDED GENES — deployed, scored from the LOG alone | 2026-08-26 | ⏳ PENDING |
| 🔧 §25 COMPANION: 32 NEW TOOLS + 3 FIXES BUILT, WAITING ON A DOWN WINDOW | — | ⏳ **DEPLOY FIRST** next time the game is down |
| 🧥 §24 THE JAWA HOOD — fix deployed, needs one spawn to prove | ✅ **DEPLOYED 2026-08-26 06:5x** | ⏳ READING PENDING |

🔴 **WHEN A LOAD IS SCORED: delete its block.**
**Do not leave a scored block here with a ✅** — that is the same rot one step slower.

---
## 4. 🌉 BATCH A — the three never-run pawn tools, ~2 minutes, no per-item gate

Order is free after call #1. **Assert on read-back fields, never on `success`.**

```
1. jawa/list_pawns                                   -> ids for everything below
2. jawa/spawn_pawn        kindDef=<jawa kind>  faction=player  xenotype=BTD_Jawa
3. jawa/set_pawn_xenotype pawnId=<id from 2>   xenotype=BTD_Jawa
4. jawa/set_pawn_rotation pawnId=<id>          dir=east      then dir=unlock
5. jawa/set_pawn_style    pawnId=<id>          hair=…  beard=…
```

- **`set_pawn_rotation`** returns `applied`, `posture`, `visible`. 🔴 **`visible:
  false` means the pawn is laying or downed and the renderer ignores the turn** —
  a real no-op wearing a success. Stand it up and repeat.
- **`set_pawn_style`** returns per-field `was`/`now`/`ok`. Tattoos silently no-op
  without Ideology; the tool **refuses** rather than lying, so a refusal there is
  correct behaviour.
- **`set_pawn_xenotype`** clears xenogenes but **not** endogenes. `BTD_Jawa` is
  inheritable, so its genes land as endogenes and survive a later conversion —
  pass `clearEndogenes` deliberately or expect residue.

---

## 6. BATCH C — the cheapest launch gate we own

### `NoPathToPilotConsole` — one call, no walk, game stays PAUSED

```
jawa/order_pawn   pawnId=<colonist>   targetId=<consoleThingId>   waitTicks=0   unpause=false
```

Returns `canReach` on a paused game. **No movement, no time passes, nothing on the
map changes.** Needs a map with the gravship on it.

🔴 **`pathEndMode` must stay `interactioncell`** — it is the default when
`targetId` is set, so do not override it. The vanilla gate is `PawnCanFillRole` →
`CanReach(…, InteractionCell, …)`, and the cell *beside* a console is a
**different verdict**. **A door is not a path**: doors are in the export, and that
is exactly what this call tests. Reference:
`design/Jawa/worldbuilding/gravship_flight_invariants.md`.

---

## 🔧 §19 — ✅ BOTH DEPLOYED, 2026-08-24 01:3x, IN THE DOWN WINDOW

> ✅ **DONE by CHECK.** `JawaRules.dll` → `deploy_custom_mods.py --apply`, VERIFIED in sync.
> `JawaBench.BridgeTools.dll` → `build.py --gm --apply`, game copy moved `c1f3121ddf9e` →
> **`c88df17ff577`**. Full deploy plan afterwards reads *"Everything in sync"* (0 files, 14 held).
> ⚠️ **The JawaBench build is NOT `b4d69b7c8c4d`** as this block expected — it is a later build
> carrying `world_tile_export`'s pollution fix (commit `ab02ef75`) on top of the extended exporter.
> **`pollution` is now BASE column 10**, not an extended-only column, so the default export
> round-trips losslessly. The §19 reading below still holds: extended is still 20 columns.
> ⛔ **The readings below have NOT been taken.** They need the next load.
>
> ✅ **Confirmed independently by BUILD 2026-08-24 01:4x, off the DEPLOYED binary rather than off
> the build command.** `build.tool_surface()` on the game copy reads **121 tools**, with
> `fire_incident`, `send_letter`, `weather_set`, `game_condition` and `fire_raid` all present —
> so it is genuinely the `--gm` build, not merely reported as one. Hashes match the repo:
> `JawaRules.dll` `f611bc35…` (11,776 B), `JawaBench.BridgeTools.dll` `c924ac52…` (1,255,936 B).
> 🔑 That check exists because a non-`--gm` deploy loses those five tools **silently**, and
> `build.py`'s own guard cannot vouch for a file someone else wrote.

## 🔧 §19 (original text) — TWO ASSEMBLIES ARE BUILT AND COMMITTED AND CANNOT DEPLOY WHILE THE GAME RUNS

Written 2026-08-23 19:5x by BUILD. ⛔ **Neither of these is drift and neither is a
mistake** — the OS memory-maps a loaded DLL, so both simply cannot be written until
RimWorld exits. **This block is the reminder; without it they sit in the repo forever
looking deployed.**

🔴 **DO THESE FIRST IN THE DOWN WINDOW, BEFORE ANYTHING THAT COSTS TIME.** A DLL deploy is
seconds and the window is the only place it can happen; an XML deploy can be done any time
and does not need the window at all.

| # | assembly | what it adds | deploy with |
|---|---|---|---|
| 1 | `JawaRules.dll` | the world-label transpiler: world feature names peak at **0.60** alpha instead of 0.30 (`WorldFeatures.UpdateAlpha`) | `python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod JawaRules --apply` |
| 2 | `JawaBench.BridgeTools.dll` | `jawa/world_tile_export` gains `extended=true` — eleven derived columns including `tempMin`, `tempMax`, `seasonalShift` | `python.exe src/RimMandrake/bridgetools/build.py --gm --apply` |

⚠️ **`--gm` IS MANDATORY on the JawaBench build.** Without it the build drops
`jawa/fire_incident` and `jawa/send_letter` and its own guard refuses the deploy. ⛔ Do not
reach for `--allow-tool-removal` to get past that; the flag is the fix.

⚠️ **Build state at the time of writing:** JawaBench built from commit `b4d69b7c8c4d`, game
copy holds `c1f3121ddf9e`. JawaRules built 2026-08-23 ~19:0x, game copy is the 15:08 build
`6c5fe361`. A deploy plan reporting *"built from a DIFFERENT COMMIT"* on either is expected
and is not a reason to stop.

### Readings after the load

The signatures are `§18` in `EXPECTED_FAILURES_next_load.md` — **W3** and **W4** are the
JawaRules half. ⭐ **W4 is the one that matters**: the transpiler counts its own
substitutions, because a transpiler that matches nothing leaves the method unchanged and
Harmony still reports success.

For JawaBench, the reading is one command and it needs no map:

```bash
python3 src/RimMandrake/Utils/vivify_world.py --live --diff-only
```

✅ **PASS** = the header line reads **20 columns EXTENDED**, and `temp_min_c`, `temp_max_c`
and `seasonal_shift_c` read **MEASURED** in the provenance block.
🔴 **FAIL, and it is a SILENT one** = it prints *"asked for extended=true and the deployed
companion IGNORED it"*. The bridge discards a parameter the deployed tool does not declare
and still returns `success: true` (`BUILDABLE.md` 23), so that warning is the only evidence
the deploy did not take. ⛔ Do not read a successful call as a successful deploy.

---
## 🎯 §20 — RE-ROLL THE ROSTER AFTER THE LOAD. The pre-reboot harvest is the BEFORE half.

Written 2026-08-24 01:3x by BUILD, from a live harvest of **285 pawns** taken minutes before the
game went down. Full result: `infrastructure/state/facts/roll_arm_harvest_2026-08-24.md`.

🔑 **Why this belongs to the load and not to the queue.** These numbers are the state of the
CURRENT build. Any def, tag or backstory change that lands in the down window moves them, and a
number with no BEFORE cannot tell "my fix worked" from "the roll came up differently".

### One command, no map needed for the first two; a map IS needed for the roll

```bash
python.exe src/RimMandrake/Utils/rimbench/roll_arm_harvest.py --rolls 5 --out D:\Luke\dev\Rimworld\infrastructure\state\facts\roll_arm_harvest_AFTER.json
```
✅ **No setup step.** With `--kinds` omitted the script derives the 49-kind roster straight from
`src/Jawa/Jawa_Patches/Defs/PawnKindDefs/JawaFactionRoster.xml`, so a kind added since this was
written is included automatically. (`--kinds <file>` still works and accepts `Kind=FactionDef`
for kinds whose name does not carry their faction — mechs, vanilla tribals.)
⚠️ **`python.exe`, not `python3`** — the bridge binds Windows loopback.

### The three readings, and what each one settles

| # | reading | BEFORE (2026-08-24, pre-reboot) | what a change means |
|---|---|---|---|
| **R1** | bare pawns across the 49 roster kinds, 5 rolls each | **21 of 285 (7.4%)**, in **16 of 49** kinds; worst `Jawa_Homestead_Heavy` 3/5 | ⬇️ = the arming work landed. ⬆️ = a tag or budget change disarmed someone |
| **R2** | violence-disabled backstories in the bare cohort | **13 of 21 bare pawns**; **0 of 264 armed** | the backstory filter is the larger half of the fix; R2 → 0 while R1 stays ~8 is the expected shape if only that half lands |
| **R3** | `MA_CapryakScatterbow` resolved `weaponTags` | `["Gun","NeolithicRangedAdvanced","VEE_HunterNeolithicWeapon"]` | 🔴 **`Gun` must be GONE and `NeolithicRangedAdvanced` must REMAIN.** That is `ANCIENT_SCATTERBOW_TAG_SEVER_1`, and it only scores if its XML deploy went out before this load |

⛔ **Do not score R1 with `jawa/pawnkind_audit`.** Measured on this same game, the audit reported
`cannotAfford: 0`, `emptyTagPool: 0` and *"every kind that intends to arm can"* while 21 pawns were
standing on the map holding nothing. It tests `weaponMoney.max` — the ceiling — and generation rolls
inside the range. **The audit cannot see a roll, and a clean audit is not a pass.**

✅ **Free while you are there:** the Orders architect category enumerates **64** designators with
`Open` present and actionable (measured 2026-08-24, with a map loaded). If a later load reports zero
again, check whether a map exists before filing anything — the architect menu is map-scoped, and that
is what `ORDERS_DESIGNATORS_ENUMERATE_ZERO_1 (✅ CLOSED — do not re-run)` turned out to be.

---
## 🏷️ §21 — THE WORLD LABELS ARE LIFTED OFF THE PLANET

> ✅ **DEPLOYED 2026-08-24 07:3x in the down window**, hash `d423ad7350315f8e0fbb8e9d8e86af5d` on both
> sides. Only the reading below is still owed.

🔴 **Owner, 2026-08-24, from a snapshot:** *"the labels for the world continue to intersect the
surface … They need to be slightly farther out from the planet."*

`JawaRules.dll` gains a second transpiler, `world-label-lift`. Every glyph of a world feature name
is projected onto a shell above the planet, and the shell height is one literal written four times
at `WorldFeatureTextMesh_TextMeshPro.cs:146-149` — `layer.Radius + 0.4f`. It is now **1.5**.

### The reading, and the trap in it

**W5** — the log line `[JawaRules] world-label-lift: armed; world feature names sit 1.50 above the
surface instead of 0.40`.

🔴 **`armed` is NOT the reading.** The transpiler counts its own substitutions and **expects exactly
FOUR** — one per quad corner. Anything else logs a named error, because a partial hit would lift
some corners of a glyph and not others and **shear the text**. Read the error line, not the armed line.

⚠️ **AND THE NUMBER MAY NOT BE THE PROBLEM.** For scale, the game's own shells on this sphere are
clouds at **+0.2** and atmospheric glow at **+16.1**, so 0.4 is hard against the surface and 1.5 is
still far below the glow. But a glyph quad's four corners are each normalised onto the shell
individually, so the chord sag *inside* one glyph is ~0.1 at most — which means a shell at +0.4
should not intersect a terrain mesh whose vertices sit at exactly `Radius`. **The observed
intersection has a cause this patch does not identify.**

⇒ 🔑 **If 1.5 does not clear it, do NOT simply raise it again.** The labels detach visibly from the
limb long before brute force would fix an unrelated cause. Find what is actually drawing above
`Radius` — a mod's world layer is the first suspect.

---
## 🎨 §22-ART — THE CREATURE ART IS ON THE ADULT PATHS NOW. Deployed; needs only eyes on it.

🔴 **Owner, 2026-08-24, from a screenshot:** *"I don't see new art for Eopie or Bantha."* He was
right, and the cause was not the deploy.

**`_j` is the JUVENILE life stage.** SW Animal Collection's PawnKindDefs read `BanthaW_j` /
`Eopie_j` for calves and **`BanthaW` / `Eopie` for adults**. Only the `_j` pair had ever been
supplied, so the redraw was bound to an animal that was not on the map — the bridge counted **11
eopies and 7 banthas, every one adult**.

✅ **Deployed 2026-08-24, `Jawa_Patches` in sync at 140 files:** `BanthaW_{n,e,s}` + masks,
`Eopie_{n,e,s}`, and `Eopie{A..E}_{n,e,s}`.

- **Bantha is fully covered.** Its ten `alternateGraphics` are COLOUR tints carrying no `texPath`,
  so every adult bantha is `BanthaW` tinted.
- **Eopie needed all six paths.** `alternateGraphicChance` is **0.8** across five *separate
  texPaths* `EopieA..EopieE`, so overriding the base alone would have reached one eopie in five.

⚠️ **The herd is now UNIFORM and that was the owner's call, not an oversight** — the mod's five
eopie colour variants are overridden rather than preserved. 🔑 Zeroing `alternateGraphicChance`
would give the identical look while leaving those five variants intact on disk, if it is revisited.

### The reading
Look at a bantha and an eopie. That is the whole test — no command, no capture. ⛔ **Do not score
this by checking that the files are deployed.** They were deployed and identical for the whole of
the previous session and still could not appear, which is exactly the failure this section records.


## 🔧 §22 FORTY-TWO BRIDGE TOOLS ARE WRITTEN AND NOT DEPLOYED — measured 2026-08-26 by CHECK

> ✅ **DEPLOYED 2026-08-26 06:36 by CHECK, game down.**
> `build.py --gm --apply` — 0 warnings, 0 errors, **no tool removal**. Verified by BYTES, not by the
> build's own report: artifact and game copy are both `sha256 b52b37cba71f4861…`, 1,523,712 B,
> against the old 1,255,936 B. Built from commit `2b519568`; source declares **165** `jawa/` tools.
> ⚠️ **RimBridgeServer discovers companions only at STARTUP**, so none of them exists until RimWorld
> is launched. The first thing to do in the new session is `--list-tools` and confirm the count — the
> live list is the only proof; a build that compiled is not a tool the bridge serves.
>
> 🔴 **CORRECTED 2026-08-26, later in the same down window, by BUILD: the number is 166, not 165.**
> BUILD added **`jawa/thing_stats`** (`STAT_ON_INSTANCE_TOOL_1` — a StatDef evaluated on a live ITEM,
> with the def-level number returned beside it) and redeployed with `build.py --gm --apply`,
> 0 warnings, 0 errors, no tool removal. Measured on the DEPLOYED DLL with `build.py`'s own
> `tool_surface`: **written 166, deployed 166, missing 0.** `prove_stat_and_room.py` now expects 166
> and carries the thing_stats checks as block 3b. **Confirm 166.**


🔴 **Do the companion deploy FIRST in the next down window.** The arithmetic is exact:

```
source declares    163 unique jawa/ tool names   (grep '"jawa/…"' over JawaBench.BridgeTools/*.cs)
live bridge reports 121 jawa tools
declared but NOT live: 42        live but not in source: 0
deployed DLL:  2026-08-24 01:37     newest source: 2026-08-26 04:02
```

⚠️ **UPDATED 2026-08-26 06:3x: it is now 44, not 42.** CHECK added `JawaBenchStatTools.cs` —
**`jawa/pawn_stats`** and **`jawa/room_get`** — so the source declares **165** and the gap is 44.
`build.py --gm` **succeeds, 0 warnings, 0 errors**, and reports **no tool removal**, so the two are
purely additive. ⛔ Not deployed: the game is running and the OS holds the DLL memory-mapped.
🔑 **They close two open blockers the moment they land** — `PAWN_STAT_READ_HAS_NO_TOOL_1` and
`ROOM_ROLE_AND_TEMP_HAVE_NO_TOOL_1` — and with them `LIVE_HALF_OF_LOAD_1` rows T1/T2/N1/N2 and
`TEMPLATE_ENGINE_ACCEPTANCE_1` criteria 1 and 2 become runnable. See §23.

The 42 from BUILD are exactly the four files written on 2026-08-26 03:56–04:02 —
`JawaBenchSimTools.cs` (12) · `JawaBenchResearchTimeTools.cs` (11) · `JawaBenchJobTools.cs` (10) ·
`JawaBenchNeedsTools.cs` (9). 12+11+10+9 = 42, and 163 − 42 = 121. Nothing else is missing.

⚠️ **Why this matters beyond the deploy:** a seat that runs `--list-tools` today sees 121 and will
conclude these tools do not exist. Several are things items have already been blocked on —
`jawa/pawn_thoughts`, `jawa/pawn_memory`, `jawa/cell_temperature`, `jawa/set_work_priority`,
`jawa/animal_train`, `jawa/research_progress`, `jawa/time_set_ticks`, `jawa/paint_area`.

⛔ **`jawa/cell_temperature` is NOT a room reader** — `ROOM_ROLE_AND_TEMP_HAVE_NO_TOOL_1` still
stands until someone reads its description; check it after the deploy before closing that item.

🔑 The DLL cannot be written while the game runs — the OS holds it memory-mapped. This is the
whole reason the window matters. `python.exe D:\Luke\dev\Rimworld\src\RimMandrake\bridgetools\build.py --gm --apply`


## 🐛 §26 TWO DEF-LAYER BUGS ARE DEPLOYED — both scored from the LOG, no bridge, no clicking

Found by `harvest_log.py` on the 2026-08-26 08:53 load, which scored **two RED lines above
baseline**. Both fixes are deployed to the game folder already; defs are parsed at startup, so
the next load is their first.

### 1. The duplicate-animal crash — DEAD MODS 2, baseline 0

A dead mod is the highest-priority finding in any log, and this one kills three:
`ChooseWildAnimalSpawns` dies in its static constructor, Giddy-Up's biome cache never completes,
and Biome Compatibility Project aborts the rest of the post-load queue.

```
grep -c "same key has already been added"      was 12 distinct keys   ->  expect 0
harvest_log.py  DEAD MODS (static ctor)        was 2                  ->  expect 0
```

⚠️ **The log could only ever name 12** — `BiomeDef.CommonalityOfAnimal` throws on the first
duplicate key **per biome** and stops. The capture found **27** pairs across those same 12
biomes. `AnimalBiomeDuplicates_Generated.xml` removes all 27 animal-side entries.
🔑 **Then re-run the instrument against the NEW capture**, because the log going quiet only
proves the first collision in each biome is gone:
```
python3 src/RimMandrake/Utils/biome_animal_conflicts.py     expect: 0 pairs
```
A non-zero there is a pair this pass could not reach, NOT a patch that failed.
Item: `BIOME_DUPLICATES_STILL_LIVE_1`.

🔑 **AND THE THIRD READING, which is the one that shows what the crash actually COST.**
`CommonalityOfAnimal` assigns its cache dictionary *before* filling it, so the throw leaves it
partially built and non-null — and every animal the loop never reached returns **0f** for the rest
of the session. `AllWildAnimals` only yields kinds above 0, so those animals are not in the
biome's list at all. Measured against this capture: of the **744** animal weights
`BiomeCast_Ashkarr.xml` writes across 26 biomes, **563 survive and 181 read 0** — about a quarter
of the hand-authored planet cast, silently not spawning.

```
python3 -c "..."   # or just re-run the numbers in items/BIOME_CAST_COMMONALITIES_ZEROED_1.md
expect after the fix:   744 of 744 non-zero   (was 563)
```
⛔ **If the duplicate pairs go to 0 and the zeros do not, the diagnosis is wrong** and
`BIOME_CAST_COMMONALITIES_ZEROED_1` is a real second defect. Written before the look, on purpose.

### 2. Four tattoo genes discarded whole — DEFS DISCARDED 6, baseline 2

`SW_Genes.xml` carried a `modExtension` naming `GeneTattooTagFilter.ModExtension_GeneTattooTagFilter`,
a type no installed mod provides. RimWorld does not drop the extension — **it drops the entire
GeneDef**, so Mirialan, Pantoran, Togruta and Zabrak had no tattoo gene at all.

```
harvest_log.py  DEFS DISCARDED                 was 6   ->  expect 2 (the two VFE torches, benign)
grep "SW_Genes.xml"                            was 4   ->  expect 0
```
✅ And the four genes should now be in the capture: `RimMandrake_tattooGene_mirialan`,
`_pantoran`, `_togruta`, `_zabrak`. ⛔ Presence in the dump is the check here, not a spawn — a
def that loads is exactly what was missing.

---
## 🔧 §25 TWO COMPANION FIXES ARE BUILT AND WAITING ON THE NEXT DOWN WINDOW

Written and compiled 2026-08-26 by BUILD at `97403eec`, **0 warnings, 0 errors, no tool
removal** — artifact and game copy both carry 166 tool names, so nothing is lost by deploying.
⛔ **Not deployed: the game is UP and the OS holds the DLL memory-mapped.**

```
python.exe D:\Luke\dev\Rimworld\src\RimMandrake\bridgetools\build.py --gm --apply
```
🔴 `--gm` or the deploy strips every player-acting tool.

| tool | what changed | what to read after the next load |
|---|---|---|
| **67 NEW TOOLS** — EASY block: `PawnKit` 10 · `Group` 11 · `System` 11. MEDIUM block: `Zone` 6 · `Incident` 8 · `Society` 10 · `Render` 11 | the last of `BRIDGE_TOOLS_EASY_BLOCK_1`: skills/abilities/genes/inventory, lords + factions + caravans + ideo, and minify/roof-collapse/anomaly/save/prefs/diagnostics | the census must read **233**, not 166. ⚠️ That is the count of `[Tool]` ATTRIBUTES; `build.py`'s byte scan runs 2 higher because `jawa/anomaly_` and `jawa/revoke` appear inside other tools' description prose |
| `jawa/build_batch` | `placed` counted spawn ATTEMPTS; eight calls reported 81 placed with `failed: []` and the map held 78 (`BUILD_BATCH_OVERWRITES_SILENTLY_1`). It now returns **`survived`**, `lostToLaterOps` and **`displaced[]`** naming everything the batch destroyed and whether the batch itself had placed it. New `refuseIfDisplaces` makes it an error instead. | Rebuild the dwelling and assert `survived == requested`, not `placed == requested`. With the footprint fix in rimplace the correct answer is now **0 displaced** |
| `jawa/pawn_gear` · `FindPawn` · `jawa/pawn_genes` | five rows of `BRIDGE_ARG_SHAPES_INCONSISTENT_1`: both pawn id forms accepted, pawn_gear declares itself a WRITE tool and names `jawa/pawn_get`, equipment/apparel rows carry `defName` beside `def`, and the gene verbs and head-re-roll ordering are documented | any pawn-addressing call with a `Thing_`-prefixed id must now resolve instead of returning an empty success |
| `jawa/fire_raid` | echoed the faction you asked for even when the worker raided with another (`FIRE_RAID_ECHOES_REQUESTED_FACTION_1`). Now returns **`actual`** (the faction the worker used, written back into parms) and **`arrived[]`** counted off the map, and warns BEFORE firing that a non-hostile faction will be substituted | `jawa/fire_raid {faction: "Jawa_FreeDroidEnclaves", dryRun: false}` must now say *substituted* and name Blackstar Company in `actual`/`arrived` |

### The validation plan for §25, in the seven-field format

```
ITEM     The companion at 233 tools - 67 new capabilities (EASY + MEDIUM) plus 3 corrected tools
SEE      The census prints 198 and names jawa/thing_stats, and one tool from each of the three
         new files answers a real call: jawa/mod_inventory lists 582 running mods,
         jawa/read_opinion returns a number AND its breakdown for two colonists,
         jawa/faction_goodwill_check refuses a change the faction cannot accept, by name
ROUTE    python.exe D:\Luke\dev\Rimworld\src\RimMandrake\bridgetools\prove_stat_and_room.py --census
         then the three calls above, in any order
PREDICT  233 jawa/ tools; mod_inventory count == the ModsConfig activeMods count == 582
CLOSE    The census at 198 plus those three calls answering - NOT exercising all 32, and NOT
         grading what any of them DOES to the colony; that is each capability's own item
RIDE     solo (a new assembly - batching destroys attribution if the load comes up wrong).
         ⚠️ It rides with §22/§23 only because those are the SAME assembly.
LIES     1. 198 is the count of [Tool] ATTRIBUTES. build.py's byte scan says 200 because
            'jawa/anomaly_' and 'jawa/revoke' appear inside other tools' description prose -
            reading the scan's number as the target makes a correct load look 2 short.
         2. A deployed DLL registers NOTHING until the game restarts, so a tool-not-found
            after a load that predates the deploy is not a failure of the tool.
         3. 67 tools written by seven agents in two passes all compiled; compiling is not
            working, and none of them has ever been CALLED.
```

⚠️ **`resolved` still exists and still means THE REQUEST.** It was not renamed — other callers read
it — but both its own comment and the ResultDescription now say so, and `actual` is the outcome.

---
## 🎯 THE DECISION STRINGS FOR THIS LOAD — written 2026-08-26 07:0x by BUILD, BEFORE the launch

⚠️ **Written before the log exists, which is the only time a decision string counts.** A signature
invented after reading the log is a story that fits.

| # | expect to SEE, verbatim | baseline (last load, 06:35) | what each outcome means |
|---|---|---|---|
| 1 | `[JawaBench] ready: 166 tools, build 70b3b1173918` | `ready: 121 tools, build c88df17ff577` | **166** = the whole companion landed, `jawa/thing_stats` included. **165** = the last deploy of this window did not take — the build stamp will say so. **121** = the game loaded a DLL from before 2026-08-26 entirely. Any other number: do NOT guess which tools are missing, run the census in §23 |
| 2 | `[JawaBench] context: modSet 582/…` | `modSet 581/fc658bb0` | 582 is the live list with `mandrake.ashkarrlandmarkart`. **581 means the game loaded the older list**, and every §22/§23 reading is against the wrong stack |
| 3 | `defDump ARMED` on that same context line | `defDump ARMED` | the capture will be written to `DefDump/captures/<id>/`. ⛔ The marker is NOT consumed — delete `dump_request.txt` afterwards or every future load pays ~27 s and ~1.2 GB |
| 4 | `[RimBridge] STARTUP_TIMING phase=bridge-start.total` | present | the bridge came up at all. **Absent = there is no bridge**, and every bridge-gated item in the queue stays where it is |

🔑 **Expected-PRESENT strings, not absences.** Every one of the four is a line that must BE there.
A clean log proves nothing here: the companion failing to load is silent in exactly the way a
successful additive load is.

🔴 **The one thing to run first, before any reading:**
```
python.exe D:\Luke\dev\Rimworld\src\RimMandrake\bridgetools\prove_stat_and_room.py --census
```
It must print **166** and name `jawa/pawn_stats`, `jawa/room_get` and `jawa/thing_stats`. Everything
in §22 and §23 is meaningless until it does — a deployed DLL registers nothing until startup.

⚠️ **The pre-load `Player.log` is already saved** at
`D:\Luke\dev\Rimworld\infrastructure\state\logs\Player.2026-08-26_0635.pre-load.log`
(973,786 B). The live one is overwritten at launch; that copy is the only evidence of the
06:35 session left.

---
## 🔬 §23 THE FOUR ROWS THAT BECOME RUNNABLE THE MOMENT `jawa/pawn_stats` LANDS

Written 2026-08-26 by CHECK. **One command runs the whole block:**

```
python.exe D:\Luke\dev\Rimworld\src\RimMandrake\bridgetools\prove_stat_and_room.py
python.exe ... prove_stat_and_room.py --census                 # stop after the tool census
python.exe ... prove_stat_and_room.py --rect 170,170,18,10     # add the room checks
```

🔑 **Its first check is the only one that matters until it passes:** does the running game register
**166** `jawa/` tools (corrected 2026-08-26 — BUILD added `jawa/thing_stats` in the same down
window), and are `jawa/pawn_stats`, `jawa/room_get` and `jawa/thing_stats` in the LIVE list. Companions are
discovered at startup only, so a deployed DLL proves nothing until that census passes.
Its second check is that `pawn_stats` **refuses** a bogus stat name and suggests the real one —
run before any reading, because a tool that silently drops a stat returns an empty answer that
reads exactly like "the pawn does not have it".

The detail, if you want to run the calls by hand:

**T1 · T2 · N1 · N2 — `LIVE_HALF_OF_LOAD_1`.** Spawn one pawn per xenotype with
`jawa/spawn_pawn … xenotype: <X>`, then:

```
jawa/pawn_stats {pawn: <id>, stats: "ComfyTemperatureMin,ComfyTemperatureMax"}
```

🔑 The defNames are **`ComfyTemperatureMin` / `ComfyTemperatureMax`** — *not* `Comfortable…`, which
does not exist. Both confirmed present in the def dump; the wrong spelling is refused with
suggestions rather than silently skipped.

Expected, from the genes already read off the instances on 2026-08-26:

| xenotype | temperature genes measured | so the stat should be |
|---|---|---|
| RimMandrakeUgnaught · Twilek · KelDor | *(none)* | the vanilla baseline, −40 … +45 |
| MandrakeJawa | `MinTemp_SmallDecrease` + `MaxTemp_SmallIncrease` | one Small step each way |
| RimMandrakeChiss | `MinTemp_LargeDecrease` + `MaxTemp_SmallDecrease` | large down, small down |
| RimMandrakeWookiee | `Furskin` + `MinTemp_SmallDecrease` + `MaxTemp_SmallIncrease` | Furskin **stacked** — this is N2 |

⛔ **Do not grade T2 before `JAWA_TEMP_RANGE_TWO_CRITERIA_1` is answered.** T2 says the Jawa should
read ≈ −40…+65 and N1 says −50…+55 for the same stat on the same pawn. The genes say N1. An
observer who picks the criterion after looking has not tested anything.

**`TEMPLATE_ENGINE_ACCEPTANCE_1` criteria 1 and 2** — the dwelling is already built at
`rect 170,170,18,10` on the current scratch map, but that map will not survive. Rebuild it
(`rimplace calls dwelling --rect <x>,<z>,18,10 --rooms 3 --occupants 4`, ⚠️ translating `rect` →
`ops` until `TEMPLATE_RECT_PARAM_NOT_ACCEPTED_1` is fixed), then:

```
jawa/room_get {rect: "170,170,18,10"}
```

* **Criterion 1** — expect three rooms whose `role` is `Bedroom`/`Barracks`, `DiningRoom`,
  `Storeroom`. Anything else and the game does not agree it is a house.
* **Criterion 2** — build the nursery variant on a hot tile, let time run, and read `temperature`
  back. **Must be ≤ 32 °C.**


## 🧥 §24 THE JAWA HOOD — the fix is deployed; one spawn proves it

Owner authorised CHECK to make the edit, 2026-08-26. `apparelRequired` now carries
**`Inherit="False"` on all four Jawa kinds** in
`src/Jawa/Jawa_Patches/Defs/PawnKindDefs/JawaColonistPawnKinds.xml`, deployed and **verified by
bytes** (repo and game copy both `sha256 6c6fcbd7544379817d5f`, four pinned blocks in the game copy).

**Why all four and not the two that were broken.** Only `Jawa_Tribal_Scavenger` (via
`TribalWarriorBase` → `Apparel_WarVeil`) and `Jawa_Tribal_Elder` (via `TribalChiefBase` →
`Apparel_TribalHeaddress` + `Apparel_PlateArmor`) were losing pieces. `Jawa_Colonist` and
`Jawa_Tribal_Slinger` were clean **by accident of what their parents happen to carry today**.
`Inherit="False"` is simply the owner's *"Jawa wear robes+hoods ONLY"* said in XML, so it belongs on
all four and it hardens the clean two against a mod update that adds one.

### The reading — one call, and three things must all be true

```
jawa/spawn_pawn {kindDef: <kind>, x: .., z: .., faction: Jawa_IndigenousTribes, count: 8}
jawa/pawn_get   {pawn: <each id>}      # apparel, read off the pawn
```

for **all four** kinds — `Jawa_Colonist` · `Jawa_Tribal_Scavenger` · `Jawa_Tribal_Slinger` ·
`Jawa_Tribal_Elder`.

1. **`guy762_Robes_jawa` AND `guy762_JawaHood` on every pawn of every kind.** Before the fix:
   Scavenger was robe 16/16, hood **0/16**; the Elder should have been losing its robe as well and
   has never been looked at.
2. **No `Apparel_WarVeil`, no `Apparel_TribalHeaddress`, no `Apparel_PlateArmor`** on any of them.
3. ✅ **DONE, 2026-08-26 by BUILD — this one is already settled and needs no game time.**
   The same grep over both logs: **3 matches** in the 06:35 load, **0** in the current one, with
   the before-reading as the positive control that the check fires at all. Evidence:
   `infrastructure/state/evidence/jawa_hood_configerror_2026-08-26_BUILD.md`. ⛔ It settles only
   that the DEFS no longer conflict — what a pawn actually wears is still criteria 1 and 2.
   The original instruction, kept because it is how it was measured:
   🔑 **`Player.log` no longer carries these three lines** — this is the cheapest check and the one
   that caught the bug in the first place:

```
Config error in Jawa_Tribal_Scavenger: required apparel can't be worn together (Apparel_WarVeil, guy762_JawaHood)
Config error in Jawa_Tribal_Elder:     required apparel can't be worn together (Apparel_TribalHeaddress, guy762_JawaHood)
Config error in Jawa_Tribal_Elder:     required apparel can't be worn together (Apparel_PlateArmor, guy762_Robes_jawa)
```

⚠️ **Presence of the defs in a dump proves nothing** — both mods were always active. The pawn
wearing it is the only evidence.
⚠️ **A def change needs a RESTART**, not a save reload. The deploy tool says so itself.

---

## 🔴 GAME-DOWN WINDOW OWED — one companion DLL deploy, added 2026-08-27 by BUILD

⛔ **This one is NOT an XML deploy and cannot ride a live game.** The OS locks a loaded
assembly, so it must happen while RimWorld is closed. **Do it FIRST in the window**, before
anything that needs the game back up.

```
taskkill.exe /F /IM RimWorldWin64.exe
python.exe D:\Luke\dev\Rimworld\src\RimMandrake\bridgetools\build.py --gm --apply
```
🔑 **`--gm` is required, not optional.** Without it `fire_incident`, `send_letter` and the new
`lord_set_job` are compiled OUT, and `build.py` then refuses with *"THIS DEPLOY WOULD REMOVE
TOOLS"*. That refusal is correct — do not reach for `--allow-tool-removal`.
🔑 **Check the output for the word `deployed`.** A piped `grep` hides the running-game refusal,
and you then test stale code and conclude the new tool "was not found".

**What is waiting** — built clean at `887d4a3d`, 0 warnings, 0 errors, surface 238, phantoms
none. Evidence: `infrastructure/state/evidence/BRIDGE_TOOLS_BATCH_2026-08-27.txt`.

| tool | item | validation plan |
|---|---|---|
| `jawa/lord_set_job` | `LORD_JOB_SWAP_TOOL_1` | on the item |
| `jawa/bridge_arg_report` | `BRIDGE_DROPS_UNKNOWN_PARAMS_1` | on the item |
| `jawa/debug_actions` | `DEBUG_ACTION_SEARCH_WEDGES_BRIDGE_1` | on the item |

🔑 **`jawa/debug_actions` wants the FULL 582-mod list to prove anything.** It replaces a
host tool that times out at 30 s and blocks every other caller *at scale*; the minimal list
does not reproduce that, so a fast reading there is not evidence. The other two prove fine
on the minimal list.

⚠️ **The deployed copy is far behind the source.** The game copy's tool surface reads **166**
against the build's **238**. Everything written since 2026-08-26 is undeployed, not just these
two — so this window pays for more than the two items above.

⚠️ **A deployed DLL registers NOTHING until the game restarts.** RimBridgeServer discovers
companions at startup only. So the sequence is kill → build --apply → launch → prove, and a
"tool not found" from a session that predates the deploy is not a failure of the tool.

⚠️ **New this build: the companion now references `0Harmony`** and installs one Harmony prefix
on a RimBridgeServer private method. If the bridge misbehaves after this deploy in a way that
has nothing to do with the two new tools, that patch is the first thing to suspect — check
`Player.log` for `[JawaBench] argument guard` (it announces both success and failure) and call
`jawa/bridge_arg_report` and read `installed`.
