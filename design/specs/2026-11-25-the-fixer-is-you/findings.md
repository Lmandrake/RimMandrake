# The fixer is you: where the rule texts let an agent defer, and where the principle should stand

Item: `RIMMANDRAKE_SCAN_RULES_FOR_FIXER_IS_YOU_HOMES`. Written 2026-11-25, about 11:15 AM PST, by a detached BENCH run
(Opus 5.5) at the Conductor's instruction. This is a report only. No rule text, skill or code was changed.

## How the texts were read

- Each listed text was searched for fence words (hand off, set down, file a ticket, wait, escalate, defer, LEFT OPEN,
  NEXT:, polish, not yours, ask him, stop, later run). Each hit was then read in its context. Long texts were not read
  end to end: a sentence that defers with none of those words could be missed.
- Texts searched: `CLAUDE.md`, `PURPOSE.md`, `GUIDING_PRINCIPLES.md`, `infrastructure/agents/` (CHARTER, CONDUCTOR,
  Agent_Policy), every file of `src/RimMandrake/rimflow/roles/`, `.claude/agents/rm-*.md`, the printed strings of every
  non-selftest hook in `.claude/hooks/`, `design/RimMandrake/standing_rulings.md`,
  `design/RimMandrake/delegation_policy.md`, every `skills/*/SKILL.md`, and the brief strings of
  `src/RimMandrake/rimflow/*.py` (search words: road back, files a named item, hand, NEXT:, LEFT OPEN, dated wait, set
  down, to the Conductor). The refusal texts of `filing_gate.py` and the defer verbs of `cli.py` (`file`, `wait`,
  `block`, `close`, `drop`) were read.
- Could not look: none of the listed texts was unreadable. Not read: `rimflow needs` (its gate, if any), and the
  brief strings of `maturation_dispatch.py` beyond the search hits.
- `GUIDING_PRINCIPLES.md`, `PURPOSE.md`, `infrastructure/agents/CONDUCTOR.md` and `delegation_policy.md` hold no fence
  of this kind. `PURPOSE.md:110-112` and `CHARTER.md:37-48, 156-158` already state the principle.

## The short answer

The principle already exists: test 2 of `CLAUDE.md` §Touching code has a cost ("you are its fixer, in the same run").
The doors around it are in four places:

1. **One list, nine stale copies.** The evidence list of test 2 still has "your assigned work would not finish" in nine
   texts. `filing_gate.py:28-29, 56` says that it is not a class. An agent that reads its role file believes that it
   may set work down because the work is long.
2. **The program-written briefs name the owner too widely.** Four fixer briefs in `maturation_autonomy.py` and the
   detached-helper footer say "the owner's decision", "a ruling", "a classification" or "more than this run" as reasons
   to leave work. None of these is one of his five acts. The footer's "an act of the Conductor's" is where most of the
   26 waits that name the Conductor come from (part 2).
3. **"Build it, or file a ticket for it."** The bridge rule gives filing as an equal choice, in four texts.
4. **The refusal texts offer a menu.** The filing gate and its Stop hook print three or six equal ways out at the moment
   the agent decides. The owner said on 2026-11-25 that the refusal must state the requirements, with no menu.

## Part 1. Fences

A row is one sentence. A sentence that stands in several files is one row, with each place. Counts: **35 NEEDED, 16
CONTRADICTS, 15 UNCLEAR** (66 rows).

### NEEDED: the fence guards a named danger

