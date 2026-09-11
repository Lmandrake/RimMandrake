# Skills / agent-tooling ecosystem for game design

Scope: the Claude skills and agent-tooling ecosystem, local and published, adjacent to
game design, dungeon/level design, narrative, worldbuilding, playtesting/metrics, and
authoring rules for skills themselves. Sibling reports (LOCAL-MODS, RW-ENGINE,
REPO-PRIOR, RPG-THEORY, METRICS, AWARDS-PUZZLES, the SW/sci-fi source agents) cover
adjacent ground — this file does not restate what our own project skills *say* about
design (that's REPO-PRIOR, `research/game_design/findings/REPO_PRIOR.md`, CONFIRMED
present at that path 2026-09-11).

Every line below is CONFIRMED (I read the file or fetched the page) unless marked
UNCERTAIN. Evidence is the path or URL on the same line.

---

## HALF 1 — What already exists

### 1. Local skills on this machine

**CONFIRMED — the CLAUDE.md-cited clone is absent.** `~/.claude/CLAUDE.md` names
`~/GDrive/JPL/dev/skills/` as a clone of `anthropics/skills`. On this machine right now,
`~/GDrive/JPL/dev/` contains only `Agentic_Processes/`, `Nemotron/`, and
`PROJECT.placard.md` — no `skills/` directory
(`/Users/mandrake/GDrive/JPL/dev/` — `ls` output, ​2026-09-11). I fetched the
authoring rules straight from GitHub (`anthropics/skills`, see §3) instead of reading
the missing local clone. This absence is itself a finding to report back — the note in
global CLAUDE.md is currently wrong for this machine/mount.

**User-global skills** — `~/.claude/skills/` (58 entries, `ls` output). Adjacent to this
work:
- `option-portfolio` — Pareto-set option generation, hard-gates before ranking.
- `blind-evaluation` — head-to-head comparison design (blinding, balanced position,
  honest small-n reading).
- `evaluation-independence` — keep build material and judge material separate.
- `validity-floors` — hard constraints (admissible) vs. soft criteria (ranking).
- `falsifiable-claims` — bracket a comparative/causal claim before publishing it.
- `claim-provenance` — gate for whether a claim earns a place in a knowledge base.
- `visual-intent` / `visual-encoding` / `visual-composition` / `visual-portfolio` /
  `visual-critic` / `visual-render-qa` / `scientific-visualization` — the full
  visual-reasoning pipeline; general-purpose, not game-specific, but directly reusable
  for any figure/diagram this campaign needs (map legends, encounter-flow diagrams).
- `review-sheets` — turning a big keep/cut/rank/grade task into an HTML sheet a human
  works in.
- `ideogram` — living request documents.
- `frozen-artifacts` and `deciding-and-superseding` are NOT in the global list
  (confirmed missing: `~/.claude/skills/frozen-artifacts/SKILL.md` does not exist) —
  they only exist as **project** skills (see below), despite being generically useful
  patterns for any design practice with frozen decisions and rulings.

All paths above verified by reading each `SKILL.md`'s frontmatter directly
(`~/.claude/skills/<name>/SKILL.md`, 2026-09-11).

**Project skills** — `/Users/mandrake/dev/RimMaster/skills/` (28 entries) and
`/Users/mandrake/dev/RimMaster/.claude/skills/` (30 entries, confirmed to be **symlinks**
into `skills/`, e.g. `.claude/skills/rimbridge -> ../../skills/rimbridge`). One symlink is
broken on this machine: `.claude/skills/review-sheets -> /mnt/d/Luke/dev/review-sheets`
— a WSL/Windows path that does not resolve here (`readlink` + `ls` output, 2026-09-11);
the global `~/.claude/skills/review-sheets/SKILL.md` still works as a fallback.

Design-adjacent project skills (frontmatter read directly, all CONFIRMED):
- `rimworld-scene-composition` — scored composition of scattered/scenic sites against
  five named metrics plus a critical-reviewer pass; the closest thing we have to a
  worked "does this dungeon read as a place" judgment skill, but scoped to RimWorld
  scattered-site dressing, not dungeon *structure* (rooms, gating, pacing).
