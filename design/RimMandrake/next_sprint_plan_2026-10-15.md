# Next sprint — replicate the ratchet across more biomes (BENCH, 2026-10-15)

**Owner, verbatim (2026-10-15 ~16:30 PDT):** *"If these three mods look pretty good (close to done) in all ways including
art and mechanics, let's generalize what we learned right now. Extract the lessons learned and make a plan for the next
sprint. Can we replicate this again across three more biomes say? Are all the biomes now in a single baroque biomes mod
as requested? So testing the biomes may not require many differing load configs but a single one? Make such a plan. ...
Present me with three options and the relative tradeoffs between them."*

Pilot item: `RATCHET_PILOT_PROVE_THREE_MODS_ONE_LOOP`. Pilot design and finish line:
`design/RimMandrake/ratchet_workflow_and_token_burst_design_2026-10-11.md` §H. Every number below carries MEASURED (read
from the cited file or the ledger) or INFERRED (my reasoning from those numbers).

---

## Short version

1. **Consolidation: yes, it is done, and the pilot already used it.** All 24 biomes and their 6 engine/extra entries are
   composed into ONE mod, *RimMandrake: Baroque Biomes* (`mandrake.rm.biomes`; 30 entries in
   `src/RimMandrake/Biomes.compose.json`). The `ratchet_pilot` tier loads that whole mod. Every pilot round therefore had
   every biome loaded (MEASURED). **One load config can test all biomes.** What differs per biome is the **map**, not the
   mod list, so the next sprint needs one saved test site per biome, not one tier per biome.
2. **The biggest lesson is that fresh maps were the bottleneck.** Rounds 5-8 spent about 6 h live, met about 9
   test-environment hazards, and found about 0 mod defects. After the switch to clean saved maps, one 1 h 43 min session
   (L2) ran all three suites and closed two features (MEASURED).
3. **Recommendation: Option B, "one tier, one saved site per biome, three biomes".** Options A (five biomes, breadth)
   and C (infrastructure first, then six biomes) follow below.

---

## 1. Lessons from the pilot

Sources: the sittings `Transient/bench_live_2026101{4,5}*/SITTING.md` (rounds r3-r9, L1, L2), `Transient/release_push_2026-10-15/*.md`,
the handoff `infrastructure/state/handoffs/BENCH_HANDOFF_202610151936.md`, `design/RimMandrake/test_site_saves_2026-10-15.md`,
`infrastructure/state/lessons/2026101[2-5]*`, and the item's ledger runs (`rimflow show RATCHET_PILOT_PROVE_THREE_MODS_ONE_LOOP`).

### What worked — keep it

| # | lesson | evidence |
|---|---|---|
| W1 | **Clean saved test maps.** Each suite loads a cleaned, calm, unfogged save. The suite starts about 10 s after the load and does not spend 1-2 h chasing hazards on a fresh map. Rounds 5-8 spent ~6 h live, met ~9 TESTENV hazards and found ~0 mod defects (MEASURED, rounded in the source). The hazards were heat, fogged mechs, shrine pawns freed by unfogging, storm fires, spiders and hives, stray drones, a river ending at the sea, and ferry banks. The L2 session (12:42-14:25 PDT) ran on saves and produced GSS 110/110 on the r6 set, FlowWorks 61/61, river 20/0/1, Pyrelands 35 PASS / 0 FAIL / 1 INFERRED, deep lake 6/6 plus reload, and fuel moat 5/5 (MEASURED). | `test_site_saves_2026-10-15.md` §Why; `Transient/bench_live_20261015_l2/SITTING.md`; the owner's card of 2026-10-15 ("Clean saved maps") |
| W2 | **Pyrelands showed the pattern first.** Its north star always reloaded a fixture save, and none of its rounds hit a shrine or a hive. Every fresh-map hazard came from the three fresh-map suites (MEASURED). | `test_site_saves_2026-10-15.md` §1 |
| W3 | **One-HEAD rounds from a `git archive` export.** Every live round deploys and runs from one exported sha, so a result is attributable to a commit. Tier launch on the 22-mod list took 86 / 86 / 116 / 105 s in r7 / r8 / r9 / L2 (MEASURED), against ~15 min on the full list. Two traps were learned: the export must include all of `src/`, and `modset_builder --apply` must run from the seat clone. | sittings r7-r9 and L2 §Deploy; lessons `20261012T122214Z-…git-archive-export-must`, `20261015T070230Z-…modset-builder-tier-x-apply` |
| W4 | **One tier, restored afterwards.** The owner's list was saved before every round (md5 ee01dae9, 550 active), `modset_builder --tier ratchet_pilot --apply` set 22 mods, and the list was restored at teardown (MEASURED, every sitting). | sittings §1 |
| W5 | **An independent full-file review finds real defects.** Example: the reviewer found that the `RM_FallenWireShock` re-string exemption covered any re-string worker on any wire anywhere (MEASURED). | `Transient/release_push_2026-10-15/review_l1fixes.md`; `review_final*.md` |
| W6 | **A review save batches his looks.** The Pyrelands walkthrough save `RM_pyre_review_20261015` holds 41 stations with a key sheet, so one load replaces many joint sessions. The plans for GSS (41 stations) and FlowWorks (75 + 8 river) are checked offline (MEASURED: commit 8b7b0ede9c; handoff). | `src/RimMandrake/{Pyrelands/review,GimmeSomeSlack/review,FlowWorks/northstar/review/map}/COVERAGE.md` |
| W7 | **Long waits became INFERRED rows.** Embergrass regrow is a 180,000-tick wait, ~50 min at the stepped 58 t/s (MEASURED). By owner card on 2026-10-13 it is scored from a compressed run plus its verified components, and is not chased to 0 UNMEASURED. | §H criterion 3; `design/RimMandrake/debug_process.md` § "Long-duration properties" |
| W8 | **Each mod has one functional script and a machine exit criterion.** §H's six criteria let any agent say "done" without asking. C1-C3 were met at one HEAD in L2; C5 waits on the nightly selftests; C6 is his sign-off (MEASURED, ledger runs). | §H; ledger `verify` events 2026-10-15T20:31-21:03Z |

