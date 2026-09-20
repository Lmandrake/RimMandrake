# SHEET_ORPHAN_CONSUMPTION_1 — the sheet verdicts nothing ever consumed

The owner graded both assignment sheets on 2026-09-10 (fauna 828 rows / 291
overrides; flora 288 rows / 19 overrides — `ASSIGNMENT_SHEETS_VERDICT_SITTING_1`).
A channel-level provenance audit (BENCH subagent, 2026-09-12) found five verdict
channels that were graded and never landed anywhere. Sidecars:
`design/Jawa/worldbuilding/review/fauna_assignment_register.decisions.json` and
`flora_assignment_register.decisions.json`; consumer:
`design/Jawa/worldbuilding/review/apply_assignment_verdicts.py`.

## the orphans (MEASURED by the audit — re-verify each before acting)

| channel | rows | evidence |
|---|---|---|
| fauna `decision=out` (cut for real) | 6 | BMT_CaveSpider, BMT_ChemSnail, BMT_GiantSlug, BMT_GiantSnail, BMT_Pillbug still in `the_rot.json`; AA_FissionMouse still in `wasteland.json`; no cut-list sidecar ever written |
| flora `decision=move` | 15 | `ROSTER_MOVE_APPLY_1` says "Flora is NOT in scope"; 6/6 spot-checked (AB_GiantGamma, AG_Gamma, AG_Septimum, AB_CrystalFlower, AB_CrystalHorn, BMT_Nogtyl) unresolved despite `flora_move_mapping.md`'s claim |
| flora `decision=out` (purge) | 4 | AB_DessertTree, AB_EyeGrass, Boomshroom, PoisonPlantBush all still present, no `flora_purged` record |
| NEW-ART/DEF commission ledger (`decision=in`) | 118 | the sitting item says these verdicts "CREATE the art queue"; no ART_REGEN_WAVE item, commission item or artpipe registry entry references any of the 118 concept slugs |
| flora `art:improve` | 148 | WAVE3 examined only flora's single `redo` row; waves 4–9 draw exclusively from the fauna improve pool |

UNKNOWN: the sizeBin rescale worklist (~29 fauna rows where sizeBin differs from
prefill) — `apply_assignment_verdicts.py`'s `size_rescale_worklist` sidecar is
never written anywhere and no item references it. Not measured whether any
bodySize actually changed. Resolve it first: measured orphan, or consumed by the
Law-3 size scaling under `FAUNA_TOLERANCE_NORMALIZATION_1`?

## 🔴 the trap — the sheet is a superseded snapshot
Every orphaned verdict is checked against the rulings landed AFTER 2026-09-10
before it is consumed. Later sittings (09-11, 09-12: homeless dispositions,
bat cull, lisk cull, Hssiss, Wave-2 rulings, the card sittings) legitimately
overrode sheet rows. **The sheet never overwrites a newer decision.** Where a
sheet row and a later ruling disagree, the later ruling stands and the row is
recorded as superseded, not applied. Grep the roster json's history
(`git log -p --since=2026-09-10 -- design/Jawa/worldbuilding/biomes/rosters/`)
and the item files named above per row before writing.

