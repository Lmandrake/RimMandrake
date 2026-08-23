# NEXT_RELOAD.md — THIS load's payload

> 🔑 **Standing procedure is NOT here — it is `infrastructure/state/LOAD_PROCEDURE.md`**
> (§1 the down window · §2 harvest the startup log · §3 the tool-surface census · §7 gates
> that cannot be collected · §8 unlock pawns · §9 after the load). Numbers are one shared
> sequence across the two files and are **deliberately not renumbered**, because other docs
> cite them.
>
> ⛔ **This file holds only what is TRUE OF THE NEXT LAUNCH and dies when that launch is
> scored.** Split out 2026-08-23 under `RUN_SHEET_PER_LOAD_BLOCKS_1`, after the file twice
> accumulated a spent load's header at the top — the second time announcing a red gate that
> had already gone green, which sent the next launcher to stop at a green light.

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

🔴 **WHEN A LOAD IS SCORED:** move its block whole into
`infrastructure/state/NEXT_RELOAD_ARCHIVE.md` with its result, and delete its index row.
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

## 10. 🧪 INHABITED — ⛔ NOT a first run any more. Owner: *"full 578 now, minimal after"*, 2026-08-20

> 🔴 **`Inhabited` is NOT a first run.** It ran on 2026-08-21/22 and loaded **193 of 294**
> characters, because all 101 CharacterDefs carrying a `<skills>` block were discarded at def
> load. ✅ The fix has landed and regenerates byte-identical.
>
> 🔑 **The baseline below is valid ONLY if `[Inhabited] ready:` reads 294.** If it reads
> **193**, the fix did not reach the game: **stop, and no number in this section counts.**
> ⚠️ **Do not delete this sequence.** The first-run test is the right test — it was the
> ORDERING that broke; it has to run after the cast fix, not before.

**On THIS load (578).** Reach a quicktest colony, then dev menu → **Inhabited**:
`Create place at current tile` → `Stuff roster (3 pawns)` → `Report roster`.
Write down the three **ThingIDs, names, relations count, hediff count** — that is the
baseline the whole architecture gate is measured against.
⭐ **The positive sighting matters more than a clean log**: a mod that loads and does
nothing logs nothing. If the `Inhabited` category is absent from the dev menu, the DLL did
not load and no other Inhabited result this load means anything.
Three first-run failure signatures are written at §4 of `EXPECTED_FAILURES_next_load.md`.

**AFTER, on minimal.** `ModsConfig.MINIMAL.xml` is now **14** — `mandrake.inhabited` added
last (it patches vanilla and needs Harmony). Ideology and `brrainz.rimbridgeserver` were
already in it, so `Patch_BeggarsFromPool` has a real target and the bridge works.
```
python3 src/RimMandrake/Utils/modlist_swap.py --minimal --apply
```
🔴 **Disarm the dump before that swap** — `rm DefDump/dump_request.txt`. A dump captured on
a 14-mod debug list reports every real mod's defs as *"does not exist in the live game"*.
🔴 **`--restore` before the owner plays.** Leaving his machine on 14 mods is the one
unacceptable outcome.
**Why minimal, in one number:** `ROSTER_SURVIVES_OFFMAP_PROOF_1` needs save → quit → RELOAD,
so it costs **two** loads. ~45 s on minimal against ~50 min on the 578.

---

## 🌱 BIOME FLORA + 🏷️ PLANT NAMES — deployed 2026-08-23, never yet loaded

Two patches in `Jawa_Patches/Patches`, both verified byte-identical to the repo copy.
Defs parse only at startup, so nothing about either is true until a cold load.

| | |
|---|---|
| `BiomeFlora_Ashkarr.xml` | 24 biomes, 604 plants, every one distinct across the 8 families |
| `PlantTolerances_Ashkarr.xml` | 🔴 **added 2026-08-23, MUST ship in the same build** — 577 plants refitted onto Ash'karr's climate. Without it 642 of 669 plants stop at 0 °C, half the planet is colder, and a CORRECT roster grows nothing. **Score the flora only if this is deployed too**; otherwise the flora result is void, not a fail. `PLANT_TOLERANCES_DEPLOY_1` |
| `PlantNames_Ashkarr.xml` | 26 Earth crop/tree **labels** become Star Wars names |

**Score in this order:**

1. 🔴 **`BiomeDef` count must still be 80.** An `<li>` in a `LoadDataFromXmlCustom` field
   discards the WHOLE def silently — that is how 26 BiomeDefs were lost on 2026-08-23. Both
   patches use the dictionary-key form to avoid it, but **the count is the proof, not the
   intent.** 54 means it happened again.
2. **Zero `Could not resolve cross-reference` naming a plant.** All defNames were checked
   against the live dump before deploy, so a hit means a mod moved underneath us.
3. **Zero red errors naming either file.** Every op is wrapped in a Conditional, so an absent
   def is skipped rather than erroring.
4. **Then LOOK.** A map in `Desert` (drago tree, saguaro, agave, hardy grass), `HorrorWastes`
   (horrorweb, blood bouquet, flesh tree — 🔴 **agave means the patch did not apply**) and
   `AB_MycoticJungle` (agarilux, domecap, devilstrand). In any growing zone, `corn plant`
   should read **kessel grain**, `haygrass` **bantha fodder**, `cotton plant` **silkstrand**.

⚠️ **A stale LABEL is the silent failure** — the Conditional swallows a miss, so a name that
did not change means that xpath did not match.

⚠️ **A biome reading BARE is not a failed patch.** 650 of 669 plants stop at
`minGrowthTemperature` 0 °C and half this planet is below that. Judge the patch by the ROSTER
a biome holds, not by what has sprouted; `NORMALIZE_TEMPERATURE_TOLERANCES_1` makes them grow.
⚠️ `ExtremeDesert` (0.008) and `Wasteland` (0.0099) read bare at any roster — 22.6% of the
planet. See `BARE_BIOMES_NEED_DENSITY_1`.

⚠️ **`PlantNames_Ashkarr.xml` was hand-copied**, not deployed by `deploy_custom_mods.py`:
BUILD had uncommitted edits in the same mod and the tool has no per-file flag.