### What wasted time — change it

| # | lesson | evidence | rule for the sprint |
|---|---|---|---|
| X1 | **Fresh-map hazard chasing.** It cost ~6 h live over r5-r8 and spawned 9+ `TESTENV_*` items. Round r7 aborted 5 of 8 GSS attempts at arm. Round r6 aborted 3 of 6 (MEASURED). | r6, r7 SITTING; item causal chain | Every biome gets its saved site before any live suite runs. `--fresh-map` is never used for suites. |
| X2 | **Builders marked their own files CLEAN.** It happened twice: "diff since last clean mark is allowed" is not a rule anywhere. Every one of those files needed an independent full-file pass that found defects (MEASURED). | lesson `20261015T070804Z-…reviewers-twice-marked-files-clean`; `review_final.md` §1 | The builder never marks a file clean. A separate reviewer agent, briefed "FULL-FILE review, every line", does. |
| X3 | **Concurrent builders swept each other's uncommitted files.** HEAD briefly did not compile: a class landed between Harmony attributes and its patch (MEASURED). | `Transient/release_push_2026-10-15/fw_gpt_fixes_C.md`; handoff Traps | One builder per mod at a time. DLLs are built from a clean export of committed source. Commits use explicit paths only. |
| X4 | **Validation re-confirmed.** GSS `proof_all` passed 110/110 at r3, r4 (twice), r5, r6 (three maps) and L2. That is ~8 identical full passes at ~270-500 s each, ~1 h (MEASURED counts; the waste is INFERRED). | ledger runs | Rerun a suite only when its mod's inputs changed since its last PASS (R7). Other mods' suites are not rerun because a neighbour moved. |
| X5 | **Harness faults looked like mod faults.** Each cost one live pass to unmask. The JawaBench companion test profile expired mid-run twice, at 12:00Z in r7 and 20:00Z in L2. EmpirePursuit was deployed but missing from the tier. A bridge dropping an empty string read as "refused" (MEASURED). | r7 §2; L2 §Void runs | Preflight checks profile expiry against the planned run length, plus tier membership for every mod a row needs. A new row's harness gets a full-file review before it goes live. |
| X6 | **Owner gates waited.** The 2026-10-12 owner queue (6 rows) still has rows 1-4, 6 and 8 open on 10-15. Criterion 6 is the only open line of the pilot (MEASURED). His looks arrived one at a time (ash, regrow numbers, art, canal front). | `Transient/ratchet_owner_review_2026-10-12.md`; handoff | All looks for a sprint go into ONE review save per biome with a key sheet, delivered together. Numbers to rule go on one card. |
| X7 | **Scope grew inside the loop.** Deep ponds, fuel moats, a re-string job and warmth signs were added during the release push. The owner said *"We need to stop increasing scope"* (2026-10-15, handoff). 706 commits landed between 2026-10-11 18:00 and now (MEASURED, `git log --since`). | handoff "What the owner should see" | Freeze each biome's feature list at sprint start (§G Q3 already parks new features until a biome is accepted). New ideas are filed, not built. |
| X8 | **Stop messages arrive late.** A subagent spawned mid-flight did not see a stop until its next tool round, and it went live anyway in r9 (MEASURED). | r9 SITTING §5 | Live drivers hold BEFORE the deploy step and are told to proceed only after it. |
| X9 | **A save goes stale when a fixture does.** A reloaded site save predated later patches (anima). Saves are pinned to their mod set (MEASURED). | §H bottleneck 5; `test_site_saves_2026-10-15.md` §5 | Each save's registry row carries the tier fingerprint, and a fingerprint mismatch refuses the load. That costs a rebuild, never a wrong result. |

