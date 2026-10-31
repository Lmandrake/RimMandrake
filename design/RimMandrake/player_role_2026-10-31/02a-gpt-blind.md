# GPT blind pass (02a)

Consult id: consult-20261031-100800-3127192 (gpt_consult.py, model gpt-6.1-sol, web on, answered in 389s). Prompt sent verbatim as given by the Conductor. Answer verbatim below.

---

Yes. **A useful agent is feasible; a trustworthy claim that it measures human fun requires validation on your players.** I would build it as a player-experience scout that plays the shipped save and produces evidence-backed accounts of friction.

The crucial distinction is between three abilities:

1. Playing competently enough to encounter the game.
2. Detecting situations that could impair player experience.
3. Predicting how actual players experience those situations.

Research supports the first two much more strongly than the third. Difficulty prediction has some good human comparisons. Boredom, attachment, anticipation and the satisfaction of long-term plans remain substantially harder.

My recommendation is a constrained, visually grounded LLM player, calibrated against human sessions. Its output should say **what happened, what understanding or intention it obstructed, and how strong the evidence is**.

The definitions, architecture and validation plan below are my proposals. The research findings are cited separately. I have not inspected or played your save.

**Give the four words operational meanings.**

These should be overlapping labels for episodes, rather than four scores assigned to the whole game.

| Word | Operational meaning | Evidence the agent should collect | Main alternative explanation |
|---|---|---|---|
| **Confusing** | The player cannot form or repair a useful understanding of what to do, why something happened, or how a rule works. | A stated expectation; contradictory feedback; unsuccessful attempts to resolve the contradiction through available UI; resulting delay, mistake or abandonment. | Productive discovery, deliberate mystery, or the agent misunderstanding something ordinary players understand. |
| **Dull** | Continuing an activity offers insufficient valued choice, learning, anticipation or payoff for the attention it demands. | Extended sequences of equivalent decisions, repetitive maintenance, compulsory waiting, or progress disconnected from the player’s chosen purpose. | Peaceful planning, suspense, attachment, or satisfying routine that the model cannot appreciate. |
| **Unreadable** | Relevant information exists but cannot practically be perceived, distinguished, located or tracked when needed. | Screenshots or video showing overlap, truncation, weak differentiation, fleeting feedback, excessive competing signals, or an action whose result cannot be followed. | Model vision/OCR limitations, screenshot scaling, or an unsuitable capture interval. |
| **Broken, as felt** | A reasonable player intention meets behavior that appears inconsistent, unresponsive or impossible to recover from. | The intention, available action, visible preconditions, attempted action and observable failure; preferably a repeatable sequence. | An undiscovered rule, legitimate randomness, slow simulation, or a bridge failure. |

**Confusing needs a record of expectations.** Before an uncertain action, have the agent briefly record: “I expect X because the interface says Y.” Afterward, record the result and what evidence changed its understanding. This makes an explanation failure distinguishable from retrospective criticism.

For example, “I could not determine why this workstation would not produce the item after checking its bill and the worker’s available information” is useful. “The production system is unintuitive” is weak. A player may eventually learn the answer and still have encountered a real problem; record the cost of reaching understanding.

