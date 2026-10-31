# Player role: can an agent tell us the game is confusing, dull, unreadable or broken as felt?

Pass 1 of a Deep-Design-3x2 run, 2026-10-31. Item: `PLAYER_ROLE_DESIGN_EMPTY_CHAIR_AT_TABLE`.

Mandrake's order: "Do the design work for this agent role now. Is this even feasible? How would an agent decide if
something was confusing, dull, unreadable, or broken as felt? I am fascinated and would very much like to see three
competing deep designs here. Feel free to reach out to literature to expand the option space on how others are
achieving this kind of player-role. This could really, really help if we can achieve it... but it's a lofty goal."

**Evidence notice.** WebSearch and WebFetch were not available in this session (ToolSearch found neither). Every source
marked `opened` in §10 was fetched by curl from arXiv, a DOI host or the publisher, and read as text. Sources marked
`metadata` were confirmed to exist but their body was not read; nothing numeric is taken from them. No live game was
touched: FOUNDRY held the bridge. All bridge capabilities below come from the skills, not from a live census.

---

## 0. Feasibility, first

**Yes as an instrument, no as a judge.** An agent can find things a player will meet. It cannot be trusted to say how
they feel. The four words are not one problem, and they do not have one answer.

| Word | Answer today | Why | My odds it earns its keep (estimated) |
|---|---|---|---|
| **broken as felt** | Feasible now | The word has an external oracle: the game state says what happened, the screen says what the player was told, and a gap between them is checkable. TITAN found new bugs in MMORPGs this way; pure pixel judging sits near precision 0.50, so state must confirm. | 0.8 |
| **unreadable** | Feasible in part | Much of it is measurable without opinion (contrast, size at true zoom, truncation, missing description). LLMs do best on exactly this heuristic family, but matched only 21.2% of human issues, so it adds to human review and replaces nothing. | 0.6 |
| **confusing** | Plausible, unproven | Measurable as behaviour: a fresh agent predicts what a control does, then is wrong, or cannot reach a goal the screen seems to offer. The danger is that agent friction is not human friction. LLM novices have been measured as over-coherent, and overestimated the novice's performance. | 0.4 |
| **dull** | **Not judgeable. Say so.** | Every direct test I opened is negative or unvalidated. See below. An agent can report dull-risk proxies; he ranks them. | as verdict < 0.1; as a ranked suspect list 0.3 |

**Why dull fails, not merely lags.** Three independent reasons:

1. *Measured.* Across 80 minutes of 20 FPS games and over 4,800 experiments, LLMs "generally fall behind" human
   engagement annotation, with few-shot multimodal only about 6% above the majority baseline on average, "far from
   consistent" (Melhart et al. 2502.04379). On paired clips, which is closest to what we would ask, vision models were
   near chance under every prompting strategy; zero-shot about 57% sat under a 67.2% majority baseline. Feeding them
   Flow, GameFlow, SDT and MDA did not reliably help and reinforced surface shortcuts (Wang et al. 2603.18480). Those
   models mistook visual intensity for engagement, and gave confident, misleading reasons. **A paused colony is the
   low-intensity case.** RimWorld's best hours can look like a still frame.
2. *Structural.* Dullness is a cost of time. An agent paused between calls has no clock, no fatigue, no other game it
   could be playing, no opportunity cost. The thing being judged does not exist for it. It can read that a span held no
   decisions; it cannot have waited through it. RimWorld's fun is long-horizon and emergent, and no study I found tests
   an LLM against players on a long-horizon simulation at all.
3. *Sycophancy and range.* Synthetic users give "shallow or overly favorable feedback" (NN/g), and simulated samples
   reproduce averages while collapsing variation (Bisbee et al. 2024; Li et al. 2507.02919). Whether it is dull depends
   on who is playing, and the variance is the signal.

**What did work against real players, and why it does not transfer.** The strongest result I found: AI playtest bots
predicted human pass rates on 168 Angry Birds Dream Blast levels at Spearman 0.80, and churn from that (Roohi et al.
2107.12061). That needed a live game's population telemetry as ground truth, and it predicts an aggregate difficulty,
not an experience. We have one player, who says he is not playing right now, and no telemetry. The other positive line
is board-game critics trained on 150,000-plus real reviews (MeepleLM 2601.07251, CoBG 2606.01976): the validity came
from a large real corpus. Lesson: **where validity was earned, it was earned against real players at scale; none of
those conditions holds here.** I found no published validation of an LLM agent against real players' felt experience
in a long-horizon simulation. Not finding it is not proof of absence: my search was arXiv and DOI lookups only.

**So "lofty" is the right word, and the role is still worth building** in a narrower form than the name promises. The
gap that hurts today is real: every current role checks whether things work, and a filter that reliably returns
"a player opens this and nothing tells them why it failed" has value with no claim about fun. The honest product is a
stranger's first-contact report, plus a suspect list for dull that a human ranks.

**Cheaper alternative that must stay on the table.** One human stranger for two hours beats all three designs on dull,
on the evidence above. See D0 in §3.

---