---

## 2. Facts (measured, not guessed)

### 2.1 Is there one biomes mod? Yes.

- **His request (MEASURED).** `design/RimMandrake/biome_mod_architecture.md` Q17, ruled by card on 2026-09-27: he proposed
  *"a single RimMandrake.Biomes mod that players can configure/select from like AlphaBiomes does"*, noting *"it might be
  simpler"*. The name is his coinage. `design/RimMandrake/biome_mod_unification_spec.md` §8 Q1: **"RimMandrake: Baroque
  Biomes"**, packageId `mandrake.rm.biomes`. It was executed on 2026-09-28 in three waves (`BAROQUE_BIOMES_WAVE{1,2,3}_*`).
  At that point 29 entries were live and three cold loads were clean.
- **What it holds today (MEASURED).** `src/RimMandrake/Biomes.compose.json` has 30 entries:
  - 24 biomes: Abyss, BlueDesert, Cauldron, Contagion, FeverWood, FloodedCanyon, GelatinousSlime, Greentide, LanternDeeps,
    LeaningScrub, LongShade, Miasma, NightsideIce, Pyrelands, RustCathedral, Stillsand, TerminalBiomes (5 BiomeDefs),
    TheForge, TheRot, TheSump, Warscar, Wasteland, Webwork, WeepingStones;
  - engines: CreatureBehaviors, EnvironmentalHazards, Wreckage;
  - extras: DivingInteraction, MovingDunes, SeaShores.

  It is composed at deploy time (`deploy_custom_mods.py --compose biomes`) into
  `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\RimMandrake.Biomes`. The per-biome folders under
  `src/RimMandrake/<Biome>` are source only, and a standalone deploy of a folded mod is refused.
- **Not in it, by design (MEASURED).**
  - The campaign/Star Wars layer: `mandrake.rut.patches` (UtinniPatches, which also holds the old `RUT_` BiomeDefs and the
    patch-added `RM_` rosters), `mandrake.rsw.swbestiary`, and the two per-biome Utinni mechanics mods
    `mandrake.rut.pyrelandsmechanics` and `src/RimUtinni/PropaneLakeMechanics`.
  - FlowWorks and LuminousPigment. Baroque Biomes hard-depends on both, and also on Alpha Biomes.
  - GimmeSomeSlack, TheBazaar, and the spec's Q4 exclusions (ExplosiveGrowth, HostileFlora, OasisMaker, Pyrinth).
- **The pilot tier already loads all biomes (MEASURED).** `TIERS["ratchet_pilot"]` in `src/RimMandrake/Utils/modset_builder.py:602`
  wants BRIDGE, `mandrake.rm.biomes`, `mandrake.rut.patches`, `mandrake.rsw.swbestiary`, `mandrake.rut.pyrelandsmechanics`,
  FlowWorks, GSS and `mandrake.rm.patches`. That resolves to 22 mods. So Pyrelands was tested with all 24 biomes loaded
  beside it, in every round.
- **What testing all biomes in one config needs (INFERRED from the above).**
  1. One tier, `biomes_sprint`: `ratchet_pilot` plus any per-biome Utinni mechanics mod a chosen biome has (today only
     Pyrelands and PropaneLake have one), and EmpirePursuit if a row needs it (X5).
  2. Keep the pilot's forbids: Geological Landforms and biome transitions, Map Designer, BCP, Pits, ManyWaters.
  3. **One saved site per biome.** A biome north star needs a map OF that biome, which a calm quicktest map is not. The
     `test_site_saves.py build` recipe takes a site of each biome on the frozen world, then cleans and saves it.
  4. Caveat: the in-mod biome toggles gate worldgen placement only, and the per-mechanic gate in `RM_BiomesMod.cs` is
     deferred. A single-load test therefore proves the mechanics run side by side. It does not prove each toggle turns
     its biome off cleanly.
  5. Per CLAUDE.md, a biome on 0 world tiles is expected. A site is founded where the biome exists on the current world,
     or painted on the test world's tile only. It is never repainted on the real planet.

