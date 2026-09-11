# Saved notes — PCG evaluation metrics & automated/agent playtesting

Compiled 2026-09-11 by the METRICS research agent. These are extracted abstracts and
findings read via WebFetch (arXiv abstract pages / export API, arXiv HTML full text,
OpenAlex bibliographic API) and ACM DOI resolution through OpenAlex. Where the full
paper was not read, that is stated. Every entry below was independently verified this
session against a real DOI/arXiv ID — none of these are guessed.

---

## Withington, Cook & Tokarchuk (2024) — "On the Evaluation of Procedural Level
Generation Systems: A Systematic Review" — arXiv:2404.18657 (FULL TEXT read via
arxiv.org/html/2404.18657)

**Taxonomy of PCG evaluation approaches (4 axes):**
1. Data Collection Method — calculated from representation directly / simulated play
   by agents / evaluated through play or observed play by humans / mixed-initiative.
2. Metrics and Features Calculated.
3. Point of Comparison — vs. no-algorithm baseline, vs. prior published systems, etc.
4. Game Domain.

**Metrics/features named:** Level Fitness (quantifiable heuristics), Solvability &
Win Rate (binary or continuous), Validated Questionnaire (they explicitly name GEQ
and the System Usability Scale as examples of validated instruments used in this
literature), Custom/non-validated questionnaires, Biological readings (eye tracking,
heart rate), Computational resource usage, Qualitative visual traits, Similarity to
training data, Metric Diversity (stdev / KL-divergence across a metric), Expressive
Range Analysis (2D plot showing diversity + coverage of the generator's output
space), Controllability, Performance as an agent-training curriculum.

**Numeric findings from their survey (CONFIRMED, read from the paper):**
- Reviewed 86 papers presenting novel PCG systems, drawn from 142 initial search hits.
- Only 5 of 137 [sic, their count across a related pool] papers were evaluation-free
  system descriptions — i.e., nearly everyone attempts *some* evaluation.
- Direct-representation-calculated metrics: 37 instances (the single most common
  method) — this is exactly the "computable from a map file" category we most want.
- Human playtesting: 27 instances.
- Comparison against prior published work: only 11 instances (rare — the field
  under-compares to itself, a reproducibility problem).
- Fitness-function-style metrics: 33 instances (most frequent metric family).
- Custom/original game domains: 47 of 86 papers (>half) — Mario AI Benchmark and
  GVGAI are the main points of standardization where they exist.

**Their recommendations:** (1) it's OK to publish an evaluation-free system
description when there's no comparable baseline yet, rather than force a weak
comparison; (2) build more diverse research frameworks, esp. for 3D domains
(cite Minecraft GDMC competition as the model); (3) reuse code/methodology instead
of re-deriving evaluation from scratch each paper.

**Relevance to RimMaster:** this is the single best "state of the field" pointer —
it says outright that metrics computed directly from the level representation are
already the most common evaluation method in the PCG literature, which validates
the brief's instinct to prioritize map-file-computable metrics.

---

## Smith & Whitehead (2010) — "Analyzing the Expressive Range of a Level Generator"
— Proc. 2010 Workshop on Procedural Content Generation in Games, ACM.
DOI: 10.1145/1814256.1814260. (Abstract only, via OpenAlex/ACM metadata.)

Foundational paper. Argues generator quality should be judged by the *variety* of
levels it can produce as its parameters vary — not output quantity or generation
speed. Applied to "Launchpad," a 2D platformer generator. Demonstrates the method
can "expose unexpected biases in algorithm design." This is the origin of
"Expressive Range Analysis" (ERA) as a named technique.

## Summerville (2018) — "Expanding Expressive Range: Evaluation Methodologies for
Procedural Content Generation" — Proc. AIIDE 2018, Vol. 14.
DOI: 10.1609/aiide.v14i1.13012. (Abstract only.)

Follow-on/extension paper; argues the field still lacks standardized evaluation
despite PCG's age and the rise of PCGML (ML-driven PCG), and proposes additional
analysis techniques.

---

## Horn, Dahlskog, Shaker, Smith & Togelius (2014) — "A Comparative Evaluation of
Procedural Level Generators in the Mario AI Framework" — Proc. FDG 2014. (Abstract
only — full text NOT read this session; could not resolve a working open-access
copy through ResearchGate [blocked, 403] or Semantic Scholar [rate-limited, 429].)

Compares 7 Mario level generators against original SMB levels using 6 metrics,
including "two novel expressivity measures." **"Leniency" and "linearity" as named
Mario-level metrics trace to this paper's lineage** (and/or Smith/Whitehead's earlier
Launchpad work), but THE EXACT FORMULAS WERE NOT VERIFIED THIS SESSION — do not
treat any specific leniency/linearity formula as sourced until the primary text (or
a paper that quotes it verbatim) is actually read. Treat the metric NAMES as real
and citable; treat any formula for them as UNVERIFIED.

## Mariño, Reis & Lelis (2015) — "An Empirical Evaluation of Evaluation Metrics of
Procedurally Generated Mario Levels" — Proc. AIIDE 2015, Vol. 11.
DOI: 10.1609/aiide.v11i1.12785. (Full abstract read verbatim.)