## 1. Problem, constraints, success

### 1.1 Problem

Find what a player meets in the shipped save that no mechanism test catches. The output is experience findings, each
with a moment and evidence, not item verdicts. The four words, made operational (agents need definitions; these are
mine and are decision D1):

- **Broken as felt:** the player did the normal thing and the visible outcome disagrees with what they were led to
  expect, whether or not the mechanism is correct. A working mechanism with no feedback counts. A broken mechanism the
  player never sees does not.
- **Unreadable:** at real resolution and zoom, the information exists but cannot be taken in: illegible, indistinct,
  truncated, buried, or a wall of text where a decision is due.
- **Confusing:** the player cannot form a correct model of what something does, or what to do next, from what the
  game shows them.
- **Dull:** time passes with no meaningful decision pending and nothing to anticipate. Used only as a risk label.

### 1.2 Constraints (from CLAUDE.md, the brief, skills)

- One bridge holder per machine, through `rimflow bridge`. The game is never fullscreened or focused, so **OS-level
  computer use is out**: clicks go through the bridge UI event system (`click_ui_target`) and `click_cell`.
- The shipped save needs the **full list**, about 15 min (TestPilot brief) to 25 min (load-round skill) per cold load.
  The 22 s minimal list cannot host it. This is what makes every live pass expensive.
- Never test flyer flight without him. A wandering agent will find the launch gizmo, so **the proxy must deny it.**
- No worldgen of any kind, so the player may not start a new colony; every DLC is assumed; our biome on 0 tiles is
  expected, not a finding.
- Canonical saves are never overwritten: play a copy, save under a disposable name, hash the original before and after.
- Nothing reaches him unread; FlowWorks and GSS findings go `--for FOUNDRY`.
- **Which save is shipped:** `infrastructure/state/canon.yml` repointed `start_savegame` on 2026-10-25 to
  `ASHKARR_DEV_START_2026-10-20_PARITY_QUIET_R3.rws` (on disk, 13.6 MB). `CANONICAL_SAVE.md` still names the 09-12 file
  and says it is `start_savegame`. That doc is stale; filed, see §9.
- He does not play right now, so designs that need his play have no input until he does.
- The item's trial is blocked until `INNOVATOR_BUILD_EXPIRY_WATCHDOG_REVERTS` closes (state: `doing`).

### 1.3 Success, and how it is measured

The item's keep bar stands: **at least 3 items filed by the role close done with a product commit within 14 days**, against
a baseline of 0, guard `process.share_7d` stop above 85. That proves usefulness, not validity, so an exam comes first.

**The Exam (shared by every design, built once):**

| Instrument | What it answers | Bar (his to change) |
|---|---|---|
| **Seeded deck:** a separate agent plants 12 defects in a disposable copy, 3 each of broken, unreadable, confusing, and 3 cross-word; the player is not told | Recall | at least 8 of 12 found across 3 fresh runs. Beware: 8/12 has a Wilson 95% interval of about 0.39 to 0.86. This is a coarse gate, not a measurement. |
| **Historic deck:** 6 to 10 of his real past complaints, replayed at old commits where the build still exists | Does it catch what he actually noticed | at least half |
| **Null arm:** 6 fake-defect slots (nothing seeded), and a **vanilla control**: same pass on a vanilla plus DLC colony | False alarm rate, and whether it discriminates at all | Ours must file clearly more than vanilla per hour. Equal rates mean it is measuring the agent, not the game. |
| **His labels:** 20 to 30 findings shuffled with the null-arm findings, blind to source: keep, false, already knew | Precision against his judgment | at least 12 of 20 top findings kept. Literature anchor: pixel QA precision 0.50 (Lu 2603.22706), GPT-4o heuristic false positives 24.3% (Guerino 2506.16345). |
| **Pairwise dull ranks:** 10 pairs of segments, "which was duller?" | Whether any proxy tracks him | Ranks over ratings (Yannakakis and Martínez 2015). Below 70% on held-out pairs (one rater, small n; a rough bar), dull stays a raw list. |
| **Repeatability:** 3 fresh runs, same segment | Reliability | Severity is excluded: GPT-4o severity gave Krippendorff alpha near zero across repeat runs while detection κ was 0.50 (Platt 2512.04262). **Do not ask the agent for severity.** |
| **Capture-recapture:** agent findings vs his next walk, N̂ = n1 n2 / m | How much is still unfound | Reported, no bar |

Calling his ruling "ground truth" is itself a soft spot: he is one player, who knows the design, and cannot be surprised
the way a stranger can. A finding he rejects may still be right for a stranger. The exam measures agreement with
Mandrake, which is what he asked for, and not agreement with players, which we cannot measure.

---

## 2. What exists

### 2.1 In this repo

- **Bridge (skills/rimbridge):** about 141 tools. Usable as player eyes and hands: `get_ui_state`, `get_ui_layout`
  (every button with a targetId), `click_ui_target`, `click_cell`, `list_selected_gizmos`, `execute_gizmo`,
  `open_inspect_tab`, `take_screenshot`, `jawa/clear_ui`, camera tools, `step_game_ticks`, `save_game`.