### 2.2 Which biomes are next-closest to done

Pyrelands is the only biome with a VALIDATED north star (21 lines). Every other biome is RED, STALE or DRAFT in modcheck
(MEASURED: `python3 src/RimMandrake/Utils/modcheck/cli.py status`, which reads `infrastructure/state/modcheck_status.json`).
**No other biome is close to done.** The ranking below is relative.

How the evidence was gathered:
- PNG and `.cs` counts come from `find` over each mod folder (MEASURED).
- Art completeness is a raw PNG count, not checked against rosters or sheet decisions (INFERRED).
- Open-item counts are ID mentions in `infrastructure/state/queue/*.md` (INFERRED, and they include cross-references).

| rank | biome | art | mechanics | north star | script | open items |
|---|---|---|---|---|---|---|
| 1 | **Cauldron** | 37 PNGs; art sheet enacted 2026-10-09; 4 overlay textures missing (dewfall, assay fleck) per `Transient/validation_cauldron_20261007.md` | 16 `.cs`; an independent audit, fuzz and mutation testing caught 32/32 (`Transient/cauldron_independent_audit_2026-10-09.md`) | DRAFT, 7 lines, RED | `validation.py` (1761 lines), `northstar_plan.py`, `northstar_site.py` and a selftest; last live run 38 PASS / 3 FAIL (`Transient/l2p2_Cauldron.log`) | ~9; one live-found defect (`CAULDRON_YIELD_HARVEST_ORDER_FAIL_1`) |
| 2 | **LeaningScrub** | 99 PNGs; an art redo is pending (`LEANINGSCRUB_SHEET_ART_REDO_1`, plus decisions on the conflict17 sheet) | 28 `.cs`; tranche 1 done; per-vine items open; `LEANINGSCRUB_BLOOM_TOGGLE_OFF_STILL_FIRES_1` | DRAFT, 8 lines, RED | the same four-file set plus 2 selftests; last live run 7 PASS / 0 FAIL, but only 7 chains (`Transient/l2p2_LeaningScrub.log`) | ~16 (the heaviest) |
| 3 | **Contagion** | 98 PNGs; limb and cast art reviewed (`Transient/contagion_cast_art_review`) | 32 `.cs`; `CONTAGION_MECHANICS_BUILD_1` is **blocked on a design hole** (Sunbeam arrest), and the grown-limbs owner sheet and mulch/trade wiring are unbuilt | DRAFT, 8 lines, RED | the same four-file set; last live run 39 PASS / 4 FAIL or UNMEASURED, a bridge timeout (`Transient/l2p2_Contagion.log`) | ~8; `CONTAGION_LIVE_SUITE_FAILS_ACC_BIOMES_1` |
| 4 | TerminalBiomes | 337 PNGs, but it is 5 biomes | 44 `.cs`; settings pass done | 0-line checklist, STALE hash | `validation.py` only | ~5, spread over 5 biomes |
| 5 | BlueDesert | 69 PNGs | 14 `.cs`; `BLUEDESERT_FLORA_PLANT_REFUSAL_1` open | DRAFT, 0 lines, RED | 4 scripts | ~6 |
| 6 | Webwork | 51 PNGs | 13 `.cs` | DRAFT, 0 lines, RED | `validation.py` only; its first-script item is still queued | ~9 |

Why the top three:
- **Cauldron**:
  - smallest mechanics surface;
  - strongest offline verification of any biome after Pyrelands;
  - the Pyrelands-style north-star scaffolding (plan, site, driver) already exists;
  - its gaps are one failing chain, 4 textures and a live proof.
- **LeaningScrub**:
  - the same scaffolding, and a clean (but short) live run;
  - it carries the most tickets, and its art redo needs him.
- **Contagion**:
  - the most complete art of the three;
  - but a design hole needs his ruling first.

What would replace it:
- TerminalBiomes (five biomes in one folder) is the "big" alternative;
- BlueDesert is the "small" one.

Not checked:
- per-roster sprite coverage against sheet decisions;
- whether the agent-drafted checklists are accurate. That is his validation, and it is a sprint-start owner act in every option.

---

## 3. Three options

### What every option shares (the generalized loop)

