> 🧹 **PRUNED 2026-08-24 01:4x on the owner's order — "clean out all stale NEXT_RELOAD files
> immediately".** Every block whose only item IDs had already closed, dropped or been superseded
> was removed; blocks naming still-live work were kept verbatim. **Nothing is lost — the full
> previous text is the parent of commit `ec0b5a61` in git.** ⚠️ A block here is a DUPLICATE of a ledger
> item; when the two disagree, the ledger is right. Live IDs kept in this file: `ANCIENT_SCATTERBOW_TAG_SEVER_1`, `C40`.

## 📇 INDEX — every block, and whether it is spent

⚠️ **A block with no ✅ has not been scored. Add the row when you add the block, and mark it
the moment you score it** — an unmarked block is how this file rotted twice.

| block | deployed | status |
|---|---|---|
| §4 BATCH A — three never-run pawn tools | — | ⏳ PENDING |
| §5 BATCH B — open live items | — | ⏳ PENDING |
| §6 BATCH C — the cheapest launch gate | — | ⏳ PENDING |
| §10 INHABITED — baseline, gated on `[Inhabited] ready: 294` | — | ⏳ PENDING |
| 🌱 BIOME FLORA + 🏷️ PLANT NAMES | 2026-08-23 | ⏳ PENDING |
| 🌡️ TOLERANCES + 🏹 ANCIENT ARSENAL + 🦴 CAST SUBSTITUTIONS | 2026-08-23 (cast NOT yet) | ⏳ PENDING |
| 🔧 §19 TWO DLLs WAITING ON THE DOWN WINDOW | ✅ **BOTH DEPLOYED 2026-08-24 01:3x** | ⏳ readings pending |
| 🎯 §20 RE-ROLL THE ROSTER — the 2026-08-24 harvest is the BEFORE | 2026-08-24 | ⏳ PENDING |
| 🏷️ §21 WORLD LABELS LIFTED — ✅ **DEPLOYED** 2026-08-24 07:3x | 2026-08-24 | ⏳ READING PENDING |
| 🌍 §21 THE WORLD ROUND TRIP — `check_world_reload.py`, 6 predictions | 2026-08-24 | ⏳ PENDING |
| 🔧 §22 FORTY-FOUR UNDEPLOYED BRIDGE TOOLS | ✅ **DEPLOYED 2026-08-26 06:36** | ⏳ readings pending |
| 🔬 §23 THE FOUR ROWS THAT UNBLOCK ON `jawa/pawn_stats` + `jawa/room_get` | — | ⏳ PENDING |

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

## 5. ⭐ BATCH B — the open live items. None needs a world; a quicktest is enough.

```
rimworld/start_debug_game_ready       -> a fresh map in ~30 s
```

⚠️ That call **exceeds the 30 s timeout and succeeds anyway** — do not retry, or
you get a second map. Reconnect and poll `list_pawns`.

🔴 **Read the rows in order.** L0 is one screenshot and it decides whether a large
body of art work closes or reopens; L1–L4 need `jawa/*` tools that only ship in
§1.0 step 1. **Detail lives in the queue item named in each row — this table is the
order and the call, not the whole plan.**

