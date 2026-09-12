# SHEET_ORPHAN_CONSUMPTION_1 — spec steps 1–2 audit (READ-ONLY)

Produced 2026-09-12. **Nothing was written outside this file.** No roster, def,
decisions json, ledger, bridge or git state was touched; no `--apply` was run.

Sources of truth used:
- `design/Jawa/worldbuilding/review/fauna_assignment_register.decisions.json` (828 rows, savedAt 2026-09-10T07:02:31-0700)
- `design/Jawa/worldbuilding/review/flora_assignment_register.decisions.json` (288 rows, savedAt 2026-09-10T18:41:42-0700)
- `design/Jawa/worldbuilding/review/apply_assignment_verdicts.py` (the consumer, 863 lines)
- `design/Jawa/worldbuilding/biomes/rosters/*.json` (31 files, live)
- `git log --since=2026-09-10` over `design/`, `infrastructure/state/items/`, `src/`

**Classification legend**
- `APPLY` — the sheet verdict is still correct and still unconsumed on disk.
- `SUPERSEDED-BY <sha|item>` — a post-09-10 ruling changed or overrode the row.
- `ALREADY-DONE` — the state the verdict asks for is already on disk.
- `UNRESOLVED` — searched, no evidence either way.

---

## Channel summary (detail in the sections below)

| § | channel | rows | APPLY | SUPERSEDED | ALREADY-DONE | UNRESOLVED |
|---|---|---|---|---|---|---|
| 0 | sizeBin rescale worklist (fauna) | 29 | 29 | 0 | 0 | 0 |
| 0 | sizeBin rescale worklist (flora) | 3 | 3 | 0 | 0 | 0 |
| 1 | fauna `decision=out` | 6 | **6** | 0 | 0 | 0 |
| 2 | flora `decision=move` | 15 | **14** | 0 | **1** | 0 |
| 3 | flora `decision=out` | 4 | **4** | 0 | 0 | 0 |
| 4 | commission ledger `decision=in` | 118 | ~91 | ~20 owned elsewhere | **7 built** | 0 |
| 5 | flora `art:improve` | 148 | **145** | **3** | 0 | 0 |

**Three corrections to the item file, all MEASURED:**
1. §4 — "no … entry references any of the 118 concept slugs" is **false**: 7 are
   already built as live defs, ~20 more are owned by named post-09-10 items.
2. §3 — "no `flora_purged` record" is imprecise: the key exists in 29 rosters with
   198 rows from another lineage; what is absent is a record for these 4 defNames.
3. §1 — the 6 fauna cuts were **re-ruled and widened** on 2026-09-11 (`cf0632c39`),
   not superseded. Nothing in this audit found a later ruling that *reverses* a
   sheet row; the supersessions found all *strengthen* or *relocate* them.

---

## 0. SIZEBIN — the UNKNOWN, RESOLVED

### VERDICT: **genuine unconsumed orphan.** Not covered by `FAUNA_TOLERANCE_NORMALIZATION_1`.

**MEASURED, by re-running the applier's own selection logic offline against the
decisions json** (`decision in ("in","move")` AND `sizeBin != sizeBinPrefill`):

| sheet | rows where the owner changed the size bin |
|---|---|
| fauna | **29** (12 biome-rostered + 17 homeless) |
| flora | **3** (all `the_rot`) |