| place | the fence | the danger it guards |
|---|---|---|
| `CLAUDE.md:105`; `standing_rulings.md:2377` | Do not run a mod forward while a BLOCKS ticket lies on its path. | a wrong verdict, a lost trial, a ghost run (pipeline repair continues, `CLAUDE.md:113`) |
| `CLAUDE.md:381`; `standing_rulings.md:2111-2118`; `maturation.py:2130-2134` | Hand off a pipeline defect only with the test-2 evidence. | this is the principle with its exceptions |
| `CLAUDE.md:388`; `standing_rulings.md:2146` | His five acts still wait for him. | his five acts |
| `CLAUDE.md:442-443`; `standing_rulings.md:697-699` | A finding that fails test 1 gets no fix and no ticket. | the touch itself (review-born tickets beget 2.5 times the descendants, `standing_rulings.md:662`) |
| `CLAUDE.md:612`; `standing_rulings.md:1687`; `designer_scene_contract.md:67`; `live_kinds.py:28`; `skills/live-debugging-proof-harness/SKILL.md:181` | A scene short of X of Y escalates to the Conductor. | a guessed X decides a bar |
| `CLAUDE.md:669, 678`; `standing_rulings.md:570, 2730, 2780`; `code_review.md:100-110`; `rm-judge.md:21` | A nit is one polish line; nobody fixes it. | review churn (same measurement) |
| `standing_rulings.md:564`; `code_review.md:56` | A FLAGGED file is not reviewed again; it waits for the weekly examination. | the third read that never ends |
| `standing_rulings.md:766-775`; `maturation.py:2219-2224` | Only an unfixable mod fault or an undecided bar goes down the road back. | a bar passed with no check |
| `standing_rulings.md:1326-1327` | A limit whose removal is outside your tools is handed off with the evidence. | no tool |
| `standing_rulings.md:2174` | A wait ends by itself and counts nothing. | none needed: a wait is not a defer |
| `bundle_worker.md:54-56` | If no game can take the pass, wait for one, with a PROGRESS note each 30 minutes. | every game held |
| `bundle_worker.md:76-79` | A refusal needs a reason about the ticket; "the fix is unknown after a real attempt (say what you tried)". | the list, worded well (a model text) |
| `code_review.md:5-6`; `quiet_scan.md:42-43` | A bar is never yours to change. | a north-star bar |
| `code_review.md:44-46` | If you cannot write the clone, return your Problems. | no tool |
| `quiet_scan.md:40-41` | Never fix a style point, a stricter test, a tuning number or a rare failure. | test 1 |
| `conductor.md:266, 371` | The Conductor sends builds and multi-file work to helpers. | the window must answer him first (`conductor.md:373` keeps small acts his) |
| `conductor.md:663-665` | A Codex lane leaves a one-mod ticket to that mod's pipeline run. | files held by another run |
| `operations.md:153-156, 405-406` | Alarm question 4 (the two tests); a loosening goes to the Conductor. | a looser bar is the Conductor's act |
| `designer.md:88, 105`; `designer_exam.md:74`; `designer_dialogue.md:13`; `designer_grounding.md:60`; `fable_rescue.md:81-82, 241-242` | Only an ask with evidence against the obvious answer waits for him. | Evidence-for-Ask |
| `designer.md:318-321` | A system fault is fixed in the run; hand it off only with the evidence and what you tried. | the principle (a model text) |
| `fable_rescue.md:59-62` | Moving work to a later version is his move or the Conductor's act. | the Design Version rule |
| `list_shape.md:32-38, 40-49` | Route a part only for a judge, the owner, the Conductor or a sitting; `--size large` only with evidence. "It is much work" is not evidence. | a model text |
| `walk_brief.md:55` | If no game is free, file the pen staging as a ticket under "Known, not fixed". | every game held |
| `designer_cleanse.md:56` | The design run writes no game code and does not touch the game. | the role's scope |
| `runner_options.md:143` | If settings are broken, stop and stamp DOWN. | a broken game |
| `rm-judge.md:22` | You do not fix the work that you judge. | a taste judge becomes the maker (`CLAUDE.md` §Only five acts: "A judge agent makes each taste call, never the maker") |
| the six `.claude/agents/rm-*.md` (for example `rm-fixer.md:92`) | File every finding that you do not fix and that passes test 1. | a finding lost in a transcript |
| `rm-testpilot.md:134` | If both takes are refused, stop and say so. Never `--force`. | his OWNER hold |
| `.claude/hooks/queue_lint.py:188-191` | Do not redirect another seat's work; fix what is false, file the rest. | files held by a live owner |
| `.claude/hooks/block_agent_over_slots.py:204-206, 227` | A full slot allowance is a wait. | the slot and account rules |
| `.claude/hooks/switch_checkpoint_signal.py:26-35` | Checkpoint and launch nothing during an account switch. | the account plan |
| `maturation_autonomy.py:2044` | No offline test can show it: LEFT OPEN and `needs --to game-up`. | Stage 6 work (the same brief runs the in-game check on a free game first) |
| `skills/rimworld-deploy/SKILL.md:278` | Assemblies deploy in the shutdown window. | the game locks the DLL |
| `skills/rimworld-layout-layers/SKILL.md:125` | Report a missing path before the write. | a blind write |
| `Agent_Policy.md:244-247` (three of its five parts) | Escalate instead of guessing if you would invent a defName, a measurement disagrees with the item, or a tool says success and you cannot see the effect. | a guess dressed as a fact |

