# Player role: merged design

Merge step of a Deep-Design-3x2 run, 2026-10-31. Item `PLAYER_ROLE_DESIGN_EMPTY_CHAIR_AT_TABLE`. Complete run: pass 1 (`01-design.md`), GPT blind (`02a-gpt-blind.md`), GPT critique (`02-gpt.md`), re-measure (`02m-remeasure.md`). The optional second Opus pass was not run; the decision is cheap to reverse.

Mandrake asked: "Is this even feasible? How would an agent decide if something was confusing, dull, unreadable, or broken as felt? ... three competing deep designs".

Provenance tags: **[P1]** pass 1, **[GB]** GPT blind, **[GC]** GPT critique, **[RM]** re-measure, **[M]** this merge.

---

## 1. The answers, plainly

### Is this even feasible?

**Partly, and the honest split is by word.** An agent can find things a player will run into. Nobody has shown one can tell how a player will feel about them. So this can be built as a **scout that brings evidence**, and it cannot be built, today, as **a judge of fun**. No study either pass found tests an agent against real players' feelings in a long colony sim. That is "not shown", and neither pass searched everything.

| Word | Feasible? | Plain reason | Odds it earns its keep (estimate, author's judgement) |
|---|---|---|---|
| Broken as felt | Yes, now | There is something to check against: what the game did versus what the screen said. State alone is not enough; a person still decides what a player would reasonably expect. | 0.8 |
| Unreadable | Partly | Size, contrast, cut-off text and missing text can be measured on the rendered screen. Whether a picture reads as its subject needs judgement. | 0.6 |
| Confusing | Unproven | The agent can record what it expected and be shown wrong. The open question is whether its stumbles are the same ones a person has. | 0.4 |
| Dull | Not as a verdict | Tests of models judging engagement from film are weak on average, and those tests were on fast shooters, not colony sims. It can list the stretches worth looking at. Only people can rank them. | verdict below 0.1; ranked suspect list 0.3 |

What changed in review: pass 1 said dull was structurally out of reach because an agent never gets bored. That was too strong. A system need not feel boredom to predict someone else's [GC]. What remains is an evidence gap, and it is wide.

### How would an agent decide?

It would not ask itself how it feels. All three passes converged on one move: **turn the feeling into a checkable event.**

- **Broken as felt:** the screen led it to expect X, the game did Y, and the screen did not say so. It must first prove its click really landed.
- **Unreadable:** it reads a value off the screen and that reading is compared with the truth, and rendered text is measured at his real scale. A misreading may be the model's own eyesight, so a person or a measurement confirms it.
- **Confusing:** before acting it writes "I expect X because the screen says Y". Afterwards a separate grader compares. Then it asks: was the guess reasonable, could it recover, did it recur? Being surprised once and learning is often just playing the game [GC, GB].
- **Dull:** it never decides. It reports stretches of repeated chores, waiting, or no change to any plan, and a person ranks them. It must not count quiet as dull or busy as interesting. A hundred forced clicks with no real choice can be dull [GC], and a quiet stretch before a dangerous trip can be absorbing.

### One moment, three reports

The moment is real RimWorld: a cook bill sits active on a stove, the raw food is outside the bill's ingredient radius, and nobody cooks. All three reports are **invented to show the format**. Nothing here was observed, and whether the game explains itself here is what a run would check.

**Stranger (plays it, knows nothing):**

> Confusing, 2 of 3 fresh runs. Goal: get these people fed. I expected the cook to start within the hour because the bill reads active. A game day passed. The input was confirmed delivered, and the grader confirms no cooking job started. I opened the bill and hovered it; nothing I found gave a reason. I abandoned the goal. Strong evidence of this agent's impasse; human confusion unconfirmed.

**Flight Recorder (no opinion, only numbers):**

> Stalled order. Stove bill active for 1.3 game days, 0 job starts, 0 rejection messages displayed. Same pattern on vanilla stove bills: 1 in 40 sessions. Not a judgement: a place to look.

**Taste Twin (knows the design and his past rulings):**

> Communication gap. The design wants food to be a problem the player can solve. Frames 40 to 55 show the problem and no visible cause. This resembles his ruling on machines that look connected and are not. Owner preference: likely cares. Stranger evidence: none. Facts checked against game state: radius and stock location confirmed.

The fourth design, the Checkpoint Auditor, would start at a saved moment just before this bill, and give the same report as the Stranger with the bill's input trace and, later, a retest.

### How we would test it against his judgment

He does not have to trust any of this. Five checks, none of which needs him to play:

1. **His own past complaints.** Replay a handful of things he really noticed, at old builds where they can be reconstructed. Does it find them unprompted?
2. **Blind sort, about an hour.** 20 to 30 reports shuffled, some from a plain cheap baseline he cannot tell apart, including low-ranked ones. For each: true? new to you? do you care? would a stranger hit it? "I already knew" is a hit, not a false alarm.
3. **Planted faults.** A separate agent plants defects in a throwaway copy. Report per-run and total catch rates. This proves it can notice, not that the faults matter.
4. **Which was duller?** Ten pairs of stretches. Exploratory only: 7 of 10 happens by luck 17% of the time, so it can raise interest and cannot pass anything.
5. **Worth his time.** Minutes of his attention per finding he keeps. If that loses to a plain screenshot review, the role is not worth building.

One limit remains. He knows the design and cannot be a stranger. All of this measures agreement with him, which is what he asked for, and not agreement with players. A finding he rejects may still be real for a newcomer. Only a real newcomer settles that.

---

## 2. Final options

Strongest version of each after review. Pass 1's null stays on the table as the benchmark: **a human, watched**. It is the only direct evidence of felt boredom, but it is not free and not infallible: pass 1's "no false positives" was wrong, and two hours may never reach late-game chores [GC]. Improved shape [GC]: an experienced player new to the mods and a true newcomer, one free session and some later checkpoints, questions tied to timestamps, someone other than the designer sorting first.

### A. The Stranger: an agent that plays cold

- A fresh agent plays a copy of the shipped save through only what a player has. Enforced by a proxy, not a prompt [P1, GB].
- Writes its expectation before each consequential act; a separate grader that can see state compares [P1, GB].
- Player-equivalent actions, and tooltips only by hovering [GB]. Hover exists: `rimworld/set_hover_target` [RM].
- Input delivery is checked before the interface is graded, and every event is sorted into: not reached, could not operate, misread, misunderstood, game broke the promise [GC].
- A pixel click must not be silently snapped to a nearby target; a miss stays a miss [GC].
- Repetition is a recorded strength, not a filter: a one-run finding survives, because a rare destructive one may be the most important [GC, replaces P1's 2-of-3 gate].
- Vanilla calibrates the agent's general competence and vetoes nothing [GC, replaces P1's subtraction].
- A few behavioural goals (seek stability, build freely, optimise) for coverage, never as a stand-in for audience [GB].
- "Stranger to RimMandrake, not to RimWorld": models know the base game [P1, GB].
- **Dominates when:** first contact matters most, and the fidelity test shows its stumbles match people's.
- **Cost:** 5 to 8 agent-days; about 9M input tokens per 300-step pass before judges; 1.7 to 3.3 hours per pass plus a 23 to 30 minute cold load (estimates; load measured).
- **Main risks:** agent incompetence read as bad design; shared blind spots across runs; retesting the first hour forever.

### B. The Flight Recorder: measure, do not opine

- Static sweep of text and art against vanilla's distribution [P1], moved to rendered checks: real clipping, font size, visibility at target UI settings [GC]. Static texture contrast is not on-screen readability [GC].
- A small event chain per interaction: intent, accepted or rejected, queued, completed or cancelled, visible feedback, with deadlines by interaction family [GC]. Replaces "no state change means broken" [P1], which is wrong for queues and mode toggles [GC].
- Records during anyone's play, human or agent [P1].
- Dull ships as "quietest stretches" [P1], plus repeated forced actions and stalled goals [GC].
- Controlled scenarios before any autonomous governor [GC]. A running colony supplies no player goals, so the governor is deferred [P1, GC].
- A colony death is a result to diagnose, not a void run [GC].
- **Dominates when:** tokens and bridge time are tight, regressions between builds matter, or he or someone else will play.
- **Cost:** sweep 1 day, recorder 2 to 3 days, governor 3 to 5 days if ever; near zero tokens (estimates).
- **Main risks:** tuning for the proxy makes a nagging game; confusing is dark with no human at the mouse; never speaks in experience terms.

### C. The Taste Twin, renamed Intent Reviewer

- Offline critic that knows the design and his rulings, built on the art judge's shape [P1].
- Three separate fields: what he prefers, what the screen fails to communicate, what outside players say. They need different evidence and must not blur [GC].
- Holds out whole mechanics, sessions and later dates, not random rulings, or the test leaks [GC].
- Must beat simple baselines: nearest past ruling, plain checklist, uncalibrated critique [GC].
- May say "the film does not show this" [GC]. Disagreement sends a thing to him rather than quietly dropping it [GC]. **It may never drop a finding on taste** [M, from GC].
- Corpus is thinner than pass 1 thought: likely under 20 real labels [RM].
- **Dominates when:** bridge time is unavailable, and the pain is design intent not reaching the screen.
- **Cost:** 3 to 4 days mining, 1 day film; 2M to 5M tokens per batch (estimates). The real cost is his labelling time.
- **Main risks:** an echo, which is the opposite of an empty chair; cannot be surprised; only sees film someone else shot.

### D. The Checkpoint Auditor: short, repeatable episodes (GPT's pick)

- Starts from saved checkpoints with a stated player goal and a fixed budget, ends in success or abandonment. Reaches midgame without paying for the opening hour [GC].
- Each step gets a player view, a prediction, independent proof of execution, and an evidence packet [GC].
- A human can check the same screenshot prediction, which directly tests the Stranger's core signal cheaply [GC].
- Labels stay apart: agent-only, human reproduced, mechanism confirmed, owner preference [GC].
- Narrow repair: change only the label or the rejection text, then retest [GC]. **Amended [M]:** later, and only for findings he keeps, because a repair needs a mod change, a deploy and a load.
- `rimworld/load_game` exists, so one cold load can serve many checkpoints [M, from the tool dump]. How long a reload takes on the full list is unmeasured.
- Add one roaming pass, because checkpoints only test where someone thought to put one [M].
- Dull: he or a tester answers "continue, speed through, change goals, or stop?" at moments in real sessions; agents only find and summarise candidates [GC].
- **Dominates when:** bridge windows are short, midgame matters, and findings must be repeatable.
- **Cost:** 6 to 9 agent-days. Kill test: 6 checkpoints, 3 fresh runs each, 40 steps, about 14M input tokens and 4 to 8 bridge hours, plus one roaming pass of about 9M and 2 to 3 hours (estimates by this merge, unmeasured; judges and vanilla runs are extra, and "mostly cached" must be measured [GC]).
- **Main risks:** a staged checkpoint is not a save reached in play; authors choose where to look, so it loses unknown unknowns; building the library needs staging work.

### Compared

| | Human | A Stranger | B Recorder | C Reviewer | D Checkpoints |
|---|---|---|---|---|---|
| Broken as felt | Good | Good, with proof of input | Best at candidates | Partial | Best overall |
| Unreadable | Good | Reading test | Rendered checks | Taste side | Rendered + reading |
| Confusing | Best | Only free-roaming candidate | Dark | Display gap only | Bounded, testable |
| Dull | Direct evidence | Suspects | Best proxy | Tests it cheaply | Finds candidates |
| Surprises | High | High | Low | Low | Medium |
| Build, agent-days (est.) | 0 | 5 to 8 | 3 to 9 | 4 to 5 | 6 to 9 |
| Holds the bridge | No | Hours | Only with play | No | Short windows |
| Main false alarm | Opinion as defect | Agent incompetence | Proxy as truth | Confident story | Staged context |

---

## 3. Claims after re-measure

Trust rule: parsed data over docs; a re-opened paper over a report of it.

| # | Claim | Pass 1 | After | Trust |
|---|---|---|---|---|
| 1* | No source validates an agent against felt experience in a long sim | measured, limited | **Holds as "not demonstrated".** Not a universal absence. Nearest human-compared work is difficulty (Xiao and Yang, abstract re-opened: strong correlation) and GUI rubric agreement on expected behaviours (Huang et al.; GPT's figures not re-opened). Neither is felt experience. | Moderate |
| 2* | Engagement judgement near chance on pairs | measured by others | **Scoped.** See citations. FPS clips, viewer annotations. | High, re-opened |
| 3* | Bridge has no hover or tooltip read | unmeasured | **FALSE.** Dump lists `rimworld/set_hover_target` and `jawa/inspect_string`. Whether a tooltip is drawn legibly is untested live. Filed `PLAYER_HOVER_PROBE_TOOLTIP_DRAWN`. | High on tools |
| 4* | Vanilla plus 2-of-3 separates agent from game | assumed | **Withdrawn as stated.** Correlated runs keep shared errors: 3p²−2p³ only if independent, p if perfectly correlated [GC]. Now calibration only. | Logic |
| 5* | Paused LLM plays the save usefully for 90 min | unmeasured | Tools exist; usefulness unmeasured. The kill test measures it. | Open |
| 6* | One human beats all designs on dull | assumed | **Narrowed:** direct evidence of that person's boredom; yield never compared. | Logic |
| 7* | Seeds represent real defects | assumed | Unsupported. Proves noticing only. | Logic |
| 8* | Comparable vanilla control is possible | unmeasured | No vanilla fixture among 180 saves. Route to test [M]: a vanilla colony on the 22-second list via a dev quicktest, throwaway and test-only, which the player-facing worldgen ruling does not address; comparability still unproven. | Open |
| 9* | He gives an hour | assumed | His call. | Open |
| 10 | Shipped save is the 10-20 file | measured | Confirmed, 13,564,631 bytes. | High |
| 11 | Cold load 15 to 25 min | sources disagree | **23 to 30 min.** | High |
| 12 | Bridge about 141 tools | measured by others | **246**, JSON parsed again here, dump dated 10-02. Skill says 125. Filed `BRIDGE_SKILL_FIX_TOOL_COUNT_STALE`. | High, ages |
| 13 | Corpus a few dozen labels | rough | **Likely under 20.** | Moderate |
| 14 | Art ledger 49 rows | measured | Unchanged. | High |
| 15 | Pass costs 10M tokens, 2 to 3.5 h | estimated | **9M; 1.7 to 3.3 h** before load, judges, resets, controls. | Estimate |
| 16 | 1080p frame is 2.7k tokens | from docs | 2,691 on the high-resolution tier; 1,560 after downscaling on standard [GC, not re-opened]. Name the tier. | Conditional |
| 17 | Build costs | estimated | Still estimates. | Low |
| 18 | LLMs know vanilla RimWorld | assumed | Both passes agree; untested. | Assumed |
| 19 | Odds | estimated | Still judgement. | Low |
| 20 | Schedule revert file exists at that path | unmeasured | **Exists:** `src/RimMandrake/rimflow/dispatcher_schedule.json`. Pass 1 looked in the wrong folder and its finding is withdrawn. | High |
| 21 | Screenshot matches what he sees | unmeasured | No resolution or scale parameter on the tool. Unknown. | Open |
| 22 | Agent severity scores unreliable | measured by others | **Support removed.** See citations. | High, re-opened |

Estimates checked here: 8/12 Wilson 0.391 to 0.862; 12/20 0.387 to 0.781; P(at least 7 of 10 by luck) 0.172.

### Citations corrected or removed

Status **re-opened** means this merge fetched the source by curl and read the passage. **GPT only** means reported, not re-read, so it may shape a question and decides nothing.

| Source | Pass 1 said | Corrected | Status |
|---|---|---|---|
| Wang et al. 2603.18480 | "On paired clips ... zero-shot about 57% under 67.2%" | 57% versus 67.2% is **pointwise** (per-window), Table 4. Pairwise majority baseline averages **56.5%**, strategy averages 47.7 to 58.8%, Table 5. Pairwise remains hard. Theory prompting is "mixed but often positive", and alone "does not reliably help". | Re-opened, corrected |
| Melhart et al. 2502.04379 | "only about 6% above baseline", "every direct test negative" | +6% on the paper's relative measure, with strong results on some games (+59% best). Target is **viewer engagement annotation**, not the player's own feeling. "Every test negative" withdrawn. | Re-opened, corrected |
| Platt et al. 2512.04262 | Severity alpha near zero; "do not ask for severity"; listed as human-validated | Tests repeatability on website source code, not correctness: "consistency shown does not imply correctness". Abstract ties alpha to severity, Table III puts −0.000234 in the multi-rater issue analysis near κ 0.5, and severity weighted κ is 0.63. Paper is inconsistent. **Removed as support**, and from the human-validated column. | Re-opened, removed |
| Guerino et al. 2506.16345 | 24.3% false positives | 27 of 111 raw reports. 27 of 68 de-duplicated is 39.7%; the paper's sentence names the 68 but its 24.3% is computed on the 111. Web screenshots only. | Re-opened, corrected |
| Zheng et al. 2311.10054 | Persona prompting has little effect | 2,410 **factual questions**. Says nothing on novice simulation. **Removed** as persona-fidelity evidence. | Re-opened, removed |
| Taesiri et al. 2210.02506 | Listed under pixel glitch detection | Works on **text descriptions** of events. **Removed** from pixel evidence. | Re-opened, removed |
| FLE 2503.09617 | "56% of steps had execution errors" read as agent failure | Program-execution errors in successful lab-play runs, which agents recovered from. Not interface error. | Re-opened, corrected |
| Zhou et al. 2606.24551 | GUI failure 30 to 50% read as noise for "confusing" | 59.1% is whole-task pass on desktop apps. **Noise-rate use removed.** | Re-opened, corrected |
| Roohi et al. 2107.12061 | ρ 0.80 prediction | ρ is the correlation of one AI pass-rate feature with human pass rate over 1,000 runs per level, not a held-out model score. | GPT only |
| Hu and Collier 2402.10811 | Persona has little effect | Under 10% of variance but modest significant gains. | GPT only |
| GlitchBench 2312.05291 | 43.4% to 64.9% as a range | Two prompt conditions, not a range. | GPT only |
| MeepleLM 2601.07251 | "Real corpus is the active ingredient" | Causal reading unsupported. Softened. | GPT only |
| Ryan et al. 2006 | "vocabulary only" | Four human studies. Empirical in humans; still no detector. | GPT only |
| Pass 1 "no game-specific frustration paper" | Absence claim | Retracted on GPT's leads: Wolterink and Bakkes (Pac-Man, 135 participants), Ali and Thue (Terraria struggle). Not opened here. | GPT only |
| Pinelle 2008, Hertzum 2001, Desurvire 2004, GameFlow | Metadata only | Bibliography real, bodies unread. Nothing may rest on them; the "evaluator effect" reasoning for 2-of-3 is dropped. | GPT only |
| arXiv "0 hits" for RimWorld | Search claim | No query log. **Removed.** | Removed |

The GPT audit found no nonexistent paper. Its new sources are leads. Re-opened and confirmed as real and on topic: Xiao and Yang 2410.02829, Huang et al. 2605.28258, Volden et al. 2507.03391, at abstract level only. Numbers from them are not re-read and are not used to decide anything.

---

## 4. Findings

| Finding | From | Status |
|---|---|---|
| Hover exists | RM | Confirmed, dump parsed twice |
| Tool count 246 | RM | Confirmed; docs filed |
| Revert schedule file exists | RM | Confirmed; pass 1's finding withdrawn |
| `CANONICAL_SAVE.md` still names the 09-12 file | P1 | Confirmed by reading both; filed `CANONICAL_SAVE_FIX_STALE_START_POINTER`. Pass 1 said it had been filed; it had not been. |
| Pass 1's "tooltip gap" finding | P1 | Refuted as stated; narrowed to a live probe, filed |
| Prior citation errors above | GC | Confirmed for the eight re-opened |
| 2-of-3 keeps shared errors, loses rare ones | GC | Confirmed by logic |
| Vanilla is no clean subtraction | GC | Confirmed by logic |
| "No state change" is not "broken" | GC | Confirmed by logic |
| Proxy click-snapping can repair bad pointing | GC | Confirmed by logic |
| 7 of 10 pairs is not a gate | GC | Confirmed, p = 0.172 |
| "Already knew" is not a false positive | GC | Confirmed by logic; exam changed |
| Capture-recapture assumptions fail, undefined at zero overlap | GC | Confirmed by logic; dropped from exam |
| Findings per hour rewards volume | GC | Confirmed by logic; replaced |
| Three-fix keep bar rewards cosmetic fixes | GC | Plausible; kept the item's bar and added his-time cost alongside |
| Random hold-out leaks | GC | Confirmed by logic |
| Static contrast is not rendered readability | GC | Confirmed by logic |
| Second judges add little | GC, Lu 2603.22706 | Unverified here; used only as caution |
| Screenshot-only misses fleeting feedback, stutter, audio | GB | Confirmed by logic; "not evaluated" must appear on reports |
| Convincing testimony is not valid testimony (Hämäläinen, CHI 2023) | GB | Unverified here; matches pass 1's report-language rule |
| Confusion can sit alongside engagement (Volden) | GB | Abstract re-opened: confirmed; shapes "recovery, not surprise" |
| Boredom includes overload as well as understimulation (Westgate and Wilson) | GB | Unverified here; shapes the dull list |

---

## 5. The exam, revised

Pass 1's exam, with replacements [GC] and his-time measure [M]. Bars are his to change.

| Check | Report | Bar |
|---|---|---|
| Planted faults, frozen before tuning, with exposure noted | Per-run, total, per-fault recurrence | Run-level catch rate at least half of faults actually reached; coarse |
| His past complaints | Found or not, unprompted | At least half |
| Scenes with nothing planted, read by hand, because unplanted is not clean | Confirmed versus false | Falsehood rate reported; no fixed bar on the first run |
| Blind sort, sampling below the top ranks, baseline mixed in | True, new, cares, stranger would hit it | Beats baseline on true-and-cares, at least 12 of 20 true. Coarse: 0.39 to 0.78 |
| Which was duller, 10 pairs | Agreement, ties allowed | None. Exploratory. |
| Repeat runs | Recurrence per finding | Reported |
| Cost | Minutes of his time per kept finding | Beats plain screenshot review |
| Human screenshot prediction, if a person is available | Do people mispredict the same controls? | The direct test of agent-versus-human friction |

Dropped: capture-recapture estimate, findings-per-hour versus vanilla, fitted dull weights on ten pairs.

---

## 6. Compositions and orders

1. **Recorder, then Checkpoints, then Reviewer as clerk** (recommended). Useful output even if agents fail; fidelity tested before spending on roaming. Gives up some surprise, restored by one roaming pass.
2. **Recorder, then Stranger, then Reviewer as filter** (pass 1's order). Maximum surprise, but the Stranger is the costliest test of the least certain claim, and the filter risks removing the novelty.
3. **Human first, then Recorder, then whichever agent the human's sessions justify.** The strongest validity, and the only order that yields real labels for dull. Depends on finding a person.
4. **Reviewer and static sweep only, no live player.** Cheapest, and right if no bridge time exists. Does not fill the empty chair.
5. **Weekly in-session pass with him, recorder on.** The item's smaller step. Tests with no build, and needs him present, which he currently is not.

The recorder comes first in every order that builds it because it pays whether or not agent judgement works [P1, GC agree].

---

## 7. Where the passes disagreed

- **What to build.** Pass 1: staged Recorder to Stranger with Reviewer as last filter. GPT blind: a situated LLM player, calibrated against human sessions. GPT critique: **a fourth design**, the Checkpoint Auditor, deferring both governor and Twin. GPT moved its own pick after seeing the design. This merge sides with GPT on shape, and keeps a roaming pass and pass 1's cheap kill test. It is still a disagreement: pass 1 valued surprise more.
- **Must it have real players?** GPT blind makes held-out human sessions the centre of validation. Pass 1 treats a human as a parallel ask, since he does not play now. Not resolved here: it is his decision, and without it validity stays agreement with him.
- **Is dull impossible?** Pass 1: structurally. GPT: an evidence gap only. Merge sides with GPT on logic and with pass 1 on what to ship.
- **Does the state oracle settle "broken"?** Pass 1: yes, nearly. GPT: only what happened, not what was expected. Merge sides with GPT.
- **Personas.** Pass 1 rejects them; GPT blind uses behavioural ones for coverage. Compatible: coverage yes, validity no.
- **Reviewer as filter.** Pass 1 wants a final taste filter; GPT says it suppresses the very findings wanted. Merge: fact-checking and duplicate removal may drop; taste may only sort. "Nothing reaches him unread" is met by a factual read.
- **Severity.** Pass 1: never ask. GPT: the citation does not support that, and blind GPT would track severity agreement. Merge: leave it off reports until tested, on the plain ground that it is unvalidated.
- **Was the source reading real?** GPT called the evidence notice unreliable and the re-measure retracted the "opened" provenance as written without web. This merge disagrees in part: curl reached arXiv and every page re-tried returned, and the disputed passages exist where pass 1 drew from them, misread in places. Pass 1's reading history itself remains unprovable.
- **Is the art judge a proven base?** Pass 1 called it proven. GPT could not verify that from the text. Nothing here tests transfer from judging art to judging experience.

---

## 8. Recommendation

**Build the scout, not the judge: Composition 1.**

1. **This week, no build:** the live tooltip probe (15 minutes once the bridge is free) and one pass by hand at the rendered-text sweep. If hover cannot be read, a screen-only agent is half blind and the design shrinks to Recorder plus human.
2. **Then the recorder's cheap half:** rendered checks and the event chain. Pays whichever way the rest goes.
3. **Then one kill test:** six checkpoints, three fresh runs each, one roaming pass, planted faults, then his blind sort beside a plain screenshot baseline. Stop if it does not beat the baseline for his time. Trial stays behind the watchdog item, still `doing`.
4. **Reviewer as clerk only:** duplicates, formatting, retrieval. No Taste Twin build until simpler means show a need.
5. **Dull ships as "quietest stretches and repeated chores", ranked by a person.** Never the word alone.
6. **Ask for one real outsider in parallel.** Two hours teaches more about dull, and grades everything else.

What would change it: hover unusable; reload too slow for checkpoints; the plain baseline ties; he returns to daily play (Recorder plus Reviewer then wins); a real newcomer's stumbles match the agent's closely (bring the Stranger forward).

Findings are leads. Reports must never say "players will feel".

---

## 9. Decisions for Mandrake

1. **Which build:** Composition 1 (recommended), pass 1's Stranger-first order, human-first, or no live player?
2. **Honest scope:** dull is a ranked suspect list, never a verdict. Agreed?
3. **The four definitions:** do those in §1 say what he means? The dull one in particular.
4. **A real person:** is one outside playtester allowed, given the private mod list? Or his own 30 minutes a week with the recorder on?
5. **His exam hour:** about an hour blind-sorting plus ten pairs. Without it nothing is validated.
6. **The spend:** about 25M input tokens plus judges and 6 to 11 bridge hours for the kill test (estimates), on which machine, and how shared with Test Pilot?
7. **Player model:** Opus throughout, or Sonnet playing with Opus judging, cheaper and unproven?
8. **Outside reviews:** drop Steam and Workshop mining unless he picks the Reviewer path (recommended: drop).

## Rulings

(none yet)