| # | call | item | why it is worth a line |
|---|---|---|---|
| **L0** | `jawa/clear_ui`, then `jawa/spawn_pawn kindDef=Colonist faction=PlayerColony xenotype=RimMandrakeRodian`. **Look at its face. Screenshot it.** | CHECK **C37** | 🔴 **FIRST ACTION ON THE MAP.** Facial Animation's per-xenotype opt-out was rewritten (86 → 156 entries) but FA reads its config **only at startup**, so it has never once been active. **Snoot visible ⇒ the whole art failure closes.** Still a human face ⇒ FA was not the cause and the head-gene findings (10 species with no head-forcer, Rodian forced to a generic Outland reptile head) move back to the top. One pawn, one look. ⚠️ **`faction` is not optional** — omit it and the pawn spawns into the Empire, hostile |
| **L0b** | Confirm the ideoligion **LOADS**, then check its **16 `AbilityDef`s resolve** | CHECK **C42** | ✅ Offline half DONE (`6c0f307`): `The Salvation.rid` 267 refs, 251 resolve, **zero dangling**, **101 precepts** (not the 82 previously written); `MandrakeJawa.xtp` 36/36. 🔴 **What is left is live-only and cannot be faked offline** — `AbilityDef.json` is one of 79 EMPTY def-type files in the dump, so "absent from the dump" says NOTHING about those 16. It bakes at world creation like the factions. ⇒ Settle before the faction/ideo row is called done |
| L1 | `rimworld/spawn_thing def=SmallThruster x=45 z=131`, then `jawa/inspect_string` on it — read for `WarningThrusterInside`. ⚠️ **`jawa/spawn_thing` DOES NOT EXIST**; the prefix is vanilla `rimworld/`, or `jawa/spawn_batch` for more than one | BUILD | **Cheapest launch gate we own.** Outdoor-required ⇒ the exported hull needs its stern cut back, a whole deck re-lay. Substructure-free-only ⇒ nothing to change. One paused call decides a large piece of rework. Needs `jawa/inspect_string` (§1.0 step 1) |
| L2 | `jawa/spawn_pawn kindDef=Jawa_Tribal_Scavenger` **×6**, then one Geonosian Foundry Hive pawn, then read a Jawa's gear | CHECK **C40** | Three deployed-but-unproven fixes in one spawn pass. **Six armed Jawa** (not civilians) · **a Geonosian that is not a baseliner** (empty `xenotypeChances` looks like a content gap, not a dropped node) · **a Jawa wearing `guy762_Robes_jawa` + `guy762_JawaHood`**. ⛔ The voice half is DEPRECATED (owner, 2026-08-16) — do not unpause to hear a line, do not grade it. 🔴 The gear defs live in a mod we KEPT — their presence in a dump proves nothing; **the pawn wearing them is the only evidence** |
| L3 | Fire ONE Galactic Empire raid and screenshot it — 🔴 **procedure below the table, do not improvise it** | DECIDE | The biggest open design question DECIDE owns: **before we repair the antagonist, someone must see whether it reads as one.** ~5 min. Needs `jawa/set_faction_relation` (§1.0 step 1) if the Empire is not already hostile |
| L4 | Spawn `KotORDroidGood_3C` **twice** — the 2nd must NRE | BUILD | 30 s, any map. The whole causal chain (`isOrganic=false` ⇒ no `Pawn_RelationsTracker` ⇒ HAR NRE on the 2nd same-def pawn) rests on this. **If the 2nd does not throw, the chain is wrong and the item re-opens.** An owner decision is queued behind it |
| L5 | **Architect ▸ Vehicles** — read the five Tier-0 land blueprint labels. Then spawn `AV_OxCart`, `AV_Chariot`, `AV_CoveredCarriage`, `AV_WarChariot`; rotate each north/south/east — ⭐ **and look at the ART while you are there**: `VEHICLE_SPRITE_ARTEFACT_CLEANUP_1` (`922b9207`, `073e5399`) removed 24 floating black specks from the north/south facings and stopped the east trim eating the beasts' tails. **No detached black mark anywhere near an animal**, and on east the dewbacks, rontos and banthas end in a tail rather than a straight vertical cut. ⛔ The Chariot's single dewback is DELIBERATELY still short-tailed — its band cannot hold the full tail without shrinking the animal, and that was decided by looking; **Architect ▸ Props and Decor** for the `VFEPD_*` twins | CHECK **C39** only — ⛔ **C41 is NOT collectable this load** | 🔴 **CORRECTED 2026-08-22 — THE TEXT PASS SHIPPED AND THIS ROW SAID THE OPPOSITE.** `VEHICLE_IDENTITY_TEXT_PASS_1` landed at `88f9fe43`, deployed. This cell used to say the beast names DO NOT EXIST YET and that seeing `Ox cart`/`Chariot` was the expected result — following it now would file today's work as a failure. **Expect, verbatim:** `dewback chariot` · `dewback war chariot` · `ronto wagon` · `bantha cart` · `eopie sled`. ⚠️ Three of those names differ from the ones this row predicted — it guessed `dewback cart`, `bantha dray`, `dewback war cart`. **Read what is on screen, not what was predicted.** `Chariot` · `Ox cart` · `Covered Carriage` · `War chariot` · `Dog Sled` must appear **zero** times. ✅ **And the architect menu is now a REAL second check rather than the only one**: every vehicle is two defs, and the `_Blueprint` half was patched this time — it had been carrying "Dog Sled … over ice and through snow" in the build menu since 2026-08-15. 🔑 **A Vehicle Framework vehicle spawns as a PAWN** — `jawa/list_things` returns nothing at the cell, use `jawa/list_pawns`. 🔴 **The art reaches every def by texPath override whether or not a patch ran** — only the LABEL and the per-def COLOUR are evidence. The **architect menu is still worth reading**, but ⚠️ its old reason is dead: it said the blueprint was "a third def the sled pass never touched", and as of `88f9fe43` every `_Blueprint` IS patched. It is now a second independent confirmation, not the only one. ⛔ Do not check west (auto-mirrored from east) |

#### 🌱 L6 — plant growth. **A SECOND MAP, and it is the point.** CHECK **C38**

Do this last: it needs its own quicktest, and then **a second one on `PoisonForest`**.
A biome branch cannot be tested by walking across the first map.