### CONTRADICTS: the fence defers where test 2 says to fix in the sitting

| place | the fence now | the corrected sentence |
|---|---|---|
| `CLAUDE.md:451`; `CHARTER.md:55`; `standing_rulings.md:712`; `rm-bridge.md:94`; `rm-builder.md:105`; `rm-consult.md:76`; `rm-fixer.md:91`; `rm-judge.md:88`; `rm-testpilot.md:256` (nine places) | "your assigned work would not finish" is evidence to set a fix down. `filing_gate.py:28-29, 56` refuses it as a class. | Delete the bullet. Add: "A large task, a long run or a full context is not evidence. A fresh session goes on from your notes." Change "the fix is not known" to "the fix is not known after a real attempt: name what you tried". (`selftest_touching_code_cost_rule.py` pins the test-2 opening, not the list, so the edit keeps it green; check at the edit.) |
| `CLAUDE.md:45`; `standing_rulings.md:1922`; `skills/rimbridge-companion/SKILL.md:15`; `skills/live-debugging-proof-harness/SKILL.md:303` | "build the bridge function, test first, or file a ticket for it" | "Build the bridge function, test first. File it only with the test-2 evidence." |
| `CLAUDE.md:382`; `standing_rulings.md:2122-2123`; `maturation.py:2134-2135` | "A mod's gaps (its bars, its build work, its findings) still go through the stages." A finding of a mod is fixed in the sitting since 2026-11-20 (`standing_rulings.md:716-791`). | "A mod's unbuilt bars still go through the stages. A mod fault that your run can fix, you fix in your run." |
| `CLAUDE.md:828` | "Edit skills only in fresh-context curation sessions." `CLAUDE.md` §Correctness outranks seat ownership says to fix a false statement on sight, in any file. | "Fix a false sentence in a skill on sight. Restructure a skill or add to it only in a fresh-context curation session." |
| `Agent_Policy.md:249` | "Escalating is a success; record it." | "An escalation that names what you tried and what would settle the question is a success. An escalation in place of an attempt is not." |
| `quiet_scan.md:44` | "When you cannot fix a Problem offline (it needs the live game, his decision, or the fix is unknown), file one ticket" | "When the fix needs one of his five acts, is unknown after a real attempt, or needs a game while `game_lock.py query all` shows none free, file one ticket that names what you tried." |
| `operations.md:78-79` | "The fold is yours. To do the fold, build the check … Or file the fold as an item" | "The fold is yours: build the check, hook, rule or live line in this run. File it only with the test-2 evidence." |
| `operations.md:375` | "find which instruction or prompt leaked the token talk, and file the fix" | "find the instruction that leaked it and fix that instruction in this run." (The check measures nothing today: the touch is small.) |
| `.claude/hooks/filing_refusal_before_stop.py:72-75` | Three equal ways out: did, filed, dropped. | Lead with the act: "Do the work now, test first, land it, then `--did-it <sha>`. You hold its context; a later run must read it all again." Then state the requirement of a valid set-down (the test-2 evidence, with what was tried), with no list of ways. |
| `filing_gate.py:52-56` | The first refusal prints the six classes. | The same as above. This repair is already part (6) of `RIMMANDRAKE_TIGHTEN_SET_DOWN_CLASSES_ANY_TWELVE_LETTERS_PASS` and its 2026-11-25 design change (an LLM filer that pushes back). Not filed again. |
| `detached_helper.py:146-147` | "build what is not built, or file it as ONE ticket and close with `--remainder`" | "Build what is not built. A remainder is filed only with the test-2 evidence (`--not-now`)." |
| `detached_helper.py:148-150` | "When what is left is not a helper's to do (the owner's decision, an act of the Conductor's, a date), also put a dated wait" | "When what is left is one of his five acts, a looser bar, a hold to lift, or a date, put a dated wait that names that act. A choice between known fixes is yours: take the one you recommend and log it delegated." |
| `maturation_autonomy.py:2059` (walk-finding fixer) | "If the fix is his (a pick, a ruling) or needs more than this run" | "If the fix is his pick (one of his five acts), do every part that is yours, then write LEFT OPEN: naming the pick. A long fix is still yours." |
| `maturation_autonomy.py:2074` (pipeline-defect fixer) | "or the fix is the owner's (a bar, a ruling, a spend cap)" | "or the fix needs one of his five acts or a looser bar (the Conductor's act)". A ruling that the standing rules settle is yours. |
| `maturation_autonomy.py:2085` (version-Problem fixer) | "If what it owes is his pick or his look, or more than one run" | Delete "or more than one run". |
| `maturation_autonomy.py:2101` (road-back fixer) | "or the fix is the owner's (a bar, a ruling, a classification)" | Delete "a classification": the same brief's `WRONG_CHECK_RULE` makes the run class the line. "a bar" becomes "a looser bar (the Conductor's act)". |