- **The instrument is lossy as a player.** `click_cell` can select nothing; `get_context_menu_options` cannot see
  `Verse.FloatMenu`; a debug log window can open and absorb clicks; armed designators trap clicks. **Every one of those
  is a false "this game is confusing" until filtered.**
- **No hover or tooltip read found** in the rimbridge skill and references. Players learn RimWorld from tooltips.
  Without one, a Stranger is half blind. The capability matrix lists "UI targeting and clicking" as unexplored, so a
  live tool census must confirm this. A new JawaBench `[Tool]` is the route (rimbridge-companion skill). Starred.
- **No game-input telemetry.** `src/RimMandrake/Utils/telemetry` records host and game series, not what a player does.
- **The art-judging precedent:** `skills/rimworld-art-evaluation` has an Opus judge, a 49-row criteria ledger of his
  overrides, a regression set and shadow sheets. This is the proven local shape for calibrating to his taste.
- **Test Pilot** (adopted by owner ruling this week): it owns live testing against item acceptance. The Player has no
  item list. They share the game, the bridge and the same scarce load, so they must be scheduled, not merged. The
  Ralph note from the same brief binds this: "not for subjective judgment", route that to an Opus judge or the owner.
- **Canary lesson:** a dead colony burned hours of testing counted as productive. The Player needs a validity canary too.
- **His judgment corpus is thin.** OWNER.jsonl has 4,056 events. Regex over them: confus 5, boring/dull/tedious 5,
  unreadable family 7, fun 1, annoying/frustrat 1, ugly/awful 7, love/great/beautiful 51, with false hits among them.
  26 of 217 conversation files match confus|boring|tedious. Six walk or owner documents are under design/. These are
  regex counts, unlabelled; call it a few dozen real labels at most.

### 2.2 Literature, read for validity against real players

| Family | Best evidence | Validated against real people? | What it means here |
|---|---|---|---|
| Fun and engagement by LLM | Melhart 2502.04379, Wang 2603.18480 | Yes: **mostly fails** | Do not judge dull from film |
| Rating from personas | PREFER 2610.19213 | No, as far as I read. Simulated persona preference | Do not count as evidence |
| Corpus-trained critics | MeepleLM 2601.07251, CoBG 2606.01976 | Partly: community alignment, human preference | Real corpus is the active ingredient |
| Difficulty and churn bots | Roohi 2107.12061 | **Yes, ρ = 0.80** | Needs population ground truth |
| Procedural personas | Holmgård 1802.06881, Ariyurek 2107.11965 | Weakly | Behaviour styles, not felt experience |
| UX heuristics by LLM | Guerino 2506.16345, Platt 2512.04262 | Yes: 21.2% overlap, new issues, 24.3% FP | Complement. Never severity |
| Synthetic users | UXAgent 2502.12561, NN/g, Bisbee 2024, Kumagae 2610.30900 | Where tested: averages right, spread wrong, overly favourable | Useful to pre-test a study, not to be the study |
| LLM novices | Borchers 2602.01015 | Yes: over-coherent, overestimated learners, **worse with richer context** | Direct warning for any novice persona |
| Persona prompting | Zheng 2311.10054, Hu 2402.10811 | Yes: little effect | Do not rest validity on "act as a novice" |
| Glitch detection | GlitchBench 2312.05291, Lu 2603.22706, Lu 2508.04895, Taesiri 2210.02506 | Yes against labels: 43.4% to 64.9%, precision 0.50, F1 0.79 once the bug is described | Pixels alone need a state check |
| State plus LLM QA | TITAN 2509.22170, Lap 2507.09490 | Against real bugs: 4 new bugs in MMORPGs, 95% task completion on abstracted state | Best model for broken |
| Raw vision play | VideoGameBench 2505.18134, BALROG 2411.13543, lmgame-Bench 2505.15146 | Scores: near zero real-time, Lite (paused) better, visual input often worse | **Pause. Scaffold. Do not expect competence from pixels alone** |
| Sim and strategy play | FLE 2503.09617, NetPlay 2403.00690, SPRING 2305.15486, CivBench 2604.07733, SIMA 2 2512.04797, Claude plays Pokémon | Scores only: weak spatial reasoning, 56% of steps in successful tasks had execution errors, poor on ambiguous goals, better with the manual | An open sandbox with no goals is the hard case; a good chunk of agent failure is the agent |
| GUI agents | Zhou 2606.24551 | Task pass 59.1% (GUI), 48.2% (CLI), 69.3% augmented | Even strong GUI agents fail a third to a half of tasks. That failure rate is noise for "confusing" |
| Measurement theory | Law 2018 (GEQ, no 7-factor evidence, N = 633), PENS 2006, MDA, Yannakakis 2015, Pichlmair 2011.09201 | N/A | Do not lean on GEQ; ask for ranks; use autonomy and competence as vocabulary only |
| Pacing models | Booth, *AI Systems of L4D* (2009) | Shipped, designer-tuned. Not a validity study | A number for "long periods of inactivity are boring" can guide a game; it is a designer's assumption |
| Frustration telemetry | Microsoft Clarity docs (rage and dead clicks) | Web product heuristic | Signals exist for humans. **No game-specific paper found**; they need a human at the mouse |
| Commercial | modl.ai, nunu.ai, PlaytestCloud (Razer page 404) | No published validity on fun that I found | Vendors sell bug-finding; PlaytestCloud sells humans, with AI to **summarise** them. That split is informative |
| RimWorld | Steam: 97% positive of 120,341 English reviews. arXiv: 0 hits for RimWorld, 0 for LLM colony sims | N/A | A vanilla control has a real reputation behind it. A review corpus can be mined |

