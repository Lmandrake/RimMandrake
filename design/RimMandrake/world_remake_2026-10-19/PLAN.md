# Remaking the world, free of the unwanted mods — plan and three options (2026-10-19)

Author: FOUNDRY. For: Lukas. Status: FOR YOUR REVIEW. GPT reviewed it (section 8); I verified its points against the evidence files and changed the plan accordingly — this version recommends Option D.
Evidence files (all in this folder): `01_mod_inventory.md`, `02_world_pipeline.md`,
`03_ticket_impact.md`, `04_scope_cuts.md`. Every number below comes from one of them; nothing is
new measurement unless marked.

## 1. Your proposal, restated, and whether it is correct

> If the biomes have the right shape, mutators and plant/animal defNames — even with placeholder art
> for everything — we can author a fresh, strange-looking but fully functional world and savegame
> free of the unwanted mods, possibly tonight, then add lost functionality back.

**Correct in principle, with four conditions that are not yet true.**

1. **"The defNames are good" must be measured, not assumed.** All 28 `RM_` paint targets resolve on
   the 536-mod list (02 §6) — good. But three still lean on mods that are loaded today
   (`RM_Wasteland` terrain, two `RM_Cauldron` dryads, three `RM_TheForge` plants), 16 roster rows
   still use donor defs (`REGEN_GAPS_DECIDE_STRAYS_AND_FLYERS`), and the pending renames
   (`BIOME_DEFNAME_MIGRATION_WAVE_1`, `CRACKEDLANDS_FULL_RENAME_1`) must land **before** the new
   save, or we repeat 2026-10-18 when 1,903 tiles fell back to TemperateForest (03).
2. **A fresh world drops the save-borne problems, not the def-borne ones.** Dead class names, lost
   biome codes and ~500 dead things all live in old saves, so a clean world removes them. It does
   not remove anything we feed it: the stamp files, the gravship (892 cells of a retired floor),
   the founders (one retired Eyeling).