**Direct critique of leniency/linearity as sole evaluation tools.** Ran a systematic
user study comparing insights from computational metrics vs. actual player
perception of PCG Mario levels. Verbatim conclusion: "current computational metrics
should not be used in lieu of user studies for evaluating content generated by
computer programs." This is the load-bearing citation for "a map-file metric is not
a substitute for playtesting — it's a cheap pre-filter."

## Hervé & Salge (2021) — "Comparing PCG metrics with Human Evaluation in Minecraft
Settlement Generation" — arXiv:2107.02457. (Full abstract read verbatim.)

Adapted existing PCG metrics + new ones to Minecraft settlements, correlated against
existing human evaluation scores. Found real but partial correlation: metrics that
count specific elements, measure block-type diversity, and measure presence of
crafting materials for complex blocks showed some relationship to human scores.
Selective, not universal, correlation — reinforces Mariño et al.'s caution.

## Rupp, Puddu, Becker-Asano & Eckert (2024) — "It might be balanced, but is it
actually good? An Empirical Evaluation of Game Level Balancing" — arXiv:2407.11396.
(Full abstract read verbatim.)

Tests PCGRL (Procedural Content Generation via Reinforcement Learning)-balanced
levels against real human playtesting across 4 scenarios. PCGRL's own balance
heuristic "neglects actual human perception." Finding: PCGRL-based balancing
"positively influences players' perceived balance for most scenarios, albeit with
differences ... between scenarios" — heuristic balance metrics are directionally
useful but not uniformly reliable, and effect size varies by scenario.

---

## Holmgård, Green, Liapis & Togelius (2018) — "Automated Playtesting with
Procedural Personas through MCTS with Evolved Heuristics" — arXiv:1802.06881.
(Full abstract read verbatim.)

Introduces "procedural personas": archetypal AI player models built by replacing
MCTS's standard UCB1 node-selection rule with an evolved (evolutionary-computation-
derived) heuristic, so each persona embodies a distinct playstyle. Explicitly framed
as building "synthetic playtesters" for use when human feedback isn't available or
when many fast evaluations are needed (e.g. inside a PCG loop). Theoretically
grounded in psychological decision theory (not just an engineering hack).

## Ariyurek, Surer & Betin-Can (2021) — "Playtesting: What is Beyond Personas" —
arXiv:2107.11965. (Full abstract read verbatim.)

Extends procedural personas two ways: (1) "developing personas" that can shift goals
mid-run instead of being locked to one fixed goal; (2) "Alternative Path Finder"
(APF) — trains an RL agent with knowledge of previously-explored paths so it
generates a genuinely different trajectory to the same goal, mimicking how a human
tester avoids repeating an identical playthrough. Uses GVG-AI and VizDoom + PPO.
Finding: developing personas gave better insight into varied playstyles than fixed
procedural personas.

## Roohi, Guckelsberger, Relas, Heiskanen, Takatalo & Hämäläinen (2021) —
"Predicting Game Engagement and Difficulty Using AI Players" — arXiv:2107.12061.
(Abstract paraphrase read — full verbatim not captured.)

Combines Deep RL with MCTS to predict human engagement/difficulty; finds this
combination beats either DRL or plain MCTS alone on the hardest levels, and that
using an agent's BEST-case run (not average performance) as the feature is more
predictive — directly relevant to "which AI-agent statistic should stand in for a
human's experience."

## Cook & Raad (2019) — "Hyperstate Space Graphs for Automated Game Analysis" —
Proc. IEEE Conference on Games (CoG) 2019. DOI: 10.1109/cig.2019.8848026.
(Existence + venue confirmed via OpenAlex; abstract not read this session.)

## Smith, Padget & Vidler (2018) — "Graph-based generation of action-adventure
dungeon levels using answer set programming" — Proc. FDG 2018.
DOI: 10.1145/3235765.3235817. (Existence + one-line abstract snippet confirmed via
OpenAlex; full text not read — ACM DL, likely paywalled.) Directly on-point for
RimMaster's ring-grammar vault dungeons: builds acyclic dungeon graphs by
declarative constraint solving and reports "quantitative expressive analysis"
against gameplay-design constraints. Worth a follow-up read before finalizing a
graph-metric rubric section.

## Dormans (2010) — "Adventures in Level Design: Generating Missions and Spaces for
Action-Adventure Games" — Proc. 2010 Workshop on PCG in Games, ACM.
DOI: 10.1145/1814256.1814257. (Abstract read; full text not captured this session.)

Splits action-adventure level authoring into two separate generative/analytic
structures: the **mission graph** (the abstract graph of goals/keys/locks/challenges
a player must traverse) and the **space graph** (the physical layout realizing that
mission). Uses generative grammars for each. This mission/space split is the
conceptual ancestor of "compute a graph metric on the mission graph" as a
map-file-only technique — directly applicable to RimMaster's ①/②/③ vault ring
grammar (`dungeons_arc_spec.md` §3.3), since the outer/garrison/core rings are
already an authored mission graph in miniature.