**The failure pattern across all of it:** systems that shine on visible, verifiable properties and fail on the felt ones,
in confident prose. Literature does not support persona prompting as a route to validity.

---

## 3. Solutions

Three real designs and a null. They differ on who the observer is, what it perceives, when it runs, and where its
verdict comes from.

| | D1 Stranger | D2 Flight Recorder | D3 Taste Twin |
|---|---|---|---|
| Observer | LLM playing | **No LLM judges**; code measures | LLM watching, not playing |
| Knows the project | Nothing, enforced by proxy | Nothing needed | Everything, on purpose |
| Perception | Pixels, visible labels | Game state and input events | Film, plus design docs |
| Verdict comes from | Its own failed predictions | Delta against vanilla | Fit to his past rulings |
| Needs live game | Yes | Yes, unattended | No |

### D0. The null: a human, and doing nothing

A friend or paid playtester for 2 hours, screen recorded, or Mandrake for 30 minutes a week with a recorder on. It is
the only option with real validity for dull. It costs his attention or a stranger's goodwill and raises a question about
sharing the mod list. Every design is measured against it where it can be. The item's smaller step, one Player pass per
week in session with him, is a form of this.

### D1. The Stranger

**Idea.** A fresh agent, knowing nothing about RimMandrake, plays the shipped save through only what a player has, and
its judgement comes from **its own prediction errors**, not its opinions. The literature's failure is asking a model how
something feels; asking what it expects, then checking, is a question with an answer.

**How it works.**

1. **A perception firewall.** A proxy, not a prompt, sits between agent and bridge. It exposes: screenshot at real
   resolution and UI scale, pixel click (resolved by the proxy to `click_ui_target` or `click_cell` from layout
   rectangles), right-click, hover, camera, speed, pause, keys. It strips all defNames, ids and the rest of the 141 tools,
   and refuses flight gizmos, new-game, debug tools and save-overwrites. The clean room is enforced in code. The agent's
   context has no repo, no CLAUDE.md, no skills.
2. **Play in pauses.** Pause-stepped, because VideoGameBench shows real-time vision fails on latency.
3. **Predict, act, reveal.** Before each consequential act it logs one line: *I expect X.* The proxy then gives the next
   frame. A separate fresh grader, which can read true game state, compares. This separation is the design's central
   claim, and it is untested.
4. **Self-set goals.** It reads the screen and states a goal a player would have ("get these people fed"), with a budget
   of attempts. A goal abandoned or met only by luck is an event. Narrative is captured, but is not evidence.
5. **Fresh, short, many.** Three independent 90-minute passes per segment, new context each, one item per pass (Ralph). A
   finding counts only when **at least two of three** hit the same control, which suppresses one-off agent failure and
   makes the evaluator effect work for us.
6. **Triage.** A state-reading judge filters instrument faults (click landed nowhere, debug window, known bridge traps)
   and a prereview judge caps output at five per pass.

**How it decides.**

- *Broken:* expected X, state confirms Y, and the screen did not say so. Needs state confirmation.
- *Unreadable:* it gives a wrong reading of something the state knows (it says "12 meals", state says 2). A test of
  reading, not an opinion. Plus: a label it cannot transcribe at real resolution.
- *Confusing:* at least two of three strangers mispredict the same control, or cannot find a route to a goal they set,
  **and the vanilla control does not show the same failure in the matching vanilla control type**. That last clause
  subtracts the agent's own general incompetence.
- *Dull:* never decided. It records decisions per game hour and spans where it wrote "nothing to do but wait" as a raw
  suspect, labelled unverified.

**Example report (illustrative, not a real finding):**

> **Confusing, 3 of 3 strangers.** Colony day 2. All three selected the workbench and predicted the top button would
> queue a bill; it opened a settings window. Vanilla control: 0 of 3 on the equivalent control. Screenshots attached.
> The hover text was read and did not change the prediction. Would a player meet this? Yes, within the first 10 minutes.

**Validation.** The Exam. Plus a *knowledge-injection check*: does a second Stranger, given the manual, lose the finding?
If so it is a docs gap, and a useful class. Borchers warns richer context worsens novice fidelity, so test this.

