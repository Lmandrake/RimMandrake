# Validation map and rules

Item `RIMMANDRAKE_INVENTORY_VALIDATION_SCHEMES_BEFORE_ANY_LADDER`. Drafted 2026-11-12 (evening, PST) for the owner, from
the scheme inventory (`design/RimMandrake/validation_inventory_2026-11-12.md`, 55 schemes) and his card answers of the
same day. **Status: a draft. Nothing here is built by this document, and no rule here is in force until he reads it.**
Open choices: `D:\ClaudeWork\rimmandrake\conductor\validation_inventory_20261112\QUESTIONS.md`.

Tags: `[measured]` means a command or a file read on 2026-11-12 produced the number (the source is named);
`[guess ~N%]` is my confidence. Times are Pacific (PST); ledger and log stamps are UTC (PST = UTC - 8 h).

Words used throughout:
- **Line item**: one checkable acceptance line. It is a selftest case, a testq row, a north-star bar, one cell of a
  matrix scene, or one art criterion. Each has an id, the inputs it reads, and a stored verdict.
- **Matrix scene**: one prepared cell (a pit, a station) copied across the variables that matter (depth x fill,
  liquid, material), each copy labelled on the map. His standing test principle (below, rule 5).
- **Look**: a stage-5 or stage-6 inspection of pictures or of the running game, as opposed to a script's verdict.
- **Revalidate**: run a line item again and store its new verdict.

---

## 1. The stage map

Work climbs from stage 0 to the last stage that applies to it. Mechanism work stops at stage 4; work with a look
goes on to 5 and 6 (rule 1). Each arrow back is an objection becoming line items (rule 2).

```
 door 0         1            2             3               4                 5               6
 PREFLIGHT ──▶ AGREE ──▶ CODE CHECK ──▶ LOGIC OFF-GAME ──▶ IN-GAME PROOF ──▶ PRE-LOOK ──▶ OWNER LOOK
 (python,      (bars       (selftests,    (kernels, fuzz,   (script verdict    (fresh judge    (Mandrake, on a
  0 tokens)    written)    lints, review)  conservation)     through testq)     on the scene)   labelled save)
                                                 ▲                 ▲                 ▲               │
                                                 └──── an objection re-enters at the LOWEST stage ──┘
                                                       that can show it, for the touched line items only
 mechanism work is DONE here ───────────────────────────────────────┘
```