- `rimworld-layout-layers` — judges a built structure on independent functional layers
  (power, pipes, roofing, floor, access) rather than mere presence — a judgment skill,
  but about engineering correctness, not player experience.
- `rimworld-quests` — the QuestScriptDef signal-wiring mechanics and a design rubric for
  "is this quest worth playing," calibrated against 151 shipped quests.
- `rimworld-ideoligion` — four-mode (design/author/validate/judge) skill with an actual
  judging rubric for religions.
- `rimworld-content-moderation` — keep/cut curation methodology (contact sheets, visual
  decision-making, tag-survivor auditing after a cut).
- `rimworld-scenario-building`, `rimworld-world-editing`, `rimworld-xenotypes`,
  `gravship-layout`, `generating-rimworld-sprites`, `reading-rimworld-graphics` —
  mechanically-scoped (how the engine's authoring surface works), not judgment skills.
- `frozen-artifacts` and `deciding-and-superseding` — process/governance skills (how a
  ruling gets recorded and propagated); relevant infrastructure for any design
  discipline, currently project-local only.

**Nothing here targets**: dungeon/level *structure* judgment (room sequencing, gating,
pacing, key/lock graphs) as a first-class skill; narrative/quest *writing craft*
judgment (as opposed to QuestNode mechanics); or playtesting/metrics analysis as a
skill at all. These are real gaps (see HALF 2).

### 2. The official Anthropic skills repo — current contents

Fetched live from GitHub (`anthropics/skills`, since the local clone is absent):
`gh api repos/anthropics/skills/contents/skills` → 18 entries: `academy-guide`,
`algorithmic-art`, `brand-guidelines`, `canvas-design`, `claude-api`,
`discernment-nudge`, `doc-coauthoring`, `docx`, `frontend-design`, `internal-comms`,
`mcp-builder`, `pdf`, `pptx`, `skill-creator`, `slack-gif-creator`, `theme-factory`,
`web-artifacts-builder`, `webapp-testing`, `xlsx`. **None are game-design-adjacent** —
this is a productivity/document-authoring set. An empty category, confirmed.

`spec/agent-skills-spec.md` in that repo is now a 3-line pointer:
*"The spec is now located at <https://agentskills.io/specification>"* (fetched content,
2026-09-11) — the spec moved off-repo since the CLAUDE.md note was written.

### 3. Current authoring rules — from `skill-creator/SKILL.md` and `agentskills.io/specification`

**Frontmatter fields** (from `https://agentskills.io/specification`, fetched
2026-09-11):

| Field | Required | Constraint |
|---|---|---|
| `name` | Yes | 1-64 chars, lowercase alphanumeric + hyphens, no leading/trailing/consecutive hyphen, **must match the parent directory name** |
| `description` | Yes | 1-1024 chars, non-empty, must say what it does AND when to use it |
| `license` | No | license name or pointer to a bundled file |
| `compatibility` | No | ≤500 chars; environment requirements (product, system packages, network) |
| `metadata` | No | arbitrary string→string map |
| `allowed-tools` | No | space-separated pre-approved tools, e.g. `Bash(git:*) Bash(jq:*) Read` — marked **Experimental** |

Minimal example quoted verbatim from the spec:
```
---
name: skill-name
description: A description of what this skill does and when to use it.
---
```

**Progressive disclosure** (spec, verbatim numbers): metadata (~100 tokens, always
loaded) → SKILL.md body (**<5000 tokens recommended**, loaded on activation) →
bundled `scripts/`/`references/`/`assets/` (loaded only as needed). Spec says "Keep
your main SKILL.md under 500 lines." `skill-creator/SKILL.md` (fetched from
`anthropics/skills`) gives the same 500-line ceiling and a looser "~100 words" for
metadata and "<500 lines ideal" for the body — the two documents are consistent but
not byte-identical in wording, so cite the live spec as authoritative.

**Description-writing rule** (`skill-creator/SKILL.md`, verbatim): *"Note: currently
Claude has a tendency to 'undertrigger' skills — to not use them when they'd be
useful. To combat this, please make the skill descriptions a little bit 'pushy'."*
The spec's own good/poor example pair:
- Good: `Extracts text and tables from PDF files, fills PDF forms, and merges
  multiple PDFs. Use when working with PDF documents or when the user mentions PDFs,
  forms, or document extraction.`
