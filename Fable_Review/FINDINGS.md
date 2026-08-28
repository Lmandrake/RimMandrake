# Findings

Numbers marked ✓ were re-measured by the reviewing agent itself on 2026-08-27; the
rest come from the seven domain agents' tool output with paths cited.

## F1 — The governance layer is heavier than the product's own rulebook needs to be

- ✓ 15,447 words across the seven governance files (`POLICY.md` 5,577 · `REP.md` 2,103
  · `DECIDE.md` 1,988 · `GAME_STATE_WORKFLOW.md` 1,981 · `CHECK.md` 1,386 · `BUILD.md`
  1,322 · `Agent_Policy.md` 1,090), roughly **200+ imperative rules** by marker count.
- All 34 dated owner rulings fall inside a single 8-day window (Aug 15–27). The
  constitution is younger than some of its own supersession chains.
- POLICY.md's own text records the cost: 47 obligations, 13–19k tokens of mandatory
  reading, "83–96% doctrine per wake" — measured by the seats themselves, then answered
  with another rule (`POLICY.md:100-106`, "a new obligation names the one it replaces")
  rather than with deletion.
- Add the typical skill load (13–20k tokens per task domain, see F5), CLAUDE.md, and
  76 memory files (~22k words), and **a seat pays on the order of 30–50k tokens of
  doctrine before touching its first work item.** Four windows each pay it, every wake.

## F2 — Process churn dominates the repo and is growing, not settling

- ✓ 3,070 commits in 15 days (first commit 2026-08-13).
- Commits touching `infrastructure/state|agents|.claude`: **54%** whole-history,
  **61%** last 14 days. Product work (world/) only began in earnest after the
  scaffolding stabilized — and the process share still rose.
- ✓ `infrastructure/state/ledger/events.jsonl` has been committed **526 times** — the
  single most-modified file in the repo. Positions 2–7 of the top-modified list are all
  queue/state files. The most-edited *content* file (`V2_DREAMS.md`, 64 commits) ranks
  eighth.
- 494 commits (~16%) carry process-keyword subjects (verify/close/stale/budget/
  trim/supersede/ruling).
- The three redesigns are visible in history exactly where the owner remembers them:
  founding (~08-14), messaging lockdown + authority rewrite (08-19→22), doc-budget +
  verification overhaul (08-25→27).

## F3 — Verification ceremony is applied to work that cannot hurt anyone

- `infrastructure/state/items/BRIDGE_GATE_HARDCODES_CHECK_1.md`: a **one-line lambda
  fix** carries full `## spec` / `## verify` / `## criteria` / `## watch out` sections
  — 32 lines of ceremony for a change git can revert in one command. Meanwhile a
  comparable small bug (`BUILD_BATCH_FACTION_REJECTS_PLAYER_1.md`) has none: the
  ceremony is inconsistent as well as heavy.
- The ledger shows 197 `verify` events against 361 closes; `rimflow` marks verify
  results **immutable** and refuses `close` without a commit sha.
- The full life of one item: `file` (prompted for spec/verify/criteria) → `claim` →
  `start` → work → `verify --result --config --evidence --sha` → `close --sha` →
  commit with `Closes:` trailer → push. That is the *minimum* path for work of any
  size, which is why "remove this file" takes minutes.
- Counter-evidence that the system already knows this: the 2026-08-27 ruling
  (`CHECK.md:57`, `BUILD.md:67`) — BUILD produces **nothing** for CHECK automatically;
  the owner playing the game is the default validation. The dismantling has begun; this
  review's job is to finish it coherently instead of ruling-by-ruling.

## F4 — The rule system is visibly correcting itself, and archiving every correction

- `CHECK.md:57-64` supersedes "the 2026-08-23 form of this rule," which was itself a
  correction (TRIM_VALIDATION_LAYERS_1) of the original verification rule — a
  correction of a correction, all three layers still described in prose.
- `DECIDE.md:106-115` records a ruling that "CORRECTS a ruling he made ~20 minutes
  earlier and this seat had already written into three files."
- `REP.md` contradicts itself internally: line 33 lists MODE values that line 85 of the
  same file calls "dead words."
- `.claude/hooks/block_paste_handoff.py` exists, by its own docstring, because the same
  rule written twice in prose failed anyway — the project's clearest proof that
  **hooks enforce and prose does not.**
- The doc-budget system polices size while the append dynamic continues: `DECIDE.md` is
  **+47 lines over** its own budget right now, POLICY.md sits 7 lines from its wall,
  and the budget warning hook exits 1 to the owner's terminal where agents cannot see
  it. Shrink passes then consume tokens re-fitting prose under limits — the treadmill
  the owner reports.