1. **Startup log first** — `[JawaPlantGrowth] scaling <N> plant defs (default x4, tree x2.5), <M> exempt, 1 terminator biome(s) at x0.4.` 🔴 **This line is the only positive evidence the assembly ran.** Absent ⇒ the answer is *"not deployed / not in ModsConfig"*, **not** *"no effect"*, and nothing below it means anything.
2. Map 1 (temperate/arid): spawn `Plant_Corn` and `Plant_TreeOak` side by side on fertile soil, read growth %, run one in-game day, read again. **The corn must be roughly 4× the oak's growth percentage** (~36% vs ~8%). Near 1× ⇒ the tree band is not firing.
3. Same map: spawn `Plant_TreeAnima` — it must read ~4% after that day, **not** ~10%. That is the exemption.
4. **Map 2, generated fresh on `PoisonForest`** (Advanced Biomes): same two plants, same day. 🔴 **The corn gains ~10%, LESS than map 1 and less than vanilla's ~8.8% would be an increase over.** Slower, not faster. **This is the check most likely to be skipped and the only one that proves the biome branch runs at all.**

⚠️ A 0% reading is not evidence — the postfix returns early on `__result <= 0`
(night, out of temperature band, unlit). **Read growth in daylight, in season.**
⛔ Not in scope: wild-plant REPOPULATION. `wildPlantRegrowDays` is R-G4, it did not
ship, and a burnt PoisonForest staying bare proves nothing about this patch.

#### 🔴 L3's procedure — IL-confirmed. Follow it verbatim.

**The faction you pass is not the faction that raids.**
`IncidentWorker_RaidEnemy::TryResolveRaidFaction` keeps your faction **only if**
non-null AND `FactionUtility::HostileTo(Faction.OfPlayer)` AND (`!deactivated` OR
`parms.forced`). Otherwise `ldflda IncidentParms::faction` goes **by reference**
into `PawnGroupMakerUtility::TryGetRandomFactionForCombatPawnGroupWeighted`,
**which overwrites it.** ⇒ if ~~`OuterRim_GalacticEmpire`~~ **`Empire`** (⛔ the vessel
changed 2026-08-20 — `infrastructure/state/OWNER_DECISIONS.md`) is not hostile, the raid
fires, reports `success:true`, and you photograph **a different antagonist**.
Nothing in the reply flags it.

1. ~~`jawa/fire_incident incidentDef=RaidEnemy faction=OuterRim_GalacticEmpire dryRun=true`~~ ⛔ **DEAD 2026-08-20 — wrong vessel.** Use `jawa/fire_incident incidentDef=RaidEnemy faction=Empire dryRun=true` — **abort on `canFireNow:false`.** ⚠️ `Empire` is hostile only once `GalacticEmpire.xml`'s `permanentEnemy` Add has landed; a `canFireNow:false` here is more likely a deploy miss than an engine problem.
2. Fire, then **read the `faction` field in the REPLY, not the one you sent.** The tool reports `parms.faction` *after* the worker ran; the read-back is the only evidence of which faction actually came.
3. **Pass `points` explicitly.** `points<=0` takes the storyteller default — tens of points on a fresh quicktest, i.e. one trivial attacker, which cannot answer *"does the Empire read as an antagonist"*.

📌 **Generalises: a parameter you pass is not a parameter that survives.** Engine
workers take `IncidentParms` **by ref** and rewrite it. **Assert on the value read
back, never the value sent.** Same shape as `jawa/set_terrain`, where the bridge
**silently drops** an unknown parameter name — `def=` instead of `terrainDef=`
paints nothing and reports no error.

#### 👁️ EYES-ON, observation only — open the xenotype picker and LOOK

Two `iconPath` warnings that **cannot** be settled offline: vanilla textures live
in asset bundles, so a right path and a wrong one look identical from outside.

| look at | path |
|---|---|
| xenotype **`Jawa_Xeno_Gamorrean`** | `UI/Icons/Xenotypes/Pigskin` |
| gene **`Jawa_Head_Plain`** | `UI/Icons/Genes/Gene_Hair` |

**A pink or blank square is the defect. Both drawing closes them permanently.**
One screen, no map required.

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
is what `ORDERS_DESIGNATORS_ENUMERATE_ZERO_1` turned out to be.

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
## 🎨 §22 — THE CREATURE ART IS ON THE ADULT PATHS NOW. Deployed; needs only eyes on it.

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
> is launched. The first thing to do in the new session is `--list-tools` and confirm 165 — the
> live list is the only proof; a build that compiled is not a tool the bridge serves.


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


## 🔬 §23 THE FOUR ROWS THAT BECOME RUNNABLE THE MOMENT `jawa/pawn_stats` LANDS

Written 2026-08-26 by CHECK. **One command runs the whole block:**

```
python.exe D:\Luke\dev\Rimworld\src\RimMandrake\bridgetools\prove_stat_and_room.py
python.exe ... prove_stat_and_room.py --census                 # stop after the tool census
python.exe ... prove_stat_and_room.py --rect 170,170,18,10     # add the room checks
```

🔑 **Its first check is the only one that matters until it passes:** does the running game register
165 `jawa/` tools, and are `jawa/pawn_stats` and `jawa/room_get` in the LIVE list. Companions are
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