The 29 fauna rows (confirming the item file's "~29"):

Dianoga (large→titan, the_greentide) · AA_Mantrap (medium→large, the_miasma) ·
AA_Plasmorph (medium→large, the_miasma) · RSW_Faa (medium→small, the_miasma) ·
AA_Agaripod (large→titan, the_rot) · AA_Wildpod (large→titan, the_rot) ·
Ling_Cockroach (medium→small, the_rust_cathedral) · RSW_SandoAquaMonster
(titan→large, the_scald) · SW_Electricgryllotalpa (large→medium, the_scarlands) ·
SW_Electrictick (medium→small, the_scarlands) · VFEI2_Boomtick (medium→small,
the_scarlands) · AA_GreenGoo (large→titan, the_slime) · AA_Locusts (medium→small,
homeless) · AA_SmallButterfly (medium→small) · BMT_AaroxisDendoriaLarvae
(medium→blank) · BMT_CaveLemming (large→small) · BMT_JewelBeetlePupa
(medium→blank) · BMT_Megapleura (large→medium) · BMT_MutatingTumorfishSpawn
(medium→small) · BMT_Stoneback (medium→small) · BMT_TruffleMole (medium→small) ·
GR_AnimusHare (medium→small) · GR_ParagonThrumbo (large→titan) · RSW_CrimsonOpee
(large→titan) · Rikknit (medium→small) · Stintaril (medium→small) · TetnissCrab
(medium→small) · VFEI2_Macrofly (medium→small) · VFEI2_Silverfish (large→titan).

Flora: AB_AgaricusDomeCap (medium→large) · AB_ArbuscularMycorrhiza (large→titan) ·
AB_GlowingAgarilux (medium→large), all `the_rot`.

### Evidence the sidecar is an orphan

1. **The file has never existed.** `apply_assignment_verdicts.py:552` writes
   `<sheet>.size_rescale_worklist.json` via `_side()`, reachable **only inside
   `apply_all()`**, i.e. only under `--apply`. No such file is on disk
   (`ls design/Jawa/worldbuilding/review/*size_rescale*` → no matches) and
   `git log --all -- "…*size_rescale*"` returns **zero commits**. The applier's
   `--apply` was never run on either sheet.
2. **Only three references exist in the whole repo** (`grep -rn size_rescale_worklist`):
   the applier's docstring (line 52), the `_side()` call (line 552), and its own
   selftest (`selftest_apply_assignment_verdicts.py:167`). Plus the item file.
   **No item, doc, manifest or generator consumes it.**
3. **`FAUNA_TOLERANCE_NORMALIZATION_1` does NOT cover it** — it explicitly
   excludes bodySize. Its RULED §4 (owner, 2026-09-11) says verbatim:
   > *"Does NOT change: bodySize itself, per the ceiling-fields lesson (each
   > parameter its own law)."*
   Its "Law 3" is **damage ≈ K×bodySize**, i.e. bodySize is the *input*, never
   the output. Law 5 is temperature, Law 6 is products. None writes a size.
4. **The one law that does write bodySize is a different instrument and is
   gated.** `design/Jawa/worldbuilding/beast_normalization_spec.md` §2 Law 1:
   `bodySize = (drawSize/1.9)²`, *"Gated on finding 3's capture fix"*
   (= `DUMP_DRAWSIZE_CAPTURE_1`), and §3 lists *"bodySize when Law 1 unlocks"*
   as a future manifest column. Law 1 derives size **from the existing art**;
   the owner's sizeBin verdicts say **what the size should be**. They are not
   the same channel.
5. **No bodySize change has landed for any of the 29.** The only `src/` hits for
   these defNames alongside `bodySize` are read-only *comments* in
   `src/RimUtinni/Doctrine/Patches/MegafaunaYield.xml` (Law 6 products, which
   *reads* bodySize: e.g. `<!-- Dianoga MeatAmount: bodySize 4.00 … -->`).
   Zero of the 29 appear in `infrastructure/artpipe/registry.jsonl`.
6. `BEAST_MASS_REALISM_AUDIT_1` (closed, 2026-08-31) is about `statBases/Mass`
   and concludes mass is definitionally `60 × bodySize` — it changes nothing and
   predates the sheet.

### 🔴 Collision risk to record before anyone runs Law 1

If `DUMP_DRAWSIZE_CAPTURE_1` unblocks and Law 1 is executed naively, it sets
bodySize from **current drawSize** — which would silently overwrite all 29 owner
size rulings without ever reading them. Whoever unlocks Law 1 must take the
sizeBin worklist as an **exemption/override list**, not discover it afterwards.
Also note MegafaunaYield.xml (Law 6 products) is already derived from the
*pre-rescale* bodySizes, so any size change re-opens that patch.

---

## 1. fauna `decision=out` — 6 rows

Scope note: the applier does **not** send these to a cherry-pick cut list. For
`kind == "fauna"` + `decision == "out"` (lines 386–398) it removes the def from the
source roster and appends to that roster's `evictions` with
`disposition: "homeless-reserve"`. Only `kind == "homeless"` rows reach
`plan.cut_list`. **The 2026-09-11 card ruling is stronger than that channel** —
it says *delete*, not *reserve*.