## spec
1. Resolve the sizeBin UNKNOWN (measure, don't infer).
2. Per channel: diff the sheet verdict against post-09-10 state; produce a
   per-row table `defName -> APPLY | SUPERSEDED-BY <commit/item> | ALREADY-DONE`
   in `Transient/` for the owner to skim.
3. Apply via `apply_assignment_verdicts.py` (report first, `--apply` writes),
   or by hand where the applier has no channel for it (flora purge/move), then
   `_validate.py --cross`, then the regeneration commands it prints.
4. The 118-row ledger becomes a real art-queue filing (an ART_REGEN_WAVE item or
   the artpipe registry) — commission / defer / drop as graded.
5. Freeze both decisions files when done (`frozen-artifacts` skill).

## verify
- Each of the 6 fauna cuts and 4 flora purges is absent from every roster json
  (or explicitly SUPERSEDED with the ruling cited).
- The 15 flora moves resolve to a target roster each.
- 118 ledger slugs each appear in exactly one art-queue artifact.
- `serve_sheet.py --decisions <file> --status` shows `frozen: true` on both.

## criteria
Zero verdict channels of the 2026-09-10 sheets without a recorded consumer, and
zero later rulings overwritten by an older sheet row.

## 2026-09-12 (FOUNDRY, offline subagent, belt mode) — audit table built, NO writes made, needs owner calls before any apply

Read-only audit only (spec steps 1-2), deliberately stopped before any
`--apply`/roster write per this pass's own brief — the trap this item warns
about ("the sheet never overwrites a newer decision") is real enough that
the actual apply step needs a human decision on several rows, not a blind
run. Full per-row table: `Transient/sheet_orphan_audit_2026-09-12.md`.

**sizeBin UNKNOWN resolved: genuine unconsumed orphan**, not covered by
`FAUNA_TOLERANCE_NORMALIZATION_1` (its own RULED §4 says verbatim "Does NOT
change: bodySize itself, per the ceiling-fields lesson"). 29 fauna + 3 flora
rows, `size_rescale_worklist` sidecar has never once been written by
`apply_assignment_verdicts.py` in this repo's history.

**Channel counts** (APPLY / SUPERSEDED / ALREADY-DONE / UNRESOLVED):
sizeBin 32/0/0/0 · fauna out 6/0/0/0 · flora move 14/0/1/0 · flora out
4/0/0/0 · art/def ledger ~91/~20/7/0 (of 118) · flora improve 145/3/0/0.

🔴 **Five findings need an owner or BENCH call before any apply runs, not a
FOUNDRY judgment call**:
1. `flora_move_mapping.md` rows 12-13 (AG_Gamma, AG_Septimum) claim a target
   roster ("already in forsaken_crags") that is MEASURED FALSE — both plants
   only exist in `the_forge.json`. Applying as written would misfile or
   effectively delete them from the world. Needs a real target roster named.
2. The two flora decision files disagree with each other (14/288 rows) —
   `ART_REGEN_WAVE3_QUEUE_1` asserted they were byte-identical and was
   wrong; commit `1caff3664` silently demoted `AB_SlimyPholiota` from `redo`
   to `improve`, which is why WAVE3 only ever saw one redo row.
3. If `DUMP_DRAWSIZE_CAPTURE_1` unblocks and a naive Law-1 rescale runs from
   current drawSize, it will silently overwrite all 29 owner sizeBin
   rulings from this sheet. Flagging now so whoever builds that item reads
   this first.
4. The 118-row "NEW-ART/DEF commission ledger" is not a clean commission
   list — **at least 9 of the 118 slugs** are ALREADY BUILT live defs
   (`RSW_Cindermare`, `RSW_Skarnix`, `RUT_FireHawk`, `RUT_FurnaceBeast`,
   `RM_FE_Plant_Quickgrass`, `RM_FE_Plant_ScorchFruit`, `RUT_LivingBolt`,
   `RUT_SweetlineTree`, `RSW_Reefback`; a 10th, a lanternwhale slug, matches
   the same pattern) — the sheet re-surfaced already-shipped concepts as
   new commissions. `RUT_SweetlineTree` (commit `0d42dd16a`) **predates the
   register's own 2026-09-10 grading date**, meaning this isn't only "a
   later ruling superseded an old row" — the register contains duplicate
   entries that were already stale on the day it was graded. Only ~130
   keyword hits across two passes were individually checked, not all 118;
   the true error rate is likely higher. Full addendum in the Transient
   audit file.
5. A third instrument (`cast_assignment.csv`) still contradicts the 6 fauna
   `decision=out` cuts (carries all 5 BMT stragglers + AA_FissionMouse as
   `import`/`keep`), and the 2026-09-11 card ruling (`cf0632c39`) actually
   WIDENS the cut list (adds `BMT_ChemSnail`@`the_cracked_lands`,
   `BMT_GlowBat`) — but that ruling's home item (`BMT_FAUNA_ABSORPTION_1`)
   is itself ledger-BLOCKED, so which list is authoritative right now is
   not this pass's call.

**Not attempted this pass, deliberately**: steps 3-5 of the spec (the
actual `apply_assignment_verdicts.py --apply` run, the flora hand-edits,
the 118-slug art-queue filing, freezing the decisions files). All of them
are gated on the 5 calls above landing first — applying blind now risks
exactly the kind of silent data loss this item exists to prevent.
`needs=owner`.


---

# 🔴 OWNER RULINGS, 2026-09-20 — all five channels answered

Verbatim: *"Yes cut the 6 fauna. Cut FissionMouse everywhere. 15 flora moves are
approved. 4 flora purges remain purged. I don't want new versions of these silly
plants. 148 flora should be improved/regened indeed, but please make sure nobody
has already done so before you. Show me the 29 fauna issues."*

| channel | rows | ruling |
|---|---:|---|
| fauna `decision=out` | 6 | **CUT.** Execute the cut that was graded and never applied |
| `AA_FissionMouse` | — | **CUT EVERYWHERE** — not just from `wasteland.json`; sweep every roster and table |
| flora `decision=move` | 15 | **APPROVED.** Apply the moves |
| flora `decision=out` | 4 | **STAY PURGED**, and ⛔ **do not re-author replacements** — *"I don't want new versions of these silly plants"* |
| flora `art:improve` | 148 | **DO IT** — but 🔴 **check prior work first** |

## 🔴 The four purged plants do NOT get successors

`AB_DessertTree`, `AB_EyeGrass`, `Boomshroom`, `PoisonPlantBush` are cut and stay
cut. ⛔ **Do not author an `RSW_` equivalent, a reskin, or a "our own version" of
any of them.** The standing donor-port ruling is *replace every donor def we use* —
these are defs we have chosen NOT to use, so the port ruling does not reach them.
A future port sweep will want to grab them; it must not.

## 🔴 The 148 flora regens: prove nobody did it first

Verbatim: *"please make sure nobody has already done so before you."*

⛔ Do not queue 148 art jobs and find out afterwards. Before filing ANY of them:
- check `infrastructure/artpipe/done/` for an existing render per slug;
- check the artpipe pending/queue for one already filed;
- check whether a later wave already regenerated it under a different name.

🔑 This is a standing rule here, not a one-off caution — duplicate art costs real
generation time and produces two candidates nobody ruled between. Report the
measured split (already done / already queued / genuinely owed) **before** filing.

## The 29 fauna sizeBin rows — he asked to SEE them

The item's own UNKNOWN. He has asked for the list, so this is now the immediate
deliverable: which rows, what the sheet's `sizeBin` says, what the prefill said,
what the live `bodySize` is now, and whether the Law-3 size scaling already
consumed the difference. ⚠️ Until that is measured, **nothing in this channel is
"orphaned" — it is UNMEASURED.** Do not present it as a finding.


## ✅ THE sizeBin UNKNOWN IS RESOLVED — MEASURED 2026-09-20

The item asked whether ~29 fauna rows whose `sizeBin` differs from the prefill were
orphaned, or already consumed by the Law-3 size scaling. Measured by joining
`fauna_assignment_register.decisions.json` to live `race.baseBodySize` from the def
dump (618 mods, `a48bc71544df1a7e`, captured 2026-09-20T17:44:19Z), against the
sheet's own bands — small <1.0, medium 1.0–2.2, large 2.2–5.0, titan ≥5.0
(`gen_fauna_assignment_sheet.py:49`).

🔴 **It is 27 rows, not ~29.** 13 carry `decision=in`, 14 carry `decision=move`.
Every one is a distinct defName; no row is double-counted across biomes.

**13 DONE · 12 OWED · 2 genuinely unresolvable.**

### DONE — the size pass already delivered these (13)
`AA_Locusts` 0.01 · `AA_SmallButterfly` 0.01 · `GR_AnimusHare` 0.35 ·
`RSW_Faa` 0.2 · `Rikknit` 0.3 · `SW_Electrictick` 0.25 · `Stintaril` 0.5 ·
`TetnissCrab` 0.5 · `VFEI2_Boomtick` 0.18 · `SW_Electricgryllotalpa` 1.5 ·
`RSW_MutatingTumorfishSpawn` 0.8 · `RSW_Stoneback` 0.4 · `RSW_TruffleMole` 0.9

### OWED — live bin still disagrees with the graded bin (12)

| defName | graded | live bodySize | live bin |
|---|---|---:|---|
| `Ling_Cockroach` | small | 2.0 | medium |
| `AA_Mantrap` | large | 2.0 | medium |
| `AA_Plasmorph` | large | 1.0 | medium |
| `RSW_SandoAquaMonster` | large | 14.0 | titan |
| `AA_Agaripod` | titan | 4.0 | large |
| `AA_GreenGoo` | titan | 0.5 | **small** |
| `AA_Wildpod` | titan | 4.0 | large |
| `Dianoga` | titan | 4.0 | large |
| `GR_ParagonThrumbo` | titan | 4.5 | large |
| `RSW_CrimsonOpee` | titan | 1.7 | **medium** |
| `RSW_CaveLemming` | small | 1.0 | medium |
| `RSW_Megapleura` | medium | 2.4 | large |

⚠️ **`AA_GreenGoo` (graded titan, live 0.5) and `RSW_CrimsonOpee` (graded titan,
live 1.7) are the two worth looking at first** — those are not one-bin drifts, they
are several bins apart, which usually means the grading and the def disagree about
what the creature IS rather than about its number.

### Unresolvable (2)
`VFEI2_Macrofly`, `VFEI2_Silverfish` — absent from the live def set under both the
donor name and an `RSW_` name.

### 🔑 The trap this row hit, recorded because it nearly produced a wrong answer

A first pass reported **7** rows as "NOT IN LIVE DEFS": the five `BMT_*` and the two
`VFEI2_*`. **Five of those seven are ours already**, absorbed under `RSW_` names —
`BMT_CaveLemming`→`RSW_CaveLemming`, `BMT_Stoneback`→`RSW_Stoneback`,
`BMT_TruffleMole`→`RSW_TruffleMole`, `BMT_MutatingTumorfishSpawn`→`RSW_…`,
`BMT_Megapleura`→`RSW_Megapleura`. Three of them are in fact **DONE**.

⇒ **A donor defName absent from the live set does NOT mean the content is gone.**
This repo absorbs donors routinely and the absorbed def usually keeps a recognisable
name. Always check the `RSW_` form before reporting an absence.


## 🔴 The 148 flora regens: 96 ALREADY DONE. Re-measured by BENCH 2026-09-20.

The owner's condition was *"please make sure nobody has already done so before you."*
A subagent audit answered **3 done / 4 queued / 141 owed** and stated *"no BMT_/AB_
prefixes in this flora set"*.

**That statement is false and the counts built on it are wrong.** MEASURED: **115 of
the 148 rows carry a donor prefix** — `AB_` 64, `BMT_` 42, plus `AG_`, `RG_`, `VRE_`.
The `RSW_`/rename check the audit was briefed to run therefore never actually ran.

**Corrected, matching each row against `infrastructure/artpipe/done/` and
`pending/` allowing artpipe's own slug shape (it DROPS the donor prefix and may add
a wave prefix — e.g. `AB_Aaklac` → `aaklac_v1`, `Plant_Bloddle` →
`desertportb_plant_bloddle`):**

| status | count |
|---|---:|
| **ALREADY DONE** | **96** |
| already queued | 3 |
| **genuinely OWED** | **37** |

⇒ **Queue 37, not 148.** Filing the full set would have re-generated 96 existing
renders and produced two ungraded candidates for each.

### The 37 owed
`AB_AlienTree_Polluted` · `AB_TentacularPlant` · `AB_ToxiGrass` ·
`BMT_Plant_Doomsprout` · `BMT_Plant_EclipsusFlower` · `BMT_Plant_EclipsusLeaves` ·
`BMT_Plant_GutterPlantain` · `BMT_Plant_PoxSorghum` · `BMT_Plant_ScorchedStars` ·
`BMT_Plant_SewerReed` · `BMT_Plant_Snaketails` · `BMT_Plant_ToxicIvy` ·
`BMT_Plant_TreeMartyr` · `BMT_Plant_TreeTanglerootMangrove` ·
`BMT_Plant_TreeTwistingThornwood` · `BMT_Plant_TumorbulbHyacinth` ·
`BMT_Plant_TwistedDandelion` · `BMT_Plant_TwistingThorngrass` ·
`BMT_Plant_TwistingThornweed` · `BMT_Plant_WildRashroot` ·
`Plant_Bubblespore_Wild` · `Plant_FelucianGlowspore_Wild` · `Plant_HealrootWild` ·
`Plant_HydenockTree_Wild` · `Plant_JoganTree_Wild` · `Plant_MujaFruit_Wild` ·
`Plant_TookeTrap_Wild` · `Plant_TreePolux` · `Plant_YellowGrass` ·
`Plant_YellowTallGrass` · `RG_Plant_AridGrass` · `RG_Plant_CreepStern` ·
`RG_Plant_CrimsonCushion` · `RG_Plant_Dervish` · `RG_Plant_TallToxiGrass` ·
`RG_Plant_ToxiGrass` · `RG_Plant_TropicalChokevine`

⚠️ **Before filing these 37, check `BMT_FLORA_ABSORPTION_1`** — 20 of them are
`BMT_Plant_*`, and that item is FOUNDRY's live work on exactly those defs. Some may
be about to be renamed or cut, which would waste the render.

### 🔑 The method note that matters

**An artpipe slug is not the defName.** It lowercases, drops the donor prefix, may
carry a wave prefix, and appends `_v<n>`. A membership test written against defNames
finds almost nothing and reports it as "owed" — which is exactly the failure above,
and it fails in the expensive direction. Match on the STEM, both directions, before
concluding any art is missing.

---

# 🔴 OWNER RULING, 2026-09-20 — the flora channel is UNBLOCKED

He was asked directly and chose: **file the 17 non-BMT flora art jobs now, HOLD the
20 `BMT_Plant_*` jobs until `BMT_FLORA_ABSORPTION_1` lands.**

This is the question the 2026-09-20 handoff recorded as *"he has not answered that"*.
It is answered. The reason for the hold is that the 20 `BMT_Plant_*` subjects are
exactly that item's scope, and absorption may move or cut their defs — art generated
against a def that then moves is art thrown away.

⇒ **FOUNDRY's to execute** (this item is theirs, state `doing`). BENCH relayed the
ruling and did not file the jobs.

⚠️ **Before filing any of the 17, search first** — owner's standing rule, 2026-09-20:
check `infrastructure/artpipe/done/`, `_artsrc/`, `registry.jsonl` and any
`Transient/*.decisions.json` by SUBJECT, not by defName. An artpipe slug lowercases,
drops the donor prefix and appends `_v<n>`, so a defName search reports a false
absence. The audit that produced "141 owed" was re-measured to **37**; the same trap
would re-queue art that already exists.

---

## flora `art:improve` channel — CLOSED OUT, 2026-09-20 (FOUNDRY, offline)

`BMT_FLORA_ABSORPTION_1` closed today, unblocking the 20 held `BMT_Plant_*` rows.
Re-derived all 37 "owed" rows against current ground truth per the owner's
standing rule (*"make sure nobody has already done so before you"*).
🔴 **The 17/20 split in the two sections above is backwards** — a script-parsed
count of this item's own "### The 37 owed" list gives **17 `BMT_Plant_*` rows,
20 non-BMT rows** (both still sum to 37). Acted on the real split.

**Result: 0 of the 37 rows are genuinely owed. Zero art jobs filed.**

- 5 `BMT_Plant_*` rows already have a live `RUT_` ThingDef AND real, non-placeholder
  art on disk (`RUT_TwistingThornwood/Thorngrass/Thornweed`, `RUT_TreeMartyr`,
  `RUT_ScorchedStars` — `src/RimUtinni/UtinniPatches/Defs/ThingDefs_Plants/RUT_PollutedFlora.xml`).
- 12 `BMT_Plant_*` rows are CUT, not merely unported: no ThingDef anywhere in
  `src/`, and `wasteland.json`/`the_miasma.json`'s `flora_purged` arrays record
  an explicit reason for each (`POLLUTED_LANDS_FLORA_PORT_1`: the donor mod
  retired 2026-09-18, our own vanilla/`AB_` poison flora already carries the
  identity). No art owed against a cut subject.
- 18 of the 20 non-BMT rows already have a finished, `status:"ok"` render in
  `infrastructure/artpipe/done/` — matched by an exact `"Source row:
  flora:<biome>:<defName>"` citation inside the job's own `style_notes`/`prompt`,
  landed via the closed `ART_REGEN_FLORA_WAVE1_QUEUE_1` (or an earlier wave).
- The remaining 2 (`Plant_YellowGrass`, `Plant_YellowTallGrass`) are vanilla
  RimWorld `ThingDef`s we only relabel (`PlantNames_Ashkarr.xml`), absent from
  every biome roster — `ART_REGEN_FLORA_WAVE1_QUEUE_1`'s own closed record
  already excluded both as superseded/dead before filing its 14 jobs; this
  item's "37 owed" figure had not carried that exclusion forward.

Full per-row table: `Transient/sheet_orphan_flora_improve_channel_2026-09-20.md`.
Not touched by this pass: the 118-row ledger, the 12 OWED sizeBin rows, and
executing the flora move/purge channels — this item stays open for those.

---

## fauna `decision=out` channel — CLOSED OUT, 2026-09-20 (FOUNDRY)

Re-verified against the live tree (8 days after the audit, per this pass's own brief).
The roster-json half of this channel was **already committed by a concurrent window**
at `c2428fb6f` (a different session than this one) before this pass started — the
5 `BMT_` species and `AA_FissionMouse` were already removed from every roster's live
`fauna` list (JSON-parsed check across all 16 roster files, not grep: zero live hits),
with eviction records recorded. `BMT_ChemSnail` was correctly caught in both
`the_rot.json` AND `the_cracked_lands.json` (a second live location the item's own
note hadn't named). `AA_FissionMouse` was only ever live in `wasteland.json` — every
other roster's mention of it was already a pre-existing `move:Wasteland` eviction
record pointing there, so "cut everywhere" was already satisfied at the roster layer.

**What was NOT done, and what this pass added:** the roster-json fix never reached
the live game. `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_Wasteland.xml` still
carried a live `<AA_FissionMouse MayRequire="sarg.alphaanimals">0.3</AA_FissionMouse>`
row in its `<wildAnimals>` block — this is the load-bearing layer
(`rosters_to_cast.py`'s own header: "MEASURED 2026-09-20: every one of those biomes'
own BiomeDef XML ... already declares `<wildAnimals>` natively", i.e. the roster JSON
is provenance/authoring record, not what the game reads). Removed that one line.
Swept every `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/*.xml` for all 6 defNames
afterward: zero remaining hits. `RUT_TheRot.xml` and `RUT_CrackedLands.xml` never
carried any of the 5 `BMT_` species natively, so no edit was owed there.

Left alone, deliberately: `MegafaunaYield.xml`, `AnimalBiomeDuplicates_Generated.xml`,
`BiomeCastEvictions_WildBiomes.xml` and `AnimalTolerances_Ashkarr.xml` still reference
`AA_FissionMouse`/`BMT_CaveSpider`/etc. — these are generated compatibility/stat
patches keyed off the donor `ThingDef`s themselves (yield amounts, vanilla/donor-biome
`race.wildBiomes` eviction pairs, temperature tolerance), not our `RUT_*` custom biome
rosters. The `ThingDef`s are not deleted, only excluded from our own world's biome
casts, so these remain valid and are out of this channel's scope.

**Cut-list sidecar: not applicable to this channel, by design.** Read
`apply_assignment_verdicts.py` directly (`_side("cherry_pick_cut_list", plan.cut_list)`,
~line 549): `plan.cut_list` is only ever populated for **`homeless:`** rows with
decision `out` (a no-home creature Cherry-Picker would cut). An in-biome **`fauna:`**
row with decision `out` takes a different code path entirely — it calls `_remove_def`
on the roster's live `fauna` list and appends an `evictions` record in the same file
(exactly the shape the concurrent window's roster edit already used by hand). So "no
cut-list sidecar was ever written" for this channel was never a gap to fill — the
tool has no sidecar for this row kind, and the roster's own `evictions` array already
carries the provenance the sidecar would have. Confirmed by reading the source, not
inferred.

Selftests: `run_selftests.py` still passes at the pre-existing baseline after this
change (see commit). Fauna `decision=out` channel of this item is done; the other
four channels (flora move/purge/improve, the 118-row ledger, sizeBin) are untouched
by this pass and remain whatever state the rest of this file already records.

---

## NEW-ART/DEF commission ledger (118 rows) channel — MEASURED and FILED, 2026-09-20 (FOUNDRY, offline)

Per this item's own note that this channel lacked an explicit 2026-09-20 owner
ruling (unlike fauna/flora-move/flora-purge/flora-improve, which were each named
verbatim), this pass treated it as **measurement-and-safe-filing only**: no
ThingDefs authored, no art jobs queued, no roster edits. Full accounting:
`Transient/sheet_orphan_118_ledger_2026-09-20.md`.

Re-parsed the 118 `ledger:<sheet>:<slug>` rows directly from
`flora_assignment_register.decisions.json` (script, not eye-count) — confirmed
exactly 118, all `decision: "in"`, zero in the fauna file, matching the
2026-09-12 audit. Re-verified that audit's specific claims by reading the cited
defs/items directly, then ran a fresh token screen across **all** 118 (the
2026-09-12 pass had only screened ~130 keyword hits across two partial passes,
not every row) against items, kit specs, all of `src/`, and — new this pass —
`infrastructure/artpipe/done/`, `pending/` and `registry.jsonl` by content (the
2026-09-12 audit never checked artpipe for this channel at all).

**Result: 12 ALREADY BUILT · 0 ALREADY QUEUED · 20 SUPERSEDED/OWNED-ELSEWHERE ·
1 FLAGGED · 85 GENUINELY OWED.**

- **0 already queued**: no artpipe job (`done/`, `pending/`, `registry.jsonl`) cites
  this channel by its `ledger:` key, the same test the flora `art:improve` channel
  used successfully. The item's original claim ("no artpipe registry entry
  references any of the 118 concept slugs") holds for artpipe specifically — it was
  only the "already built as a def" and "already owned by another item" halves of
  the claim that were wrong.
- **12 already built** (not 9-10 as the 2026-09-12 audit and the owner-ruling
  section above both said): all previously-found ones re-verified, **plus one new
  catch, `RUT_PaleTree`** (`the_rot:the-pale-tree-anima-reskin-...`) — its art
  (`rot_paletree_v3`) landed via `ROT_FLORA_FAUNA_VERDICTS_1` on 2026-09-20, **the
  same day as this audit**. The error rate really was higher than either prior
  pass found, exactly as the addendum warned.
- **20 owned-elsewhere**: every kit spec and mechanics item that names one of these
  concepts (`RUST_CATHEDRAL_MECHANICS_1`, `sump_kit_spec.md`, `GREENTIDE_MECHANICS_2`,
  `fever_wood_kit_spec.md`, `MIASMA_MECHANICS_1`, `SCALD_MECHANICS_1`,
  `webwork_kit_spec.md`, `scarlands_kit_spec.md`, `FORGE_MECHANICS_1`) is still open
  today — none had closed or gone stale since 2026-09-12. `greatbole` turned out to
  already have a real ThingDef (`RUT_GreatboleHeartwood`/`RUT_GreatboleCore`,
  placeholder art, DEPLOY_HOLD) owned by `GREENTIDE_MECHANICS_2` — a step further
  along than "just named in a spec," but still not a fresh commission to file.
- **1 flagged, not filed as owed**: `forsaken_crags:dusk-rat-art-redo` asks to redo
  `AA_DuskRat`'s art, but `creature_art_register.decisions.json` already carries
  `c:AA_DuskRat → decision: "approve"` — a separate, already-run curation channel
  that approved the current art. This is a register data-quality defect (an
  art-redo row for a creature a different channel already cleared), not a new
  commission and not something this pass adjudicated — it needs an owner/BENCH call
  on which channel is authoritative, same posture as the item's own finding #2
  (the two flora decision files disagreeing).

**Filed `COMMISSION_LEDGER_CLEANUP_1`** (FOUNDRY, v1, offline) carrying the 85
genuinely-owed slugs verbatim, grouped by sheet, plus the watch-outs a future build
pass needs (re-verify currency, several slugs name body-donor/mechanic dependencies,
some may turn out to be mechanics asks rather than art commissions on closer read).
No ThingDefs, art jobs, or roster edits were made by this filing pass.

Selftests: `run_selftests.py` re-run after this pass, same pre-existing baseline
(see commit). **Not touched by this pass**: the sizeBin OWED rows, executing the
flora move/purge channels — this item stays open for those; they are not this
pass's scope.

---

## flora `decision=move` (15) / `decision=out` (4) channels — CLOSED OUT, 2026-09-20 (FOUNDRY, offline)

Ran concurrently with the fauna and 118-ledger passes above, and its own closing
note was never appended here — recorded now for accuracy. Full detail in that
pass's commit `90e203d46`.

Most of the 15 moves (12 of 15) and all 4 purges were **already applied by an
earlier pass today** (`c2428fb6f`, `b416de522`, `ef4500918`, `ac8b64d1c`) —
verified correct against current rosters, not re-done. The remaining 3
(`AB_GiantGamma`, `AG_Gamma`, `AG_Septimum`, all sourced from `the_forge.json`)
were applied this pass, landing in `forsaken_crags.json`. **`AG_Gamma`/
`AG_Septimum`'s known-bad target claim was resolved, not left unapplied**: the
mapping doc's "already in forsaken_crags" was false, but the destination itself
was still correct (the same Alpha Genes gamma/septimum family already resident
there, matching climate band) — moved with the corrected reasoning recorded.
All 4 purges (`AB_DessertTree`, `AB_EyeGrass`, `Boomshroom`, `PoisonPlantBush`)
confirmed absent from every roster, each with a `flora_purged` sidecar reason;
no forbidden successor authored.

Two real defects caught and fixed along the way, not just the graded moves:
`biome_flora.py`'s `FAMILIES` dict was out of sync with today's roster edits
(hand-corrected before `--write`), and `RUT_BlueDesert.xml` had **no
`<wildPlants>` element at all**, meaning its generated patch would have
silently matched nothing and dropped the blue-desert flora move — added the
missing anchor element. Also fixed `_validate.py`'s cross-check, which only
checked a flora move's target against the target roster's `fauna` list (a false
"target does not roster it" on every flora move, all 15).

Selftests: 66/66, 2 skipped — baseline held.

---

## Where this item stands now, 2026-09-20 (FOUNDRY)

Four of the five original orphan channels are closed out: fauna `decision=out`,
flora `decision=move`, flora `decision=out`, flora `art:improve`. The 118-row
NEW-ART/DEF ledger is measured and its genuinely-owed remainder (85 of 118)
filed cleanly as `COMMISSION_LEDGER_CLEANUP_1` rather than commissioned blind,
since (unlike the other four) the owner never ruled on this channel by name.

**Still open, and why this item does not close yet:**
- The 12 OWED sizeBin corrections (`## The 29 fauna sizeBin rows` section
  above) — the owner asked to see them (done, this doc), but no ruling exists
  yet on whether to actually apply any bodySize/grade correction. Not FOUNDRY's
  call to make alone; needs his read of the table above, especially
  `AA_GreenGoo` and `RSW_CrimsonOpee` (several bins off, likely a graded-wrong
  species rather than a numeric drift).
- The 1 flagged register conflict (`forsaken_crags:dusk-rat-art-redo` vs.
  `AA_DuskRat`'s already-approved art) — same posture, needs an owner/BENCH call
  on which channel is authoritative.
- `COMMISSION_LEDGER_CLEANUP_1` itself is a fresh, unstarted item.
- Freezing both decisions files (`frozen-artifacts` skill, item's own spec step
  5) is premature while the two items above are still open — freeze once they
  land, not before.