3. **"Everything regenerated" is not free.** The one recorded build took 37 min; generation, the
   faction pass and a load on the 536 list have never been timed. The faction pass is irreversible
   per run (your 2026-08-21 ruling: don't redraft to test).
4. **No single exporter exists for the save's real roads, mutators and landmarks** (live export exists; nothing writes the stamp files back). The stamp files are stale
   (roads 09-07; mutators/landmarks 08-23): 10,084 mutator entries vs the save's 27,856; 563
   landmarks vs 3,008. A remake from the files silently loses most of them unless we build an
   exporter first.

**Rulings it touches** (flagged for you, not decided): remake-is-the-last-step (2026-09-20),
paint-once (BIOME_PAINT_ONCE_AT_THE_END_1), one-hand-made-world (re-stamping Ash'karr is fine; a
new layout is not), no-redraft-to-test. Placeholder art is already your own idea.

## 2. The mod classification (from 01)

Live list 536 = 6 Ludeon + 62 ours + 468 third-party; identical to the donor-free 536 file.

| Class | Count | What |
|---|---|---|
| Retired already | 22 | all owner-ruled, none active |
| **Retire now** | **39** | Retirement Wave 1, ruled 2026-10-10, **never run**; only Pyrinth is a hard dependence and its replacement `mandrake.rm.pyrinth` is built but not on the list |
| Likely retire — rebuild first | 28 | Outer Rim Core, Galactic Empire, Rebel Alliance, Advanced Biomes, Alpha Memes, VFE Tribals, RimTek, Bones, Yayo, Landforms… (what to rebuild is 01 §9: beskar, hypertech component, Binary Star faction, two terrains) |
| Likely retire — simply drop | 124 | nothing of ours hard-depends on them; 12 are HOLD (retained third-party dependants, or world-generation mods): `05_drop_closure.md` |
| Exclude during dev, maybe v2 | 32 | the evaluation-hostile set. **Real Fog of War and CAI 5000 are a pair: CAI strips the fog, so exclude both or neither.** Yayo's Combat 3 also. |
| Authoring tools | 21 | world/pawn editors, dev tools — keep to author, remove at release (ruling C04) |
| Keep | 256 | 24 hard-dependency frameworks (VEF, HAR, Big and Small, EBSG, Outland Genetics…) + 232 others |

Also: `ModsConfig.FULL.LATEST.xml` (542) still lists the 7 donors retired 10-18; a `--restore` to it
resurrects them. We depend on third-party mods for **zero textures** — what ties us is defNames,
C# classes and About.xml dependencies.

**Recommendation that holds in every option:** run Wave 1 (39) and drop the 112 SAFE of the 124 (`05_drop_closure.md`; 12 HOLD) — a mod-list
edit plus one load, independent of the world — and put the 32 evaluation-hostile mods on the
"not during dev" list today. That alone shrinks every load, every test and the world-gen time.

## 3. What the queue says (from 03)

874 open items: 21 obsolete/shrinking under a remake, 801 unchanged, 31 must come first,
13 easier after, 8 need your word. The remake saves ~21 items of save repair and donor-art work
(largest: `BIOME_WORLD_SWITCH_WAVE_1`); it does not save def porting. Critical path:
your word → defs off donors → renames → mod list → donor-off load proof → paint inputs (ported
mutators, world textures, factions) → remake → the 13 "easier after" items.

And from 04: testing, not code, is the bottleneck (922 owed live checks, 992 filed vs 323
closed in 14 days). The scope cuts shrink what the new world must carry: 268 items / 356 live
checks out of v1.

## 4. Three options

### Option A — Remake tonight (your proposal, hardened)
**Tonight, with you present:** (1) rebuild the mod list = live list minus Wave 1 (39) minus the
124 drops, minus the 32 evaluation-hostile; (2) offline remaps — biome names (incl. `RUT_Umbra`→`RUT_FuelSnows`,
2,531 tiles, per the paint list), mutator and landmark ports, faction names, gravship floor, founder;
(3) build the missing exporter OR accept older layers; (4) one generate + faction pass + stamp +
your look; (5) first start save from the stamped world, run through `save_class_census.py`,
`save_def_census.py` and `save_adoption_check.py`, then a cold reload.
- **Wins:** ends the save-compat class of work today; every later test runs on a clean world.
- **Costs/risks:** spends the one irreversible faction pass before the renames,
  pilgrim camps, 4 unported mutators and the 16 donor roster rows are settled → a second paint is
  likely; loses save-only layers unless the exporter exists; the ideoligion and late-faction bridge
  tools (`jawa/faction_ideo_set`, `jawa/ideo_create`, `jawa/faction_create`) have never run on a fresh world; a
  tested end-to-end start save has never existed; contradicts the "last step" ruling.
- **Realistic?** The tile stamp, yes. A *complete* tested world tonight, no (02 §7).

### Option B — Prerequisite sprint, then ONE remake
**Tonight:** the Option-A offline work only (list rebuild, remaps, Wave 1, drops, evaluation-hostile
exclusion) plus the exporter spec. **Next, until the gates in §5a pass (no date promised):** land the renames and the 31 "must come first"
items that matter (donor defs off, 16 roster rows, 3 leaning biomes, 4 mutators), run one donor-off load proof on the new list, **time** generation + load on the 536
list on a throwaway world (no faction pass). **Then** the single remake — which is the paint-once
ruling honoured, with placeholder art allowed.
- **Wins:** one paint; every ruling respected; the dry-run measures the unknowns before the
  irreversible step; most of Option A's tonight work is reused unchanged.
- **Costs:** the world stays on the old save for a few days; saves-based traps stay alive until then
  (mitigation: the census scripts and `_AREAFIX2` copies already contain them).

### Option C — Keep the world, finish in place
Run Wave 1, drop, finish retirement, repair the one save with the census tools, never remake
before v1. **Wins:** zero world risk. **Costs:** the slowest to remove the retirement drag — each
new retirement can leave a new class/def trap in the save, and the redraw/AREAFIX work in 03 class A
(21 items) must all be done. Choose only if you decide the remake is not worth its irreversible pass.

| | A tonight | B sprint → one remake | C in place |
|---|---|---|---|
| Rulings touched | 3 (last-step, paint-once likely, no-redraft) | last-step moved, others honoured if the rehearsal is not a redraft (needs your word) | none |
| Irreversible pass spent | tonight, unfinished inputs | once, with dry-run data | never |
| Save-compat work remaining | old-save residue gone, but anything we re-import (founders, ship, stamps) can reintroduce it | same | all 21 class-A items (some only shrink) |
| Time to a clean world | hours (incomplete) | UNMEASURED; gated, not dated | open-ended |
| Biggest unknown | faction pass + load time | same, but measured first | per-retirement save traps |
| Option D (below) | — | — | — |

## 5. My improvements to your proposal
1. **Split "remake" from "free of mods".** Freeing the list (Wave 1 + drops + exclusions) is
   independent of the world and cheap; do it first in all options.
2. **Measure the unknowns on a throwaway world before the irreversible pass.** Generation time,
   536-list load time, whether each of the 28 biomes spawns plants and animals on a real tile.
3. **Build the exporter** (save → roads/mutators/landmarks files) so the remake does not discard
   10k+ authored layer entries. Small, offline-testable, and useful beyond this remake.
4. **Put the fog-of-war pair out of dev now.** It is the only item you named that is both
   evaluation-hostile and trivially removable (exclude Real Fog of War **and** CAI 5000).
5. **Adopt the scope cuts first** (04): the fewer systems the new world must carry, the less there
   is to re-prove after it. At minimum the testing-rule change (offline tests + your play for minor
   fixes, settings tested at defaults and all-off).
6. **Decide whether this is the shipped freeze** before anything irreversible — it decides whether
   pilgrims are prerequisites. Factions are not, on a development world: one absent at creation
   (`HORRORS_RAIDING_FACTION_1`) can be created later with `jawa/faction_create` (UNMEASURED; `06_remake_runbook.md` §0).


### Option D — Decouple development from the canonical remake (recommended; added after GPT review)
A, B and C bundle four independent decisions: retiring mods, the development fixture, replacing the
canonical world, and the release freeze. D separates them.
1. **Retire through validated candidate profiles, not through the live save.** Build the reduced mod
   list as a candidate profile, prove it with a donor-off load on `_AREAFIX2` copies and fresh scratch
   maps (the existing quicktest workflow, ~90 s/map), and promote it only after it passes.
2. **Develop and test on scratch maps and throwaway fixtures.** Stop repairing old saves except to
   rescue authoritative content or to keep your current play going.
3. **Keep the authoritative world and keeper saves untouched** until the canonical remake.
4. **One canonical remake when explicit freeze gates pass** (5a), with placeholder art allowed.
   It may not be, or authorise, a test redraft or an alternate planet.
- **Wins:** no repair treadmill (C) and no premature irreversible pass (A, B); retirement and the
  scope cuts proceed immediately and independently; the remake becomes a gate-driven event.
- **Costs:** the old save lives on as a reference; scratch-map tests do not prove the canonical save.
- B is D with a date attached; choose B only if you want the remake scheduled rather than gated.

## 5a. Gates before the irreversible faction pass (from GPT, verified against 02)
Freeze deployed builds, the ordered creation profile, settings and the Cherry Picker profile · audit
removed dependencies including C# strings and XPath references (01 §1: unmeasured) · freeze names ·
validate every stamp reference and worldgen worker · export the authoritative layers and compare tile
IDs, edge topology, assignments and settlement identities (not counts: settlements are 121 CSV rows vs
96 canonical NPC settlements; include factions, names, features, worldTags; name the authoritative save
including edits after 09-12) · resolve the contradictory `AB_PropaneLakes` evidence · write the missing
start-save procedure (scenario, landing site, ideology mode and fixed ideos, faction roster, founder
references and bonds, ship import with the two missing ship boulders and the floor remapped, Ikee
re-bond) · after stamping: lint, compare the globe, your LOOK, build the start save, run all three
censuses, **cold reload**, exercise landing, founders, ship and representative biome generation ·
keep checkpoints before promotion · rebuild or quarantine contaminated `RM_TestSite_*` fixtures.

## 5b. Corrections to this plan's own claims (GPT, verified)
- "Remove the 124" is **not yet dependency-safe**: Custom Quest Framework supports the retained
  `mlie.dungeonpack` (01 line 219), and other retained dependants exist (VFE Props / Gerrymon's Dungeon,
  Apparel Accessories / More Utility Packs, Minerals Framework / Minerals Sparkle). The closure is computed in
  `05_drop_closure.md` (112 SAFE, 12 HOLD).
- **World-generation mods must not be dropped yet**: Alien Worlds (and its Tidally Locked patch, 01
  lines 208/291), My Little Planet, Sensible Factions and Deep Orbit are assumed present at generation
  (02 §2, line 117). Prove the generator mods inert first (03 critical path).
- **Wave 1 is a deployment transaction**, not "subtract 39 ids": activate `mandrake.rm.pyrinth` with the
  donor removal, deploy prerequisites and reconcile the Cherry Picker ship profile.
- **Scope cuts conflict with prerequisites**: 04 cuts Pyrinth (needed by Wave 1) and
  `WARSCAR_SHEET_DONOR_PORT_1` (a prerequisite in 03); Utility Columns' removal conflicts with keeping the
  trade stack when Bazaar is deferred. Reconcile before adopting cuts wholesale.
- "Cheap", "one load", "small exporter", "~3 days" and "zero world risk" are **unmeasured** — struck.
  "Zero textures" is "~0, one missing path". Fog pair exclusion has tier-specific exceptions (01 §7).
  Stale queue blocker edges can be cleared but their prose blockers may remain.

## 6. Decisions only you can make
1. Option D (recommended), B (scheduled), A (tonight) or C (never)? And first: is the remake the canonical FREEZE, or an interim development world?
2. May the remake precede "all biomes mod-migrated" (changes your 2026-09-20 ruling)?
3. Is the remake the shipped freeze, or a dev world we may repaint? **Answered 2026-10-19 (card): a development world
   that may be repainted.** So `HORRORS_RAIDING_FACTION_1` is "create later" (`jawa/faction_create`), not a prerequisite.
4. Wave 1 already has your 2026-10-10 authorization — approve only the changed execution (transactional deploy). The 124 drops' dependency closure is computed (`05_drop_closure.md`: 112 SAFE, 12 HOLD); approve the 112 and the fog pair exclusion with its tier exceptions.
   Also: exactly which factions/ideoligions are retained, and which world-layer losses are acceptable.
5. Which of the 04 scope cuts that reverse your rulings do you accept (its section 7)?

## 7. What I will do without waiting
Nothing irreversible. Identical in B and D, so I can start them: compute the dependency closure of the
39 + 124 and the generator-mod check, draft the candidate profile, file the exporter (scoped as in 5a),
clear the five stale queue blocks, and order the 31 "must come first" items. I will not drop a mod or
spend a faction pass without your word.

## 8. GPT review
Full answer: `Transient/gpt_review_world_remake_plan_2026-10-19.txt` (gpt-6.1-sol, high effort). Its verdict: "Option B is directionally sensible, but not ready for approval as written." Accepted (verified in the evidence files): a fourth option D; the dependency-closure and generator-mod errors; the wider exporter scope; the missing `save_adoption_check.py` and cold-reload gates; the unsupported-claim list. Not accepted as stated: none rejected; the "2–3 days" estimate was struck because nothing measured it.