- Poor: `Helps with PDFs.`

**`name` must equal the directory name** — this is a hard validation rule in the
current spec (not previously documented in this repo's own skills, worth checking our
skills against `skills-ref validate` if that tool is ever installed;
`agentskills/agentskills` `skills-ref` referenced by the spec, not fetched/verified
beyond the pointer).

**Directory layout** (spec, verbatim): `SKILL.md` (required) + optional `scripts/`,
`references/`, `assets/` — matches what our own skills already do
(`rimworld-quests` has `scripts/validate_quest.py`, `rimworld-ideoligion` has
`references/design.md`, both CONFIRMED by directory listing).

### 4. Published/third-party — searched via `gh api search/repositories` and
`search/code` (WebSearch returned the documented 400 for this model group, confirmed;
Fetcher's own queue had 22 other agents' jobs ahead of mine so I used `gh api` directly
against GitHub's public search instead — `gh auth status` confirmed logged in).

**RimWorld modding skills** (mechanical, not design-judgment — genuinely a different
category from this report's target, flagged for LOCAL-MODS/RW-ENGINE, not authored
further here):
- `Kon-on/rimworld-modding-skill` — <https://github.com/Kon-on/rimworld-modding-skill>
  — Chinese-language, XML Def/C#/Harmony/Steam Workshop authoring guide, template-first
  decision tree. Fetched `SKILL.md`, confirmed content.
- `Jeffrharr/ModDevSkills`, `nabkey/rimmod`, `ying636/Custom-Quest-Framework` — not
  opened in depth; same category by name/description.

**Tabletop RPG adventure authoring** — one real hit:
- `mburnamfink/rpg-dev-skills` — <https://github.com/mburnamfink/rpg-dev-skills> —
  five skills (`rpg-dev`, `rpg-npc-cast`, `rpg-critic`, `rpg-revise`, `rpg-publish`)
  forming a **dev → critic → revise → publish** loop for a system-agnostic adventure
  module, plus an NPC-portrait skill wired to Gemini 2.5 Flash Image. README and
  install instructions fetched directly (`gh api .../contents/README.md`). This is the
  single best structural analogue found for a "site-map dungeon design" authoring loop.
- D&D-specific GM-toolkit hits (not opened beyond name/description):
  `neuralinitiative/claude-dnd-skill`, `deocarvalho/dnd-dm-toolkit`,
  `JoeCotellese/dnd-dm-skill`, `glato/dnd-gm-skillkit`, `k5cents/dm-skills`.

**Game-design-framework suites** — the strongest published prior art for
"judgment skills," worth returning to when authoring HALF 2:
- `baxatron-git/claude-game-design-suite` — <https://github.com/baxatron-git/claude-game-design-suite>
  — 22-skill "vision to delivery" suite (repo description, fetched 2026-09-10 update).
  Directory listing fetched directly; skills read in full include:
  - `level-encounter-planner` — *"Structure spaces and encounters to deliver on pillars
    and pacing... designing level layouts, encounter sequences... building pacing
    curves (tension/release)... spatial flow."* (frontmatter description, fetched
    verbatim) — closest published analogue to our dungeon-structure judgment gap.
  - `playtest-protocol-designer` — *"Structure playtests to generate actionable data,
    not just 'it was fun'... choosing between playtest types (blind, facilitated, A/B,
    stress test)."* Direct analogue for the METRICS sibling's territory.
  - `narrative-systems-designer` — *"the machinery of storytelling in the game... how
    story and mechanics interact... quest/mission/scenario structures."*
  - `world-logic-checker` — *"Keep the fiction internally consistent as the game
    scales... checking new content for lore contradictions."*
  - `game-balance-analyst` — *"no dominant strategies, no dead options, no runaway
    leaders."*
  - Also present: `core-loop-designer`, `design-coherence-engine`,
    `design-iteration-tracker`, `design-pillars-architect`,
    `economy-progression-designer`, `gdd-author`, `high-concept-pitch-writer`,
    `player-experience-modeler`, `prototype-scope-definer`,
    `rules-formalizer`, `scope-feature-prioritizer`, `systems-interaction-mapper`,
    `technical-design-bridge`, `ui-ux-systems-designer`, `game-market-analyst`,
    `aesthetic-direction-framework`. **UNCERTAIN**: I read frontmatter for 5 of the 22;
    the rest are named/listed but not opened — do not cite their content as more than
    a name.