**Cost.** Build: proxy, hover tool, grader, deny list, control run: 5 to 8 agent-days (estimated). Tokens per 90-minute pass: about 300 steps; each frame about 2.7k visual tokens at 1920x1080 by Anthropic's ⌈w/28⌉×⌈h/28⌉ formula; with a rolling context of about 30k, about 10M mostly cached input tokens per pass (estimated). Three passes on Opus plus judges: 30M to 40M tokens. Latency: one cold load plus 2 to 3.5 hours per pass at 20 to 40 s a step (estimated), holding the bridge throughout. Upkeep: proxy tracks bridge changes; control runs repeat as the game changes.

**Risks and false positives.** Agent friction read as human friction is the core risk: spatial weakness (FLE), GUI failure at 30 to 50% (Zhou), Pokémon-style perception oddity. The vanilla control and 2-of-3 rule are the mitigation, and they may not be enough. Opposite failure: LLMs know RimWorld from training data, so the "Stranger" is not new to the base game, and may read through traps a real newcomer falls in. It becomes a *stranger to RimMandrake, not to RimWorld*, which suits us but must be stated. It may simply not get far in a 90-minute pass, and test only the first hour, forever. Bridge hold competes with Test Pilot.

**What it buys.** Genuine first-contact evidence, and no reliance on anyone having played. **What it costs.** The most tokens and the most bridge time, with a real chance of a noise machine.

**Dominates when:** the Exam shows recall on confusing and the vanilla control discriminates; first-contact and onboarding matter most; a hover tool exists; a spare machine has the full list.

### D2. The Flight Recorder

**Idea.** Do not ask anyone's opinion. A colony sim runs itself, so *the game can be measured without a player at all*.
Telemetry and static checks produce numbers; those are compared with vanilla; a person gets ranked suspects. The LLM is
only a clerk who writes it up. This is the Clarity and L4D lineage.

**How it works.** Three layers.

1. **Static sweep (no game).** Over def dumps and Textures: missing or empty descriptions, label length beyond what fits,
   icon contrast and occupied pixels at true size, gizmos with no tooltip, and description reading level; a measured
   table against vanilla's distribution.
2. **Attended recorder.** A small mod with Harmony hooks logging only player-facing events: letters received and
   whether opened, alerts raised and how long unaddressed, gizmo clicks with no state change, repeat-click bursts, undo-right-after-do,
   window open and dwell, order-cancel pairs. Costs nothing unless someone plays. It runs when Mandrake plays, when Test Pilot
   drives, and under D1.
3. **Unattended autopilot.** A scripted governor runs a disposable copy of the shipped save and a vanilla baseline for N
   game days: pause-free, with the fixed policy of answering letters the default way. It measures **decision demand**:
   the rate of letters, research and build unlocks, new options, alert density, colonist idle share, repeated chore share,
   colony-death rate; plus red errors and silent failures.

**How it decides.**

- *Broken:* new red errors, gizmos that change nothing, jobs that fail repeatedly, a "success" letter with no state
  change. All deterministic. Best of the three on this word.
- *Unreadable:* outliers from vanilla's distribution: this icon's contrast is lower than 99% of vanilla's, this description
  is empty, this label truncates. Deterministic. Cannot judge whether an image reads as its subject.
- *Confusing:* in attended data, alerts ignored, repeat-click bursts, order-cancel pairs, dwell. With no human at the
  mouse this word is **dark**, and repeat clicks from an agent mean little.
- *Dull:* the best *proxy* of the three, and a proxy only: stretches of over X game days with no new decision demand,
  ranked against vanilla's distribution, then **he** ranks pairs and the weights are fitted to him. Never reported as "dull";
  reported as "quietest stretch: 6.1 game days without a new decision, 94th percentile of vanilla".

**Example report (illustrative):**

> **Dull-risk, unranked.** Autopilot day 18 to 24: 0 letters, 0 unlocks, 71% of colonist hours in hauling. Vanilla at equal
> wealth: median 1.9 decisions a day, this span 0.3. Not a judgement: a place to look.

**Validation.** Seed by construction: the deterministic layers can be fully tested by planting each defect (recall
should be near 1, or it is a bug). Then his pairwise ranks test only the dull proxy. Check test-retest across seeds: the storyteller is random, so run enough seeds to read variance.

**Cost.** Build: static sweep 1 day; recorder 2 to 3 days; autopilot 3 to 5 days; a C# DLL means a game restart to deploy (estimated). Tokens: near zero per run; a few thousand for write-up. Latency: an unattended run can use a spare machine; a full-list cold load, then game time. Upkeep: hooks break with game updates; baselines refresh.

**Risks and false positives.** Goodhart: tune decision density and you build a nagging game, which is the classic error of treating the proxy as fun; quiet can be good, since RimWorld's pacing wants valleys (L4D says exactly that). The autopilot does not play like a person and dies or stalls differently, so a stable governor over 24 game days is itself a hard build; a colony that dies invalidates the run (canary). Measures easy things, so confusing stays dark until a human plays. High surface area in Harmony hooks; must be off in shipped builds.

**What it buys.** Numbers free of opinion and hallucination, cheap repeat runs, a real baseline, a permanent asset that makes the other designs stronger. **What it costs.** It never says anything a person would call an experience.