Confusion also need not be undesirable. A 2025 exploratory study collected minute-by-minute affect reports from 40 players of an intentionally confusing prototype and found confusion occurring alongside engagement. Its small, purpose-built setting limits generalization, but supports evaluating **recovery and consequences**, rather than reporting every uncertainty as a defect. [Volden et al., *On the dynamics of affective states during play and the role of confusion*](https://arxiv.org/abs/2507.03391)

**Dull needs a purpose and a timescale.** Count meaningful decisions relative to what the player is trying to achieve. Repeated clicks are not automatically dull; a quiet colony is not automatically dull; a disastrous outcome is not automatically bad.

Useful candidate signals include:

- Repeating a solved procedure without variation or delegation.
- Waiting that requires supervision but offers little intervention.
- Repeatedly opening the same information because the game fails to preserve it.
- Progress that produces another quantitatively larger version of the same obligation.
- Long stretches with no development in a goal, relationship, uncertainty or plan the player values.

These remain hypotheses about boredom. Human boredom research associates it with failures of both attention and meaning, including **overload as well as understimulation**. That undermines a simple “few events means boring” detector. [Westgate and Wilson, 2018, *Boring thoughts and bored minds*](https://doi.org/10.1037/rev0000097)

For RimWorld, retain a running account of plans, threats, relationships and expected payoffs. A construction delay can sustain anticipation; a hundred incidents can become tiresome interruption. A model that only counts novelty will get both wrong.

**Unreadable needs perceptual evidence.** Separate:

- Can the information be seen?
- Can competing signals be distinguished?
- Can the relevant information be found?
- Can the player follow the relationship between an action and its outcome?

Test at the intended resolution, UI scale and ordinary zoom. Preserve the complete screen alongside crops. Successful OCR does not establish human readability, and failed OCR does not establish unreadability. Claims about human search time or visual accessibility need human confirmation.

**Broken needs a player-visible contract.** The contract can come from a label, tooltip, prior behavior or an ordinary interaction convention. An internal exception matters to this role only when it has an observable consequence.

Thus “the order appears accepted, but nothing changes and no reason is shown” can be a legitimate finding even before its cause is known. “Mod X throws an exception” belongs elsewhere unless the player encounters its effects.

**The literature supports this role, with important limits on what was actually validated.**

The strongest studies distinguish behavioral resemblance, task performance and subjective experience. They are different validation targets.

| Automated playtesting and player modelling | What was compared with humans | What it establishes—and what it leaves open |
|---|---|---|
| **Sweetser and Wyeth, 2005, GameFlow; Desurvire and Wiberg, 2009, PLAY.** Heuristics cover goals, feedback, control, challenge and related concerns. | GameFlow initially used expert reviews of two differently rated RTS games. PLAY had 54 gamers rate high- and low-ranked games against 116 candidate heuristics. | Useful inspection vocabulary. Neither establishes that an autonomous agent can predict individual enjoyment. [GameFlow](https://doi.org/10.1145/1077246.1077253), [PLAY](https://citeseerx.ist.psu.edu/document?doi=f3c116678ad19784b4db8c11b26eaaef8dac48f5&repid=rep1&type=pdf) |
| **Pedersen, Togelius and Yannakakis, 2009; Yannakakis and Togelius, 2011.** Learn experience models from play and use them to evaluate or generate content. | The Mario study used 480 human sessions and reported preferences. Reported prediction accuracy was approximately 69% for fun, 78% for challenge and 89% for frustration. | Experience prediction can work within a constrained game and measured population. Those accuracies do not transfer to another genre or modpack. The later EDPCG paper provides the broader framework. [Mario study](https://doi.org/10.1109/CIG.2009.5286482), [EDPCG](https://yannakakis.net/wp-content/uploads/2019/02/EDPCG.pdf) |
| **Holmgård et al., 2016, Personas versus Clones; 2018, procedural personas through MCTS.** Agents pursue different utilities and therefore traverse content differently. | The 2016 work compared agents with 38 humans’ MiniDungeons traces at action, tactical and strategic levels. The 2018 experiments explicitly did **not** include human players. | Persona diversity can be operationalized through behavior. The 2016 validation concerned decisions, not enjoyment; the 2018 results establish designer-specified archetypes rather than human fidelity. [2016 paper](https://www.antoniosliapis.com/papers/evolving_models_of_player_decision_making.pdf), [2018 paper](https://arxiv.org/abs/1802.06881) |
| **Gudmundsson et al., 2018, Human-Like Playtesting with Deep Learning.** Learn Candy Crush actions from player data. | Compared predicted level difficulty against actual player difficulty in Candy Crush Saga and Soda Saga; improved correlation over MCTS. | Strong industrial evidence for a calibrated, narrow behavioral proxy. Pass rates still do not measure whether a level feels satisfying or tedious. [Paper](https://doi.org/10.1109/CIG.2018.8490442) |
| **Zook, Fruchter and Riedl, 2014, active-learning playtesting.** Select informative parameter settings for human tests. | Difficulty experiments used data from 138 players; preference analysis used 416 paired control comparisons from 47 players. Evaluated learning strategies through cross-validation. | Automation can reduce the human feedback needed to tune difficulty and controls. It depends on human judgments rather than manufacturing them. [Paper](https://sites.cc.gatech.edu/fac/riedl/pubs/zook-fdg14.pdf) |
| **Ariyurek, Betin-Can and Surer, 2019, synthetic and human-like testing agents.** Learn test goals from human trajectories. | Used 427 trajectories from 15 participants across three games, with 45 injected bugs; compared bug finding and behavioral similarity. | Human-like agents can find bugs and improve coverage. The validation target was testing behavior and fault discovery, not boredom or enjoyment. [Paper](https://arxiv.org/abs/1906.00317) |
| **Ansari et al., 2023/2024, PX-MBT.** Combine model-based tests with computational emotion appraisal and temporal requirements. | The 2023 evaluation used mutation testing and comparisons between generated test suites; it did not establish agreement with actual players’ emotional reports. | A practical architecture for checking declared experience patterns. A simulated “hope” or “distress” variable remains a model assumption until validated. [FASE paper](https://doi.org/10.1007/978-3-031-30826-0_9), [framework](https://github.com/iv4xr-project/eplaytesting-pipeline) |

This makes persona agents useful for **encounter coverage**: a cautious builder, curious explorer and production optimizer will meet different problems. It does not justify treating their opinions as a representative player panel.

LLMs add flexible interpretation and long-horizon action, but playing benchmarks mostly validate their ability to act.

| LLM game-playing research | Validation against people | Implication for your agent |
|---|---|---|
| **Voyager, 2023; Cradle, 2024.** Voyager develops reusable Minecraft skills through code; Cradle acts through screenshots and keyboard/mouse across commercial games. | Evaluated chiefly through achievements, task completion, exploration and agent ablations. Neither validates an enjoyment predictor against human players. | They support feasibility of exploration, memory and control. Their success metrics cannot serve as fun metrics. [Voyager](https://arxiv.org/abs/2305.16291), [Cradle](https://baai-agents.github.io/Cradle/) |
| **BALROG, ICLR 2025.** Evaluates agentic reasoning across games of widely differing difficulty. | Uses game progress; its NetHack progression metric is informed by human gameplay data. It does not compare agents’ felt difficulty or enjoyment with player reports. | Agent failure can originate in perception, memory or planning. A difficult encounter for the agent is not automatically a design flaw. The paper’s results describe the tested models, not a permanent capability ceiling. [Paper](https://arxiv.org/abs/2411.13543) |
| **Xiao and Yang, 2024, measuring difficulty with LLM agents.** Tests Wordle and Slay the Spire. | Compared performance with human gameplay-derived difficulty. Best reported correlations included \(r=.624\) for Wordle and up to \(r=.871\) for Slay the Spire. | Encouraging direct evidence for relative difficulty estimation. The study focuses on isolated challenges, leaving cumulative history, player learning and broader experience open. [Paper](https://arxiv.org/abs/2410.02829) |
| **Huang et al., 2026, PlaytestArena/Play2Code — preprint.** GUI agents play generated browser games and supply refinement feedback. | On 32 games, reported GUI–human rubric agreement was 84.2%, versus 90.7% human–human. Also compared refinement with reports from five human annotators. | Interaction exposes failures missed by code inspection. The rubric agreement concerns expected game behaviors; it does not establish equivalent boredom or aesthetic judgment. Complex games remained a bottleneck. [Paper](https://arxiv.org/abs/2605.28258) |

One especially relevant failure comes from **behavioral imitation**. A Bleeding Edge study analyzed more than 100,000 human games and found substantial differences between human and transformer-agent behavior: agents disproportionately played solo and did not reproduce human variation along interpretable behavioral dimensions. Learning from human actions did not automatically preserve human play patterns. [*Toward Human-AI Alignment in Large-Scale Multi-Player Games*, 2024](https://arxiv.org/abs/2402.03575)

**Game-feel research argues against simple proxy scores.**

“More feedback” is not a dependable rule. Hicks et al.’s 2019 juiciness studies used human samples of 40 and 32 across different games. A larger action-RPG experiment with 3,018 participants found that both absent and extreme juiciness performed worse than intermediate conditions on several experience and behavioral measures. These are human experiments, not automated judges. [Hicks et al., *Juicy Game Design*](https://doi.org/10.1145/3311350.3347171), [*The effects of juiciness in an action RPG*](https://doi.org/10.1016/j.entcom.2020.100359)

A preregistered 2024 experiment with 1,699 participants varied feedback properties and measured enjoyment, motivation and free-choice playtime. Success-dependent feedback helped, while amplification unexpectedly reduced the measured motives in the tested implementation. The authors connect positive experience to legible action–outcome relationships and graded success. That is useful guidance for your “unreadable” and “broken as felt” categories, but still needs testing in a colony-management context. [Kao et al., *How does Juicy Game Feedback Motivate?*](https://doi.org/10.1145/3613904.3642656)

Likewise, predicting affect from gameplay pixels is possible within datasets, but the target matters. *From Pixels to Affect* evaluated arousal classification using 50 annotated gameplay videos and leave-one-video-out validation. **Arousal is not enjoyment**: boredom, frustration and satisfaction cannot be recovered merely by detecting visual activity. [Makantasis et al., 2019](https://arxiv.org/abs/1907.02288)

For human calibration, the **Player Experience Inventory** is useful because it separates functional consequences—control, feedback, clarity, challenge and audiovisual appeal—from psychosocial experiences such as curiosity, mastery, autonomy, immersion and meaning. Its development included expert input and five subsequent studies totaling 529 players. It validates a human questionnaire, not answers generated by an LLM. Preserve the instrument’s wording and scoring if claiming its validation. [Vanden Abeele et al., 2020](https://doi.org/10.1016/j.ijhcs.2019.102370), [usage guidance](https://playerexperienceinventory.org/docs)

**LLM UX evaluation has promising results and substantial failures.**

| Study | Human comparison and result | Limit |
|---|---|---|
| **Zhong, McDonald and Hsieh, 2025, Synthetic Heuristic Evaluation — preprint.** | Across two apps, synthetic evaluation identified 73% and 77% of the compiled heuristic issues, compared with 57% and 63% for the human evaluator condition. | The reference set combined AI and expert findings. This is expert heuristic agreement, not demonstrated impact on end users. The model struggled with UI conventions and cross-screen relationships. [Paper](https://arxiv.org/abs/2507.02306) |
| **Ebrahimi Pourasad and Maalej, 2024, UX-LLM — preprint.** | Compared two apps with usability tests involving ten participants per app and expert assessment. Reported precision .61–.66 and recall .35–.38. | Useful findings, but missed most reference issues. Also used source-code access, which can reveal paths a player has not encountered. [Paper](https://arxiv.org/abs/2411.00634) |
| **Bougie et al., 2026, PerceptUI — preprint.** | Evaluated against A/B-test outcomes, human design preferences, aesthetics ratings and participant-level interface responses. Specialized training improved results; zero-shot models showed pronounced input-order bias on design selection. | Stronger than judging explanations for plausibility, but static and task-specific UI predictions do not validate a long-form game experience model. [Paper](https://arxiv.org/abs/2606.05697) |
| **Avenir UX, 2026, benchmark proposal.** | Describes matched human–agent comparison using task-level usability ratings, step-level ease ratings and think-aloud transcripts. | The project page’s preliminary results are agent pilots preceding the full human study. They should not be cited as completed human validation. Semantic similarity of commentary also need not mean the same friction occurred. [Project and protocol](https://onflow-ai.github.io/Avenir-UX/) |

The synthetic-user literature supplies a particularly important warning: **convincing testimony is easy to mistake for valid testimony.**

- **Hämäläinen, Tavast and Kunnari, CHI 2023:** compared generated accounts of games-as-art with 178 actual responses. Generated text was highly convincing to human raters, yet included invented gameplay and reduced diversity. One model variant mentioned *Journey* in 151 of 178 responses, versus seven human responses. This is unusually direct evidence that plausible experience reports can be misleading. [Paper](https://doi.org/10.1145/3544548.3580688)
- **Park et al., UIST 2023, Generative Agents:** human evaluators judged believable behavior in a 25-agent social sandbox, with architecture ablations. That validates perceived believability, not correspondence with real players’ preferences. [Paper](https://arxiv.org/abs/2304.03442)
- **Park et al., 2024, simulations of 1,052 people:** grounding agents in interviews produced survey answers approximately 85% as accurate as participants’ own two-week repeat answers. This is a relative test–retest comparison, not 85% universal human accuracy, and it was not a game-experience study. It supports learning from actual individuals rather than assigning generic personas. [Paper](https://arxiv.org/abs/2411.10109)
- **Gao et al., PNAS 2025:** compared LLM choices with human behavior in a simple money-request game, including 143 newly recruited participants. Roles, language and examples substantially changed model distributions; demographic prompting did not repair alignment. [Paper](https://doi.org/10.1073/pnas.2501660122)
- **Chen et al., July 2026 — preprint:** benchmarked demographic-prompted synthetic respondents against held-out human social-attitude and cross-cultural survey data. Models failed to outperform strong non-LLM individual-prediction baselines and exaggerated demographic differences. This concerns the tested survey protocols, not every possible learned simulator. [Paper](https://arxiv.org/abs/2607.26348)

Together, these findings favor behavioral personas such as “new to this pack, seeks colony stability, explores cautiously” over elaborate demographic biographies. Persona diversity should be checked in actual actions, discoveries and recovery strategies.

**Commercial tools demonstrate practical workflows, with limited public evidence for fun prediction.**

| Tool | Publicly described capability | Human-validation status relevant here |
|---|---|---|
| **modl.ai** | Visual agents execute tasks and report visual, performance and logic problems with evidence. | Its documentation describes functional QA and acknowledges limits around skill and intuition; the cited page supplies no human-enjoyment validation. [Product documentation](https://modl.ai/) |
| **Regression Games** | Bot framework, replay and validation infrastructure for automated game testing. | Useful infrastructure; its documentation does not establish subjective-experience prediction against players. [Documentation](https://docs.regression.gg/what-is-regression-games) |
| **Ravensight AI Playtest** | Persona runs against local builds, with screenshots and structured findings. | Closely resembles your proposed workflow. Its public page explicitly presents the reports as supplementary to human playtesting and provides no quantified human-comparison study. [Product page](https://ravensight.io/ai-playtesting/) |
| **Synthetic Users** | Grounds synthetic participants in customer material such as interviews and support data. | Grounding is relevant, but the cited vendor FAQ does not establish validity for gameplay, boredom or emergent narrative. [Vendor FAQ](https://www.syntheticusers.com/faqs) |
| **PlaytestCloud First Findings** | AI analyzes actual players’ think-aloud transcripts and survey responses. | The experience evidence originates with humans. Its help page explains inputs and workflow, but does not itself provide a blinded accuracy study of the analysis. [Documentation](https://help.playtestcloud.com/en/articles/7941599-how-does-first-findings-ai-powered-analysis-work) |

The commercially mature pattern is automated encounter generation, evidence capture and analysis. The public material reviewed does not establish a validated fun oracle for heavily modded RimWorld.

**Your bridge should enforce the player’s information boundary.**

This is the most consequential implementation choice.

The agent should load a copy of the actual shipped save, with the shipped mod order, settings, interface and onboarding. Give it the knowledge your intended player has: for example, “experienced in RimWorld, unfamiliar with this modpack.” Keep fresh-player and returning-player sessions separate.

Then constrain its inputs and actions:

- **Expose information through the same discovery path available to players.** A state field buried behind several windows should not appear automatically in the agent’s summary. Tooltips require hovering; hidden mechanics remain hidden.
- **Use screenshots for visual claims.** Structured state can help maintain continuity, but cannot establish that an alert was noticeable or a panel readable.
- **Make bridge actions player-equivalent.** A direct “configure production” command bypasses menu discovery, click burden and feedback. Either exercise the UI or explicitly mark those aspects unevaluated.
- **Separate game time, interface latency and model deliberation.** A slow model response is not game tedium. A paused simulation while the model thinks cannot test real-time interruption load.
- **Preserve ordinary play.** Let it choose valued goals and respond to events. Rewarding issue count encourages contrived mistakes and complaint generation.
- **Keep developer knowledge out of the player’s memory.** Other roles may diagnose a finding afterward; their explanations should not retroactively erase the encounter.
- **Capture temporal evidence.** Screenshots alone miss fleeting messages, stutter and action feedback. Without audio capture and analysis, auditory feel remains unevaluated.

An LLM’s prior RimWorld knowledge cannot reliably be erased by declaring it a novice. Treat the expertise profile as an experimental condition whose behavior must be checked.

**Three genuinely different designs fit your setup.**

| Design | How it plays and judges | Advantages | Costs and failure modes |
|---|---|---|---|
| **1. Situated LLM player** | Plays from screenshots and constrained observations. Maintains goals, expectations and an encounter diary. Flags friction from witnessed episodes and attempts ordinary recovery. | Fastest route using your existing bridge; flexible with unfamiliar mods; useful explanations; can notice unexpected combinations. | Model-specific perception and knowledge; inconsistent judgments; persuasive invented rationale; weak boredom validity. |
| **2. Model-based experience monitor** | A planner or utility-driven persona plays. Explicit monitors detect patterns such as unexplained rejected actions, repeated equivalent chores, unavailable goal paths or excessive competing alerts. | Repeatable, inspectable, inexpensive to rerun; excellent for tracking established problems across builds. | Substantial authoring; only detects formalized concerns; easily equates designer expectations with player experience. Its simulated emotion variables need external validation. |
| **3. Empirically learned synthetic players** | Learn policies and experience predictors from human play traces, screenshots, goals and episode ratings. Agents play new build/save copies; uncertainty selects episodes for additional human testing. | Best prospect for population-specific predictions and differentiated playstyles; confidence can be evaluated empirically. | Highest data and maintenance cost; mod changes cause distribution shift; behavior cloning can drift; rare experiences remain poorly represented. |

These differ in the **source of judgment**: general model interpretation, authored experience rules, or learned human evidence. Merely giving three LLMs different personalities would not provide this architectural diversity.

**I would start with design 1, with a strict evidence gate and human calibration.**

Your infrastructure already makes ordinary play possible. The main unanswered question is whether this new role adds useful findings. Building a large experience model before answering that question would be premature.

Use a small set of behaviorally distinct runs: someone new to the pack seeking stability, an exploratory builder, and an experienced optimizer, for example. These are coverage strategies, not estimates of audience prevalence.

Each finding should contain:

> **Confusing — production stalled without an explanation I could find.**  
> **Intent:** Produce the item needed for my current construction plan.  
> **Encounter:** The bill remained active; I checked the workstation and worker information available through the interface but could not identify the blocker.  
> **Consequence:** I abandoned the construction plan after repeated attempts.  
> **Evidence:** Timestamped interaction sequence and screenshots.  
> **Confidence:** Strong evidence of this agent’s impasse; human confusion remains unconfirmed.

That is an illustrative format, not a finding about your save.

For dullness, prefer “this sequence repeated the same solved maintenance task with no change in my plan” over a fabricated assertion of felt boredom. Human confirmation can later strengthen the label.

Keep root-cause hypotheses and proposed fixes out of this role’s report. The requested product is the encounter. The agent should be allowed to report no findings; successful completion should never force a complaint.

**Validate the role on encounters, then validate its usefulness.**

I would run a staged pilot:

1. **Collect real play before showing agent reports.** Recruit intended players with recorded base-game and modpack familiarity. Use the same shipped save and interface conditions. Include ordinary free play and several longer or returning sessions; a short onboarding test cannot assess narrative attachment or accumulated chores.
2. **Obtain independent experience evidence.** Record gameplay, brief contemporaneous comments where appropriate, and retrospective episode review. Ask whether moments were confusing, dull, unreadable or felt broken without first suggesting the agent’s interpretation. Use PXI alongside these episode questions if broader measurement helps.
3. **Calibrate on one set and evaluate on held-out players and sessions.** Splitting adjacent screenshots from the same session between training and evaluation would exaggerate generalization. Later, test another build or save progression state.
4. **Measure each category separately.** Track human confirmation of reported issues, human-discovered issues missed by the agent, encounter opportunities, severity agreement, unsupported claims and review time. Include unflagged episodes so evaluation can expose false negatives.
5. **Compare against cheap alternatives.** A screenshot heuristic review, your existing functional agents, simple telemetry rules and human testing alone are meaningful baselines. Several agreeing LLMs are not independent human validation.
6. **Test consequential fixes with new players.** If a finding leads to a change, assess whether the relevant experience improves without damaging discovery, autonomy or pacing. Prediction agreement alone does not prove that acting on the report helps.

A modest pilot can establish whether the role earns its review cost; it cannot establish precise audience-wide boredom rates. Report uncertainty and human disagreement rather than combining everything into one “fun score.”

**The success criterion I would use is: does this role repeatedly find consequential player encounters that your existing agents miss, and do real players corroborate them?** That is achievable, testable, and directly aligned with the gap you described.