These parts come straight from the lessons. None of them is new invention.

1. **One tier, `biomes_sprint`.** It is `ratchet_pilot` plus the chosen biomes' Utinni mechanics mods, if they have any.
   It loads all of Baroque Biomes and the three pilot mods. One launch (~90-120 s) serves every suite.
2. **One clean saved site per biome.** `test_site_saves.py build <biome>` is generalized from the `pyrelands` profile:
   the biome IS the subject, so its ruins and wildlife stay and danger containers go. Each site is rebuilt only when
   the tier fingerprint changes.
3. **One-HEAD live rounds** from a full-`src/` export, with one live driver holding the bridge. Preflight checks
   companion-profile expiry and tier membership (X5).
4. **Role separation.** The builder builds. A different agent does the full-file review and the CLEAN marks (X2). One
   builder per mod at a time, and DLLs are built from a clean export (X3).
5. **Scope frozen at sprint start** (§G Q3). New ideas are filed, not built (X7).
6. **The pilot's three mods are regression guards.** Their suites rerun only when their inputs changed (X4).
7. **His time goes into three fixed slots and nowhere else** (X6):
   - **S0, sprint start, ~15 min, one card:** confirm the biomes and the scope freeze, validate the draft north-star
     checklists, and answer any blocking design question.
   - **S1, mid-sprint, ~30-45 min:** one walkthrough review save per biome (the Pyrelands pattern: stations plus a key
     sheet), all delivered together, so he does all his looks in one load.
   - **S2, end, ~10 min, one card:** sign-off, which is the only non-machine exit line.

### Exit criterion (per biome, machine-checkable except the last line)

All of the following hold at ONE HEAD on `biomes_sprint`, each recorded by `rimflow verify`:

1. `northstar_driver run --mod <Biome> --plan src/RimMandrake/<Biome>/northstar_plan.py` on the biome's saved site gives
   **0 FAIL**. Every non-PASS row is either INFERRED (its verified components named) or a labelled gap with a filed item.
   `modcheck floor --all` shows the validated hash as current. *(Pass `--plan`: without it the run is EMPTY, with 0 rows
   and no error. Lesson `20261012T183003Z`.)*
2. Every roster def's texture resolves. Zero missing textures is checked offline against the deployed composite.
3. Every in-biome item named in the S0 scope list is `done` or `superseded`, or the S0 list explicitly defers it.
4. `run_selftests.py --only` passes on changed files. `code_review_status.py check` is CLEAN on every changed file, and
   the reviewer is not the builder.
5. The pilot guards are still green. The GSS, FlowWorks and Pyrelands suites have a PASS at a sha whose inputs equal
   HEAD's, or a fresh PASS at HEAD.
6. *(Owner.)* S2 sign-off on the ledger, by `--by-card` or `--owner-said`.

### Option A — Breadth: five biomes to "machine-validated", art looks deferred

- **Scope:**
  - Cauldron, LeaningScrub, Contagion, BlueDesert and Webwork, taken through criteria 1, 3, 4 and 5 only.
  - Art (criterion 2 and the S1 looks) moves to a later sprint, together with the planet paint.
  - BlueDesert and Webwork first need checklists written: both have 0 lines today.
- **His time:**
  - S0 is longer, ~30 min: validating five checklists, two of them new, plus the Contagion design hole.
  - No S1 this sprint.
  - S2 is ~10 min.
  - About 40 min in total.
- **Agent/token cost:** high. It is five north-star scripts brought to green, roughly 1.5-2x the pilot's live time
  without the hazard waste (INFERRED).
- **Calendar:** ~5-7 days (INFERRED). The pilot took ~4 days for three mods, including ~6 h of hazard chasing and
  scope growth.
- **Risks:**
  - "Done" without art is not what he asked for ("in all ways including art and mechanics").
  - Agent-drafted checklists get validated in bulk, the F7 trap of rubber-stamping.
  - Five sites to build means five chances for a biome-specific site hazard. Desert heat cooked Pyrelands colonists
    (`TESTENV_SITE_HEAT_*`), and BlueDesert will likely repeat that (INFERRED).
- **Exit:** criteria 1, 3, 4 and 5 for all five, then 6.

### Option B — Depth, replicated: three biomes fully done, art included (**RECOMMENDED**)

- **Scope:**
  - Cauldron, LeaningScrub and Contagion, taken through all six criteria. This is exactly what the pilot did, with the
    lessons applied.
  - Day 0 builds the `biomes_sprint` tier and the three sites.
  - The live rounds then interleave biomes, so one launch carries all three suites.
  - Art is fixed on two fronts: Cauldron's 4 overlays and the LeaningScrub redo through `art install`.