**Dominates when:** tokens and bridge time are tight; he will play or ask others to play; the Exam finds LLM judges noisy; you want regression tracking between builds.

### D3. The Taste Twin

**Idea.** Do the opposite of D1: not a stranger but **a critic who knows the design and knows him**, offline, watching
film. This extends the art-judge pipeline, the one calibration to his taste this project has already proven. Validity comes
from a held-out test of his own rulings and from a real-player corpus, the one ingredient that worked in the literature.

**How it works.**

1. **Corpus.** His rulings on experience, mined from OWNER.jsonl, conversations and walks; a **criteria ledger** like
   art's. Plus an outside voice: Steam reviews of RimWorld and comments on Workshop mods near ours, separated from his,
   to learn what real players complain about in this genre. Use Pinelle-style game heuristics only as a checklist (metadata only; to be read before use).
2. **Film.** Any cheap record of play: Test Pilot screenshots, D2 recorder traces, frames stepped through a save, or
   a human's video. No game time of its own. Design docs tell it what each mechanic is for.
3. **Judgement.** It compares *design intent to what the film shows*: "this is meant to feel dangerous; the film shows no way
   for a player to know the danger exists". A second fresh judge checks every finding (as art's two-stage pipeline does), and
   hard-checkable statements are verified against state.
4. **Learning.** Each ruling of his on a finding becomes a ledger row and a regression case. Agent overrides require
   a regression rerun.

**How it decides.**

- *Broken:* design says X, film shows Y. Good for intent mismatches a telemetry rule cannot express. Reports only what film
  contains.
- *Unreadable:* it sees frames at true size against his recorded rulings. Good fit: this is art judging's closest neighbour.
- *Confusing:* weakest. Curse of knowledge: it knows what the thing does, and must simulate not knowing. Reported only
  as "the screen in film does not say what the doc says a player must know": a gap between doc and display, not a confusion.
- *Dull:* predicts which of two segments he would call duller, **only if it beats a majority baseline on held-out pairs**.
  Otherwise the word is off. Wang's results predict it will not beat it. This is a cheap way to find out.

**Example report (illustrative):**

> **Unreadable, matches criterion 14 (his ruling: "disconnected and confusing winch designs").** Frame 212. The design says the
> two machines form a chain; at true zoom nothing shows the link. Second judge agrees. Confidence is not given.

**Validation.** Hold out a third of his labelled rulings: can it recover them on old artefacts, against a majority baseline? Then
back-test on historic deck. Shadow sheets first, as art has. This is the cheapest validation of the three, needing no game.

**Cost.** Build: corpus mining and ledger 3 to 4 days, film capture 1 day, review harness reuse from art (estimated). Tokens: 2M to 5M per review batch (estimated). Latency: offline, no bridge. Upkeep: ledger grows with each ruling. **The real cost is his labelling time**, and a thin corpus means it pays out late.

**Risks and false positives.** It is an echo: reports what he already thinks, misses the unknown unknowns that are the point of a Player; the corpus's few dozen labels may not generalise beyond art-adjacent complaints; a rich ledger overfits; it sees only film someone else shot, so anything no one reached does not exist; it is not playing, so is that even "the Player"? Confident rationale (Wang) is the risk, and the second judge shares its blind spots. Reviews on Steam mostly rate vanilla, not mods. Scraping needs a licence-and-ToS check.

**What it buys.** No bridge, cheap, a calibrated filter that improves everything else, and it scales his taste. **What it costs.** It cannot be surprised, and it finds few things he would not have.

**Dominates when:** bridge time is scarce; he is willing to label; the worst pain is things that violate his intent, rather than things strangers cannot follow; as the final filter before anything reaches him.

### 3.1 Compared

| | D0 Human | D1 Stranger | D2 Recorder | D3 Twin |
|---|---|---|---|---|
| Broken as felt | Good | Good, with state check | **Best** | Partial |
| Unreadable | Good | Good, reading test | Good, deterministic part | Good, taste part |
| Confusing | **Best** | **Only candidate that plays** | Dark without a human | Doc-vs-display only |
| Dull | **Only valid** | Suspect only | Best proxy | Tests the claim cheaply |
| Unknown unknowns | High | High | Low | Low |
| Build, agent-days (est.) | 0 | 5 to 8 | 6 to 9 | 4 to 5 |
| Tokens per pass (est.) | 0 | 30M to 40M | near 0 | 2M to 5M |
| Holds bridge | no | hours | hours, machine | no |
| Main false positive | none | agent incompetence | Goodhart, proxy | echo, confident story |
| His time | play | exam, 1 hour | ranks, 30 min | labels, hours |

---

## 4. Recommendation

**Build the Exam, then a staged D2-to-D1 stack, with D3 reduced to the final filter. Never let any of it say "dull" as a verdict.**

1. **Stage 0: the Exam deck, and the cheap half of D2.** Static sweep, recorder, and the hover-tool census. No trial
   needed; useful on its own. Static sweep can run offline at once.