- `indieshade/game-design-analysis-skill` —
  <https://github.com/indieshade/game-design-analysis-skill> — single skill applying
  MDA, Core Loop, Flow Theory, Game Feel frameworks to analyze or derive mechanics;
  `SKILL.md` + `frameworks.md` read directly. Small (0 stars, last updated
  2026-05-07) but on-topic and genuinely a judgment skill ("apply systematic
  evaluation rather than intuition alone" — frontmatter body, fetched verbatim).
- `SCKOROT/game-design-document-creater`, `jasonxu610/game-design-skills`,
  `VoidexSoft/game-design-studio`, `apetrovCode/game-design-skills`,
  `neko233-com/skill-neko233-game-design`, `takaoumehara/intuitive-game-design-skill` —
  found by repo search, descriptions only (GDD generators / generic "game design skill"
  collections); not opened in depth. **UNCERTAIN** whether any encode judgment vs.
  templating.

**Dungeon/level generation, narrative/interactive-fiction, sci-fi worldbuilding,
playtesting/PCG as EXPLICIT categories**: searched
(`claude skill narrative interactive-fiction storytelling` → **0 results**;
`claude skill sci-fi worldbuilding` → **0 results**;
`claude skill playtesting game-analytics` → **0 results**;
`claude skill procedural-generation game` → 3 weak/generic hits:
`rondorkerin/gamestack`, `bgrenat/godot-game-dev-studio`,
`ismael-joffroy-chandoutis/claude-skills-public`, none opened in depth). **These are
confirmed-empty categories as named searches** — real absence, not a search-quality
artifact (each query returned a well-formed 0 or near-0 count from GitHub's search
API, not an error). This is the strongest finding in HALF 1: nobody has published a
Claude skill specifically for "dungeon design judgment," "narrative-delivery-system
judgment for games," or "game telemetry/playtest analysis" as such — the nearest
things are the general-purpose `baxatron-git` suite entries and `indieshade`'s
single analysis skill.

**MCP servers**: not separately searched beyond what repo search surfaced
incidentally (`afbqwer/RimworldDataMCP`, `Glade-tool/glade-mcp`) — out of scope depth
for this pass; flag as UNCERTAIN/unexplored if the MCP angle matters later.

---

## HALF 2 — Proposed skills (judgment-encoding, not reference lookup)

Each below fills a gap confirmed empty or thin in HALF 1, and each is a repeated
*decision* a designer makes, not a fact lookup.

1. **`dungeon-structure-judge`** — *"Judge whether an authored dungeon's room graph
   actually produces the intended pacing and difficulty curve — gating logic (key/
   lock, coordinate, knowledge chains), backtrack cost, dead-end ratio, and
   `RSW_` shape (site-map / sealed-substructure / chained). Use before calling any
   dungeon 'done,' and whenever a built site 'feels flat' or 'too easy to skip.'"*
   Contains: a graph-based checklist (branching factor, critical-path length vs.
   optional-path length, gate-before-payoff ordering), worked failure examples,
   and a scoring rubric. Judgment, not lookup: two structurally-valid graphs can
   both be "correct" and only one delivers the intended tension curve — that call
   is exactly what `level-encounter-planner` (baxatron-git) gestures at but does
   not specialize for the three named RimMaster dungeon shapes.

2. **`quest-reward-pacing-judge`** — *"Judge whether a chain of RimWorld quests
   (or dungeon-gated rewards) escalates stakes and payout at the right rate across
   a campaign arc, not just within one QuestScriptDef. Use before locking a
   quest chain's ordering or reward tier."* Builds on `rimworld-quests`'
   mechanical validator but adds the cross-quest pacing judgment that validator
   explicitly does not make (it checks wiring, not arc).

3. **`lore-consistency-arbiter`** — *"Decide whether a new piece of authored content
   (a faction, an ideoligion, a dungeon backstory) contradicts frozen worldbuilding
   canon, and where the contradiction actually lives (the new content vs. the old
   canon vs. an ambiguous prior ruling). Use before shipping any new lore-bearing
   def, description, or quest text."* Directly modeled on the confirmed
   `world-logic-checker` (baxatron-git) but scoped to this repo's specific canon
   sources (`design/Jawa/worldbuilding/the_one_map.md`, frozen rulings) — a genuine
   judgment skill because "is this consistent" requires weighing which of two
   conflicting-sounding facts is the frozen one.

4. **`playtest-signal-triage`** — *"Decide which of several playtest observations
   (a save file walked, a screenshot reviewed, a log of pawn behavior) is signal
   worth acting on versus noise from a one-off pawn AI quirk. Use whenever a
   review-sheets session or in-game LOOK produces qualitative feedback that needs
   turning into a design change or explicitly NOT acting on."* Fills the confirmed
   0-result "playtesting/game-analytics" gap; complements `playtest-protocol-designer`
   (baxatron-git, protocol design) by covering the *reading* side once data exists —
   this is squarely METRICS-sibling territory but framed as a judgment call
   (act / don't-act), not a metrics-computation skill.

5. **`difficulty-fairness-judge`** — *"Judge whether a dangerous authored place
   (a dungeon, a raid, a sealed substructure) is 'hard but fair' versus 'a
   run-killer with no legible tell' — using the same admissible-vs-optimal framing
   as `validity-floors`, applied to encounter design instead of decision-making."*
   A direct, deliberate specialization of the already-confirmed `validity-floors`
   and `game-balance-analyst` patterns onto RimWorld's specific tools (raid points,
   pawn kind lethality, escape routes) — judgment because "hard" is not itself the
   failure, "hard without a legible reason" is.

6. **`narrative-delivery-fit-judge`** — *"Decide which narrative-delivery mechanism
   (environmental storytelling via scene composition, a quest's dialogue text, an
   ideoligion precept, a discovered log/lore item) is the right one for a given
   story beat in a colony-sim with indirect pawn control — and reject the ones that
   assume player agency this genre doesn't have."* Fills the confirmed 0-result
   "narrative design for games" gap, and is explicitly RimWorld-genre-aware (indirect
   control, no player avatar) in a way `narrative-systems-designer` (baxatron-git,
   engine-agnostic) is not — genre-fit is the judgment.

7. **`skill-description-trigger-tuner`** — *"Before shipping a new or edited project
   skill, run the `skill-creator` description-optimization loop against this
   project's own designers' phrasing (Jawa/RSW/RUT naming, queue-item names,
   BENCH/FOUNDRY jargon) rather than generic prompts, so a skill actually fires on
   how *we* talk, not how a generic user talks."* Not a doc: it operationalizes
   `skill-creator`'s existing `run_loop.py` (CONFIRMED present in that skill,
   `anthropics/skills/skills/skill-creator/SKILL.md` §"Description Optimization")
   against a fixed, project-specific eval set the generic tool doesn't ship with —
   the judgment is which near-miss phrasing (queue-item name vs. lore text vs.
   BENCH-window jargon) should or shouldn't fire a given skill.

8. **`option-portfolio-for-dungeons`** — *"Apply `option-portfolio`'s Pareto-set
   discipline specifically to 'give me a few dungeon options to review as a
   savegame' — enumerate the genuinely distinct DESIGN questions a dungeon review
   can interrogate (structure-first vs. atmosphere-first vs. reward-pacing-first)
   before generating options, so three builds on one grid aren't three coats of
   paint on the same layout."* A thin, deliberate specialization of the already-
   confirmed generic `option-portfolio` skill onto this project's own "ship as a
   savegame, one map, all options" ritual (`CLAUDE.md` §"Options he must LOOK at").

---

**File written to**: `/Users/mandrake/dev/RimMaster/research/game_design/findings/SKILLS_ECOSYSTEM.md`