- **His time:**
  - S0, ~20 min: the three checklists, and the Contagion Sunbeam ruling. If he will not rule it at S0, swap
    Contagion for BlueDesert at S0.
  - S1, ~45 min: three review saves in one sitting.
  - S2, ~10 min.
  - About 75 min in total, in three sittings.
- **Agent/token cost:** medium. About the pilot's agent load, minus the hazard chasing and the re-confirming reruns
  (INFERRED: ~0.6-0.8x the pilot).
- **Calendar:** ~3-4 days (INFERRED).
- **Risks:**
  - LeaningScrub's ~16 tickets may not fit. The S0 scope freeze decides which ones are in.
  - Contagion depends on one design answer.
  - Some of the fresh-map hazards may come back on biome sites. The saves remove most of them, and the clean-map
    read-back refuses a dirty save.
- **Why this one:**
  - It is the only option that produces "done in all ways" again, and it does so on three biomes.
  - It is the smallest change from a loop already proven once.
  - It produces the per-biome site and review-save recipes that A and C both need anyway.
  - GPT's objection still applies (§A item 5, "building another control plane before proving one complete convergence
    cycle"). The pilot proved one cycle on mixed mods, and B proves it on biomes specifically before anything widens.

### Option C — Infrastructure first, then a factory: six biomes

- **Scope:**
  - **Days 1-1.5 are machine-only.** Make the loop a product:
    - generalize `test_site_saves.py` to build a clean site for **every** biome on the frozen world (24 sites, built
      unattended overnight);
    - a generic review-save builder that turns any `COVERAGE.md` into a save plus a key sheet;
    - a preflight that checks profile expiry, tier membership and the site fingerprint;
    - a results join that skips a suite whose inputs have not changed (`NORTHSTAR_RESULTS_JOIN_1`);
    - one `biomes_sprint` runner that runs every biome's north star in one launch.
  - **Days 2-7:** six biomes (the top six) through all six criteria, two or three at a time.
- **His time:**
  - Nothing during the infrastructure days.
  - Then S0, ~30 min, for six checklists.
  - S1 twice, ~45 min each, three biomes per sitting.
  - S2, ~10 min.
  - About 2 h 10 min in total, but per biome it is the cheapest of the three options.
- **Agent/token cost:** highest up front, lowest per biome after that (INFERRED).
- **Calendar:** ~7-9 days (INFERRED).
- **Risks:**
  - The day-1 tooling is unproven on biomes. If the generic site builder fails on odd biomes (sea floor, Nightside
    ice, the TerminalBiomes set), days are lost before any biome advances.
  - This is the control-plane-before-proof risk from §A item 5.
  - Six concurrent biome lanes bring back the X3 collisions unless each has its own builder and one integrator (R11).
- **Exit:** the infrastructure gate first: 24 sites built and read back clean, and the review-save builder reproduces
  `RM_pyre_review_20261015` 41/41. Then criteria 1-6 for six biomes.

### Side by side

| | A: breadth (5) | **B: depth (3)** | C: infra then factory (6) |
|---|---|---|---|
| biomes fully done (all 6 criteria) | 0 (5 machine-validated) | **3** | 6 |
| his time | ~40 min, 2 sittings | **~75 min, 3 sittings** | ~2 h 10 min, 4 sittings |
| his time per fully-done biome | n/a | **~25 min** | ~22 min |
| calendar (INFERRED) | 5-7 d | **3-4 d** | 7-9 d |
| agent cost | high | **medium** | highest, front-loaded |
| main risk | not "done in all ways"; bulk checklist validation | **LeaningScrub ticket load; one Contagion ruling** | tooling slips before any biome moves |
| what it leaves behind | 5 green scripts | **3 done biomes plus the reusable site and review-save recipe** | the factory and 6 done biomes |

**Recommendation: B, and run C's tooling as the next sprint once B has shown which parts actually repeat per biome.**

### Questions for S0 (card-ready)

1. Which option: A, B or C?
2. Is the biome list Cauldron, LeaningScrub, Contagion? Or swap Contagion for BlueDesert if the Sunbeam ruling waits?
3. Seats: the pilot was "BENCH owns everything, an experiment only" (§G). Repeat that for the three biomes, or let
   FOUNDRY build while BENCH runs live and integrates?
4. Do the scope freeze lists come from the agents (drafted, then shown to him on the S0 card) or from him?