2. **Stage 1: one Stranger, one night.** Proxy, 3 passes against seeded deck, vanilla control. This is the experiment that
   decides the design, for one load and roughly 40M tokens. If the vanilla control does not discriminate, stop and keep D2.
3. **Stage 2: if it passes,** run Stranger weekly by the item's trial terms, with a D3-style prereview judge calibrated on
   his labels from the Exam.
4. **Dull ships as "Quietest stretches", from D2, ranked by him.** Fitted to his pairs if the rank test passes. Label stays
   "risk".
5. **Ask for D0 in parallel:** the recorder on his next real session or a friend's. Two hours of a real stranger would
   teach us more about dull than any stage here, and would also grade D1.

**Why this order.** D2's static and recorder layers are the only parts that are useful whether or not LLM judgement
works. D1 is the only one that can surprise us and the only candidate for confusing, but its validity is the least
certain, so it sits behind a cheap kill test. D3 alone fails the role's reason for being: an agent that shares his view
cannot occupy an empty chair. D3 as filter serves "nothing reaches him unread".

The D2 autopilot (layer 3) is deliberately deferred: it is the costliest part and depends on a governor nobody has built.

**What would change my mind.**

- Hover tool is impossible or a pass cannot get past the first in-game hour: D1 falls, D2 plus D0 is the role.
- Stranger's discrimination vs vanilla is strong on confusing: bring it forward, cut the recorder.
- D3 beats baseline on held-out pairs for dull: that would contradict Wang and Melhart, and is worth a real look.
- He is back to playing daily: D2's recorder plus D3 outperforms D1, as telemetry from a real player beats any simulated one.
- A real external validation paper appears for long-horizon sims: re-open dull.
- Bridge time cannot be found alongside Test Pilot: D3 plus static D2 only, no live player.
- Vanilla control is unbuildable on the same list (see claim 8): the D1 discrimination test needs redesign.

---

## 5. Open decisions

1. **Q1. Definitions:** are the four operational definitions in §1.1 his meaning?
2. **Q2. Agree the honest scope?** Dull is never a verdict, only a ranked list. His word "dull" stays on a label only with "risk".
3. **Q3. A human?** Is one outside playtester acceptable, or is the mod list private? His own 30 minutes weekly with recorder?
4. **Q4. Which machine?** SteveDesktop or Archmagi, and how bridge time is shared with Test Pilot.
5. **Q5. His exam hour:** will he give about 1 hour for blind labels and pairs? Without it nothing is validated.
6. **Q6. Spoilers:** does Stage 1 run before he has seen seeded defects, and may seeds be left only in a disposable copy? (Recommended: yes, disposable only.)
7. **Q7. Spend:** about 40M tokens for the kill test, on Opus. Sonnet for the player with Opus judging is cheaper, unproven.
8. **Q8. Steam and Workshop mining:** allowed under their terms? Needed only for D3's outside voice.

---

## 6. Claims table

Starred claims would change the recommendation if wrong.

| # | Claim | Status | How / source |
|---|---|---|---|
| 1* | No opened source validates an LLM agent against real players' felt experience in a long-horizon sim | measured, limited | arXiv and DOI lookups, no WebSearch; absence of evidence |
| 2* | LLM judgement of engagement is near chance on pairs and rarely above majority | measured by others | 2502.04379, 2603.18480; FPS clips only, not colony sims |
| 3* | Bridge has no hover or tooltip read | unmeasured | Grep of skill, no live census; capability matrix says UI unexplored |
| 4* | Agent friction can be separated from game friction using a vanilla control and 2-of-3 | assumed | The core untested claim of D1 |
| 5* | A pause-stepped LLM can play the shipped save for 90 minutes usefully | unmeasured | VideoGameBench Lite, FLE suggest difficulty; no RimWorld data |
| 6* | One real human beats all designs on dull | assumed, strongly | Follows from 2; never tested here |
| 7* | Seeded defects represent real experience defects | assumed | Seeds are likely easier than real ones; historic deck hedges |
| 8* | A vanilla plus DLC control can run on a comparable colony and resolution | unmeasured | Needs a colony fixture; no worldgen constraint binds new game there too, unresolved |
| 9* | He will give about 1 hour of labels | assumed | His call |
| 10 | Shipped save is the 10-20 file | measured | canon.yml lines 86 to 88, file on disk, 13.6 MB |
| 11 | Full list cold load 15 to 25 min | measured by others, sources disagree | TestPilot brief vs load-round skill |
| 12 | Bridge has about 141 tools | measured by others | capability matrix census, date not re-checked |
| 13 | His experience-labelled corpus is a few dozen items | measured, rough | Regex over OWNER.jsonl (4,056 events) and conversations; unlabelled, false hits seen |
| 14 | Art criteria ledger has 49 rows | measured | `wc -l` |
| 15 | D1 pass: 10M input tokens, 2 to 3.5 h | estimated | 300 steps × 30k context; 20 to 40 s step assumed |
| 16 | 1920x1080 frame is about 2.7k visual tokens | measured from the docs | Formula on Anthropic vision page; 69 × 39 |
| 17 | Build costs in agent-days | estimated | Judgement; see rimbridge-companion for tool cycle |
| 18 | LLMs know vanilla RimWorld from training data | assumed | Not tested; matters for what "stranger" means |
| 19 | Odds in §0 | estimated | Author's judgement, not derived |
| 20 | Item's `dispatcher_schedule.json` revert path exists at that path | unmeasured | Grep under infrastructure/state found nothing; trial revert needs checking |
| 21 | Screenshot resolution equals what he sees | unmeasured | The game is windowed for agents; unreadable needs his UI scale |
| 22 | Agent severity scores are unreliable | measured by others | 2512.04262, on websites |

