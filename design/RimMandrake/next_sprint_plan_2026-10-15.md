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
   (L2) ran all three suites and closed two features (MEASURED). The link is correlational: fixtures, code and harnesses all
   changed between those rounds (GPT consultation).
3. **Recommendation (after adversarial review and GPT consultation): Option 1, "decisions first, two biomes deep".**
   Cauldron and Contagion through the finish line against a scope frozen at S0, with a one-agent-day tooling slice that
   serves only them; LeaningScrub is a stretch. Option 2 (the original three-biome depth) and Option 3 (machine-only
   breadth, five biomes) follow in §3. All three candidate biomes have mechanics builds BLOCKED on design calls (§2.2),
   so the owner's response time, not agent time, sets the calendar.

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
| X6 | **Owner gates waited.** The 2026-10-12 owner queue still has rows 1-4, 6 and 8 open on 10-15. Criterion 6 is the only open line of the pilot (MEASURED). His looks arrived one at a time (ash, regrow numbers, art, canal front). | `Transient/ratchet_owner_review_2026-10-12.md`; handoff | All looks for a sprint go into ONE review save per biome with a key sheet, delivered together. Numbers to rule go on one card. |
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
  3. **One saved site per biome.** A biome north star needs a map OF that biome, which a calm quicktest map is not.
     `src/RimMandrake/Utils/modcheck/test_site_saves.py` knows three sites today (`calm`, `pyrelands`, `river`) and has
     no per-biome recipe (MEASURED). Its `pyrelands` site is a cleaned copy of a save made by Pyrelands' own
     `northstar_site.py`. Cauldron, LeaningScrub and Contagion each already have a `northstar_site.py`, so a biome site
     is that builder plus `test_site_saves` clean/save/register. A clean site is not a hazard-free site: the Pyrelands
     site was saved at 56.7 °C outdoors (registry `outdoorAtSave`).
  4. Caveat: the in-mod biome toggles gate worldgen placement only, and the per-mechanic gate in `RM_BiomesMod.cs` is
     deferred. A single-load test therefore proves the mechanics run side by side. It does not prove each toggle turns
     its biome off cleanly.
  5. Per CLAUDE.md, a biome on 0 world tiles is expected. A site is founded where the biome exists on the current world,
     or painted on the test world's tile only. It is never repainted on the real planet.

### 2.2 Which biomes are next-closest to done

Pyrelands is the only BIOME with a VALIDATED north star (21 lines, `modcheck floor --all`: "bar met"). Graffiti and
FireEcology also have validated north stars but are not biomes. Every other biome is DRAFT: Cauldron 7 lines,
Contagion 8, LeaningScrub 8, BlueDesert / Webwork / TerminalBiomes 0 (MEASURED: `modcheck status`). **No other biome is
close to done.** The ranking below is relative.

Evidence, all MEASURED on 2026-10-15:
- PNG and `.cs` counts from `find` over each mod folder. Art completeness is a raw PNG count, not checked against rosters
  or sheet decisions.
- Latest live runs are the modcheck records of 2026-10-08 on `acc_biomes-15` (`Transient/modcheck/<Biome>_<stamp>.json`).
  They ran on fresh maps at HEADs before the pilot, and every FAIL they found has since been filed and closed. They show
  how far each suite reaches, not today's state.
- Open items are live item files (`infrastructure/state/items/<ID>.md`) naming the biome.
- Blockers are the ledger state of each biome's mechanics build item.

