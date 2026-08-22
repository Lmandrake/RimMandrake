# Re-measuring two REP subagent sweeps — CHECK, 2026-08-22

Both `TEST_PLAN_SIX_WRONG_ANCHORS_1` and `BUILDABLE_REGISTER_SIX_STALE_1` arrived as
**subagent findings, not measurements**, and both item files said so. Every row was
re-measured independently before either file was edited. Offline, game DOWN.

## TEST_PLAN.md — 5 of 6 confirmed, 1 REFUTED, plus an unevidenced PASS

| row | sweep said | measured | action |
|---|---|---|---|
| line 64, "ten art-fix mods are live" | 7 active | **CONFIRMED.** `ModsConfig.xml`: 6 art-fix + `desertvehiclereskin` = 7. `phytokinbarkheadfix`, `kotorbandoliernorthfix`, `missingartfixes`, `galacticdiversity` inactive; **`mandrake.cereanmanefix` absent from the file entirely** | row rewritten with the seven named |
| lines 71/73, "the EIGHT live mods" | 7, table row 6 struck | **CONFIRMED.** Eight numbered rows, row 6 `CereanManeFix` struck closed 2026-08-21 ⇒ 7 live | header → SEVEN; the eight-rows/seven-live gap stated in the body |
| line 127, "exactly two PNGs" | 14 | **CONFIRMED.** 14 PNGs: 13 faction icons under `Textures/World/JawaFactions/` + `JawaClaimRumour.png` | count corrected; the no-collision conclusion survives and is kept |
| lines 217-218, `JawaBenchTerrainTools.cs:69` | wrong anchor | **CONFIRMED.** `SetTerrain` declared at **:61**; `string terrainDef` at **:73**; `:69` is a `[ToolParameter]` continuation string. 🔑 The *parameter-name* claim is TRUE and was kept | anchor → `:61`, with `:73` named |
| lines 60/88, `Apparel_FieldKits.xml:62` / `:51` | mod ships no 1.6 folder | 🔴 **REFUTED — the doc was right and the sweep was wrong.** Workshop 2868392160 ships `v1.3`, `v1.4`, `v1.5` **and `v1.6`** (note the `v` prefix, which is what the sweep missed). In `v1.6`: `texPath` at **51**, `wornGraphicPath` at **62** — exactly as cited. The game is 1.6 | **no edit** |
| line 126, "My `C12` warning was STALE" | ID points at the wrong thing | **CONFIRMED.** `C12` appears **0 times** in `ledger/events.jsonl`; `design/V2_DREAMS.md:248` uses `C12` for `NoPathToPilotConsole`, unrelated | ID struck from both places; no ID cited, because it never had one |
| line 198 row 1, "✅ ALREADY PASSED LIVE — 144 cells, 0 failed verify" | no capture exists | **CONFIRMED NOT FOUND.** Both `observed/` roots swept (34,814 files), plus targeted reads of the two oversized logs (148 MB / 149 MB). Zero `set_terrain` / `cellsChanged` / `144 cells` captures; the only `SaltCrust` hits are def-load lines. "144 cells" exists in exactly three docs that cite each other | **downgraded PASSED → UNMEASURED**, with the re-run named |

## BUILDABLE.md — 5 confirmed stale, 1 SPLIT, 1 count corrected