### UNCLEAR: what would settle each

| place | the fence | what would settle it |
|---|---|---|
| `standing_rulings.md:714` | "The ticket that you file carries that evidence, and the fix where you could see it." | Whether "the fix where you could see it" invites a diagnosis on the ticket, which `standing_rulings.md:818` and `CHARTER.md:48` forbid. Settle by the Conductor's reading; "the fix that you would make, when the evidence stops you" removes the doubt. |
| `standing_rulings.md:1543` | "An instrument fault becomes repair work, and the item waits without a strike." | It names no repairer. If the run that attributes the fault repairs it (as `standing_rulings.md:743` says for a wrong check), say so here. |
| `Agent_Policy.md:244-245` (two of its five parts) | Escalate if "the criteria do not decide the case" or "the change reaches files outside the ones named". | This is the only guard against a cheap worker that widens its task (part 5). Settle by a count: did a Sonnet worker widen a task and cause a failure? If yes, NEEDED. If none in the record, reword to "name the extra files in your close". |
| `conductor.md:300-301` | A canon finding that is more than a one-file wording edit is filed to the Conductor lane. | Whether the Conductor can launch the fix at once instead of filing it to itself. |
| `conductor.md:516` | "Park an owed item on a trigger with `rimflow wait`." | Whether the trigger must be outside the Conductor (a date, a run's end). An owed item parked on the Conductor's own act is a self-wait. |
| `conductor.md:632` | "repeat errors: `lessons.py add` and a ticket" | Whether "a ticket" means a launched fixer now. "and launch the fix" removes the doubt. |
| `list_shape.md:59-60` | A dated wait "when the next act is someone else's". | Bound "someone else's" to the four routes of step 3 (judge, owner, Conductor, review). |
| `walk_brief.md:27-30` | Each thing the walk-brief reader notices goes in the brief or in a ticket; it has no veto. | Whether a fix before his walk would make the staged walk save stale. If yes, NEEDED. If no, a fixable thing is fixed. |
| `rm-testpilot.md:100, 152` | At most about 5 new items per sitting; past that, an observation stays a PROGRESS note. | The cap names no danger beside it (`CLAUDE.md` §No limit without the danger it guards). Name the danger (review-born ticket churn) or remove the cap. |
| `cli.py:2285` | "Not built (and not yours to waive)? Leave the item open with a `LEFT OPEN:` note saying so." | Whether the close refusal should first say "build it". |
| `detached_helper.py:143-145` | "close it … or, when anything is left, write a note whose text starts `LEFT OPEN:`" | LEFT OPEN relaunches a fresh session, so it is not a defer by itself. It becomes one with a dated wait (row above). Settle by whether the relaunch is enough of a guard. |
| `detached_helper.py:151` | "write your state, evidence paths and one imperative NEXT as a note" | Whether a NEXT asked of every run invites the "diagnosis instead of the fix" that `standing_rulings.md:818` forbids. |
| `maturation_autonomy.py:2075` | The pipeline-defect fixer: "Never take the bridge or a game." | `standing_rulings.md` §The bridge is passed through one file lets any role take a free game. Settle by the reason for this ban (a held mod? a slot?). |
| `maturation.py:2330-2333` | A bar that cannot get a check offline goes as a question to the Conductor. | Whether this builder stage may take a free game for a live check. |
| `skills/rimworld-art-evaluation/SKILL.md:45` | Regeneration round ≤ 3, then ESCALATE. | To whom: a delegated art judge (NEEDED) or the owner (then it contradicts "agents decide nearly everything, art included"), and the danger of the count of 3. |

## Part 2. The other doors

| door | what the tool checks now |
|---|---|
| `rimflow file` / `spawn` in a helper run | Gated: `filing_gate.py` refuses without `--not-now "<class>: <evidence>"` (exit 6). Any class plus 12 characters passes (`MIN_EVIDENCE`, `filing_gate.py:46`; `RIMMANDRAKE_TIGHTEN_SET_DOWN_CLASSES_ANY_TWELVE_LETTERS_PASS`). The Stop hook `filing_refusal_before_stop.py` blocks the end twice (`MAX_BLOCKS = 2`), then lets the run end. |
| `rimflow file` by the Conductor, the owner or a program | No gate. |
| `close --remainder <ID>` | The remainder is a `file`, so a helper's goes through the filing gate. `close` asks when its words name an unbuilt part. |
| `rimflow wait` | No gate on the reason. `cmd_wait` (`cli.py:2505-2520`) checks only that `--until` is a date ahead of now. It does not check who the reason names or why that party must act. |
| `rimflow block` | Form only: kind, lift event, a cycle, a blocker that can deliver (`cli.py:2415-2470`). No evidence. |
| a `LEFT OPEN:` note | No gate on its text. `left_open_continue.py` relaunches a fresh session; `list_shape.md` gives one more run. A LEFT OPEN plus a dated wait stops the relaunch: that pair is an ungated defer. |
| a `NEXT:` note | No gate. `standing_rulings.md:818` forbids a NEXT in place of the fix; nothing checks it. The helper footer asks for one NEXT of every run. |
| a line on `polish.md` | No gate, by design: the significance rule bounds it, and a line there is never work. |
| a report that ends "still owed", OWED or LEFT OPEN | `run_end_wake.py:174` lists such runs first for the Conductor. That routes the debt; it does not check its evidence. |
| `REFUSED BY BUNDLE:` note | No gate; it reaches the Conductor and his digest (`bundle_worker.md:80-82`). |
| `drop --not-worth-it` | 12 characters. `drop` refuses only while open items wait on the item. |
| an escalation under `Agent_Policy.md:244` | No gate. |
| a Designer `waiting_owner` ask | Gated: the launcher sends an ask only with its `evidence_against` filled. |

### The waits that name the Conductor

`python3 src/RimMandrake/rimflow/cli.py queue CONDUCTOR --owed --all` at 11:08 AM PST printed `OWED 36 (actionable 25,
waiting 11) … 26 waits name you`. The 26 are "YOURS BY A WAIT: a ticket whose dated wait names the Conductor; nothing
else starts it". Five of the 26 dates had passed (2026-11-20 to 2026-11-24) and still stood.

The sample is the odd positions of that list (1, 3, …, 19), each read from its own wait event:

| item | the wait, short | class | why |
|---|---|---|---|
| `RIMMANDRAKE_CLEAR_FLOWWORKS_PAPERWORK_TO_GAME_ONLY_ROAD` | the Conductor picks a route on another item and runs the game-only advance (date passed 2026-11-20) | CONTRADICTS | a choice between known routes; the run could take its recommendation, logged delegated |
| `RIMMANDRAKE_UNSTICK_PYRELANDS_FIXER_COUNT_TWELVE_FOUR_REFUSED` | the Conductor decides the fixer_runs limit, and the unguarded `steward_max_per_version` | NEEDED | raising a limit is a loosening, the Conductor's act. (The unguarded limit itself was a pipeline defect that the run could have fixed.) |
| `RIMMANDRAKE_STUDY_ONE_PLACE_FOR_OWED_WORK_HE_ASSUMED_IT_EXISTED` | the Conductor shows him `ways_forward.md`; he picks a way | UNCLEAR | settled by whether the study's order asked for his pick |
| `RIMMANDRAKE_CUTOVER_PILOT_MODS_TO_LEDGER_SAME_DAY` | the Conductor rules on the scope: shrink (recommended), drop, or build | CONTRADICTS | a recommended choice between known options |
| `RIMMANDRAKE_FIX_MINER_JUDGE_FAILED_SLACK_EIGHT_OF_TWENTY` | the Conductor rules: end at round 5 (recommended) or order round 6 | CONTRADICTS | the same |
| `STEVE_FILLER_MONITOR_FAIL_FINDINGS` (the legacy name of the testq filler's FAIL host) | the Conductor ends the 2026-11-24 non-mod-work order, then removes `fill.stop` | NEEDED | a stop order binds until its owner lifts it |
| `RIMMANDRAKE_CENSUS_COSTLY_TEST_ACTS_REPEATED_HE_SAW_SHIP_FLY` | the Conductor files the groups from `one_page.md` and rules on the wire | CONTRADICTS | filing the groups is a helper's act; the run held the context |
| `RIMMANDRAKE_SEND_STAGE_SIX_CHECKS_TO_STEVE_GAMES_NONE_CARRY_A_BLOCK` | the Conductor reads the report and closes; "nothing is left for a helper" | CONTRADICTS | the agent that did the work closes it with its evidence (`standing_rulings.md` §A small change is checked by the agent that made it) |
| `HARNESS_REPAIR_CAUSE_AC81755A_4` (the legacy name of a FlowWorks harness repair) | the Conductor resumes the SteveDesktop lane after the owner's pause for the SSD move | NEEDED | his pause |
| `RIMMANDRAKE_ANSWER_SEVEN_TERMS_NO_SOURCE_DEFINES_GREY_MUD` | the Conductor settles five terms | UNCLEAR | settled by whether a term's meaning needs his words or a run may take the obvious reading, logged delegated |

Sample result: **3 NEEDED, 5 CONTRADICTS, 2 UNCLEAR.** Each CONTRADICTS wait matches the footer sentence
`detached_helper.py:148-150` ("an act of the Conductor's"). Four of the five are a choice between known answers, which
the TIGHTEN item (its part 2) already names. The fifth is a close that the run could make itself.

## Part 3. The statement

Three wordings, each under 30 words. Each names the few exceptions: no tool, files that a live run holds, a verdict
that must stay blind, one of his five acts (a looser bar is the Conductor's), and a fix still unknown after real tries.

1. **The plain rule (28 words).** "You are the fixer. When you find a fault, fix it in this run, test first. A later run
   knows less. Hand it on only with test-2 evidence."
2. **The higher calling (29 words).** "In every role the fix is yours. See it, do it, now. Hand on only for no tool, held
   files, a blind verdict, his five acts or failed tries."
3. **The doubt rule (28 words).** "When in doubt, the responsibility is yours: find, fix, test and close it now. To defer,
   write why you cannot: one of the test-2 reasons, with its evidence."

**Recommended: wording 1**, with the corrected test-2 list printed under it at each home.

- It gives the reason, and the reason is the measured cause: the run that sets work down holds the context, and the
  later run must read it all again.
- It names the exceptions by one reference. The copied list has already drifted: the gate dropped "would not finish",
  and nine texts still carry it. One list, in `standing_rulings.md` §Touching code has a cost, test 2, stops new drift.
- "test-2 evidence" is a term that a reader can name in one step only when the list stands beside it. So each home
  prints the list under the sentence.
- Wording 2 suits a refusal text, where the list must be in the line. Wording 3 keeps "When in doubt", from the owner's
  draft, and it suits the role files of judges and reviewers, where doubt is the usual state.
- His suggestion of three distinct attempts before a set-down is the Conductor's to weigh. A fixed count is a limit,
  and §No limit without the danger it guards asks for its danger. "Failed tries" in wording 2, and "what you tried" in
  the list, carry the idea without a number.

## Part 4. Homes (six)

Each home is a place that an agent reads at the moment it decides to defer. Each replaces sentences; none only adds.

1. **The filing refusal.** `filing_gate.py` `refusal()` (lines 52-56) and `.claude/hooks/filing_refusal_before_stop.py`
   lines 72-75. Replace the class list and the three-way menu with wording 2 and the requirements of a valid set-down.
   `RIMMANDRAKE_TIGHTEN_SET_DOWN_CLASSES_ANY_TWELVE_LETTERS_PASS` holds `filing_gate.py` and is redesigning it, so this
   home is that item's. Give it the wording; do not open a second run on the file.
2. **The detached-helper footer.** `detached_helper.py:143-151`, read by every detached run at its start. Replace the
   "or file it as ONE ticket" sentence and the "(the owner's decision, an act of the Conductor's, a date)" sentence
   with wording 1 and the corrected sentences of part 1. This home stops the largest measured source of Conductor
   waits.
3. **The fixer briefs that a program writes.** `maturation_autonomy.py` `fixer_brief` (lines 2059, 2074, 2085, 2101)
   and `maturation.py` `SELF_FIX_RULE` (2130-2136). Replace the four different "the fix is the owner's (…)" lists with
   one constant that holds wording 1 and the corrected list. Each brief then cites the constant.
4. **The six agent files.** The test-2 line of `.claude/agents/rm-*.md` (for example `rm-fixer.md:91`). Replace that
   line with wording 1 and the corrected list. This deletes "your assigned work would not finish" six times. Use wording
   3 in `rm-judge.md` and keep its "a verdict that must stay blind" exception first.
5. **The root rule.** `CLAUDE.md` §Touching code has a cost, the test-2 bullets (444-451). Replace the opening
   sentence with wording 1 and the bullet list with the corrected list. In the same edit, fix `CLAUDE.md:45`,
   `CLAUDE.md:382` and `CLAUDE.md:828` (part 1), and replace `CHARTER.md:52-55` with a pointer to this section. The
   CHARTER gains no rule.
6. **The wait door.** `cli.py` `cmd_wait`, in a helper run. Today the door prints only `wait <ID> until <date>`. When
   the reason names the Conductor or the owner, the door would print wording 2 and accept the wait only if the reason
   names one of his five acts, a looser bar, a hold to lift, or a date outside the run. This is the one home that is
   new code. The evidence for it: 5 of the 10 sampled waits contradict the rule, and no door checks a wait now.

Not a home: `GUIDING_PRINCIPLES.md` says what is always true of the game, not of the process. `standing_rulings.md`
already holds the full rule; only its list (line 712) and the two rows of part 1 change there.

## Part 5. Risks of the principle

| risk | already guarded? |
|---|---|
| A blind judge fixes the work, becomes its maker, and nobody judges the fix. | Yes. The test-2 exception "your verdict must stay independent"; `rm-judge.md:22` for taste calls; for a mod fault fixed in a sitting, one fresh reader reads only the fix (`standing_rulings.md:761-765`); a resume never crosses a blind boundary (`standing_rulings.md:775-779`). Every wording keeps the blind exception. |
| Two runs fix the same file. | In part. The `files-held` class is checked against the live runs (`filing_gate.py:88-93`), and each writer works in its own clone and lands with `./publish`. Not guarded: two runs that both choose to fix (neither files) meet only at landing. No new guard is proposed until one such collision is measured. |
| An agent widens its task without limit. | In part. Test 1 comes before test 2, and "if you see it, do it" never licenses a touch that fails test 1 (`standing_rulings.md:715`); a judging brief states its stop level; a bundle adds no ticket of another system (`bundle_worker.md:25`); `other-mod` keeps another mod's work in its own run; the per-run spend stop (`spend_watchdog`) ends a runaway run. The cheap-worker clause "the change reaches files outside the ones named" (`Agent_Policy.md:245`) is the one direct guard, which is why part 1 leaves it UNCLEAR, not CONTRADICTS. |
| A fixer changes the check, not the mod, to pass. | Yes. A repaired check counts only when seen FAIL on a planted fault and PASS on the real build (`standing_rulings.md:747-756`); never edit an old check to pass (`rm-builder.md:34`, `rm-fixer.md:25`). |
| "Do it now" sends a run to a game that he is looking at. | Yes. His OWNER hold, `./pipe off game:<name>` and the 45-minute clock bind every take (`CLAUDE.md` §The bridge is passed through one file). |
| A run that fixes a held mod's file runs the mod forward. | Yes. A held mod takes design text only (`CLAUDE.md` §Six biome mods are held). Builds, tests and live runs stay held. |
| The principle makes the rule files longer. | Guarded by the homes of part 4: each replaces sentences, and the CHARTER gains no rule. The risk returns if the statement is added beside the old list instead of in its place. |
| Quoting the owner as absolute truth. | His instruction on the item: quote him only when useful. The three wordings carry no quote. |