| rank | biome | art | mechanics build | latest live run (2026-10-08) | live items | scripts |
|---|---|---|---|---|---|---|
| 1 | **Contagion** | 98 PNGs; cast art reviewed; `CONTAGION_RULED_CONTENT_1` built (L0) | 32 `.cs`; `CONTAGION_MECHANICS_BUILD_1` BLOCKED: grown-limbs owner sheet, Sunbeam arrest (design), mulch item, trade/quest wiring, rattle render seam | 52 PASS / 0 FAIL / 7 UNMEASURED | 3 | `validation.py`, `northstar_plan.py`, `northstar_site.py`, 2 selftests |
| 2 | **Cauldron** | 37 PNGs; 4 overlay textures not on disk (`lint_cauldron_defs.py`); `CAULDRON_ENRICHMENT_VISUALS_1` owes his in-game look | 16 `.cs`; independent audit caught 32/32 planted defects; `CAULDRON_MECHANICS_BUILD_1` BLOCKED: gas grid and falter-tell foreknowledge (design), unbuilt FlowWorks/ruins parts | 58 / 1 / 4 | 5 | same set, 1 selftest; `validation.py` 1761 lines |
| 3 | **LeaningScrub** | 99 PNGs; `LEANINGSCRUB_SHEET_ART_REDO_1` proposed: new renders, 3 donor plants to port to owned defs, 2 re-picks, a Dustflutter numbers call, flyer frames | 28 `.cs`; `LEANINGSCRUB_MECHANICS_BUILD_1` BLOCKED: calling-pyre ritual (precept design), vaporator art + farmstead source, ripple cover system, scene layouts | 50 / 1 / 17 | 7 | same set, 2 selftests |
| 4 | TerminalBiomes | 337 PNGs over 5 BiomeDefs | 44 `.cs` | not compared | — | `validation.py` only; 0-line checklist |
| 5 | BlueDesert | 69 PNGs | 14 `.cs`; `BLUEDESERT_MECHANICS_BUILD_1` live | not compared | 2 | 4 scripts; 0-line checklist |
| 6 | Webwork | 51 PNGs | 13 `.cs` | not compared | 5 | `WEBWORK_FIRST_SCRIPT_1` validated; 0-line checklist |

What this means:
- **Every top-three biome needs design calls from him before it can be "done in all ways"**: about 9 across the three
  (INFERRED from the BLOCKED notes). Either he rules them or the S0 scope freeze defers them, and then "done" means "done
  against the scope he froze". That must be said to him in those words.
- Contagion and Cauldron have the cleanest suites and the lightest art debt. LeaningScrub has the heaviest art loop, the
  most design calls and the most UNMEASURED rows, so it is the stretch candidate, not a core one.

Not checked: per-roster sprite coverage against sheet decisions; whether the agent-drafted checklists are accurate (that
is his validation, a sprint-start owner act in every option).

---

## 3. Three options

### What every option shares (the generalized loop)

1. **One tier, `biomes_sprint`**: `ratchet_pilot` plus any Utinni mechanics mod a chosen biome has (none of the five
   candidates has one today). It loads all of Baroque Biomes and the pilot mods. One launch (~90-120 s) serves every suite.
2. **One clean saved site per biome**, built by the biome's own `northstar_site.py` and cleaned, saved and registered by
   `test_site_saves.py`. The biome is the subject: its wildlife, ruins and heat stay; danger containers go. A site is
   founded where the biome is, or on a test tile painted for the test only, never saved over the shipped world.
   Rebuilt only when the tier fingerprint changes.
3. **One-HEAD live rounds** from a full-`src/` export, one live driver on the bridge, preflight for companion-profile
   expiry and tier membership (X5).
4. **Role separation** (X2, X3): builder builds; a different agent reviews full files and marks CLEAN; one builder per
   mod; DLLs from a clean export.
5. **Scope frozen at S0 in a versioned acceptance manifest** (below). New ideas are filed, not built (X7).
6. **The pilot's three mods are regression guards**, rerun only when their declared inputs changed (X4). The pilot
   itself is not closed (C5 nightly pending, C6 his sign-off): close it before or at S0.
7. **His time is a decision packet, not meetings** (X6, GPT): one asynchronous packet per gate with numbered design
   questions, concrete alternatives and a recommendation each, rendered art sheets, and an estimate of review effort.
   At most one unanswered blocking packet at a time; agents work independent items while it waits; silence is never
   approval. Cosmetic changes still need his permission first, and flyers are never live-tested without him.
8. **Budgets are two numbers**: active owner minutes, and elapsed owner response time. The measured bottleneck is the
   second: the 2026-10-12 queue was mostly open three days later. Every calendar below is agent time **plus** his
   response intervals.

### Exit criterion (per biome)

A per-biome **acceptance manifest** is frozen and owner-approved at S0 (its hash recorded on the ledger). It lists
non-empty requirement IDs, the north-star rows, the roster including the patch-added RM_ cast in
`UtinniPatches/Patches/WildAnimals_<Biome>.xml`, the in-biome items in scope, and the visual must-show bars. A biome is
done when ALL of the following hold at ONE HEAD on `biomes_sprint`, each recorded by `rimflow verify`:

1. `northstar_driver run --mod <Biome> --plan src/RimMandrake/<Biome>/northstar_plan.py` on the biome's registered site
   gives **0 FAIL, 0 UNMEASURED, and is not EMPTY** (row count equals the manifest's). INFERRED is allowed only for rows
   the manifest pre-approves as INFERRED, with their component proofs named. The run records HEAD and the tier
   fingerprint. *(Pass `--plan`: without it the run is EMPTY, 0 rows, no error. Lesson `20261012T183003Z`.)*
2. Every manifest roster def's texture resolves against the deployed composite, offline. Zero missing.
3. `modcheck floor --all` shows the biome **"bar met" with bars > 0**. Today all three show 0 bars, so the floor passes
   vacuously; the manifest's must-show bars must be written into the north star first, and their coverage is his
   acceptance of the reviewed artifacts. Texture existence alone never proves art quality.
4. Every manifest item is `done`, or deferred by a manifest revision he approved. `superseded` counts only with a named
   replacement item.
5. `run_selftests.py --only` passes on changed files; `code_review_status.py check` is CLEAN on every changed file, and
   the reviewer is not the builder.
6. Pilot guards green: GSS, FlowWorks and Pyrelands each have a PASS at a sha whose declared inputs (including the shared
   engines and patches) equal HEAD's, or a fresh PASS at HEAD.
7. *(Owner.)* Acceptance on the ledger (`--by-card` or `--owner-said`) citing the manifest hash.

Lines 1-6 are machine-checked; line 3's coverage and line 7 are checked as **recorded owner approvals**, so a verifier
can still say "done" or "not done" without asking.

### Option 1 — Decisions first, two biomes deep, third as stretch (**RECOMMENDED**)

- **Scope:**
  - Cauldron and Contagion through all seven exit lines. LeaningScrub only after both pass, with no calendar promise.
  - **Day 0, at most one agent-day of tooling, and only what these two need:** the site wrapper (`northstar_site.py` +
    `test_site_saves`), the preflight, the review-save builder from `COVERAGE.md`, and the acceptance-manifest
    verifier. Prove each on Cauldron before reusing it on Contagion. No 24-site factory.
  - **S0 packet goes out on day 0, in parallel with the tooling:** the two checklists to validate, the ~5 design calls
    (Cauldron gas grid and falter-tell; Contagion Sunbeam arrest, grown limbs, mulch), each with a recommended answer and
    a "defer" choice, plus one art sheet for Cauldron's 4 overlays.
- **His time:** S0 packet ~30-45 min; S1 review saves for two biomes ~60 min (Pyrelands' one save has 41 stations); S2
  ~10 min. **About 1 h 40 min - 2 h active**, in three sittings (INFERRED). Re-picks on the art sheet can add a round.
- **Token cost:** lowest of the three.
- **Calendar:** ~3-4 agent days **plus** his two response intervals (S0 packet, S1 saves). If each takes a day, ~5-6 days
  (INFERRED).
- **Risks:**
  - An unanswered S0 packet stalls both builds; the defer choice on every question bounds that.
  - "Done" is done against a scope he froze, possibly without some of the mechanics he designed.
  - Two biomes instead of the three he asked about.
- **Why this one:** it is the review's and GPT's independent pick. It spends his scarce response time on the two
  biomes whose suites are cleanest, it front-loads every decision instead of discovering them mid-build, and it builds
  only the tooling it uses.

### Option 2 — Three biomes deep (the original B, corrected)

- **Scope:** Cauldron, Contagion and LeaningScrub through all seven exit lines, with the same day-0 tooling slice and
  S0 packet. LeaningScrub adds its art redo (new renders, three donor-plant ports, re-picks, flyer frames on a sheet he
  works in) and four design calls.
- **His time:** S0 packet ~60 min (~9 design calls, three checklists); one LeaningScrub art sheet loop ~30-60 min,
  likely two rounds; S1 three review saves ~90 min or two sittings; S2 ~10 min. **About 3-3.5 h active** in four or five
  sittings (INFERRED).
- **Token cost:** highest of the three (three biomes, art regeneration rounds).
- **Calendar:** ~5-6 agent days plus three or four response intervals: ~7-10 days (INFERRED).
- **Risks:**
  - The LeaningScrub art loop and its 17 UNMEASURED rows set the end date for all three.
  - Nine design calls in one packet invite sub-questions, which turns a card into review work.
- **Exit:** the seven lines for all three.

### Option 3 — Machine-only breadth now, his looks later

- **Scope:** Contagion, Cauldron, LeaningScrub, BlueDesert and Webwork, each brought to a fresh run at one HEAD on its
  saved site with exit lines 1, 2, 5 and 6 only. Nothing BLOCKED on design is built; no art is generated. BlueDesert and
  Webwork first need draft checklists (0 lines today). Output: five biomes with honest, current, comparable suites and a
  ranked list of exactly what each still needs from him.
- **His time:** S0 ~30 min to validate five checklists (two new); one card at the end. **About 40 min**, two sittings.
- **Token cost:** middle (five suites, but no art and no design-call builds).
- **Calendar:** ~4-5 days, nearly independent of his response time (INFERRED).
- **Risks:**
  - Nothing ends "done in all ways", which is what he asked for.
  - Bulk validation of agent-drafted checklists is the rubber-stamping trap (F7).
  - Five sites means five biome-specific site hazards (heat for BlueDesert, as Pyrelands showed).
- **Exit:** lines 1, 2, 5, 6 for all five, plus the ranked readiness list on one card.

The original Option C (tooling first, then a six-biome factory) is dropped: building sites for all 24 biomes assumes they
are on the world, and most are expected on 0 tiles until the planet is painted at the end, so it needs test-tile painting
for most of them; TerminalBiomes alone is five BiomeDefs; and both the review and GPT judged it control-plane before proof.

### Side by side

| | **1: decisions first, 2 deep** | 2: 3 deep | 3: machine-only breadth (5) |
|---|---|---|---|
| biomes done (all 7 lines) | **2 (3rd stretch)** | 3 | 0 (5 with current suites) |
| his active time | **~1 h 40 min - 2 h, 3 sittings** | ~3-3.5 h, 4-5 sittings | ~40 min, 2 sittings |
| his response intervals | **2** | 3-4 | 1 |
| calendar (INFERRED) | **~5-6 d** | ~7-10 d | ~4-5 d |
| token cost order | **lowest** | highest | middle |
| main risk | **unanswered S0 packet; frozen-scope "done"** | LeaningScrub art loop sets the end date | not "done in all ways"; bulk checklist validation |
| leaves behind | **2 accepted biomes, the site/review/manifest tooling proven on biomes** | 3 accepted biomes, same tooling | 5 honest suites and a readiness list |

**Recommendation: Option 1.** Add LeaningScrub only when Cauldron and Contagion pass; run Option 3's readiness sweep as
background work while his packets are outstanding.

### Questions for S0 (card-ready)

> **Owner picked Option 2 ("Three biomes deep") by card on 2026-10-15.** Kickoff packet, with criteria lists, the design-call cards, the LeaningScrub art status and the schedule: `design/RimMandrake/biome_sprint_kickoff_2026-10-15.md`.

1. Which option: 1, 2 or 3?
2. For each design call in the packet: rule it, take the recommended answer, or defer it out of this sprint?
3. Seats: BENCH owns everything as in the pilot (§G), or FOUNDRY builds while BENCH runs live and integrates?
4. Is a response window for packets (for example, within a day) workable for you?

---

## Adversarial review (BENCH, 2026-10-15)

Load-bearing facts were re-measured from disk and the ledger. What held: all 24 biome entries (30 compose entries) are in
`mandrake.rm.biomes`; `ratchet_pilot` loads it; checklist line counts; Cauldron's 4 missing overlays. What was wrong and
is now corrected above:
- The cited "last live runs" were the 2026-10-07 l2p2 logs, and misquoted (Cauldron's 22 UNMEASURED omitted;
  LeaningScrub's "7/7" was a truncated log). The latest runs are the 2026-10-08 modcheck records.
- The three "open live defects" cited were already `done`.
- Contagion was presented as the only biome with a design blocker; all three mechanics builds are BLOCKED on design.
- Open-item counts were cross-reference counts (now live item files); `WEBWORK_FIRST_SCRIPT_1` is validated, not queued.
- `test_site_saves.py` has no per-biome recipe; "Pyrelands is the only validated north star" holds only for biomes.
- The exit criterion relied on `modcheck floor`, which passes vacuously with 0 bars, and called owner acts machine checks.
- Owner time was counted in meeting minutes; art regeneration loops, design calls and response latency were missing.
What changed: the biome ranking (Contagion and Cauldron first, LeaningScrub stretch), the exit criterion (manifest, no
UNMEASURED, bars > 0), owner budgeting (two numbers), and a new hybrid option replacing the six-biome factory.

## GPT consultation (gpt_consult.py, 2026-10-15)

GPT was given this plan as first drafted and the review findings. **Its pick: a readiness-gated hybrid — two biomes deep
(Cauldron and Contagion provisionally), at most one agent-day of tooling, a third biome as stretch, drop the 24-site
factory.** Its main critiques beyond the review: loaded is not tested (one config proves coexistence only on exercised
paths); clean fixtures can remove the mechanic under test, so sites need preservation rules; the "fresh maps were the
bottleneck" claim is causal overreach, since fixtures, code and harnesses all changed at once; and the old gate allowed
false completion (zero rows, unlimited INFERRED, missing bars, loose "unchanged inputs"). What changed because of it:
Option 1's shape; the asynchronous decision packet with at most one outstanding; budgets as active minutes plus response
intervals; the acceptance manifest with pre-approved INFERRED rows and declared transitive inputs; "accepted frozen scope"
as the honest name for done. Its full answer:

> I would choose a **readiness-gated hybrid: two-biome depth, with a small tooling allowance and a third biome as stretch**. Cauldron and Contagion are provisional candidates; LeaningScrub waits because its art and unresolved decisions create more owner dependency. Selection should follow a current readiness audit, not stale PASS counts.
>
> 1. **Independent critique** — The review substantially weakens B's promised scope and calendar. Its corrections are supplied evidence, not facts I independently verified. All three builds reportedly need owner decisions; therefore "three fully done in 3–4 days" has no supported basis. Owner response latency, rather than agent throughput or meeting minutes, governs delivery. The review also misses several problems: **Loaded does not mean tested.** One composite configuration proves coexistence only for exercised paths. It does not establish biome coverage, toggle behavior, optional-dependency behavior, or compatibility with the excluded configurations. **Clean fixtures can hide defects.** Removing wildlife, threats, or environmental conditions may remove the mechanic under test. Saved sites need documented preservation rules, plus separate representative map-generation and hazard checks. **The bottleneck claim is causal overreach.** Later sessions changed fixtures, code, harnesses, and experience simultaneously. Saved maps appear valuable; the evidence does not isolate their contribution. **The accounting unit changes.** TerminalBiomes contains five BiomeDefs. C's six candidate folders therefore represent ten biome definitions, undermining its cost comparison. **The proposed gate permits false completion.** Zero rows, unlimited INFERRED rows, labelled gaps, superseded tickets, missing visual bars, and loosely defined "unchanged inputs" can all yield green without complete evidence. **The pilot remains unfinished.** Pending nightly checks and owner acceptance limit the claim that a complete convergence cycle has already been proved.
>
> 2. **Scope and owner-time changes** — Commit to one biome first; admit the second only after its blocking decisions are resolved and the first passes the revised gate. Treat three as stretch, without a calendar promise. Describe the result as **accepted frozen scope**, not "fully done" if required mechanics are deferred. Allow at most one agent-day for tooling serving those candidates: wrap their existing `northstar_site.py`, add preflight, and produce evidence manifests. Prove this on biome one before generalizing. Drop the 24-site factory. Replace three assumed meetings with a prepared asynchronous decision packet: numbered design questions, concrete alternatives, recommended choices, rendered art sheets, and estimated review effort. Separate owner approval of requirements from final acceptance; preserve permission requirements for cosmetic changes and owner-attended flyer testing. Budget both **active owner minutes and elapsed response time**. Forecast effort from a timed sample of review stations; include repeat art picks and re-review. Agree response windows explicitly. Keep at most one unanswered blocking packet outstanding, and use waiting time for independent work. Silence never constitutes approval. Report calendar estimates as agent execution time **plus outstanding owner-response intervals**.
>
> 3. **Replace the exit criterion** — Freeze a versioned acceptance manifest before implementation. A verifier must reject completion unless: the manifest contains explicit, nonempty requirement IDs, required scenarios, expected assertions, roster entries—including patch-added cast—and visual must-show bars; every mandatory assertion has fresh PASS evidence (missing rows, EMPTY runs, FAIL, UNMEASURED, and unexplained skips fail; INFERRED only for individually preapproved properties with specified component proofs); each run records source/build hashes, deployed assets and dependencies, game version, settings, harness, fixture, and results, and reuse requires equality of declared transitive inputs, including shared engines and patches; fixtures pass biome-specific validity checks and retain required hazards; texture references resolve, and required visual bars have owner acceptance tied to the reviewed artifacts; required selftests, independent review, and pilot regressions pass; supersession requires a mapped replacement requirement and deferrals an approved manifest revision; final owner acceptance references the exact manifest and artifact hashes. That makes completion machine-checkable **by checking recorded human approvals**, while keeping subjective judgment explicit.