| entry | measured | action |
|---|---|---|
| def-dump collision (824 defs), "does nothing until the dumper is redeployed" | **STALE.** Live `RimDefDump.dll` is md5-identical to the repo copy (26,112 B, `d4bdad92`/`0a3c310b`); capture `2026-08-21T22:44:59Z` carries **533 `defTypes` + 13 `defTypeCollisions`** | warning → deployed-and-captured, keeping "a dump older than that timestamp still lies" |
| instrument row 3, "✅ fixed d7cf154 (undeployed)" | **STALE**, same evidence | "(undeployed)" → deployed + captured |
| instrument 12 `jawa/faction_name_get`, "do not run clear" | **STALE.** Live companion `JawaBench.BridgeTools.dll` dated **2026-08-22 12:47**, md5-identical to the repo build, **19 h after `37ac949d`**. ⚠️ Note it deploys to `RimWorld\BridgeTools\`, **not** `Mods\` | narrowed: deploy landed, only a LOAD is owed; `clear` still refused against a game that has not restarted since 12:47 |
| "nothing on the **155-tool** bridge can order an attack" | 🔑 **SPLIT.** The count is wrong; **the finding is not.** Source-derived count (regex over `[Tool("…")]` across 53 `.cs` files, never `strings`): **119 distinct `jawa/` tools**. Exactly three are combat-adjacent — `fire_raid`, `order_pawn`, `raid_preview` — and repo-wide the only `JobDefOf` members referenced are `Goto` and `LayDown`. ⚠️ The **live** total (119 + RimBridgeServer's own `rimworld/*`) is **UNMEASURED offline** | count replaced by the measured 119 + an explicit UNMEASURED for the live total; the substantive claim kept verbatim |
| "pawnGroupMakers on the ABSTRACT parent ⇒ five `Jawa_Homestead_*` spawn nowhere" | 🔑 **SPLIT.** The *mechanism* is sound and stays. The *consequence* is dead: `HomesteadDefenseLeague.xml` now patches the abstract base and the five are **fielded**. The live orphan set is **nine different kinds** (`AUTHORED_KINDS_MUST_FIELD_1`, `38cabab0`), which also **rejects `Inherit="False"`** — it drops all twelve inherited groups | consequence sentence replaced; mechanism untouched |
| `validate_patch.py` row, "✅ fixed, selftest 36 cases" | **HALF STALE.** The xpath fix is real (`fc10b9a5`). **No selftest exists** — no `--selftest` flag, no case table, no test file touched by that commit. The "36" is a bleed from `validate_save_artifact.py`, which resolves `MandrakeJawa.xtp` in 36/36 | "selftest 36 cases" replaced with the bleed named |
| header banner, "one hand-made world, frozen, then shipped" | **STALE AS TENSE ONLY.** `canon.yml` → `planet.status: remaking`. ⚠️ The 2026-08-15 no-worldgen ruling is **not** stale; only the framing of a frozen world as an existing state | "frozen **once he saves it**", with the remaking note |
| entry 8, `DefDump/defs.sqlite` with no root | **CONFIRMED rootless.** Only copy is `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\DefDump\defs.sqlite` (788 MB, 2026-08-21 16:10); repo-wide `find` returns nothing | full native path written in |

## What this cost the sweep's credibility, and what it didn't

11 of 13 rows held. **One was flat wrong** (`Apparel_FieldKits`, where a `v` prefix on the
version folder was read as the folder's absence) and **two were half wrong** — the bridge tool
count and the Homestead consequence both carried a true finding under a false number or a false
effect. 🔑 **Both half-wrong rows would have been made WORSE by acting on the sweep as written**:
deleting the attack-order warning because its count was stale, or deleting the abstract-parent
mechanism because its example had been fixed. The item files were right to say *verify first*.

---

# Reconciling the bridge capability roster — CHECK, 2026-08-22

`design/Jawa/bridge/BRIDGE_CAPABILITY_ROSTER.md` was written 2026-08-19 against 57 built
tools, to be culled by the owner. The companion source now declares **119**. A 2026-08-22
pass marked 15 rows built and 113 open; that pass matched on NAME and is wrong by ~4×.

**Measured:** 119 `[Tool]` declarations, unique, across the seven `JawaBench*Tools.cs` files
(Diagnostic 4 · Event 13 · Faction 3 · Map 16 · Pawn 18 · Terrain 32 · World 33). Two are
GM-gated (`#if JAWA_GM_TOOLS`) ⇒ **a default deploy ships 117**. 🪤 The `[Tool(` attribute
carries its name on the FOLLOWING line, so a single-line `\[Tool\("` regex returns 0 and
reads as a clean answer — the same shape as every instrument in `BUILDABLE.md`.

**103 capability rows ⇒ 56 fully delivered · 10 partial · 37 open.**

🔑 **Why the name match failed: absorption.** Every capability folded into a multi-action
tool was missed. `set_under_terrain`, `set_temp_terrain`, `set_terrain_color` and
`remove_top_layer` are four MODES of `jawa/set_terrain_layer`; `set_snow`, `add_snow_radial`,
`set_sand`, `add_sand_radial` are `set_weather_buildup(kind, mode)`; the whole of §3's gear,
health and psychic surface is four tools. ⇒ **A roster row is a CAPABILITY, not a tool name,
and only a semantic match can retire one.**

📛 **The 10 partial rows are the real hazard** — "built" and "open" are both wrong about
them. `social_cancel` clears gathering/ritual lords only and returns a count, so
`lord_list`/`lord_destroy` is not delivered; `order_pawn` is Goto/walk only, so
`pawn_force_job` is not; `weather_get` READS storyteller/difficulty/threatScale
(EventTools:87-90) with no setter and no `Notify_DefChanged`.

**Open work concentrates in §0 lords/settlements (7), §1 map generation (7), §2
incidents/clock (6), §4 pipes and power (3), §5 patrol (3), §7 layout/blueprints/power (10).**
§3 DEEP PAWN EDITING is complete but for `set_pawn_gender` — `gender` is read at
PawnTools:115 and never written.

⚠️ **Two UNCERTAINs source alone cannot settle, and a live tool list would:** whether
`get_time`/`set_time_speed` already exist in core RimBridge rather than the companion, and
whether `connect_cells` handles a modded pipe def's grid-dirty step. Both are marked
UNCERTAIN in the roster rather than guessed.

Header superseded in place per the project's supersede-in-place rule; the name-match pass is
kept as provenance, not deleted.