| stage | passing proves | judged by | evidence left | cost per pass | schemes that live here (kept by his picks of 2026-11-12) |
|---|---|---|---|---|---|
| **0 Preflight** (a door, not a stage of the work) | the ticket names real files, defs, races and mod lists, its acceptance test is sane, and a full-list test says why | a deterministic Python module, no model | a preflight record with its run time | seconds, 0 tokens (the spec's budget; unbuilt) | ticket preflight, spec `design/specs/2026-11-12-ticket-preflight-before-any-token.md` (absorbs the idea of the deleted L1 manifests, his 23:18Z ruling) |
| **1 Agree** | what the player must and must never see is written down, and he signed the bars | Designer or builder drafts; he validates the north star (`modcheck validate`), or a delegated judge per `delegation_policy.md` | the walk's `## north star` (hash-bound), Designer pass | his minutes per mod; Designer coverage judge about 720k tokens a run `[measured in the refusal-contract spec §0]` | north-star checklist; Designer stage with its light path and "live walk first" when code exists (01:06Z ruling); player-truth sweep, to be re-examined (23:18Z ruling) |
| **2 Code check** | code and XML are consistent, reviewed, and the checkers can fail | the builder before every commit (`run_selftests.py --only`); hooks on every tool call; the nightly sweep repeats it | selftest output, `code_review_status.py` CLEAN, commit | seconds to minutes, 0 tokens (reviews and GPT rounds cost tokens) | targeted selftests, def/patch linters, `validate_patch.py`, code review, GPT review, hooks, planted mutants, **mutmut (pick 4, keep)**, validator replay, nightly sweep |
| **3 Logic off-game** | the rules and the maths hold over thousands of cases without the game | the builder; nightly | selftest rows, seeded fuzz with shrunk cases | seconds to minutes, 0 tokens, no game | C# kernels with fuzz (61 mods), FlowWorks offline program, C#/Python parity vectors, geometry libraries, **shipped-settings fuzz with conservation laws (pick 10, keep; item `RIMMANDRAKE_REVIVE_SHIPPED_FUZZ_WITH_LAWS`)** |
| **4 In-game proof** | the real engine does what the logic says: it loads, each function works, each bar shows | a script's exit code through the test queue (testq); close gates read it; no agent judges | testq rows, live-proof lines, results JSON | 22 s minimal load; about 71 s median per job plus about 140 s fixed on SteveDesktop `[measured there, inventory §1D]`; full list about 15 min cold; tokens only to stage and debug | load checks, each mod's `validation.py`, north-star suites, **generic north-star driver (pick 5, keep)**, in-game proof classes, tick-speed equality, **shared in-game scene runner (pick 14, prioritised; `RIMMANDRAKE_BUILD_SHARED_SCENE_RUNNER_FIRST_SLICE`)**, **bridge validation observatory as the run's report (pick 15, keep; `RIMMANDRAKE_BUILD_OBSERVATORY_SMALL_PROVEN_FIRST`)**; the **one refusing gate** at close (card "One gate, and it refuses"; the Marker's idea folds in, pick 3) |
| **5 Pre-look** | a fresh judge who did not make it, asked an open question, finds nothing obviously wrong in the matrix scene or the art | an Opus judge (GPT second look), brief `design/RimMandrake/scene_look_judge_brief.md`; art by the art pipeline | `VERDICT.md` beside the captures, prereview record | one judge run per scene: tokens UNMEASURED per run `[guess ~300k-700k tokens]`; game minutes to capture | open and checklist pre-look judges, art evaluation, offline art checks, prereview record, **frame judge folded in (pick 11; `RIMMANDRAKE_FOLD_FRAME_JUDGE_INTO_PRELOOK`)** |
| **6 Owner look** | Mandrake looked at a dense, labelled savegame and said pass, fix or question per thing | the owner | his words verbatim in the ledger (`--owner-said`), screenshots | his minutes: UNMEASURED `[guess 5-20 min a look]`; tonight he gave three looks in one evening | owner sittings, keeper saves, review sheets, flyers in a joint session, **first-human-look savegame (pick 12, combined with matrix scenes; `RIMMANDRAKE_PREPARE_FIRST_LOOK_MATRIX_SAVEGAME`)** |

**Beside the ladder, not stages** (they measure or unstick the stages):
- **Test Pilot** (pick 7, keep): a live debugging sitting when stage 4 keeps failing (`rimflow pilot`).
- **Findings judge** (pick 8, keep and switch on): judges filed findings daily; re-enabled 2026-11-12 (ledger close of
  `FINDINGS_JUDGE_TIMER_REPLACE_FOUNDRY`).
- **Proof cost ledger** and **process sims**: measure what the stages cost.

**Deleted by his picks (2026-11-12, 22:55Z):** the Relentless acceptance exam (1), the Relentless live round (2),
the L1 expectations manifests (6; already deleted, 4594675ed9), the player-truth sweep (9; deletion put on hold by
the Conductor at 23:08Z, then "re-examine" by his 23:18Z ruling), `modcheck run --extended` (13; deleted,
99a2633071). The Relentless retirement scope is in
`D:\ClaudeWork\rimmandrake\conductor\validation_inventory_20261112\RELENTLESS_RETIRE_SCOPE.md`.

**Vocabulary that this map replaces.** RimFlow's levels L0, L1, L2, GREEN-MIN, GREEN-FULL, L3, L4
(`rimflow/model.py`), the north-star rungs (`debug_process.md` §6a) and `infrastructure/VALIDATION_LADDER.md` L0-L4
all describe parts of this map with different words. Mapping, for a reader of the older docs: L0 = stages 2-3;
L1 and L2 = stage 4 (minimal list); GREEN-MIN / GREEN-FULL = stage 4 on the minimal / full list; L3 = stage 5; L4 =
stage 6. Retiring the old words is not decided (card draft rule 1; it is not his yet).

---

## 2. The rules

### Rule 1. Where done ends

His card answer, 2026-11-12 about 2:2x PM PST (ledger OWNER note 22:47:51Z): option 1, *mechanism work is done at
stage 4 (in-game script proof), work with a look goes on to stages 5-6*, with his typed condition:

> *"(1) as long as we acknowledge that steps 5 and 6 will almost certainly raise new items... describing precisely how
> that "throws you backwards" is key. Small, fussy objections can trigger extremely expensive re-testing of entire
> suites otherwise. Piecemeal revalidation of specific touched line items is crucial, or converting all steps to very
> rapid validation passes."*

So:
- **Mechanism work** (no picture decides it: pumps, counts, jobs, hediffs, timing) closes at stage 4 on the script's
  verdict. He sees it only if he asks, or if it is part of a scene he looks at anyway.
- **Work with a look** (art, scenes, under-liquid drawing, biomes, flyers) is ready for stage 6 only after stage 5.
  It closes on his pass, cell by cell.
- **"Ready for him" is a state, not a close.** A look item sits at "ready for look" with its save named. Stage 4 rows
  stay green while it waits, and nothing reruns because it waits.

### Rule 2. How an objection "throws you backwards" (the rule he asked for first)

His words are the condition above (22:47Z). The precise procedure:

**2a. Every objection becomes line items in the same sitting.** One line item per thing he named, each written with:
his words verbatim; where (save, cell, thing); a **class**, one of
- MOD (our code draws or behaves wrong),
- SITE (the test map was wrong: roof, animals, geysers),
- HARNESS (the scene builder or verifier was wrong),
- ART (a picture needs redrawing),
- NEW BAR (he set a new standard, see 2g),
- QUESTION (he asked something; it is answered, not fixed);

and `would_pass`, what he would accept, in his terms where he gave them. A pass he gives is written down too, as a
**pinned line** (2e). One look with nine observations is nine line items, not one item with nine paragraphs.

**2b. Each line item names its inputs.** These are the source files, defs, constants, scene id and cell ids it reads.
This is the `inputs` contract already specified in the refusal-contract spec (§4, build ticket T7). The mechanism
under it exists and does not work: the testq skip-when-unchanged cache answered 0 of 1,583 `[measured, inventory §4]`.
Fixing that cache key (line id, criterion hash, inputs hash, game build plus mod-list hash) is the mechanism. **No new
layer is needed.**

**2c. A line item re-enters at the lowest stage that can show the objection.**