| defName | sheet | state on disk | classification | evidence |
|---|---|---|---|---|
| `BMT_CaveSpider` | the_rot | present in `the_rot.json` (+`the_scarlands.json`) | **APPLY** — reinforced | `cf0632c39` (Card sitting 2026-09-11, into `BMT_FAUNA_ABSORPTION_1.md`): *"**The 7 stragglers are CUT** … `BMT_CaveSpider`, `BMT_GiantSlug`, `BMT_GiantSnail`, `BMT_Pillbug`, `BMT_GlowBat`): delete their live biome entries … They are NOT added to the port."* |
| `BMT_ChemSnail` | the_rot | present in `the_rot.json` **and** `the_cracked_lands.json` | **APPLY — and the later ruling WIDENS it** | Same ruling, verbatim: *"`BMT_ChemSnail` at **BOTH** `the_cracked_lands` and `the_rot`"*. The sheet only cut the_rot; `decisions_propagated.json` still carries `fauna:the_cracked_lands:BMT_ChemSnail` as `decision: in` (propagated) — **that propagated row is SUPERSEDED-BY `cf0632c39`.** |
| `BMT_GiantSlug` | the_rot (+`the_forge.json`) | present | **APPLY** — reinforced | `cf0632c39` as above |
| `BMT_GiantSnail` | the_rot (+`the_forge.json`) | present | **APPLY** — reinforced | `cf0632c39` as above |
| `BMT_Pillbug` | the_rot (+`the_rust_cathedral.json`) | present | **APPLY** — reinforced | `cf0632c39` as above |
| `AA_FissionMouse` | wasteland | present in `wasteland.json` (and 13 other rosters) | **APPLY** | No post-09-10 ruling found. `git log --since=2026-09-10 -S"AA_FissionMouse"` returns only `097ec3110` (RESTORE_FALLOUT_TRIAGE_1 duplicate fix), `688bddbb2` (ROSTER_MOVE_APPLY_1, fauna moves only) and `919d5c155` (this item's own filing). None rules on the verdict. |

**Counts: APPLY 6 · SUPERSEDED 0 · ALREADY-DONE 0 · UNRESOLVED 0.**

### 🔴 Three traps on this channel

1. **The cut ruling's home item is BLOCKED.** `BMT_FAUNA_ABSORPTION_1` is
   `block`ed in the ledger (last events `2026-09-11T07:47:39Z block`,
   `15:56:36Z note`, `15:59:37Z block`) with an escalation that the donor mod
   name itself is wrong (`mlie.beastsoftherim` vs `biomesteam.*`). So the ruling
   *"FOUNDRY executes with the rest of this item"* is parked. The roster-side
   removal is nevertheless independently ruled twice (sheet + card).
2. **There is a THIRD instrument still saying the opposite.**
   `design/Jawa/fauna/cast_assignment.csv` still carries all five as
   `import`/`keep` with round-1 §7b reasons (lines 46, 49, 51, 58, 60), plus
   `AA_FissionMouse` at line 332 as `import` ("wasteland: §9 (binding): RESKIN →
   the radiotroph archetype"). Its last commits are `a72757b9d` /
   `e2b1262d3` / `e62125946` — all post-09-10, and **none of them applied the
   out verdicts.** Any consumption pass must touch rosters *and* this CSV or the
   deck will lie (ROSTER_MOVE_APPLY_1 §6: *"Every ruling lands in THREE files
   together or the deck lies"*).
3. `BMT_GlowBat` is in the card ruling's cut list but is **not** one of the six
   sheet rows — it comes from the bat cull. Do not drop it when scoping the work.

---

## 2. flora `decision=move` — 15 rows

`ROSTER_MOVE_APPLY_1` (ledger: filed 2026-09-11T05:19, **closed 07:01**) states
at line 34: *"Flora is NOT in scope: its 15 move rows have no structured targets
yet — 6 need …"*. So the closed move item did **not** consume this channel.

`design/Jawa/worldbuilding/review/round2/flora_move_mapping.md` supplies targets
for 6 of the 15 and claims at its foot: *"Consumed by `ROSTER_MOVE_APPLY_1`
alongside `move_mapping_v2.md`."* **That claim is false** — measured below.

Source/target state measured from the live roster JSONs:

| defName | source sheet | owner's note (verbatim) | target | still in source? | in target? | classification |
|---|---|---|---|---|---|---|
| `AB_CrystalHorn` | poison_forest | "propane lakes and blue desert only" | the_propane_lakes ✓ / the_blue_desert | **yes** | propane **yes**, blue desert **no** | **APPLY** (remove src, ADD the_blue_desert) |
| `AB_GiantGamma` | the_forge | "to crags" | forsaken_crags | **yes** | **yes** | **APPLY** (source removal only) |
| `AG_Gamma` | the_forge | "to crags" | forsaken_crags | **yes** | **NO** | **APPLY — 🔴 mapping doc is WRONG** (see below) |
| `AG_Septimum` | the_forge | "elsewhere, not heat resistant" | (unparseable) | **yes** | **NO** | **APPLY — 🔴 mapping doc is WRONG** (see below) |
| `AB_CrystalFlower` | the_propane_lakes | "This was placed elsewhere, so it can't also be here…" | poison_forest (keep) | **yes** | **yes** | **APPLY** (source removal only) |
| `AB_HardyGrass` | the_pyrelands | "the grass here has to be unique" | — (evict) | **no** | — | **ALREADY-DONE** — `b40cadf81` ("all generic grasses evicted from Pyrelands per owner ruling"). `the_pyrelands.json` flora is now exactly `['RM_FE_Plant_Quickgrass']`. |
| `BMT_Nogtyl` | the_rot | "miasma" | the_miasma | **yes** | **no** | **APPLY** |
| `BMT_RustPuff` | the_rot | "The Contagion… and hatches occular creature when damaged" | the_contagion | **yes** | **no** | **APPLY** |
| `AB_SlimyPholiota` | the_slime | "only the rot" | the_rot | **yes** | **yes** | **APPLY** (source removal only) |
| `AB_GiantToxicFlower` | wasteland | "poison forest" | poison_forest | **yes** | **no** | **APPLY** |
| `AB_ToxiGrass` | wasteland | "blue desert rare" | the_blue_desert | **yes** | **no** | **APPLY** (note: "rare" = low commonality, not carried by the applier) |
| `BMT_Plant_Doomsprout` | wasteland | "poison forest" | poison_forest | **yes** | **no** | **APPLY** |
| `BMT_Plant_EclipsusLeaves` | wasteland | "miasma" | the_miasma | **yes** | **no** | **APPLY** |
| `PoisonPlantTallGrass` | wasteland | "blue desert rare" | the_blue_desert | **yes** | **no** | **APPLY** |
| `PoisonShrub` | wasteland | ".8 cells, propane lakes" | the_propane_lakes | **yes** | **no** | **APPLY** ("`.8 cells`" is an unconsumed density instruction with no field) |

**Counts: APPLY 14 · SUPERSEDED 0 · ALREADY-DONE 1 · UNRESOLVED 0.**

### 🔴 `flora_move_mapping.md` would DELETE two plants from the world

Rows 12 and 13 of `design/Jawa/worldbuilding/review/round2/flora_move_mapping.md`
say:

> `flora:the_forge:AG_Gamma` | to crags | REMOVE from the_forge (**already in forsaken_crags**)
> `flora:the_forge:AG_Septimum` | elsewhere, not heat resistant | REMOVE from the_forge (**already in forsaken_crags** — "elsewhere" satisfied)

**MEASURED, false.** Across all 31 roster JSONs:
- `AG_Gamma` → `the_forge.json` **only**
- `AG_Septimum` → `the_forge.json` **only**
- `AB_GiantGamma` → `forsaken_crags.json` + `the_forge.json`
- `AB_GiantSeptimum` → `forsaken_crags.json`

The mapping author conflated the `AG_*` pair with the `AB_Giant*` pair. Executing
the mapping literally removes `AG_Gamma` and `AG_Septimum` from the only roster
that holds them — a silent world-tier deletion. **These two rows need an owner
target before any apply.** (`AG_Septimum`'s note "elsewhere, not heat resistant"
names no biome at all; the applier would refuse it with
`"Move but the note does not name one unambiguous biome"`.)

The mapping's other four rows check out: `AB_GiantGamma` and `AB_CrystalFlower`
are genuinely already in their stated targets, `AB_CrystalHorn`'s propane-lakes
half is present (only the blue-desert ADD is owed), and `AB_HardyGrass` is done.

---

## 3. flora `decision=out` — 4 rows

The applier (lines 391–399) writes these to the source roster's `flora_purged`
list. That key **does exist** in 29 of 31 rosters with 198 rows total — but it is
a *different lineage* (kit-spec donor purges: `VEE_*`, `GRim*`, vanilla wholesale).
**None of the four sheet rows is in any `flora_purged` list**, and all four are
still live `flora` entries:

| defName | sheet | in `flora`? | in `flora_purged`? | classification | evidence |
|---|---|---|---|---|---|
| `AB_DessertTree` | desert | **yes** | no (25 rows checked, absent) | **APPLY** | `git log --since=2026-09-10 -S"AB_DessertTree"` over `design/…/biomes/` + `items/` returns only `919d5c155` (this item's own filing). No later ruling. |
| `AB_EyeGrass` | the_contagion | **yes** | no | **APPLY** | same — only `919d5c155` |
| `Boomshroom` | the_rot | **yes** | no (`the_rot.flora_purged` = `['BMT_Blastpod']` only) | **APPLY** | same — only `919d5c155` |
| `PoisonPlantBush` | wasteland | **yes** | no (18 rows checked; the purged `Poison*` set is `PoisonAlocasia, PoisonRafflesia, PoisonMushroom, PoisonPlantDandelion, PoisonPlantRaspberry, PoisonPlantTreeCecropia, PoisonTreeCypress, PoisonTreePalm, PoisonPlantTreeTeak, PoisonTreeWillow` — **not** `PoisonPlantBush`) | **APPLY** | `105c4746b` (LOCKJAW_ART_WIRE_IN_1) touches the same file but rules nothing on this def |

**Counts: APPLY 4 · SUPERSEDED 0 · ALREADY-DONE 0 · UNRESOLVED 0.**

⚠️ Correction to the item file: it says "no `flora_purged` record". The *key*
exists and is populated from another source; what is absent is a record **for
these four defNames**. An apply must append, never initialise.

---

## 4. NEW-ART/DEF commission ledger, `decision=in` — 118 rows

All 118 `ledger:*` rows live in the **flora** decisions file (the fauna file has
zero `ledger:` rows); all 118 are `decision: in`; they span **27 sheets**. The
applier's channel for them is `plan.art_queue` with `kind: "commission"`
(lines 364–371) → the `<sheet>.art_queue.json` sidecar, which — like the size
worklist — **has never been written** (no file, no commit).

### 🔴 The item file's claim for this channel is WRONG

> *"no ART_REGEN_WAVE item, commission item or artpipe registry entry references
> any of the 118 concept slugs"*

**At least 7 are fully BUILT — defs on disk, verified by reading the XML:**

| slug | sheet | what shipped | evidence |
|---|---|---|---|
| `cindermare` | forsaken_crags | `RSW_Cindermare` ThingDef **and** PawnKindDef | `src/RimStarWars/SWBestiary/Defs/Livestock/ThingDefs_Animals/ThingDefs_ForsakenCrags.xml` + `.../PawnKindDefs/PawnKindDefs_ForsakenCrags.xml`; items `FORSAKEN_CRAGS_PREDATORS_BUILD_1`, `FORSAKEN_CRAGS_FAUNA_1`. **Built 2026-09-01 — predates the grading**; the register re-surfaced an already-built concept as new. |
| `skarnix` | forsaken_crags | `RSW_Skarnix` ThingDef + PawnKindDef | same files / same items; same pre-dating caveat |
| `fire-hawk-twig-carrying-raptor-analog` | the_pyrelands | `RUT_FireHawk` ThingDef + PawnKindDef, plus a think tree (`RUT_FireHawkThinkTree.xml`) and job defs | `src/RimUtinni/UtinniPatches/Defs/ThingDefs_Races/RUT_PyrelandsFauna.xml`; art in `infrastructure/artpipe/done/pyrelands_firehawk_v1*.json`; commit `9406d5e08`, item `PYRELANDS_FIRE_WEB_COMMISSION_1` |
| `furnace-beast-thermal-circuit-megafauna` | the_pyrelands | `RUT_FurnaceBeast` ThingDef + PawnKindDef (+ `RUT_FurnaceHide` item) | same file; art in `infrastructure/artpipe/done/pyrelands_furnacebeast_v1*.json`; commit `9406d5e08` |
| `quickgrass-rakatan-feral-forage-crop` | the_pyrelands | `RM_FE_Plant_Quickgrass` | `src/RimMandrake/Pyrelands/Defs/ThingDefs_Plants/Quickgrass.xml`; commit `b40cadf81`, built **and deployed** |
| `scorch-fruit-plant-yield` | the_pyrelands | `RM_FE_Plant_ScorchFruit` + `RM_FE_ScorchFruitYield` | `src/RimMandrake/Pyrelands/Defs/ThingDefs_ScorchFruit/ScorchFruit.xml`; items `PYRELANDS_SELF_CONTAINED_BIOME_1`, `FIRE_ECOLOGY_LOOP_1` |
| `living-bolts` | the_rust_cathedral | `RUT_LivingBolt` ThingDef (line 219) + PawnKindDef (line 290), plus `RUT_BoltFrame` and a think tree | `src/RimUtinni/RustCathedralHum/Defs/ThingDefs_Races/RUT_LivingBolt.xml`, `.../ThinkTreeDefs/RUT_ThinkTree_LivingBolt.xml` |

### Counts

A keyword screen of **all 118** slugs (two longest distinctive tokens, proximity
match) against `infrastructure/state/items/**`, `src/**` and
`design/Jawa/worldbuilding/biomes/kits/**` (1,870 files, handoff and
code-review-loop files excluded):

| | rows |
|---|---|
| **ALREADY-DONE** (def on disk, individually verified) | **7** |
| **SUPERSEDED / OWNED-ELSEWHERE** (a named post-09-10 item or kit spec already owns the concept, build explicitly deferred) | **~20** (see below) |
| **APPLY** (no evidence of any consumer) | **~91** |
| **UNRESOLVED** | 0 rows carry contradictory evidence |

Screen results: **45 of 118 slugs produced at least one keyword hit; 73 produced
none.** ⚠️ The hit set contains false positives from generic tokens — e.g.
`nightside_ice:the-one-move-animal` (428 hits) and `the_rot:heat-generating-gene`
(92 hits) match common words, not the concept. **Treat the 45 as candidates to
check, the 73 as APPLY.** Per-sheet hits/total:

```
arid_shrubland 2/7 · desert 3/7 · dune_sea+deep_desert 3/8 · fall_line 1/3
forsaken_crags 2/4 · nightside_ice 1/6 · poison_forest 0/3
terminator_sea+the_grey_deep 1/5 · terminator_sea+the_twilight_deep 1/7
the_blue_desert 1/4 · the_contagion 1/1 · the_cracked_lands 1/4
the_fever_wood 1/4 · the_forge 1/3 · the_greentide 1/5 · the_miasma 3/5
the_propane_lakes 1/2 · the_pyrelands 4/5 · the_rot 4/5 · the_rust_cathedral 2/2
the_scald 2/3 · the_scarlands 3/3 · the_slime 1/1 · the_sump 0/4
the_webwork 1/4 · wasteland 2/5 · weeping_stones 2/8
```

### SUPERSEDED / OWNED-ELSEWHERE — named by a live item, build deferred

These are **not orphans**: a post-09-10 mechanics item or kit spec already names
the concept and explicitly parks its creature/art build on "the roster pass".
Filing them again as fresh commissions would double-book them.

- `the_rust_cathedral:coolant-eels` — `rust_cathedral_kit_spec.md` §3/eel-fishing
  and `RUT_RustCathedral.xml` name it as a roster exception; `RUST_CATHEDRAL_MECHANICS_1`'s
  own log says §4 eel-fishing is *still untouched*. **Verified: no `CoolantEel` def exists.** Named, not built.
- `the_sump:` tar-beast · wick-plant · sump-mouse · edge-chemotroph — all four
  scoped in `sump_kit_spec.md` (card sitting 2026-09-12), each deferred to the roster pass.
- `the_greentide:` gnawer · greatbole · shatterer — `greentide_kit_spec.md` (2026-09-11); creature defs punted.
- `the_fever_wood:` thornbug-nectar-beast · seep-oil · deep-thing — `fever_wood_kit_spec.md` §F4/F8.
- `the_miasma:` rainbow-flora-suite · warden-mother — `miasma_kit_spec.md`, `MIASMA_MECHANICS_1`, `RUT_Miasma.xml`.
- `the_scald:` bubble-sailor · silver-shoal — `scald_kit_spec.md`, `SCALD_MECHANICS_1`.
- `the_webwork:` egg-mite · pale-flowers · wyyyschokk-guild-pawnkinds — `webwork_kit_spec.md` (2026-09-11).
- `the_scarlands:plated-grazer…` — `scarlands_kit_spec.md` (scaria-onset section).
- `the_forge:tibanna-gland-harvest-on-the-beldon` — folded into `FORGE_MECHANICS_1` §F2
  (`forge_kit_spec.md`, 2026-09-11; `RM_CompGatherableGas` not yet built).
  `TIBANNA_SOURCE_CUT_1` separately cut other tibanna sources, ratifying beldon-only.

⚠️ **Do not conflate** `the_webwork:wyyyschokk-guild-pawnkinds-nettik-chirrik-rothrik`
with the "Wyyyschokk" row in `ART_REGEN_WAVE6_QUEUE_1` — that wave is an art redo
of the **pre-existing** Shokk creature, not this new guild-pawnkind concept.

### Confidence / what was not done

The 7 ALREADY-DONE rows were verified by reading the defs. The ~20
OWNED-ELSEWHERE rows come from a delegated sweep that individually verified ~20
slugs and whose broader grep timed out; the keyword screen above is mine and
covers all 118, but it is a **screen, not proof**. No `git log -S` per slug, no
savegame check, no row-by-row pass over `design/Jawa/fauna/cast_assignment.csv`.
**Before step 4 files this as an art queue, every slug with a keyword hit above
should get one targeted check** — 6 of the 7 already-built ones were found this way.

---

## 5. flora `art:improve` — 148 rows

**148 rows / 136 distinct defNames** (10 defNames span 2–3 biomes:
`AB_HardyGrass`×3, `Plant_Chakroot_Wild`×3, and ×2 each `AB_BloodBouquet`,
`AB_CrystalHorn`, `AB_GiantStikehr`, `BMT_Dewshrooms`, `BMT_Plant_Snaketails`,
`BMT_Plant_TreeTwistingThornwood`, `BMT_Sagecrust`, `Plant_HubbaGourd_Wild`).

| | rows | distinct defNames |
|---|---|---|
| **APPLY** | **145** | **134** |
| **SUPERSEDED** | **3** | 2 fully dead + 1 row of a surviving def |
| **ALREADY-DONE** | **0** | **0** |
| **UNRESOLVED** | 0 | 0 |

### ALREADY-DONE = 0, MEASURED

- `grep -F` of all 136 defNames against `infrastructure/artpipe/registry.jsonl`
  and `throughput.jsonl` → **zero matches** (case-sensitive and insensitive).
- The registry's only `source` values are `ART_REGEN_WAVE4_QUEUE_1` …
  `WAVE9_QUEUE_1` (22/21/21/21/9/9), `LOCKJAW_ART_WIRE_IN_1` (3), `backfill` (51),
  and 561 rows with no source — **all fauna**.
- `ART_REGEN_WAVE3_QUEUE_1.md` says in its own text that it checked the flora
  file and found *exactly one* `art: "redo"` row (`PoisonPlantBush`, whose
  `decision` is `out`, so not in the improve pool) — nothing eligible. Waves 4–9
  each define their pool as `fauna:<biome>:Name` keys only; flora and
  `homeless:*` were carved out by construction and never revisited. **No WAVE10+
  item exists.**
- `git log --since=2026-09-10` on plant `Textures/` folders shows PNGs added for
  AloeVera, BunnyEarsCactus, Echeveria, JadePlant, Peyote, PincushionPlant,
  Schlumbergera, SnakePlant, SweetheartPlant, FairyWashboard — an unrelated
  decorative-plant pack; **none matches any of the 136**.

This independently confirms the item file's claim for this channel.

### SUPERSEDED — 3 rows

| defName | row | classification | evidence |
|---|---|---|---|
| `Plant_YellowGrass` | `flora:the_pyrelands:*` | **SUPERSEDED-BY `b40cadf81` + owner card 2026-09-11** — and **fully dead**: absent from **every** roster JSON | `flora_move_mapping.md` row 16 records the owner verbatim: *"Plant_YellowGrass and Plant_YellowTallGrass are evicted from the_pyrelands too … Pyrelands ground layer = quickgrass + commissioned fire-chain flora only."* Verified: `grep -l '"Plant_YellowGrass"' rosters/*.json` → no matches. |
| `Plant_YellowTallGrass` | `flora:the_pyrelands:*` | same — **fully dead** | same; verified absent from all 31 rosters |
| `AB_HardyGrass` | the_pyrelands row only (1 of its 3) | **SUPERSEDED** for that row; the def survives | still live in `desert.json` and `the_cracked_lands.json` — its other 2 rows remain valid APPLY targets |

**Do not commission art for `Plant_YellowGrass` / `Plant_YellowTallGrass`** —
they exist in no roster on this planet.

### Flagged but NOT contradicted

The 9 flora `move` rows that also carry `art: improve` (`AB_CrystalHorn`,
`AG_Septimum`, `BMT_Nogtyl`, `AB_GiantToxicFlower`, `AB_ToxiGrass`,
`BMT_Plant_Doomsprout`, `BMT_Plant_EclipsusLeaves`, `PoisonPlantTallGrass`,
`PoisonShrub`) are all alive in some roster — the art verdict stands, only the
biome attribution on the register row is stale. The 4 flora `out` rows do **not**
overlap the improve list at all, so there is no conflict there.

### 🔴 The two flora decision files DISAGREE — and the waves read the wrong one

`ART_REGEN_WAVE3_QUEUE_1.md` lines 44–45 assert that
`flora_assignment_register.decisions.json` *"is byte-identical in content to
`round2/flora_decisions_propagated.json`"*. **MEASURED false — 14 of 288 rows differ.**

| | register (`review/flora_assignment_register.decisions.json`) | propagated (`review/round2/flora_decisions_propagated.json`) |
|---|---|---|
| `art: improve` | **148** | **162** |
| `art: redo` | **2** | **1** |

Commit `1caff3664` ("Flora verdict propagation: plant-level art/size inherit
across sibling rows, 0 conflicts") wrote the propagated file by inheriting a
plant's art verdict onto its sibling biome rows. It:

1. **Promoted 13 rows `keep` → `improve`** (all carry `inheritedFrom`):
   `the_fever_wood:AB_KeeningCordax`, `the_forge:AB_GiantGamma`,
   `the_greentide:BMT_GiantLeaf`, `the_greentide:Plant_HydenockTree_Wild`,
   `the_greentide:Plant_JoganTree_Wild`, `the_propane_lakes:AB_CrystalFlower`,
   `the_webwork:AB_Aaklac`, `the_webwork:AB_Gomphoeria`,
   `the_webwork:AB_JungleTree`, `the_webwork:AB_RedBugloss`,
   `the_webwork:Plant_TookeTrap_Wild`, `wasteland:BMT_Plant_ScorchedStars`,
   `wasteland:BMT_RainbowTongue`.
2. **DEMOTED one owner verdict**: `flora:the_slime:AB_SlimyPholiota` is
   `art: "redo"` in the register and `art: "improve"` in the propagated file
   (`inheritedFrom: flora:the_rot:AB_SlimyPholiota`). **The inheritance
   overwrote the stronger verdict with the weaker one** — which is exactly why
   WAVE3 reported *"exactly one `art: redo` row"* and skipped this plant.
   `AB_SlimyPholiota` is a second orphaned `redo`, never examined by any wave.

**Consequence for consumption:** the real flora improve pool is **162 rows** if
you take the propagated file (what every wave item reads), **148** if you take
the register (what the item file counts, and the owner's literal grading). Both
numbers are defensible; **pick one deliberately and say which**, and do not let
`1caff3664`'s "0 conflicts" claim stand — it silently resolved one.
`AB_SlimyPholiota` also happens to be a `move` row (§2 above) and an
`art: redo` row: it needs both treatments.

⚠️ **Caveat carried from the sweep:** Cherry Picker was checked only by grepping
the live `CherryPicker.SHIP.xml` for the 136 names (0 hits). Per this project's
own doctrine that instrument has **three** cut sources and `OWNER_EXCLUDE`
filters only one — a 0 there is suggestive, not proof. `plant_register.decisions.json`
was not walked row-by-row for additional post-09-10 supersession beyond the names
listed above.

---

## Appendix — what was NOT done

Per the task scope, only spec steps 1–2. **Not done:** step 3 (apply via
`apply_assignment_verdicts.py --apply` / by hand), step 4 (filing the 118-row
ledger as a real art queue), step 5 (freezing both decisions files). No
`_validate.py --cross`, no regeneration commands, no ledger or bridge action.