## F5 — The skill corpus is being bloated by a specific, identifiable pump

- 26 repo skills; the top five SKILL.md files alone are ~19,700 words. A typical
  3–4-skill task load is **13–20k tokens** before any work.
- ✓ `skills/generating-rimworld-sprites/SKILL.md` contains the same 52-line
  "Multi-facing assets" section **three times**, near-verbatim, each copy ending in a
  different session's dated tip — three separate end-of-session "move lessons to
  skills" passes each appended instead of merging.
- ✓ `skills/rimbridge/references/traps.md` is **10,110 words** against its parent
  skill's 3,715 — the designed append-then-prune journal where the prune step has
  never kept pace with the append step.
- `skills/README.md`'s generated roster lists 24 skills and is missing
  `rimworld-layout-layers` entirely; the roster generator was last run before the skill
  existed. (Small, but it means the index agents trust is wrong.)
- No dead path references were found in sampled skills — the *content* is largely
  accurate; the problem is mass and duplication, not rot.

## F6 — Queue staleness costs are a design choice, not an accident

- `NEXT_RELOAD.md` needed an owner-ordered manual prune (08-24) of blocks whose IDs
  had already closed, then was found stale **again** on 08-26. It also carries a
  "✅ Closed today, do NOT re-open" list — written because re-opening closed items is a
  recurring behavior.
- V1.md's gate table shows a row "reopened — proven only after the next restart."
- The current default is *prove an item stale before dropping it* — which is exactly
  the 10-minute token burn the owner describes for items that are already done. The
  ledger's own numbers say ~95 filed-minus-closed against ~46 visible open items, so
  roughly half the nominal backlog is bookkeeping residue rather than work.

## F7 — Seat asymmetry: two of the four resident windows no longer earn their residency

- Closes by seat: **BUILD 140 · DECIDE 100 · CHECK 60 · OWNER 49 · REP 12.**
- CHECK's charter was already cut to "only what has never once been observed running"
  (08-27). Its remaining function is a *lane*, not a window.
- REP closed 12 items in 15 days; her real outputs (board render, queue views,
  routing) are executed by scripts (`render.py`, `Utils/board/` static JS) that a cron
  job can run without a model. The board needs no resident Opus window.
- DECIDE's authority was already reduced on 08-22 ("DECIDE is a domain, not an
  authority; BUILD owns implementation entirely") — and the actual decider is, and
  always was, the owner.

## F8 — What is working and must be kept

- **Hooks.** Every hook in `.claude/hooks/` maps to a real incident and actually
  enforces. This is the project's best invention.
- **`canon.yml` as single-source tiebreaker** for contested numbers, and the
  superseded-banner discipline in design docs — the design corpus's drift is
  *self-documenting*, not orphaned (39 of 138 docs carry explicit supersession
  markers; readers are warned, structure is healthy).
- **BENCH/BELT/AFK.** BENCH is the correct default posture; the redesign generalizes
  it rather than replacing it.
- **The measurement discipline** (`measure`, instrument registers, "grade the answer
  not the exit code") — genuinely necessary in a domain where a cold load costs 25
  minutes and byte-scans return confident wrong numbers.
- **Minimal-modlist regime + quicktest + bridge** — the real cost-savers; 22 s vs 25
  min is the highest-leverage engineering in the repo.
- **Derived queues from a single-writer ledger** — right idea; the implementation is
  heavier than the remaining v1 needs (see REDESIGN).
- **`facts/` unbudgeted** — correct; knowledge should never be dropped for space.

## F9 — Product state (so the process is judged against what remains)

- V1.md: steps 8/11/12 (biomes, gravship, scenario) done; step 2 authored but unproven
  pending a cold load; steps 3–7 (equipment→pawns, xenotypes, droids, religions defs,
  48 pawnkinds) are the bulk; step 9 factions specced; step 10 is the owner's one-time
  manual worldmap stamp; quests moved to v2.
- Source side: the shippable product is a curated fix-pack (nine facing-art fixes, each
  precisely scoped), one quest mod, world art, `PlanetPresetPrime`, `JawaRules` — plus
  an infrastructure codebase (bridge, rimflow, Utils' 152 scripts) that dwarfs the
  content in volume. The gravship ("Corrosion Halo") is mid-iteration as of today.
- Conclusion: **v1 is weeks of content work, not months** — and most of the remaining
  risk is concentrated in a handful of cold-load-proven items, which is exactly where
  ceremony belongs.
