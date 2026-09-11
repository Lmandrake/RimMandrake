# Game design metrics — a catalog, a ranked shortlist, and a rubric for judging one dungeon design

Compiled 2026-09-11 for RimMaster's dungeon-design review problem: given a candidate
dungeon (layout, encounters, loot, event triggers — on paper or walked in-game),
produce a defensible judgment of playability, enjoyability, length, challenge curve,
and tedium, ideally BEFORE a human plays it.

**How to read the markers used throughout:**
- **CONFIRMED** — I read the primary abstract/full text/site myself this session,
  via a real DOI, arXiv ID, or a live URL, and the claim traces to that read.
- **CONFIRMED-VIA-SECONDARY** — I read a tertiary source (mainly Wikipedia) that
  itself cites a primary source; the primary source's existence is real but its
  content was not independently re-verified.
- **UNCERTAIN** — a real named thing (paper, instrument, book) whose existence is
  established but whose specific content (a formula, an item count, a factor
  structure) I could not verify this session. Never treat an UNCERTAIN number as
  safe to paste into a rubric without a follow-up read.
- **UNSOURCED / FOLKLORE** — widely believed in the design community, not chased
  down to a citable source this session. Flagged, not asserted.

Every citation below has a DOI, arXiv ID, or a live URL I actually fetched. Nothing
here is a guessed defName-equivalent: no invented formula, no invented item count,
no invented paper. Where I don't know a number, I say `UNVERIFIED` rather than
supply a plausible-looking one. Full extracted notes with more quotes and context
live in `research/game_design/sources/metrics/` (four files, one per topic
cluster) — this document is the synthesis.

**A tooling note up front, because it shaped what's below:** `WebSearch` is refused
outright for this model group (confirmed: 400 error). Fetcher's own `SEARCH`
directive was degraded for this entire session — queries were effectively
truncated to their first word and matched against ad inventory, not real results
(evidence: querying "MCTS agent playtesting balance level generation" returned
office-furniture retailers). Every real citation in this document instead came from
**WebFetch against arXiv's export API, OpenAlex's bibliographic API (a legitimate,
DOI-backed scholarly database), and direct site fetches** — not from Fetcher SEARCH.
This closed off some leads entirely (Valve/Riot's own published playtest practice,
which lives in blog posts and GDC talks that neither arXiv nor OpenAlex indexes).
Those gaps are named explicitly in §6 rather than papered over.

---

## 1. The catalog

### 1.1 Computable from a map file or static design — no players, no agents

This is the highest-value tier per the brief. It is also, per the single best
survey found this session, already the dominant approach in the PCG-evaluation
literature: Withington, Cook & Tokarchuk (2024, arXiv:2404.18657, **CONFIRMED**,
full text read) surveyed 86 published PCG systems and found **37 of them** computed
metrics directly from the level representation — the single most common evaluation
method, ahead of human playtesting (27) and every agent-based method combined.