---

## 7. How the role fits

Input: a disposable copy of the shipped save, a proxy, no repo. Output: at most five findings per pass, each a rimflow item
after prereview. It is not a tester: it holds no acceptance list and closes nothing. FOUNDRY keeps FlowWorks and GSS findings. Test Pilot owns whether a fix works. A Player finding closed by a product commit is the item's trial metric. Each pass needs its own canary: a live colony at start, a healthy proxy, and a known-seeded test control the agent must find.

## 8. Risks common to every design

- **The volume trap.** Thirty soft findings a week cost more of him than they save. Hence the cap, and the trial's guard.
- **Reading its output as the player's voice.** A finding is a lead. The report language must never say "players will feel".
- **Measure-then-drift.** Every game change shifts baselines; passing the Exam once is not a licence. Rerun quarterly, or on model change.
- **Model changes silently alter the instrument.** Pin the model per Exam.

## 9. Findings filed with this design

- `CANONICAL_SAVE.md` contradicts `canon.yml` about `start_savegame`.
- The bridge appears unable to read a tooltip; live census owed.
- The item names a schedule file not found at that path.

## 10. Sources

Opened (read as text unless noted):

- arXiv, abs/<id>: 2502.04379 Melhart et al.; 2603.18480 Wang et al.; 2107.12061 Roohi et al.; 2610.19213 PREFER; 2601.07251
  MeepleLM; 2606.01976 CoBG; 2407.12787 GameVibe; 2506.16345 Guerino et al.; 2512.04262 Platt et al.; 2402.10811 Hu and Collier;
  2311.10054 Zheng et al.; 2602.01015 Borchers et al.; 2507.02919 Li et al.; 2610.30900 Kumagae et al.; 2607.28550 Heath et al.;
  2502.12561 UXAgent; 2312.05291 GlitchBench; 2603.22706 Lu et al.; 2508.04895 Lu et al.; 2210.02506 Taesiri et al.; 2509.22170
  TITAN; 2507.09490 Lap et al.; 2202.12777 Politowski et al.; 2505.18134 VideoGameBench; 2411.13543 BALROG; 2505.15146
  lmgame-Bench; 2503.09617 FLE; 2403.00690 NetPlay; 2305.15486 SPRING; 2604.07733 CivBench; 2512.04797 SIMA 2; 2606.24551
  Zhou et al.; 1802.06881 Holmgård et al.; 2107.11965 Ariyurek et al.; 2011.09201 Pichlmair and Johansen. Several were abstract
  level; full text read for 2502.04379, 2603.18480, 2107.12061, 2603.22706, 2506.16345, 2601.07251.
- Bisbee et al. 2024, Political Analysis, 10.1017/pan.2024.5 (abstract). Law et al. 2018, 10.1145/3242671.3242683 (abstract).
  Yannakakis and Martínez 2015, 10.3389/fict.2015.00013. Ryan, Rigby, Przybylski 2006, 10.1007/s11031-006-9051-8. Hunicke,
  LeBlanc, Zubek, MDA.
- Mike Booth, The AI Systems of Left 4 Dead, Valve 2009, steamcdn-a.akamaihd.net/apps/valve/2009/ai_systems_of_l4d_mike_booth.pdf.
- Ars Technica on Claude and Pokémon, arstechnica.com/ai/2025/03/why-anthropics-claude-still-hasnt-beaten-pokemon/. Anthropic's
  visible extended thinking post. Anthropic vision docs (image tokens).
- NN/g: heuristic evaluation; synthetic users; AI simulations. Microsoft Learn: Clarity semantic metrics.
- modl.ai, nunu.ai, playtestcloud.com (marketing pages). Steam store page for RimWorld.

Metadata only, not read: Hertzum and Jacobsen 2001, 10.1207/s15327590ijhc1304_05; Pinelle et al. CHI 2008,
10.1145/1357054.1357282; Desurvire et al. 2004, 10.1145/985921.986102; Sweetser and Wyeth GameFlow, 10.1145/1077246.1077253;
Duan et al. CHI 2024, 10.1145/3613904.3642782; Martínez et al. 2014, 10.1109/taffc.2014.2352268; Vox Deorum 2512.18564.

Gaps: no Minecraft agent paper opened; no game-specific frustration detection paper found; Razer QA Copilot page 404; LessWrong
blocked; FLE site empty. Pokémon failure details rest on Ars and Anthropic only.
