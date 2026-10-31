# GPT pass 2: critique of 01-design.md (02)

Consult id: consult-20261031-102551-3244271 (gpt_consult.py, model gpt-6.1-sol, web on, answered in about 9 min). Design sent inline as "a design", author not named; prompt asked for citation verification, per-solution critique and improvement, missed options, starred-claim check, and a pick. Answer verbatim below. GPT is guidance, not authority; its citation verdicts are unchecked by me.

---

**I would build a fourth design: a checkpointed experience auditor combining a small part of D1, lightweight D2 instrumentation, and selective human validation.** I would defer the autonomous governor and the Taste Twin.

The references are substantially more real than the unreliable evidence notice warrants assuming. I found **no demonstrably nonexistent cited paper**. The main defects are misinterpretation, weak transfer between domains, and an Exam that could certify a consistently mistaken agent.

**1. Citation audit**

I independently opened the links below. “Verified” establishes the source and the stated finding; it does **not** automatically establish transfer to RimWorld. “MISATTRIBUTED” includes assigning an existing finding to the wrong task, modality, or validation setting. “UNVERIFIABLE” means the supplied information or accessible material was insufficient.

Repeated citations are consolidated.

| Citation and URL opened | Status | What it actually establishes; accuracy of the design’s use |
|---|---|---|
| [Melhart et al., 2502.04379 — *Can Large Language Models Capture Video Game Engagement?*](https://arxiv.org/html/2502.04379v2) | **Verified; overstated interpretation** | Confirms 80 minutes, 20 FPS games, over 4,800 experiments, and inconsistent performance. GPT-4o few-shot averages approximately +6% **relative gain, ΔA**, over the zero-rule baseline, with substantial successes on some games. Crucially, the target is **viewers’ engagement annotations**, not the feelings of the person playing. “Every direct test is negative” is too strong. |
| [Wang et al., 2603.18480 — *Do Vision–Language Models Understand Human Engagement in Games?*](https://arxiv.org/html/2603.18480v2) | **MISATTRIBUTED numbers; otherwise verified** | Near-chance pairwise performance and visual-intensity shortcuts are supported. But approximately **57% versus 67.2% is pointwise**, not pairwise. The pairwise majority baseline averages **56.5%**; strategy averages range roughly 47.7–58.8%. Some adapted pointwise configurations improve substantially. This supports caution, not impossibility. |
| [Roohi et al., 2107.12061 — *Predicting Game Engagement and Difficulty Using AI Players*](https://arxiv.org/html/2107.12061v1) | **Verified; statistic needs qualification** | Confirms 168 Dream Blast levels and human pass/churn data. **ρ=.80** is the correlation between an AI-pass-rate feature and human pass rate, averaged over 1,000 DRL runs per level. It is not itself the held-out prediction score of the complete proposed model. Correct that aggregate behavior prediction is a different target from felt boredom. |
| [PREFER, 2610.19213](https://arxiv.org/html/2610.19213v1) | **Verified** | Uses LLM personas playing card games and predicted preference gains. The paper explicitly leaves transfer to human players for future studies. Correctly excluded as human-experience validation. |
| [MeepleLM, 2601.07251](https://arxiv.org/html/2601.07251v5) | **Verified; causal inference overstated** | Confirms 1,727 rulebooks, 150K reviews, community-alignment evaluations, and human judgments of critique utility. Preference for useful critique is not proof that an agent reproduces a player’s unfolding experience. The corpus is part of the method; these results do not establish that corpus size alone caused validity. |
| [CoBG, 2606.01976](https://arxiv.org/abs/2606.01976) | **Verified** | Reports 2.2K rulebooks, 180K reviews, 207 held-out games, a 30-participant study, and paper-prototype playtests. Stronger than merely generating plausible reviews, but still no validation of autonomous colony-sim experience assessment. |
| [GameVibe, 2407.12787](https://arxiv.org/abs/2407.12787) | **Verified** | Barthet et al.’s corpus contains gameplay videos and **third-person viewer-engagement traces** across 30 games. This distinction should appear prominently in the design. Melhart and Wang also share this dataset lineage; they are not independent replications across unrelated experience datasets. |
| [Guerino et al., 2506.16345](https://arxiv.org/html/2506.16345v1) | **Verified; denominator obscured** | Confirms 21.2% recovery of human-identified issues in a screenshot-based web-interface study. The reported 24.3% is **27 false positives /111 raw reports**. After removing 43 duplicates, it is **27/68≈39.7%**. This is not a general false-positive probability for game agents. Better performance on minimalist design does not establish precise text-legibility assessment. |
| [Platt et al., 2512.04262](https://arxiv.org/pdf/2512.04262) | **MISATTRIBUTED validation and interpretation** | Evaluates repeated GPT-4o inspections of **website source code**, not correctness against human experts. Detection κ≈.50 and severity weighted κ≈.63 are reported. Although its abstract associates near-zero alpha with severity, the body’s Table III places α=−.000234 in the **binary issue-detection** analysis. The paper is internally inconsistent here. It cannot justify “never ask for severity,” nor §2.2’s human-validation label. |
| [Hu and Collier, 2402.10811](https://arxiv.org/abs/2402.10811) | **Verified; selectively summarized** | Persona variables explain under 10% of annotation variance in the studied NLP datasets, but persona prompting produces modest, statistically significant improvements. Benefits depend on how informative the persona variables actually are. This is not a general demonstration that behavioral personas are ineffective. |
| [Zheng et al., 2311.10054](https://arxiv.org/abs/2311.10054) | **MISATTRIBUTED scope** | Tests role prompts on 2,410 **factual questions**, finding no general improvement. It does not test novice simulation or whether personas reproduce gameplay behavior. Useful warning against assuming that role text creates competence; weak evidence about player fidelity. |
| [Borchers et al., 2602.01015](https://arxiv.org/abs/2602.01015) | **Verified** | Confirms 630 chemistry-tutoring think-aloud utterances, overly coherent and confident simulated reasoning, performance overestimation, and stronger distortions with richer context. Relevant warning, but the richer-context result is task-specific, not a universal law. |
| [Li et al., 2507.02919](https://arxiv.org/abs/2507.02919) | **Verified** | Finds structural inconsistency and homogenization in synthetic answers to political survey questions. Supports concern about missing variation; does not directly measure player experience. |
| [Kumagae and Kaneko, 2610.30900](https://arxiv.org/abs/2610.30900) | **Verified** | Shows synthetic respondents can reproduce answer distributions while failing to cover real combinations of answers. Strong reason to test individual profiles and joint behavior, not just averages. |
| [Heath and Alexander, 2607.28550](https://arxiv.org/abs/2607.28550) | **Verified; relevant qualification omitted** | Studies low-variance silicon samples and reports improvements using text responses mapped through semantic-similarity ratings. It suggests a mitigation worth testing; it does not validate game-experience prediction. |
| [UXAgent, 2502.12561](https://arxiv.org/abs/2502.12561) | **Verified** | Designed to help researchers rehearse and improve usability-study designs before human studies. Evaluated with five UX researchers. Correctly presented as study support rather than replacement participants. |
| [GlitchBench, 2312.05291](https://arxiv.org/html/2312.05291v2) | **Verified; metrics need labels** | GPT-4V scores 43.4% on the main glitch-description evaluation and 64.9% with extensive captioning. These are different prompting/evaluation conditions, not an interchangeable detection range or precision estimate. |
| [Lu et al., 2603.22706](https://arxiv.org/abs/2603.22706) | **Verified** | Confirms 100 industrial QA videos, 41 hours, 19,738 keyframes, baseline precision .50 and accuracy .72. Secondary judges and metadata give marginal gains with added cost and variance. Directly weakens the assumption that adding another judge reliably solves hallucinated findings. |
| [Lu et al., 2508.04895](https://arxiv.org/abs/2508.04895) | **Verified** | Reports F1=.79 for retrieving the frame matching an **existing bug description**. The design acknowledges this qualification correctly. It is evidence for triage, not discovering unknown bugs. |
| [Taesiri et al., 2210.02506](https://arxiv.org/abs/2210.02506) | **MISATTRIBUTED modality** | Detects buggy events from **textual event descriptions**, with 70.66% reported accuracy under the selected prompt. It belongs under text-based bug reasoning, not evidence about pixel-only judging. |
| [TITAN, 2509.22170](https://arxiv.org/abs/2509.22170) | **Verified** | Reports 95% task completion, four previously unknown bugs, and state abstraction plus LLM reasoning in commercial MMORPGs. Supports hybrid QA architecture. It does not validate “broken as felt” or prove that state resolves ambiguous interface expectations. |
| [Lap, 2507.09490](https://arxiv.org/abs/2507.09490) | **Verified** | Zhao and Tang convert match-3 screenshots into numeric matrices, then use an LLM for moves. Reports improved coverage and crash triggering. Not a subjective-experience study. |
| [Politowski et al., 2202.12777](https://arxiv.org/abs/2202.12777) | **Verified** | Literature review and developer survey identify gaps between automated testing research and practical workflows, emphasizing goals and oracles. No felt-experience validation. |
| [VideoGameBench, 2505.18134](https://arxiv.org/abs/2505.18134) | **Verified** | Reports 0.48% completion in real time and 1.6% in paused Lite for the strongest tested configurations. Pausing helps latency; competence remains poor. These percentages are game-completion measures, not click-error rates. |
| [BALROG, 2411.13543](https://arxiv.org/abs/2411.13543) | **Verified** | Confirms severe limitations in harder games and cases where visual observations worsen performance. Correctly motivates instrument calibration. |
| [lmgame-Bench, 2505.15146](https://arxiv.org/abs/2505.15146) | **Verified** | Identifies brittle vision, prompt sensitivity, contamination, and benefits of lightweight perception/memory scaffolds. Supports scaffolding, while showing that the scaffold itself changes what is being evaluated. |
| [FLE, 2503.09617](https://arxiv.org/html/2503.09617v1) | **Verified** | Confirms spatial and debugging weaknesses. The **56%** figure concerns **program-execution errors in successful lab-play trajectories**, from which agents recovered. It is not 56% erroneous mouse actions or a human-confusion estimate. |
| [NetPlay, 2403.00690](https://arxiv.org/html/2403.00690v1) | **Verified** | Jeurissen et al. report trouble with ambiguous tasks and missing explicit feedback; detailed context helps performance. Relevant to agent operation, without establishing human fidelity. |
| [SPRING, 2305.15486](https://arxiv.org/abs/2305.15486) | **Verified** | Uses the Crafter paper as context and structured reasoning; reports improvements over selected RL baselines. Supports documentation-assisted competence, not faithful novice experience. |
| [CivBench, 2604.07733](https://arxiv.org/abs/2604.07733) | **Verified** | Evaluates strategic capability through state-value estimates across 307 Civilization V games. No validation of predicted boredom or confusion. |
| [SIMA 2, 2512.04797](https://arxiv.org/html/2512.04797v1) | **Verified** | Generalist embodied agent with human demonstrations and human task-performance baselines. Human comparison here concerns **task execution**, not predicting human experience. |
| [Zhou et al., 2606.24551](https://arxiv.org/abs/2606.24551) | **Verified; transfer overstated** | Confirms 59.1% GUI, 48.2% original-skill CLI, and 69.3% augmented CLI pass rates on matched desktop tasks. These are **whole-task failures** across applications. They cannot be inserted as a 30–50% noise rate for RimWorld confusion findings. |
| [Holmgård et al., 1802.06881](https://arxiv.org/abs/1802.06881) | **Verified** | Procedural personas enact different play styles through evolved MCTS heuristics. Useful for coverage and behavioral diversity; not validated feelings. |
| [Ariyurek et al., 2107.11965](https://arxiv.org/abs/2107.11965) | **Verified** | Developing personas and alternative-path finding improve behavioral coverage in GVG-AI/VizDoom. Particularly relevant to avoiding D1’s repeated-first-hour problem. |
| [Pichlmair and Johansen, 2011.09201](https://arxiv.org/abs/2011.09201) | **Verified** | Survey of game feel organized around physicality, amplification, and support. A design vocabulary, not a psychometric instrument or automated-experience validator. |
| [Vox Deorum, 2512.18564](https://arxiv.org/abs/2512.18564) | **Verified** | Reports hybrid macro-level LLM strategy with delegated tactical execution across 2,327 complete Civilization V games. A missed architectural option: delegate execution without asking the strategic agent to behave like a human participant. |

The publisher and foundational references:

| Citation and URL opened | Status | Actual content and relevance |
|---|---|---|
| [Bisbee et al. 2024, 10.1017/pan.2024.5](https://doi.org/10.1017/pan.2024.5) | **Verified** | *Synthetic Replacements for Human Survey Data? The Perils of Large Language Models*. Synthetic political-survey answers have reduced variation and problematic conditional relationships. The design’s caution is accurate; transfer to games remains inferential. |
| [Law, Brühlmann and Mekler 2018, 10.1145/3242671.3242683 — author-institution record](https://research.aalto.fi/en/publications/systematic-review-and-validation-of-the-game-experience-questionn/) | **Verified** | DOI opening returned 403; the institutional abstract confirms **N=633** and no evidence for the original GEQ seven-factor structure. Accurate. This argues against uncritical GEQ use, not against all player-experience questionnaires. |
| [Yannakakis and Martínez 2015, 10.3389/fict.2015.00013](https://doi.org/10.3389/fict.2015.00013) | **Verified** | *Ratings are Overrated!* argues for rank-based subjective reporting. Supports considering comparisons; does not validate the design’s ten-pair sample or 70% gate. |
| [Ryan, Rigby and Przybylski 2006, 10.1007/s11031-006-9051-8](https://doi.org/10.1007/s11031-006-9051-8) | **Verified** | Four human studies link autonomy, competence, relatedness and game enjoyment/motivation. Calling this merely vocabulary understates its empirical basis. It still does not supply an automated RimWorld boredom detector. |
| [Hunicke, LeBlanc and Zubek, *MDA*](https://www.cs.northwestern.edu/~hunicke/MDA.pdf) | **Verified** | Mechanics–Dynamics–Aesthetics framework. Correct authors and conceptual use; no validated numerical experience score follows from it. |
| [Hertzum and Jacobsen 2001, DOI attempted](https://doi.org/10.1207/s15327590ijhc1304_05), [author bibliography opened](https://mortenhertzum.dk/publ.html) | **Verified bibliography; body UNVERIFIABLE in this audit** | Author bibliography confirms the 2001 article and corrected 2003 reprint. The evaluator-effect argument concerns different evaluators finding different problems. It does not establish that majority agreement among correlated LLM runs identifies genuine problems. |
| [Pinelle, Wong and Stach 2008, 10.1145/1357054.1357282](https://doi.org/10.1145/1357054.1357282) | **Verified bibliography; body UNVERIFIABLE** | Publisher and alternative PDF fetches failed. Title/authors/DOI are independently corroborated in the opened [Duan paper’s references](https://people.eecs.berkeley.edu/~bjoern/papers/duan-heuristic-chi2024.pdf): *Heuristic Evaluation for Games: Usability Principles for Video Game Design*. The design correctly labels it metadata-only. |
| [Desurvire, Caplan and Toth 2004, 10.1145/985921.986102](https://doi.org/10.1145/985921.986102) | **Verified bibliography; full body UNVERIFIABLE** | *Using Heuristics to Evaluate the Playability of Games*. Publisher fetch failed; a [paper copy was located](https://www.valuesatplay.org/wp-content/uploads/2007/09/desurvireplayabilityheurist.pdf), but opening timed out. Its indexed abstract describes HEP. No numerical finding is attributed to it in the design. |
| [Sweetser and Wyeth, GameFlow, 10.1145/1077246.1077253](https://doi.org/10.1145/1077246.1077253) | **Verified bibliography and indexed abstract; full body UNVERIFIABLE** | Publisher fetch failed. The located [paper abstract](https://www.valuesatplay.org/wp-content/uploads/2007/09/sweetser.pdf) describes eight enjoyment elements and initial expert reviews of two RTS games. This is not broad human validation of an automated judge. |
| [Duan et al. CHI 2024, 10.1145/3613904.3642782 — paper opened](https://people.eecs.berkeley.edu/~bjoern/papers/duan-heuristic-chi2024.pdf) | **Verified** | *Generating Automatic Feedback on UI Mockups with Large Language Models*. Evaluates 51 UIs and studies use with 12 expert designers. A relevant precedent for constrained critique of interface artifacts. |
| [Martínez, Yannakakis and Hallam 2014 — institutional record](https://www.um.edu.mt/library/oar/handle/123456789/29597), [full paper](https://www.um.edu.mt/library/oar/bitstream/123456789/29597/1/Dont_classify_ratings_of_affect_rank_them.pdf) | **Verified** | Matches 10.1109/TAFFC.2014.2352268, *Don’t Classify Ratings of Affect; Rank Them!* Supports ordinal representations for affect modeling. Does not establish universal superiority of arbitrary pairwise study designs. |

Web, documentation, and commercial references:

| Citation and URL opened | Status | Actual content and relevance |
|---|---|---|
| [Booth, *The AI Systems of Left 4 Dead*, Valve](https://steamcdn-a.akamaihd.net/apps/valve/2009/ai_systems_of_l4d_mike_booth.pdf) | **Verified** | Contains the inactivity statement and intensity peaks/valleys. Accurate as a shipped design approach, not validation of decision-density thresholds for RimWorld. |
| [Ars Technica, Claude/Pokémon article](https://arstechnica.com/ai/2025/03/why-anthropics-claude-still-hasnt-beaten-pokemon/) | **Verified, dated secondary report** | Real March 2025 article about Sonnet’s difficulties. It establishes a historical example, not current-model limitations. |
| [Anthropic, visible extended thinking](https://www.anthropic.com/news/visible-extended-thinking) | **Verified** | Real February 2025 post discussing Claude 3.7 and extended thinking, including Pokémon. Product demonstration, not a controlled usability-validation study. |
| [Anthropic vision documentation](https://platform.claude.com/docs/en/build-with-claude/vision) | **Verified, conditional** | The 28×28 patch formula exists. Current documentation gives **2,691 tokens for 1920×1080 on the high-resolution tier**, but **1,560 after downscaling on the standard tier**. Claim 16 must name the model/tier and image-processing path. |
| [NN/g, ten usability heuristics](https://www.nngroup.com/articles/ten-usability-heuristics/) | **Verified** | Correct general heuristic framework. A checklist does not make its application objectively correct. |
| [NN/g, synthetic users](https://www.nngroup.com/articles/synthetic-users/) | **Verified** | Supports the warning about shallow/favorable synthetic feedback and using it for hypotheses. This is practitioner guidance, not a controlled game study. |
| [NN/g, AI simulation studies](https://www.nngroup.com/articles/ai-simulations-studies/) | **Verified; selectively represented** | Reports both promising individual/population prediction with rich human data and failures to reproduce variation. It explicitly says richer contextual information can help. The design should distinguish these settings from Borchers’s novice-reasoning task. |
| [NN/g, digital twins](https://www.nngroup.com/articles/digital-twins/) | **Verified** | Discusses a continuum from generic synthetic users to person-specific models. Does not establish that a few dozen owner rulings create a valid Taste Twin. |
| [Microsoft Clarity semantic metrics](https://learn.microsoft.com/en-us/clarity/insights/semantic-metrics) | **Verified** | Defines clustered rapid clicks and clicks without timely feedback. These are behavioral indicators, not diagnoses of frustration or confusion. |
| [modl.ai](https://modl.ai/) | **Verified marketing claim** | Markets AI agents/analysts for game QA and coverage. No human-fun validation is supplied by the opened page. |
| [nunu.ai](https://nunu.ai/) | **Verified marketing claim** | Markets agents for testing and other tasks. No published felt-experience validation on the opened page. |
| [PlaytestCloud](https://www.playtestcloud.com/) | **Verified** | Offers real-player research and AI-assisted analysis of recordings. The design describes this split accurately. |
| [Razer QA Companion-AI](https://www.razer.com/blog/ai-that-plays-to-test-razer-qa-companion-ai-at-gdc-2026) | **Verified replacement reference; historical 404 UNVERIFIABLE** | A working official page describes the successor to QA Copilot, including visual QA and autonomous test previews. The unidentified original URL’s 404 cannot be checked. Product existence does not establish fun validity. |
| [RimWorld Steam page](https://store.steampowered.com/app/294100/RimWorld/) | **Verified snapshot** | The opened page displays **97% of 120,341 English reviews**. Correct figure. Positive recommendation rates do not make vanilla a usability-negative control. |
| “arXiv: zero RimWorld/LLM colony-sim hits” | **UNVERIFIABLE search claim** | No reproducible query, endpoint, date-specific result, or search log is supplied. Search-result absence is especially sensitive to query construction. |
| “LessWrong blocked” | **UNVERIFIABLE** | No article URL is given. The [homepage opened](https://www.lesswrong.com/); that says nothing about the unidentified historical fetch. |
| “FLE site empty” | **Verified only as a text-extraction observation** | The [project homepage](https://jackhopkins.github.io/factorio-learning-environment/) returned no readable lines, while its [paper PDF opened successfully](https://jackhopkins.github.io/factorio-learning-environment/assets/documents/paper.pdf). Empty extracted text is not evidence of an empty project. |

The repo citations cannot be independently verified from the supplied file:

| Internal evidence cited | Status | What remains unknown |
|---|---|---|
| CLAUDE.md, bridge skills/capability matrix, companion skill, Test Pilot/Ralph briefs, load-round skill | **UNVERIFIABLE** | Actual restrictions, hover support, tool count, cold-load times, and deployment cycle. |
| `canon.yml`, `CANONICAL_SAVE.md`, save file and size | **UNVERIFIABLE** | Claims 10 and the alleged documentation contradiction require those artifacts. |
| Telemetry source, OWNER.jsonl, conversations, walks, art ledger/regression sheets | **UNVERIFIABLE** | Input coverage, counts, label quality, and whether the art pipeline is actually validated. |
| Watchdog item, schedule/revert path, trial metrics and process guard | **UNVERIFIABLE** | Current state, operational meaning, and whether the proposed trial can run. |

These are missing evidence, not established falsehoods. I did not open anything from disk.

**2. The central inference needs correction**

The design correctly distinguishes an agent’s report from a human’s experience. It then sometimes turns that distinction into an impossibility argument.

**A system need not experience boredom to predict a person’s boredom.** Its lack of fatigue is a reason not to treat its own waiting behavior as human evidence. It is not proof that prediction from appropriately validated observations cannot work.

Conversely, state access supplies only part of the “broken as felt” oracle. It can establish what happened. It cannot, by itself, establish what a reasonable player expected, whether feedback was noticeable, or whether the outcome mattered.

Two counterexamples:

- A pawn correctly queues a task for tomorrow. Immediate state change is minimal; the interaction is working.
- A machine silently consumes a resource exactly as implemented. The state is correct; the interface may still mislead players about the cost.

There is also relevant literature beyond the design’s search. [Wolterink and Bakkes’s Pac-Man study](https://sander.landofsand.com/publications/3472538.3472566.pdf) collected gameplay and self-report data from 135 participants to predict frustration, while finding that removing self-report features substantially hurt accuracy. [Ali and Thue’s Terraria study](https://ojs.aaai.org/index.php/AIIDE/article/download/36821/38959/40898) uses human-annotated telemetry to detect struggle in unseen players, with results varying by quest. These do not solve RimWorld, but they rebut any broad implication that game-specific frustration/struggle research is absent.

**3. D0–D3: critique and concrete improvements**

**D0 — Human playtesting**

The comparison table’s “main false positive: none” is false. Humans can misremember, misunderstand intended difficulty, dislike the genre, or report a preference as a universal defect. Friends may soften criticism. The owner may unconsciously supply missing knowledge.

“One stranger for two hours beats everything on dull” is plausible for obtaining that stranger’s direct experience, but untested as a comparison of discovery yield. Two hours may never reach the repetitive late-game mechanic.

Improve D0 by making it an actual study:

- Separate an experienced RimWorld player new to the mod from a base-game novice.
- Give each a playable checkpoint and a short neutral orientation to the colony.
- Include one natural-play session and selected later-game checkpoints.
- Record timestamps and ask retrospective questions about specific moments.
- Ask separately: “Were you bored?”, “What were you anticipating?”, and “What would you have preferred to do?”
- Have someone other than the designer initially classify observations.

Budget installation, save preparation, recruiting, recording review, and follow-up. D0 has zero agent tokens, not zero cost.

**D1 — Stranger**

The useful core is **prediction before action**. The claimed causal interpretation is much weaker.

1. **Two-of-three agreement can preserve shared mistakes.** Three copies may all interpret a toggle symbol incorrectly because they share training and visual weaknesses. Fresh context does not make their errors independent.

   Under genuinely independent false alarms with probability \(p\), majority voting yields \(3p^2-2p^3\). With perfectly correlated errors, the rate remains \(p\).

2. **Vanilla does not subtract agent incompetence cleanly.** A mod can use a genuinely confusing vanilla interaction. Equal failure rates then indicate a shared usability problem, not necessarily agent noise. Conversely, a mod control can be less familiar to the model while being clear to people.

3. **The proxy changes the task.** Resolving a coordinate to a nearby valid target can silently repair bad pointing. Direct tool activation can bypass disabled states or event semantics unless faithfully implemented.

4. **Prediction errors include learning.** Discovering that an unfamiliar button opens settings is not automatically a defect. Was the prediction reasonable? Was the surprise recoverable? Did it recur?

5. **Requiring two discoveries loses rare important findings.** A single agent might encounter a destructive confirmation ambiguity that the others never reach.

6. **“Wrong reading versus state” conflates different failures.** Saying “12 meals” when the screen contains “2” could be model OCR failure. The state count could also include items the interface intentionally excludes.

7. **The clocks are undefined.** Ninety wall-clock minutes, ninety simulated minutes, and 300 actions describe different exposures. At 20–40 seconds per step, 300 steps alone take **1.67–3.33 hours**.

Improve D1:

- Replace roaming-first evaluation with **short tasks from multiple checkpoints**.
- Log goal, visible evidence, prediction, action, action acknowledgment, simulation interval, and result.
- Distinguish: “not encountered,” “could not operate instrument,” “misread,” “misunderstood,” and “game violated expectation.”
- Verify actual input delivery before grading the interface.
- Preserve singleton findings; use repetition to assess recurrence rather than erase them.
- Compare the **same mod interaction before and after a minimal UI repair**.
- Use vanilla to calibrate general competence, not veto mod findings.
- Maintain separate discovery and validation sets.

Manual injection is diagnostic but not decisive: the manual could explain the interaction, supply the answer, or simply improve task execution. Those are different effects.

**D2 — Flight Recorder**

D2 is useful infrastructure, but its claimed determinism concerns measurement, not interpretation.

- **No state change does not imply a broken gizmo.** Opening a window, selecting a mode, issuing an already-active command, or queueing asynchronous work can all be legitimate.
- **A red error does not imply a player-visible defect.** Conversely, serious silent failures can produce no red log.
- **Ignored alerts have many causes.** They may be understood and deliberately tolerated.
- **Static texture contrast is not rendered readability.** Background, tint, overlap, UI scaling, selection outlines and localization determine what reaches the screen.
- **Empty descriptions can inherit useful text elsewhere.** Long descriptions can be perfectly appropriate behind an optional information button.
- **A self-running colony is not a self-playing colony.** Colonists do jobs; they do not supply the player’s goals, construction planning, research choices or tactical decisions.
- **Equal wealth does not make colonies comparable.** Difficulty, storyteller, season, pawn skills, technology, threats and queued plans all matter.
- **Death cannot always invalidate a run.** If the product caused the death, discarding it removes the most important observation.

The dull proxy also misses a major form of boredom: **many obligatory decisions with no meaningful alternatives**. Repeatedly authorizing the same chore can be dull despite high decision density. A quiet interval before a dangerous expedition can be absorbing.

Improve D2:

- Start with a small event schema: **intent → accepted/rejected → queued → completed/cancelled → visible feedback**.
- Define expected transitions and deadlines per interaction family.
- Measure actual rendered clipping, font size and visibility at target UI settings.
- Add wall-clock latency, simulation speed, repeated obligatory actions, unresolved goals, and progress toward chosen goals.
- Keep player-specific annotations distinct from automated signals.
- Use controlled scenarios before attempting an autonomous governor.
- Record death as an outcome, then diagnose whether the cause was policy, instrument or product.

“Fully tested by planting each defect” is also wrong: tests demonstrate coverage of the specified rules and seeds, not near-perfect recall of all real experience failures.

**D3 — Taste Twin**

The largest problem is that it mixes three targets:

1. What the owner prefers.
2. Whether design intent is communicated.
3. What an unfamiliar player experiences.

They require different evidence.

An owner who understands a machine can prefer its minimal interface even when newcomers consistently misunderstand it. An owner’s statement that a feature should feel dangerous does not establish that the feature actually creates tension.

Additional failure modes:

- Randomly holding out individual rulings can leak the same mechanic or complaint across train and test.
- Steam/Workshop reviews overrepresent self-selected reviewers and often omit the screen or state needed to explain a complaint.
- Sparse screenshots omit timing, sound, cursor activity and failed attempts.
- A second similar judge can merely endorse the first judge’s story.
- “Already knew” is not a false-positive label.
- A taste filter can suppress precisely the unfamiliar criticism the role is supposed to discover.

Improve D3:

- Rename it **owner-preference assistant** or **intent reviewer**.
- Keep owner preference, observable communication gaps and external-player evidence in separate fields.
- Hold out entire mechanics, sessions and later dates.
- Require timestamps and explicit evidence for each factual claim.
- Allow abstention when film lacks the required view.
- Test against simple baselines: nearest prior ruling, rule-based checklist, and uncalibrated critique.
- Use disagreement to select human review, rather than letting a second judge quietly discard novelty.

Beating baseline on owner-specific dull comparisons would **not contradict** FPS viewer-engagement studies. It would establish a narrower result in another task.

**4. The shared Exam needs redesign**

Several problems could make the Exam reward the wrong system.

| Proposed element | Failure mode | Concrete replacement |
|---|---|---|
| Twelve seeded defects | The seed author can accidentally write defects tailored to the evaluator’s strengths. “Confusing” seeds may not confuse people. | Have humans verify seed effects; include historical defects and unseen mechanisms. Freeze seeds before tuning. |
| Eight of twelve across three runs | Union recall can hide weak individual runs; correlated seeds are not independent Bernoulli trials. | Report per-run recall, union recall, exposure and per-defect recurrence separately. |
| Six fake-defect slots | An unseeded slot can contain a real pre-existing issue. | Adjudicate matched negative scenarios and all reports; do not equate “unseeded” with “defect-free.” |
| More findings/hour than vanilla | Rewards report volume and confounds interface complexity with quality. | Measure confirmed findings per encountered interaction, plus reviewer time and missed historical issues. |
| Twelve of twenty owner “keeps” | Measures owner agreement on selected findings, not population validity or full pipeline precision. | Separate factual correctness, novelty, owner priority and human reproduction. Sample beyond the top-ranked findings. |
| Ten dull pairs, 70% success | Seven of ten has one-sided binomial \(p≈.172\) against independent fair guessing. Related segments make independence weaker. | Treat as exploratory. Collect more independent sessions; allow ties; hold out sessions and report uncertainty. |
| Fit weights and test ranks | Ten pairs cannot support exploratory feature selection, fitting and convincing evaluation. | Freeze a simple score first; collect later data for a genuinely separate test. |
| Capture–recapture \(n_1n_2/m\) | Assumes conditions badly violated by correlated discovery and unequal detectability. With zero overlap it is undefined. | Report observed overlap and coverage. Do not publish a total-unfound estimate without a defensible sampling model. |
| Three fixes within fourteen days | Easy cosmetic findings can beat a difficult, important problem awaiting a fix. | Track accepted novel findings, demonstrated player impact, verification cost and reviewer burden separately from closure. |

The stated Wilson interval for 8/12 is correct: approximately **.391–.862**. Likewise, 12/20 has a broad interval, approximately **.387–.781**, before considering selection and dependence.

The proposed Stage 1 cost also excludes an explicit accounting of control passes, resets, judge calls and validation repetitions. “Mostly cached input” is a billing assumption that must be measured for the actual context-management strategy.

**5. Every starred claim**

| Claim | Verdict | Evidence and consequence |
|---|---|---|
| **1. No opened source validates felt experience in a long-horizon sim** | **Unsupported as a provenance claim; consistent with this audit’s identifiable sources** | The “opened” history is unreliable. I found no direct validation of that exact target among the audited studies. That supports “not demonstrated here,” not a universal absence claim. |
| **2. Engagement judgment is near chance on pairs and rarely above majority** | **True only with scope restrictions** | Wang’s tested pairwise configurations are weak. The design attaches the wrong baseline numbers, and Melhart contains meaningful successes. Both concern FPS viewer annotations, not colony players’ boredom. |
| **3. Bridge has no hover/tooltip read** | **Unsupported** | A grep of an unavailable skill cannot establish absence from the live interface. Requires a capability census and an end-to-end tooltip test. |
| **4. Vanilla plus two-of-three separates agent friction from game friction** | **Unsupported** | Neither controls shared model errors or establishes matched tasks. Equal vanilla/mod failures can be real problems in both. Treat these as diagnostics, not identification. |
| **5. Paused agent can usefully play this save for ninety minutes** | **Unsupported** | No observation of the shipped save is supplied. Paused-benchmark improvements establish possibility, not useful coverage here. Test bounded tasks and exposure first. |
| **6. One real human beats all designs on dull** | **Unsupported comparative claim** | A person supplies direct evidence of their own boredom. No head-to-head yield/cost comparison is supplied, and a short session can miss later repetition. |
| **7. Seeds represent real experience defects** | **Unsupported** | Construction validity is not experience validity. A missing tooltip may matter enormously, or nobody may need it. Validate effects with humans and historical cases. |
| **8. Comparable vanilla+DLC control is feasible** | **Unsupported** | Requires an existing permissible save and a matching protocol. Even if technically feasible, equal wealth/resolution do not establish experimental comparability. |
| **9. Owner will provide one hour of labels** | **Unsupported** | A commitment, not a literature finding. One hour of reviewing reports also does not replace actual player-experience observations. |

For the remaining claims: #16 is conditional on image-processing tier; #22 overgeneralizes an internally inconsistent paper without human correctness validation. The local measurements remain unverifiable. Estimates in #15, #17 and #19 should remain explicitly estimates.

**6. Options missed**

The design treats autonomous play, telemetry and personalized criticism as more mutually exclusive than necessary.

- **Cognitive walkthroughs:** At each step, inspect whether the goal, available action and resulting feedback are discoverable. This can find communication gaps without pretending to simulate a whole human.
- **Checkpoint libraries:** Start directly before unfamiliar mechanics, midgame bottlenecks and repeated chores. This avoids paying repeatedly for the opening hour.
- **Minimal UI interventions:** Change only the label, disabled-state explanation or feedback. Compare whether misunderstanding decreases.
- **Human predictions from screenshots:** Ask unfamiliar humans what a control will do before letting them use it. This directly tests D1’s proposed prediction signal at low playtime cost.
- **Accessibility and localization review:** Test actual fonts, UI scales, translated strings, color dependence and clutter. Model transcription is only one detector.
- **Human-annotated telemetry models:** Terraria’s struggle work illustrates this middle ground between arbitrary heuristics and synthetic participants. It needs local labels, but not necessarily a giant review corpus.
- **Validated human questionnaires:** Criticism of GEQ does not eliminate instruments such as the Player Experience Inventory. PREFER itself references alternatives; question selection should follow the construct being measured.
- **Coverage-oriented procedural agents:** Different explicit goals and path-diversity policies can explore mechanics without claiming that prompted personas reproduce feelings.
- **Reusable behavioral scaffolds:** Vox Deorum’s separation of high-level decisions from execution suggests avoiding expensive pixel operation where it does not contribute to the question being tested.

**7. D4 — the design I would build**

**Build an experience auditor around short, reproducible episodes and causal checks.**

An episode begins at a saved checkpoint, with a player goal and a fixed observation/input channel. It ends at success, abandonment or a bounded budget.

The sequence:

1. **Capture the player view.** Screenshot, tooltip, relevant audio/event timing, UI scale and visible feedback.
2. **Record a prediction.** “What will this do, and what visible result should follow?” Allow uncertainty.
3. **Verify execution independently.** Establish whether the input was delivered, accepted, queued and completed.
4. **Produce an evidence packet.** Before/after views, prediction, trace, observed consequence and reproduction steps.
5. **Try one narrow repair.** Add a clearer label or rejection explanation while keeping the mechanic unchanged.
6. **Retest with fresh agents and selected humans.** Keep operational improvement and human validation separate.
7. **Preserve uncertainty.** Report “agent-only,” “human reproduced,” “mechanism confirmed,” and “owner preference” as distinct evidence.

Example:

> At the “Connect winch” checkpoint, the command was accepted but no connection formed. The trace shows “outside range”; the interface displayed no rejection reason. Adding the range explanation resolved agent retries. Two unfamiliar human testers also identified the original feedback gap.

That supports an actionable communication finding without requiring a claim that the agent felt confused.

For dullness, collect **actual-session reports** alongside repeated-work and progress signals. A useful prompt is: “At this moment, did you want to continue, speed through, change goals, or stop—and why?” Have the agent locate and summarize candidate spans. Learn personal predictions only when later held-out sessions justify them.

D4 is the strongest option **for this project’s stated constraints**, because it:

- Uses short bridge windows and multiple game stages.
- Produces attributable findings rather than free-form impressions.
- Tests the interface change implicated by the diagnosis.
- Gives humans small, targeted validation tasks.
- Retains useful output even if autonomous player fidelity fails.

It sacrifices some naturalistic discovery. Keep occasional human free play to cover that gap.

**My build order is decisive:** lightweight D2 traces and rendered checks; a checkpoint library; bounded D1 prediction tasks; targeted D0 sessions; then optional D3 assistance with retrieval and report preparation. Defer the governor and Taste Twin until simpler methods demonstrate a need.

Judge the system by **confirmed novel problems found per unit of total review and execution cost**, with human reproduction tracked separately. Its strongest role is supplying precise evidence about what the interface communicates and where action breaks down. Claims about felt boredom should be earned on actual players and actual sessions.