| # | Metric | What it measures | Input needed | Validity / status | Source |
|---|---|---|---|---|---|
| 1 | **Solvability / reachability** | Can every required objective actually be reached from the entry, by simple graph search (BFS/A*)? | The map's connectivity graph (walkable tiles/doors/keys) | Folklore-strong, near-universal in practice — Vieira et al. (2026, arXiv:2606.03857) explicitly verify "navigability of generated maps by verifying connectivity using Breadth-First Search (BFS)." **CONFIRMED** existence of this exact technique in a real 2026 paper. | arXiv:2606.03857 |
| 2 | **Graph connectivity metrics** (branching factor, path length, cycle count, dead-end count) | Structural shape of the level as an abstract graph, independent of dressing | A mission/space graph extracted from the map (rooms as nodes, doors/passages as edges) | The generative *ancestor* of this analytic move is Dormans (2010, arXiv-free, DOI 10.1145/1814256.1814257, **CONFIRMED** abstract) — mission graphs (goals/keys/locks) vs. space graphs (physical layout) as two separately analyzable structures. A dedicated evaluation paper exists (Smith, Padget & Vidler 2018, DOI 10.1145/3235765.3235817, **CONFIRMED existence + one-line abstract**, full text not read) doing exactly this for acyclic action-adventure dungeons, with "quantitative expressive analysis." | Dormans 2010; Smith/Padget/Vidler 2018 |
| 3 | **Expressive Range Analysis (ERA)** | Not a single level's score — the *diversity and coverage* of an entire generator's/designer's possible output space, as parameters vary, plotted as a 2D scatter | A family of maps (or a generator that can produce variants), not one map | Origin: Smith & Whitehead (2010, DOI 10.1145/1814256.1814260, **CONFIRMED** abstract). Extended: Summerville (2018 AIIDE, DOI 10.1609/aiide.v14i1.13012, **CONFIRMED** abstract). For RimMaster's *hand-authored, one-map, no-worldgen* doctrine this applies to comparing several **candidate layouts for one dungeon slot** against each other (e.g. the six vaults, or several V1-outer-ring drafts), not to any generator. | Smith & Whitehead 2010; Summerville 2018 |
| 4 | **Leniency / linearity / density** (the "Mario metrics" family) | How forgiving a segment is (leniency); how closely the traversal path hews to a straight line (linearity); how many meaningful elements per unit length (density) | The map's layout + placed content | **NAME CONFIRMED, FORMULA UNVERIFIED.** These metric names trace to Horn, Dahlskog, Shaker, Smith & Togelius (2014 FDG) comparing 7 Mario generators with "6 metrics" including "two novel expressivity measures" — but the paper was paywalled/unreachable this session (ResearchGate 403, Semantic Scholar 429) so **no formula from it should be trusted until it is actually read.** ⚠️ **Directly and empirically challenged**: Mariño, Reis & Lelis (2015 AIIDE, DOI 10.1609/aiide.v11i1.12785, **CONFIRMED**, full abstract read) ran a user study and concluded verbatim that "current computational metrics should not be used in lieu of user studies for evaluating content generated by computer programs." Treat this whole family as a cheap PRE-FILTER, never a verdict. | Horn et al. 2014 (unverified formula); Mariño et al. 2015 (critique, confirmed) |
| 5 | **Metric-vs-human correlation checks** | Whether any computed metric actually tracks human judgment, and how much | A metric + an existing set of human ratings for the same content | Hervé & Salge (2021, arXiv:2107.02457, **CONFIRMED** full abstract): adapting PCG metrics to Minecraft settlements found only *partial, metric-specific* correlation with human scores — element-counting, block-diversity, and crafting-material-presence metrics correlated; others didn't. Rupp et al. (2024, arXiv:2407.11396, **CONFIRMED** full abstract): PCGRL's own heuristic balance metric "positively influences players' perceived balance for most scenarios, albeit with differences... between scenarios" when checked against real human playtesting. **Takeaway with a real number behind it: even the best map-file metrics are directionally right some of the time, not all of the time — budget for at least one human check per metric family before trusting it on a new dungeon type.** | Hervé & Salge 2021; Rupp et al. 2024 |
| 6 | **Metric diversity across a set** (stdev / KL-divergence of a metric over many outputs) | Whether a *set* of dungeons is actually varied, not just individually fine | A metric computed over several candidate maps | Named as a category in Withington et al.'s taxonomy (**CONFIRMED**, read this session) — "Metric Diversity." Useful for RimMaster's six vaults: are V1–V6 actually distinguishable on any computed axis, or do they only differ in flavor text? | Withington et al. 2024 |
| 7 | **Simulated-agent solvability/performance as a curriculum stat** | Whether an AI agent trained/scripted to play can complete the level, and how well, as a stand-in for "is this beatable at all" | A scripted or trained agent + the map | Category named in Withington et al.'s taxonomy: "Performance as Agent Curriculum" (**CONFIRMED**). This sits at the boundary between §1.1 and §1.2 below — technically needs an agent, but the agent can be a simple deterministic solver (A*, not learned), making it nearly as cheap as a pure graph check. | Withington et al. 2024 |

**Ranking within this tier**, by (validity-per-effort) for a hand-authored,
single-map campaign like RimMaster's — this is the METRICS agent's own synthesis,
not a sourced ranking:

1. **Solvability/reachability (BFS/A\*)** — cheapest, hardest to get wrong, and a
   genuine PASS/FAIL floor (a dungeon that cannot be completed as designed is not a
   "tedium" problem, it's a broken one). Should gate every other metric.
2. **Graph connectivity metrics on the mission graph** — RimMaster's ring grammar
   (outer/garrison/core, `dungeons_arc_spec.md` §3.3) is *already* an authored
   mission graph with exactly 3 nodes per vault type; computing branching factor,
   dead-end count, and "is the core reachable ONLY through the garrison ring" (the
   pass bar already written into `dungeons_arc_spec.md` §3.7 step 2: "no gaps
   letting a raider path around the garrison ring entirely") is a direct, cheap,
   almost-free-lunch application of Dormans's split.
3. **Metric-vs-human correlation spot-checks** — not a metric itself, but the
   discipline that keeps 1–4 honest; budget one real playtest per new dungeon
   *type* (not per instance) to calibrate whatever computed metrics get adopted.
4. **Leniency/linearity/density family** — real, cheap, but per Mariño et al.'s own
   empirical finding, not to be trusted alone; use as a same-family comparison tool
   ("is V5's garrison ring denser than V4's, as intended by the owner's "V5 must
   read as a breach, distinct from V4" ruling") rather than an absolute quality
   score.
5. **Expressive Range Analysis** — most valuable when several DRAFT layouts exist
   for the same slot (comparing candidate V1 outer-ring drafts before the owner
   picks one), least valuable once a slot is already down to one authored map.

### 1.2 Requires simulated agents, not human players

| Metric/technique | What it measures | Source | Status |
|---|---|---|---|
| **MCTS "procedural personas"** | Archetypal AI playstyles (built by evolving MCTS's node-selection heuristic instead of using stock UCB1) act as synthetic playtesters, exposing how different play *styles* fare on the same content | Holmgård, Green, Liapis & Togelius (2018), arXiv:1802.06881 | **CONFIRMED**, full abstract read |
| **"Developing personas" + Alternative Path Finder (APF)** | Extends personas to shift goals mid-run, and trains an RL agent aware of previously-explored paths so it finds a genuinely DIFFERENT route to the same goal — mimicking a human who avoids repeating an identical playthrough | Ariyurek, Surer & Betin-Can (2021), arXiv:2107.11965 | **CONFIRMED**, full abstract read |
| **DRL+MCTS engagement/difficulty prediction, best-case agent run as feature** | Predicts human engagement and difficulty perception from AI-agent play; found that an agent's BEST run (not its average) is more predictive on hard levels | Roohi, Guckelsberger, Relas, Heiskanen, Takatalo & Hämäläinen (2021), arXiv:2107.12061 | **CONFIRMED** (paraphrase-level; not full verbatim abstract) |
| **Hyperstate space graphs** | Automated structural analysis of a game's reachable state space, as a graph | Cook & Raad (2019), DOI 10.1109/cig.2019.8848026 | **CONFIRMED existence**, abstract not read |
| **Matching-tile automated playtesting** | Automated playtesting applied to a specific simple genre, as a worked example of the whole approach | Mugrai, de Mesentier Silva, Holmgård & Togelius (2019), arXiv:1907.06570 | **CONFIRMED existence** via arXiv API search, abstract not read |

**Applicability to RimMaster:** a scripted RimWorld pawn-AI walkthrough (not a
learned agent — just the vanilla AI or a bridge-driven script ordering a pawn
through the dungeon) is a cheap version of "agent playtesting" that answers
solvability and rough pacing (how many in-game hours/ticks to clear each ring)
without needing a human tester or any RL training. This is a downgrade of the
academic technique to something achievable with existing `rimbridge` tooling, not
the real MCTS-persona method — say so if proposing it.

### 1.3 Requires human playtesters — validated psychometric instruments

⚠️ **This is exactly the domain where a discredited instrument is worse than no
instrument.** Full notes: `sources/metrics/psychometric_instruments_and_critiques.md`.

| Instrument | Measures | Item count / structure | Validation status | Source |
|---|---|---|---|---|
| **GEQ** (Game Experience Questionnaire) | Immersion, flow, competence, positive/negative affect, tension, challenge (originally 7 factors) | Structure UNVERIFIED this session (never formally published) | ⚠️ **DIRECTLY CHALLENGED.** Law, Brühlmann & Mekler (2018, CHI PLAY, DOI 10.1145/3242671.3242683) reviewed 73 papers using it, found it "operationalized in 24 distinct ways," and their own N=633 validation found **"no evidence for [the] originally postulated 7-factor structure."** | **CONFIRMED**, full abstract read |
| **PENS** (Player Experience of Need Satisfaction) | Competence, autonomy, relatedness (Self-Determination Theory) + presence/immersion + intuitive controls | Item count UNVERIFIED | Theoretical grounding solid (Przybylski, Rigby & Ryan 2010, Review of General Psychology, DOI 10.1037/a0019440); a joint 2018 validation exists (Johnson, Gardner & Perry, DOI 10.1016/j.ijhcs.2018.05.003, N=629 EFA + N=729 CFA) but I could not get a consistent read of whether its conclusion is supportive or critical — **flag as UNCERTAIN, read it directly before citing a verdict.** | Theory: **CONFIRMED**. Validation paper's conclusion: **UNCERTAIN** |
| **PXI** (Player Experience Inventory) | Functional Consequences (audiovisual appeal, ease-of-control) vs. Psychosocial Consequences (immersion, mastery) — a Means-End-Theory-grounded split | 10-factor model (confirmed by a German replication); 529 participants across 5 studies in the original validation | Solidly validated relative to the others here; even its own German replication flagged room to improve discriminant validity. | **CONFIRMED**, full abstract read (Vanden Abeele et al. 2019, DOI 10.1016/j.ijhcs.2019.102370) |
| **miniPXI** | Abbreviated PXI | **11 items** | Per-construct single-item reliability 0.51–0.83, avg ≈0.68 | **CONFIRMED** (Haider et al. 2022, DOI 10.1145/3549507) |
| **CEGEQ** (Core Elements of Gaming Experience Questionnaire) | Enjoyment, gameplay understanding, control, ownership | UNVERIFIED | Origin paper (attributed to Calvillo-Gámez, Cairns & Cox) **not located this session** despite repeated targeted search — confirmed only indirectly via a paper that USES it (Chesham et al. 2017, DOI 10.2196/games.7025) | Existence: **CONFIRMED-VIA-USAGE**. Origin/validation: **UNSOURCED** |
| **GUESS** (Game User Experience Satisfaction Scale) | 9 subscales of game UX satisfaction | 9 subscales, tested across 450+ titles | Content and discriminant validity reported | **CONFIRMED** abstract (Phan, Keebler & Chaparro 2016, DOI 10.1177/0018720816669646) |
| **CORGIS** (Challenge Originating from Recent Gameplay Interaction Scale) | Perceived CHALLENGE specifically (not the broader GEQ bundle) | UNVERIFIED item count | A dedicated, purpose-built challenge instrument — directly the most on-point validated tool for the "is this dungeon appropriately hard" rubric dimension | **CONFIRMED** existence (Denisova, Cairns, Guckelsberger & Zendle 2019, DOI 10.1016/j.ijhcs.2019.102383) |
| **Jennett et al. immersion model** (engagement / engrossment / total immersion) | Immersion as a 3-level construct | UNVERIFIED this session | 2,005 citations (per OpenAlex) — one of the most-cited papers in the entire field. Content NOT independently re-verified this session (abstract text unavailable via API, guessed PDF URL 404'd). | Existence/venue/authors: **CONFIRMED**. 3-level model content: **UNCERTAIN** |
| **IMI** (Intrinsic Motivation Inventory), as used in games | Intrinsic motivation subcomponents | UNVERIFIED | **Not located this session** — searches surfaced only tangential IMI applications (workplace motivation, schizophrenia research), never the games-specific foundational use | **UNSOURCED this session** |
| Physiological (EMG/EDA, heart rate) alongside questionnaires | Objective arousal/affect, independent of self-report | N/A — hardware, not a scale | Nacke & Lindley (2010, arXiv:1004.0248): a combat-oriented level produced measurably different high-arousal-positive-affect readings than other level designs, from the SAME game — i.e. level design alone shifts measurable physiology | **CONFIRMED**, full abstract read |

### 1.4 Methodology for running a human playtest well

- **Nielsen's "5 users" heuristic is real but genuinely contested, with numbers on
  both sides.** Formula: U = 1 − (1−p)ⁿ (Nielsen/Landauer). Refutation: Faulkner
  (2003, Behavior Research Methods, DOI 10.3758/bf03195514, 1,078 citations) found
  (per secondary paraphrase) that some 5-person test groups caught only **55%** of
  known problems, while no 20-person group caught fewer than **95%.** — Treat
  "5 is enough" as CONTESTED, not settled; a dungeon with several independent rare
  failure modes (softlock, guardian-skip, loot-starve) is exactly the case where
  the low end of that range bites.
- **What players say vs. what they do is not just an ordinary self-report bias —
  it's structural to games as a medium.** Gundry & Deterding (2018, Simulation &
  Gaming, DOI 10.1177/1046878118805515, **CONFIRMED** full abstract): games are
  complex systems resisting isolated treatments, are "rich in unwanted variance,"
  and their social framing differs from the situation being studied — with an
  explicit admission that methodological study of this is thin relative to the risk.
- **Think-aloud protocol** is named as a standard usability technique (Wikipedia,
  **CONFIRMED-VIA-SECONDARY**) but its specific procedure was not independently
  verified this session.
- **Valve's and Riot's own published playtest methodology, and the "1-on-1
  synchronous playtesting" strand named in the brief: NOT FOUND this session.**
  This is a tooling gap (search was broken), not evidence that nothing exists —
  see §6.

### 1.5 Telemetry / analytics

The standard reference — Seif El-Nasr, Drachen & Canossa (eds.), *Game Analytics:
Maximizing the Value of Player Data* (Springer, 2013) — is **CONFIRMED to exist**
via two independent lookups but was **not read this session**; treat any specific
metric-family claim attributed to it as UNSOURCED until a chapter is actually read.

**Why this whole family barely transfers to RimMaster, stated plainly:** DAU/MAU,
retention curves, funnels, and A/B drop-off all presume a live population and an
instrumentation pipeline. RimMaster ships ONE frozen savegame with no telemetry SDK
and (per repo CLAUDE.md) no player population beyond the owner and whoever he
shares it with. The only things that survive the downgrade to a handful of manual
playtests: a **hand-logged death/failure map** (record tile + cause on every
playtest death or forced retreat) and a **hand-logged funnel** (record which ring
each of N playtesters actually reached). Both are real, both are cheap, neither is
"telemetry" in the sense the book means — say so rather than borrowing the term's
authority for a manual process.

### 1.6 Domain-specific reference points

- **Darkest Dungeon's stress system** (darkestdungeon.wiki.gg, **CONFIRMED**, live
  game data not academic literature): 0–200 stress bar; 100 = affliction/virtue
  roll; 200 = heart attack (or Death's Door); idle recovery 5/week baseline (15/week
  with a specific building); stress-reduction sources explicitly capped at 80% so
  attrition can never be fully optimized away. The cleanest real-number example
  found this session of a designed, irreversible attrition floor — directly
  comparable to RimMaster's vault WAKE/LOOT/LEAVE ladder and the Assailant
  complex's one-way thaw trigger (`dungeons_arc_spec.md` §2.3, §3.4).
- **Dynamic Difficulty Adjustment** (Wikipedia, **CONFIRMED-VIA-SECONDARY**, but
  rich and specific): named techniques (parameter manipulation, dynamic scripting,
  ML-estimated "challenge"/"curiosity," genetic-algorithm opponent coevolution),
  real shipped examples (Left 4 Dead's AI Director, Resident Evil 4's 10-point
  scale, Mario Kart's rubber-banding), a named criticism ("rubber-band effect" +
  exploitability once detected), and a real 2020–21 lawsuit against EA over
  undisclosed DDA in sports titles. **RimMaster has no DDA and the campaign is a
  single frozen world** — this is background for how OTHER games think about
  difficulty, not a technique to import directly, since a fixed, hand-authored
  dungeon cannot adapt to the player who happens to walk it.
- **RimWorld's own storyteller** (Wikipedia "RimWorld," **CONFIRMED-VIA-SECONDARY**):
  three named storytellers (Cassandra Classic, Phoebe Chillax, Randy Random) with
  explicitly different PACING philosophies, and the storyteller is framed as
  optimizing for "the most interesting narrative," not a fixed difficulty curve.
  Sylvester's own book, *Designing Games: A Guide to Engineering Experiences*
  (O'Reilly, 2013, ISBN 978-1-4493-3802-2 — **CONFIRMED bibliographic facts only**,
  content not read this session), is the single most directly authoritative
  design-philosophy source that exists for this specific game, and a follow-up
  session should actually read it before this rubric is finalized.
- **Tabletop review criteria — tenfootpole.org/Bryce Lynch** (**CONFIRMED**, site
  read directly this session): the operative distinction is "specificity" (a terse,
  concrete, memorable detail that inspires actual play) vs. "detail" (unnecessary
  explanatory trivia). Values interactivity, the environment itself as the
  obstacle, coherent theming; penalizes padding, long read-aloud text, generic NPCs,
  incoherent modular assembly. Verdicts are short, decisive, and quotable ("No
  Regerts" / "Meh. It's fine" / "Do Not Buy Ever") rather than a weighted numeric
  score — a STYLE worth borrowing for how a reviewer states a verdict, even though
  the underlying judgment is still a human's holistic read.

---

## 2. Proposed rubric for judging one dungeon design

Every dimension below is grounded in something found above; the synthesis (how the
dimensions are grouped, worded, and weighted for RimMaster specifically) is this
agent's own construction, marked where it departs from a source.

### 2.0 Gate 0 — Solvability (pass/fail, before anything else is scored)

**Reviewer question:** "Run BFS/A* from the entry to every required objective
(power-core socket, casket hall, garrison exit) on the actual map file or KCSG
layout. Does a path exist? Does the core remain reachable ONLY through the intended
ring sequence, or can a raider path around the garrison ring entirely?"

- **Good:** every required objective reachable; the ring sequence cannot be
  bypassed; matches the pass bar RimMaster already wrote for itself in
  `dungeons_arc_spec.md` §3.7 step 2.
- **Bad:** an unreachable objective, or a skip path around an intended gate.
- **Source:** solvability/reachability (§1.1 #1, Vieira et al. 2026); the specific
  "no bypass" bar is RimMaster's own existing standard, not invented here.
- **This gate is binary and must pass before any of the below are scored** — a
  dungeon that fails Gate 0 doesn't have a tedium or difficulty problem, it has a
  build defect.

### 2.1 Structural shape (map-file computable)

**Reviewer question:** "Compute the mission-graph's branching factor, dead-end
count, and critical-path length vs. total explorable path length (a backtracking
ratio). Does the shape match what this dungeon is TRYING to be?"

- **Good:** a garrison-type (①) vault reads as dense and branching (many
  simultaneous threats, per `dungeons_arc_spec.md`'s "disciplined, powered" outer
  ring); a frozen-Rakata-type (③) vault reads as thin and linear (matches its own
  "mostly silence" garrison-ring description). The graph SHAPE should visibly
  differ between vault types, the way the owner's ruling already requires their
  fiction to differ.
- **Bad:** every vault has the same branching factor and path-length regardless of
  type — the mechanical shape contradicts the authored fiction.
- **Source:** graph connectivity metrics (§1.1 #2, Dormans 2010; Smith/Padget/
  Vidler 2018). The specific "shape should match fiction" framing is this agent's
  synthesis, grounded in RimMaster's own already-ruled type-differentiation
  requirement.

### 2.2 Density and pacing within a ring (map-file computable, cross-checked)

**Reviewer question:** "Compute density (guardians/loot/hazards per unit path
length) per ring. Does density step UP from outer to garrison to core, or does it
spike/dip inconsistently? Compare V5's density against V4's — do they actually read
as different (per the owner's ruling that V5 must be 'distinct... not a reused
garrison landmark')?"

- **Good:** monotonic or intentional density curve per ring; siblings that are
  supposed to differ (V4 vs V5) actually differ on this axis.
- **Bad:** flat density throughout (nothing escalates) or two "distinct" vaults
  that are mechanically identical.
- **Source:** leniency/linearity/density family (§1.1 #4) — used here strictly as a
  *within-family comparison tool*, per Mariño et al.'s (2015) own finding that
  these metrics should not be trusted as absolute quality scores. **Cross-check
  requirement, sourced from the same finding:** before this dimension's score is
  trusted on a NEW dungeon type, run at least one human walkthrough and check
  whether the computed density curve matches the human's felt sense of escalation
  (Hervé & Salge 2021; Rupp et al. 2024 — partial-correlation finding).

### 2.3 Challenge fit (needs at least one human check, or a scripted-agent proxy)

**Reviewer question:** "Does a scripted pawn-AI or bench playtester actually
survive the intended path with plausible-but-not-trivial losses? If a human
playtest is run, administer CORGIS (challenge-specific) rather than assuming
difficulty from the density number alone."

- **Good:** the intended crew composition/gear tier clears the ring with real
  risk (casualties possible, not guaranteed, not impossible) — matches the
  brief's "challenge vs skill band" framing (Csikszentmihalyi, §1.6/flow notes).
- **Bad:** trivial clear (boredom per the flow model) or reliable wipe (anxiety per
  the flow model) for the intended crew tier.
- **Source:** flow channel boredom/anxiety framing (CONFIRMED-VIA-SECONDARY,
  Csikszentmihalyi via Wikipedia); CORGIS as the validated instrument if a human
  check is run (Denisova et al. 2019).
- **Explicit caution, sourced:** RimMaster's world is hand-authored and never
  adapts to the specific player (no DDA) — so this dimension must be checked
  against the INTENDED crew tier the quest-gating already sets (per
  `dungeons_arc_spec.md` §2.3's "gating context: entry itself is mid-campaign"),
  not against an abstract "average player."

### 2.4 Narrative/tedium fit (human judgment, tenfootpole-style verdict)

**Reviewer question:** "Read every piece of authored text and every set-piece.
Is each one SPECIFIC (a concrete, memorable detail) or merely DETAILED (trivia
explaining why/how, that a player will skim)? Does the environment itself
constitute an obstacle, or is it just a pawn-density wall with scenery in front of
it?"

- **Good:** text like the V6 casket-hall passage already drafted in
  `dungeons_arc_spec.md` §3.10 — short, concrete, and the WAKE/LOOT/LEAVE choice
  IS the obstacle, not a stat check.
- **Bad:** padding, long read-aloud-style narrator text, a "hard room" that is only
  hard because of raw guardian count with no environmental logic to it.
- **Source:** tenfootpole/Bryce Lynch's specificity-vs-detail criterion (§1.6,
  CONFIRMED this session by reading the site directly).
- **Verdict style, explicitly borrowed:** end this dimension's review with a short,
  decisive, quotable line, not a 1–10 score — matching tenfootpole's own
  "No Regerts / Meh, it's fine / Do Not Buy Ever" register, because that is the
  one part of Lynch's method that is a stated STYLE choice rather than a hidden
  numeric rubric he never actually published.

### 2.5 Attrition/stakes shape (does the payoff structure have a real floor?)

**Reviewer question:** "Is there an irreversible, non-optimizable cost or choice
point (a WAKE/LOOT/LEAVE fork; a one-way thaw trigger)? Or can a sufficiently
careful/wealthy crew avoid ALL risk and cost?"

- **Good:** a real floor exists — per Darkest Dungeon's own explicit 80%-cap design
  guardrail (§1.6), SOME attrition or SOME consequence survives even perfect play.
  RimMaster's vault ladder and Assailant thaw-gate already have this by design.
- **Bad:** every risk in the dungeon can be fully avoided or trivially reversed by
  a well-equipped crew, so nothing is ever actually at stake.
- **Source:** Darkest Dungeon's stress-cap design precedent (§1.6, CONFIRMED game
  data). This dimension is the METRICS agent's own synthesis of that precedent
  applied to RimMaster's existing one-way-choice architecture — not something
  found stated as a general rubric dimension in the literature.

### 2.6 Duration fit (weakest-sourced dimension — flag accordingly)

**Reviewer question:** "How many real-time minutes or in-game hours does the
intended path take, end to end, at the intended crew tier? Does that match what
this dungeon's narrative weight can sustain?"

- **Status:** ⚠️ **This dimension is the least sourced in this entire rubric.** No
  validated duration-estimation method or "level overstays past N minutes"
  threshold was found this session (search degradation prevented chasing
  HowLongToBeat-style data or Schell's pacing claims to ground truth). Treat this
  purely as a bench-judgment call for now, explicitly flagged as UNSOURCED, and
  revisit once a working search path can chase Schell's "interest curve" and any
  HowLongToBeat-style literature down properly.

### Summary table

| Dim | Question | Input needed | Gate/score | Grounded in |
|---|---|---|---|---|
| 0. Solvability | Can every objective be reached, without bypass? | map graph | pass/fail | §1.1 #1–2 |
| 1. Structural shape | Does graph shape match the vault type's fiction? | mission graph | score | Dormans 2010 |
| 2. Density/pacing | Does density escalate per ring; do siblings differ? | map + content | score, cross-checked | Horn-family + Hervé/Rupp corr. findings |
| 3. Challenge fit | Trivial, right, or wipe for the intended crew? | scripted/human run | score | flow channel + CORGIS |
| 4. Narrative/tedium | Specific or merely detailed? Environment-as-obstacle? | human read | verdict line | tenfootpole |
| 5. Attrition shape | Is there a real, non-optimizable floor? | design read | pass/fail-ish | Darkest Dungeon precedent (synthesis) |
| 6. Duration fit | Right length for its narrative weight? | timed run | UNSOURCED, bench call only | — |

---

## 3. Thresholds and numbers — consolidated, with contested ones marked

| Number | Context | Contested? | Source |
|---|---|---|---|
| U = 1 − (1−p)ⁿ | Nielsen/Landauer usability-problem-discovery model | Formula itself uncontested; its USE to justify n=5 is contested | Wikipedia "Usability testing," CONFIRMED-VIA-SECONDARY |
| 5-person test groups found as low as **55%** of known problems | Empirical challenge to the "5 users is enough" heuristic | **CONTESTED** — this is the refutation number, not the original claim | Faulkner (2003), DOI 10.3758/bf03195514, via secondary paraphrase |
| No 20-person group found fewer than **95%** of known problems | Same study | Same caveat | Faulkner (2003), via secondary paraphrase |
| N=633; "no evidence for 7-factor structure" | GEQ's own postulated structure, directly tested | **This IS the contested finding** — GEQ is the thing being challenged | Law, Brühlmann & Mekler (2018), DOI 10.1145/3242671.3242683, CONFIRMED |
| 24 distinct ways GEQ has been operationalized, across 42 of 73 reviewed papers | Field-wide inconsistency in using GEQ | Not contested — this is itself the finding | Same paper |
| PXI: 529 participants, 5 studies, 64 experts in item design | PXI's own validation scale | Not contested | Vanden Abeele et al. (2019), DOI 10.1016/j.ijhcs.2019.102370, CONFIRMED |
| miniPXI: 11 items, per-construct reliability 0.51–0.83 (avg ≈0.68) | Cost of abbreviating PXI | Not contested, but note the wide 0.51–0.83 range — some constructs abbreviate much worse than others | Haider et al. (2022), DOI 10.1145/3549507, CONFIRMED |
| 86 papers surveyed (of 142 initial hits); 37 used direct-representation metrics; 27 used human playtesting; only 11 compared against prior published work | State of PCG evaluation practice, field-wide | Not contested; a genuine field self-report | Withington, Cook & Tokarchuk (2024), arXiv:2404.18657, CONFIRMED full text |
| Darkest Dungeon: 100/200 stress thresholds; stress-reduction capped at 80% | A shipped game's explicit attrition-floor design | Not contested (it's just game data), but note it is DESIGN PRECEDENT, not a validated research finding | darkestdungeon.wiki.gg, CONFIRMED |
| miniPXI/mPXI: **two different** abbreviated PXI scales exist | Naming collision risk | N/A — a caution, not a threshold | Haider et al. 2022 vs. Harteveld et al. 2020 |

---

## 4. What is NOT measurable, or where the field admits it's guessing

- **Tedium/boredom as a directly measured quantity:** targeted searches this
  session (OpenAlex, full-text) turned up essentially nothing that measures
  "tedium" as its own construct — the field routes around it through adjacent,
  validated constructs instead (CORGIS for challenge, PXI's psychosocial
  consequences for immersion/mastery) rather than measuring boredom/tedium head-on.
  Koster's and Schell's designer-level treatments of boredom/interest-curves exist
  but were **not independently verified this session** (§6) — until they are, this
  entire area should be treated as **folklore, not measured fact.**
- **Duration/length-vs-satisfaction relationships:** no HowLongToBeat-style dataset
  or academic time-to-complete-distribution literature was reached this session.
  §2.6 is flagged accordingly as the weakest rubric dimension.
- **Whether ANY single computed map-file metric predicts human enjoyment reliably
  across dungeon types:** the strongest finding available (Mariño et al. 2015,
  reinforced by Hervé & Salge 2021 and Rupp et al. 2024) is that correlation is
  real but **partial and metric-specific** — there is no evidence for a single
  metric that generalizes. The field's own remedy (Withington et al. 2024) is
  procedural (reuse methodology, don't force weak comparisons) rather than a
  silver-bullet metric.
- **Valve's and Riot's actual internal playtest methodology, and "1-on-1
  synchronous playtesting":** genuinely not found this session — a tooling gap
  (§6), not a finding that it doesn't exist.
- **CEGEQ's and the games-specific IMI's original validation:** both real,
  named, cited-by-others instruments whose ORIGIN papers could not be located this
  session despite repeated targeted search. Do not treat either as validated
  until the origin paper is actually read.
- **XCOM and Dwarf Fortress balance discussion:** not reached at all this session.

---

## 5. Highest-value next steps for a follow-up pass

1. Get a working search path (a healthy Fetcher SEARCH, or direct WebSearch on a
   different model group) and chase: Valve/Riot playtest practice; Schell's
   "interest curve"; Koster's boredom/fun claims; XCOM/Dwarf Fortress balance
   writing; the CEGEQ and games-IMI origin papers.
2. Actually read (not just abstract) Horn et al. (2014) for the real leniency/
   linearity/density formulas before any formula from that family goes into a
   scored rubric — ResearchGate and Semantic Scholar were both unreachable this
   session; try the authors' own institutional pages or a library proxy.
3. Actually read Smith, Padget & Vidler (2018) in full — it is the single most
   directly on-point paper found (dungeon graphs + quantitative expressive
   analysis) and was only confirmed to exist, not read.
4. Read Sylvester's *Designing Games* directly — it is the single most
   authoritative source for THIS game's own design philosophy and was only
   bibliographically confirmed this session.
5. Pilot §2's rubric against the six vaults + the Assailant complex once their
   KCSG layouts exist, and use that pilot to replace every "UNSOURCED, bench call
   only" flag with either a real number or an honest, permanent "not measurable."

---

## 6. Sources saved

Full extracted notes, quotes, and additional citations (more than fit in this
synthesis) are saved at:

- `research/game_design/sources/metrics/pcg_evaluation_and_automated_playtesting.md`
- `research/game_design/sources/metrics/psychometric_instruments_and_critiques.md`
- `research/game_design/sources/metrics/flow_difficulty_dda_usability.md`
- `research/game_design/sources/metrics/telemetry_tabletop_colonysim.md`

No PDFs were successfully persisted to `sources/metrics/` this session — arXiv PDF
fetches returned binary content that landed in the tool's own transcript storage
(outside this repo's write permissions) rather than a readable text extraction, and
Fetcher's `FILE` queue was still processing at end-of-session under heavy
concurrent load from sibling research agents (queue depth ~40 requests). A
follow-up pass should re-run the `FILE` downloads queued at
`/Users/mandrake/dev/Fetcher/Requests/2026-09-11_metrics_i_arxiv_pdfs.txt` (or
their `Complete/` outcome, if they finished after this session ended) and move any
successfully retrieved PDFs into `sources/metrics/`.