| what the objection is about | re-enters at | what is written first |
|---|---|---|
| a number, a curve, a geometry (opacity at 4 m, a label's depth, a footprint inside the walls) | stage 3 | an offline row that fails on the old code (the 2026-10-24 rule: *"Please find ways to test for those defects in your own offline and in-game testing from now on, so we don't repeat mistakes."*) |
| engine behaviour (a building is not covered in game, a tool refuses) | stage 4 | a state-read row in the mod's script that fails on the old build |
| a look only (a colour reads grey, a shadow looks wrong) | stage 5 | a judge criterion or crop, plus an art criteria-ledger entry when it is taste |
| SITE or HARNESS | the harness's own selftest | the site assertion (as the open-sky guard of 01:43Z), proven both ways |

From there the line item climbs again, but **only through the stages it needs**: a number fixed at stage 3 still
needs its stage 4 row and its look; it does not rerun stages it does not read.

**2d. The revalidation set is the objected line items plus every line item whose inputs changed. Nothing else.** Every
other stored PASS stands, because its key is unchanged. A whole-suite rerun is right only when:
- the fix changed a shared core file that every line reads (tonight's one under-liquid law, `RM_UnderLiquid`,
  441c321a20dc, correctly reran every under-liquid row);
- the game build or the mod list changed (live lines only);
- the criterion set changed as a whole;
- a line declares no inputs. Such a line always reruns, and gets a ticket to declare them.

**2e. His passes are pinned.** Whatever he passed in a look ("cover-line is good (pass)", "the shallow end is right")
becomes a pinned line: a stored PASS plus, where it is a number, an offline row that holds it. A fix whose diff moves
a pinned line stops at stage 3. The builder first looks for a fix that keeps the pin. If none exists, the next look
shows the pinned cell labelled **"changed something you passed"**, beside the old one. Tonight this would have caught
the water retune halving the shallow end (section 3).

**2f. Small objections stay small.**
- A SITE or HARNESS line never revalidates a MOD row. It voids only the rows that ran on the bad site, and those rerun
  on the fixed site.
- An objection to one matrix cell re-stages that cell, plus the cells that share the touched fitting or art. The
  pre-look judge re-judges only those crops.
- The re-look is of the changed cells only. The next first-look save carries a **"changed since your last look"**
  label on each of them, so he does not re-inspect what he passed.
- A QUESTION costs no revalidation at all.

**2g. A new standard is not an objection.** When a look sets a new bar ("Acceptance tests really should have pits like
this prepared that span many pit depths + water depths", 2026-11-12 ~10:4x AM; "filled with a wide assortment of
different items different from the existing tests", 2026-11-12 5:36 PM), the result is a set of **new** line items.
They are written at stage 1 and climb from stage 3 or 4 for those lines only. Old passes stand.

**2h. "Very rapid validation passes", his alternative, is how stages 4-5 run for a touched line.** The touched rows run
on the minimal list (22 s load) in an already-staged save, with the scene runner when it exists. The full list is used
only for a line that the preflight shows to be a full-list line (his 23:18Z ruling: *"Any Full Mod tests should have
to justify why they need the Full Mod test: minimal mod lists are to be preferred unless it is explicitly a Full Mod
test called out."*).

### Rule 3. A refusal carries its fix path, and a broken criterion is repaired at once

His ruling, 2026-11-12 2:50 PM PST (log 22:50:36Z; ledger `said` on `RIMMANDRAKE_BIND_REFUSALS_TO_FIXES_NO_CEREMONY_LOOPS`):

> *"We MUST ensure that we don't get trapped letting poorly tuned Judges refuse everything forever, burning tokens, and
> providing no signal to improve upon. ANY refusals must be as detailed as the evidence they are rejecting and include
> the fixes and paths towards passing that are attainable and reasonable. It also MUST include assessment of the
> acceptance criteria themselves. If they are found to be flawed, we need a process to immediately bring a neutral
> fixer in to repair them independent of the Judge itself so as not to bias towards pass = success and repair the
> demonstrated flaws or insufficiencies. Evidence that "this item doesn't pass" is not valuable. Evidence that "nothing
> could ever pass" is grounds for immediate, swift action. Then the item is immediately rejudged once the acceptance
> criteria are repaired. Agreed? This is VITAL. No more repeated loops for the sake of ceremony! No more broken
> acceptance tests causing judges to destroy my account uselessly."*

And his card on the same day (ledger 22:51Z, `EVIDENCE_GATE_FLIP_ENFORCE_AFTER_NOV9`): *who judges a proof → "One
gate, and it refuses"*.

On this map:
- Stage 4's one gate (the evidence gate, flipped from shadow to refusing) and stage 5's judges emit **refusal
  records**, one per refused line item: `evidence`, `observed`, `would_pass`, `smallest_fix`, `criterion_verdict`.
  The full contract, its loop limits and the neutral fixer are already specified in
  `design/specs/2026-11-12-refusal-contract-for-judges-and-gates.md` (nothing built). This map adds no mechanism to it.
- **A refusal is a line item like an objection**, and rule 2 applies to it unchanged: it re-enters at the lowest stage
  that can show it, and only touched items revalidate.
- **His own objections already have this shape** after 2a (what he saw, where, would_pass), so a stage-6 objection
  and a stage-5 refusal travel the same road back.
- The gate flip waits on that spec's T3 (its "no marker" clause cannot pass while the Marker is stopped: 73 of 78
  shadow rejects `[measured in that spec §0]`).

### Rule 4. Nothing reaches him unread, and what stage 5 found is listed first

User-level rule (owner, 2026-10-22: *"Read it first and see if it's obviously broken, malfunctioning, or problematic
before wasting a human's time to tell that to you."*). On this map: stage 6 needs stage 5. Addition: every finding the
pre-look judge made that is **not fixed** heads the look brief as "known, not fixed: you need not report these".
That way his minutes go to what no judge saw.

### Rule 5. The first human look is a dense, labelled savegame built on matrix scenes

His standing principle, 2026-11-12 ~10:4x AM PST (log 18:43:50Z): *"Acceptance tests really should have pits like
this prepared that span many pit depths + water depths to ensure the art works everywhere [...] this is what I
normally expect to see when confirming a solution, so we don't miss anything. This is a basic testing principle I'd
like you to follow when we're doing 1-on-1 testing please."*

His pick 12 (2026-11-12, 22:55Z): *"this is the generalized version of the matrix scenes... combine. It's important
for "first human look" after the system thinks a mod is ready for the human to have a well prepared savegame like this
that's dense and informative and intuitive and well labeled"*.

The save is built by the mod's own proof script (existing rule, `debug_process.md` "Owner-look scenes come from the
proof scripts"), with the zoom mod (standing rule 2026-11-03). Item: `RIMMANDRAKE_PREPARE_FIRST_LOOK_MATRIX_SAVEGAME`.

### Rule 6. A site is asserted, never hoped

His words, 2026-11-12 5:43 PM PST (ledger OWNER note 01:51Z on `RIMMANDRAKE_PROVE_UNDER_LIQUID_LAW_LIVE`): *"You failed
to assert "no mountain above" on the test map, and it collapsed all over."* and *"I believe you can remove overhead
mountain yourself as part of a test map creation from now on."* On this map, every stage-4 run and every stage-6 save
is preceded by site assertions that refuse with the cells named (open sky is built: `validation_core.open_sky_site` /
`assert_open_sky`, 4a06cd3f11). Rows from a site that fails its assertions are void (class SITE, rule 2f).

### Rule 7. When code exists, walk it live before designing more

His ruling, 2026-11-12 5:06 PM PST (log 2026-11-13T01:06:37Z): *"If any part of the mod is built, suggest a live walk
of what already exists today before additional design is added."* That way it doesn't ask predictive things that can
be measured. On this map, stage 1 for a partly built mod takes stage-4 or stage-6 evidence first. (Written into
`roles/designer.md` by the Conductor; program enforcement owed.)

### Rule 8. Check everything Python can before a token is spent

His ruling, 2026-11-12 3:18 PM PST (log 23:18:34Z): *"Before a single token is spent, a deterministic python script
should confirm everything it can about a ticket's setup, specification, environment, basic sanity checks for its
acceptance tests, etc. [...] The only thing to watch is that they don't take 1 hour to check a ticket every time we try
to start, so a metric that should be recorded every run is the precise time this took to run."* This is door 0. Spec:
`design/specs/2026-11-12-ticket-preflight-before-any-token.md`.

### Rule 9. A gate that is always red is not a gate

His card, 2026-11-12 about 2:2x PM PST (ledger 22:47:51Z): *Always-red nightly sweep → "One clean-up, then red wakes
me"* (the option label is our text; he picked it). Section 4 measures the sweep and names the one clean-up.

**Carried from the card draft, not his yet** (no owner words; listed so they are not lost):
- cheapest stage first: maths is proven at stage 3 and pinned by one live row;
- scripts decide stage 4;
- an instrument that cannot tell is fixed before it is read;
- no run in 14 days means deleted or put on a clock;
- one rule for "is this a proof" (he answered this one: rule 3, "One gate").

---

## 3. Tonight as the worked example: the under-liquid pit looks (2026-11-12)

Items: `RIMMANDRAKE_SUBMERGE_PIT_FITTINGS_BY_LEVEL`, `RIMMANDRAKE_FIX_BIG_PIT_SCENE_BUILDINGS_STAY_DRY`,
`RIMMANDRAKE_TUNE_WATER_CLARITY_DARKER_AND_HALF_AS_OPAQUE`, `RIMMANDRAKE_PROVE_UNDER_LIQUID_LAW_LIVE`. Folders:
`D:\ClaudeWork\rimmandrake\conductor\submerge_matrix_20261112\` and `...\underliquid_20261112_evening\`.

| PST | stage | what happened `[measured from the ledger, the log and those folders]` | what the rules say | saved, or silent |
|---|---|---|---|---|
| ~10:40 AM | 6 | Look 1 on `EWA_SUBMERGE_REVIEW_20261112`: one fix ("2m water depth put the northern ladder behind the pit wall art") and one pass (1 m). | One MOD line item, re-entering at stage 3. | **Followed.** Fix 029034d0efce, offline 9 of 9 with a planted fault caught, read back on his save. Narrow, as rule 2 wants. |
| same look | 1 | He set the matrix principle. | Rule 2g: new line items, not an objection. | **Followed:** the 44-pit matrix was built. |
| 11:35 AM | 4 | Matrix: 2,204 rows, 0 FAIL, on the 13-mod list. | Stage 4 green. | **Silent on the main miss.** The rows checked each fitting's own share. Seven code paths each used their own level and visibility rule (`ROOT_CAUSE.md`), and no row asked "same level, same visibility, for every kind of thing". Rule 2c's stage-3 law row would have gone red offline `[guess ~70%]`. |
| 11:39 AM | 5 | Open pre-look found the bed, stone chunk, crate and shelf never covered, and the post drawn as two stubs. | Rule 4: list them first. | **Partly followed:** the report put goods and swale to him as "Your call" and filed four side findings. The D8 inconsistency and the shadows were not seen by the judge. |
| ~4:2x PM | 6 | Look 2 on the matrix save: 8 fixes, 3 passes, 1 question. Two were "major fix": the D8 row's case-by-case variety, and shadows outside the pit. | Rule 2a: 12 line items, 3 of them pinned. | Root cause: seven paths, replaced by one law, `RM_UnderLiquid` (441c321a20dc). **A shared core change: the full rerun was right (2d).** The passes ("cover-line is good", "peaks out correctly") were not pinned (2e). |
| 5:43 PM | 4 | The matrix collapsed under a mountain roof while he watched. | Rule 6: SITE class; void the site's rows only. | **The rule was born here.** The guard landed and was proven 7 of 7 both ways; rows from that site were voided. No MOD row was reopened. Correct under 2f. |
| 5:53-5:57 PM | 6 | Items destroyed by the collapse (HARNESS); a label read "Canal 1m" (MOD); he asked for god-mode pour and drain. | 2a classes; the god-mode ask is new work, not an objection. | Followed: one item each. |
| 6:12 PM | 6 | Water look: 2x too opaque at depth, colour too light, a dark-to-light jump on a wet floor. One pass: "it's very transparent at first". | Three MOD line items at stage 3. "Transparent at first" is a pinned line. | **The rule would have saved a regression.** The retune (4f158b6cb442) halved the whole curve: shallow 0.5 m went from 0.49 to 0.25, by the builder's own note ("Judgement call"). Nothing held the pass; 2e would have stopped it at stage 3 or labelled it for him. |
| 6:16 PM | 6 | Big-pit screenshots: nine observations. MOD: buildings dry, shadows, corpses/pawns dry, labels bright. SITE/HARNESS: ring straddles the walls, wild animals, `stuff=null`. SAVE: spike references not deep-saved. QUESTION: the Segnosaurus. | 2a: nine line items in four classes. | **Silent at filing.** All nine went into ONE item. The briefs split them across two helpers (draw = MOD, scene = HARNESS); the ledger did not. His deepest-pit screenshot was never found: a look taken outside a prepared save leaves no cell ids. |
| 7:15 PM | 2-3 | Draw + retune landed: dotnet SelfTest 1,310 of 1,310, parity selftest GREEN, model sweep 1,680 cases 0 breaks; L0 recorded; "every picture UNTESTED". Scene builder: 674 checks, planted fault red. God mode: 11 of 11. | Stage 3 done for those lines; stage 4 owed. | Followed. Two files left DIRTY (not yet reviewed). |
| 8:01 PM | 4 | Live helper: big-pit verify 253 PASS, 6 FAIL (item HP, a HARNESS baseline), 1 UNMEASURED (label text: no reader). God mode: DrainAll refuses on an emptied square (MOD). | 2f: the HARNESS fails do not hold the MOD rows. | In progress at this writing. Stage 5 self-look and the keeper save `UNDER_LIQUID_LAW_BIGPIT_20261112b` are next. |

Spend on this thread tonight, from the ledger end notes `[measured]`:
- submerge fittings, 6.77M tokens (Opus, 53 min);
- scene builder, 1.47M (Sonnet, 8 min);
- god mode, 2.60M (33 min);
- draw + retune, 0.25M (41 min);
- the live helper is still running (UNMEASURED).

His minutes: three looks, UNMEASURED.

**What the rules would have saved:**
- one regression reaching his next look (the pinned shallow end);
- most of look 2's "major fix" `[guess ~70%]`, by one stage-3 law row asking every thing kind the same question;
- a mixed-class item whose state can only say "partly done".

**Where the rules are silent (open, see QUESTIONS.md):**
- who decides that an objection is small enough to close on a stage-5 crop without his re-look;
- what wakes when a stage-4 helper finds a MOD fault after he has left (tonight's DrainAll);
- a look taken from screenshots outside a prepared save. Rule 5 prevents it for first looks only.

---

## 4. The always-red nightly sweep

### Measured

- `Transient/selftests_nightly.log` in the bench clone holds 29 RESULT lines, **all RED** `[measured]`.
- Last night (2026-11-12 03:00, 2,913 s wall): PASS 1,531, FAIL 41, CRASH 3, UNMEASURED 8, SKIPPED 3, of 1,586
  `[measured, selftests_nightly.last]`.
- I re-ran the 34 quickest of the 44 reds at HEAD 3bf1e44fbf: **30 FAIL and 1 CRASH are still red**, 3 now pass
  (`selftest_codex_seats`, `selftest_dispatcher_r2`, `selftest_required_checks`, all host-state dependent)
  `[measured, run_selftests.py --only, 48 s]`. The 10 slow ones were not re-run.

The 44 reds, by cause. Each test was classed from its first failure line, so each assignment is `[guess ~75%]`. The
list is in `design/RimMandrake/validation_map_nightly_reds_2026-11-12.txt`.

| cause | count | the tests |
|---|---|---|
| **A repo-wide guard broken by an unrelated commit.** The test is right, and the tree drifted under it: stale baselines and generated files, prose naming retired things, unparsable live-proof files, unreviewed statics, a call without a timeout | **26** | `block_orphan_item_prose`, `lines_proof`, `drawn_art_ruled`, `extra_art_commission`, `extra_art_filed_rows_kept`, `standin_shadowed`, `alpha_biomes_census`, `biome_twins_retired`, `call_deadline_lint`, `fauna_normalization`, `fuelsnows_name_cull`, `modlist_order_lint`, `one_path_seam`, `proof_restore_check`, `rmpaths`, `settings_screens`, `static_game_state`, `bridge_hooks`, `bench_word_prose`, `conductor_authority`, `liveproofs_wrappers_ruling`, `relentless_live_round`, `launch_gate`, `swbestiary_pack_overlays`, `researchretag`, `entrypoint_inventory` |
| **A fixture or expectation behind changed code** (a tier's mod set changed, a module moved, a scene renamed) | 8 | `flowworks_northstar`, `northstar_driver/selftest`, `northstar_driver/selftest_record_status`, `natives_drink_own_water`, `metal_eater`, `cathedralpass_retaliation`, `selftest_incident`, `checkout_identity` (CRASH: `No module named 'scene_rows'`) |
| **Host dependence** (Windows tools, a live lock on SteveDesktop, /tmp races) | 7 | `codex_pwset_retry`, `codex_seats`, `engine_review_leftovers` (no `tasklist.exe`), `dispatcher_r2`, `required_checks`, `modlist_case`, `scratch_reap_tmp` |
| **Slower than the 240 s cap** (CRASH: timeout) | 2 | `hole_prison`, `tilefeatures_landform_geometry` |
| **A checker gap**: 1 of 79 planted mutants not caught (`session_b_uses_steam`) | 1 | `second_game_mutants` |

**Why it stays red.** Most of the reds (26 of 44) are guards over the whole tree. The commit rule runs "only the tests
for what you changed", and a repo-wide guard is never one of those. So the commit that breaks it never runs it, and the
nightly sweep is the first to see it, with no author attached.

### What already exists (searched before proposing)

- **The known-red list and the build cop** (`src/RimMandrake/Utils/known_reds.py`, list
  `src/RimMandrake/rimflow/selftest_known_reds.json`; design `build_system_practices_2026-11-03.md` #4). A red on the
  list is silence; any other red gets an item and a 72 h deadline. Today the list has 12 entries, all expiring
  2026-11-15, 7 of them parked on `NIGHTLY_SELFTESTS_DRAIN_THIRTEEN_RED_NIGHTS`. `known_reds.py report` shows **25
  OVERDUE** reds `[measured]`.
- **Its reader, `rm-ops-watch.timer`, is inactive**, and so is `rm-metronome.timer` `[measured: systemctl --user
  is-active]`. The ledger records it broken since 2026-11-07, the night of his pipeline stop. So the "red wakes"
  half is built and switched off. `RED_COP_BUILD_NO_ORPHAN_REDS` was reopened by its dead-man.
- **The drain item already exists**: `NIGHTLY_SELFTESTS_DRAIN_THIRTEEN_RED_NIGHTS`. It has been "doing" since
  2026-11-04, taken by Relentless, which stopped on 2026-11-06. `NIGHTLY_SELFTESTS_RESCUE_RED_SINCE_FOREVER` was
  superseded into it; `SELFTEST_NIGHTLY_SILENCE_KNOWN_REDS` (the known-red list's own item) is still open.
- **The nightly job** reports to `pulse.py` (RimPulse, retired 2026-11-03). No route in
  `rimflow/alarm_routes.json` names the nightly sweep `[measured: grep]`.

### The one clean-up (filed, not done)

Filed as `RIMMANDRAKE_CLEAN_NIGHTLY_SWEEP_ONCE_THEN_RED_RINGS`. It **replaces** the stranded
`NIGHTLY_SELFTESTS_DRAIN_THIRTEEN_RED_NIGHTS`, so that item closes and names its successor. One side effect follows:
the 7 known-red entries parked on the old item stop covering their tests, which is the clean-up's intent.

One pass over the 44:
- each test is fixed;
- or it is deleted, with its reason in the commit;
- or, for a red that truly needs longer, it is parked on `known_reds.py` with its own open item (then this item
  stays open until that one closes: the acceptance test below does not excuse parked tests);
- the two timeouts get a measured budget or a split;
- the five host-dependent tests stop reading live host state, or are tagged into the deployed tier.

Then the waker is switched on, so that the next red wakes someone (which waker is a real choice: QUESTIONS.md Q1).

**Acceptance test** (watched failing on base 3bf1e44fbf: 31 of the 34 light ones red, and 25 OVERDUE):

```
cd <clone>
L=design/RimMandrake/validation_map_nightly_reds_2026-11-12.txt
python3 src/RimMandrake/Utils/run_selftests.py --only $(for f in $(cat $L); do [ -e "$f" ] && echo "$f"; done) \
  | grep -E '^PASS [0-9]+/[0-9]+ +FAIL 0/[0-9]+ .*CRASH 0/'        # expect 1 line
python3 src/RimMandrake/Utils/known_reds.py report | grep -c OVERDUE   # expect 0
```

The item closes with `--live` on the waker unit (the operational-item rule). Expected pass: both greps as noted, on the
first nightly after the pass.

---

## 5. Inventory errors, filed

These are the errors in `validation_inventory_2026-11-12.md` and its neighbours that the card draft found (§5) and
nobody had filed. Each item carries a grep acceptance test, watched failing on 3bf1e44fbf.

| item | the error |
|---|---|
| `RIMMANDRAKE_RECOUNT_INVENTORY_KERNELS_ONE_FILTER_THREE_ANSWERS` | §0 says 72 fuzz/kernel tests ran and 71 passed; the table row says 81 PASS; a filename filter gives 74. And "3 of 110" `validation.py` files with `shows=` dates from 2026-10-03, when 137 files exist today |
| `RIMMANDRAKE_CORRECT_INVENTORY_SKIPPED_MEANS_TIER_NOT_CACHE` | §2 defines SKIPPED as "skipped on unchanged evidence". The 3 SKIPPED are deployed-tier tests; the cache answered 0. The same row garbles the RESULT line |
| `RIMMANDRAKE_RECOUNT_NEVER_BUILT_ONE_SAID_THREE_LISTED` | §0 counts 1 designed-never-built scheme; §4 lists more (the scene runner and the observatory have no table row) |
| `RIMMANDRAKE_REWORD_STOPPED_A_FREEZE_IS_NOT_A_PAUSE` | "STOPPED with Relentless on 2026-11-06" mixes the 2026-11-06 freeze with the later owner pause; the Relentless store still runs detached helpers |
| `RIMMANDRAKE_STRIP_FOUNDRY_ACCEPTANCE_PROSE_RETIRED_TWICE` | CLAUDE.md still calls Relentless' live round "the acceptance sweep for every mod" (stopped, and picked for deletion). `testing_policy_2026-10-28.md` §2.10 says FOUNDRY owns FlowWorks, and `infrastructure/VALIDATION_LADDER.md` L3 says "beyond FOUNDRY's grade", after FOUNDRY's retirement |

The card draft's seventh point (flyer paused state reads) touches his flyer rule, so it is a question (QUESTIONS.md
Q5), not an item.
