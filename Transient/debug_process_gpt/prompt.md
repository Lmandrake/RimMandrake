You are a senior engineer reviewing a PROCESS proposal for a RimWorld modding project
(a large solo-owner project, ~600 active mods, many of them the owner's own; AI coding agents do
most of the work in two "seats", BENCH (with the owner) and FOUNDRY (autonomous queue)). The game
is driven from outside through a bridge (RimBridge, a local RPC server inside the running game);
a cold game load costs ~15 minutes, so the game stays up and is driven by scripts. A "north-star"
script is a per-mod Python verification plan whose bars come from an owner-approved checklist
(hash-locked; edits revert it to DRAFT); a fast driver runs it over the bridge (~100 s for one mod,
723 calls). Project rules you should respect: the default is SOURCE (a live run must be proven
needed); one bridge driver at a time; never live-test flying creatures unattended; read the FIRST
exception in Player.log on load failures; a check that passed before and fails now is a stop;
a rising score with flat findings is not progress.

THE OWNER'S PROPOSAL (his intent, verbatim in substance):
"Rather than debugging mods interactively and impromptu, create and improve a verification
north-star script that is rerun each time, observing it succeed ever farther; this leaves an
excellent testing harness behind. Policy: all debugging first tries to use the existing north-star
script to evaluate any known error; if it does not reveal it and impromptu debugging is required,
additions are made to the north-star script and it is rerun until satisfied. The north-star python
scripts are very fast over the bridge. Want this to be an official process. It would NOT apply to
everything - defining the boundaries is part of the work. There may be exceptions where rapid
iteration is required for efficiency, but minimise them."
He added: GPT (you) is available as an escalation when debugging is stuck, and the process must
say when and how.

Below is the agent's draft proposal in full. Please:
(a) ATTACK it adversarially: what will fail in practice, what is over-engineered, what is missing,
    where the incentives go wrong, where the metrics can be gamed or cannot actually be measured;
(b) define SHARPER boundaries and exception criteria (where the rule applies, where not, and an
    exception test an agent cannot rationalise its way through);
(c) propose the MINIMAL VIABLE version (what to adopt on day one, what to defer) and a concrete
    PILOT design (scope, duration, what to measure, the kill criterion);
(d) list the concerns you would want the OWNER to rule on, each as a question with 2-4 options.
Also critique the GPT-escalation rung (trigger, brief, the "hypothesis not verdict" rule).
Be concrete and blunt; no preamble; ~1200-2000 words; markdown with headings (a)-(d).

=================== PROPOSAL ===================
# Debug process proposal — debug through the script, leave the harness behind

status: PROPOSAL, not policy until the owner approves · drafted 2026-10-01 by a FOUNDRY
subagent · GPT-reviewed (appendix) · nothing here edits CHARTER, FOUNDRY, CLAUDE.md or a skill

## 1. Problem and evidence

**The owner's intent:** stop debugging mods interactively and impromptu. Debug by
rerunning one fast verification script per mod and watching it get further each run;
when it cannot see a known error, extend the script until it can. The script left
behind is the testing harness. Exceptions for rapid iteration exist but are minimised.

**What 2026-10-01 showed** (every line traced to a commit or note, re-checked today):

| found | by | source |
|---|---|---|
| Graffiti full live run: 723 calls, ~100 s | the driver | ledger note; `f4428e8f1` |
| `set_draft` called with `draft=`, tool declares `drafted=` | script red | `f4428e8f1` |
| `waitTicks` a no-op on a paused site (ticksElapsed 0) | script red | `afcd048bd`, `8b1029f7b` |
| `step_game_ticks` gives up at ~10 s; client timeout 30 s | script | `f4428e8f1`, `transport.py` |
| preflight read wrong result fields (dlc, weather, modal, devMode); deploy check ignored the deploy tool's skip rules | script | `f4428e8f1`, `63d1771f1` |
| **10/10 PASS was state-only; the judge then found 76 of 79 frames UNJUDGEABLE** (marks clipped, 544×75 crops) | judge pass | `Transient/worker_notes_NORTHSTAR_JUDGE_PASS_1.md`, `757ee7521` |
| 22 Pyrelands call sites passed undeclared params or non-existent tools — found by an ad-hoc AST walk, no committed tool | hand probe | `cceea3071` |
| a bridge-made map that is not a player home is culled on save | live, ad hoc | `1be6f727e` |
| loading over a live game NREs in `GlowGrid.GlowPool.Take`; cell temp 41.6 vs 50.4 °C until ticks run; closing the naming dialog hops to the colony map | live, ad hoc | `6271d0aba`, `cceea3071` |
| burnedDef gate allowance was 12 lines, not 4 | script red | `795c1b008` |
| one-tick-per-frame waits made a Pyrelands run take ~4 h until fixed | script | `e2879e83a` |
| MOD defect: `RUT_Barbslinger` carried two turret comps (duplicate load IDs, corrupt save) | tier load + site | `710208b9d` |
| 158 ConfigErrors in the pyrelands tier, ~111 of them one advisory | log triage | `Transient/pyrelands_tier_log_triage_2026-10-01.md` |

**Three lessons, honestly weighed.**
1. **It works, and it is fast.** A rerunnable script turned a day of findings into
   commits. Most findings were caught *because* a check went red and was rerun.
2. **Most of what it found was the HARNESS, not the mods** — tool params, result
   shapes, timeouts, site recipe. Of the table above, one row is a mod defect found by
   the run itself; the rest is the instrument learning to see. That is the expected
   cost of a young harness, and it is also the trap: hours spent fixing the instrument
   can read as progress on the mod.
3. **What lived outside the script nearly vanished.** The scratch probes the seat used
   (`Transient/ns_probe_*.py`, `ns_load_site*.py`) are **not on disk in the shared tree
   or this worktree today** — what they learned survives only where a commit message
   carried it. The 22-site schema walk was never committed as a tool.

**Counter-evidence that bounds the policy.** The fast driver has plans for **two** mods
(`src/RimMandrake/Graffiti/northstar_plan.py`, `src/RimMandrake/Pyrelands/northstar_plan.py`);
three walks are VALIDATED (FlowWorks, Graffiti, Pyrelands); **22** mods have a modcheck
`validation.py`; the rest — dozens of mods — have no script at all. A rule that says
"debug via the north-star script" says nothing for most of the project unless it also
says what to do where none exists (§3). And the project's standing rule stays:
**the default is source; a live run must be proven needed.** This proposal governs what
happens *once* live is needed — it does not make live the default.

## 2. The process — a decision ladder

"How do we debug X?" Walk the rungs in order; stop at the first that settles it.

**Rung 0 — classify the symptom (one line, written before anything runs).**

| class | example | first instrument |
|---|---|---|
| LOAD | red error / NRE / ConfigError at startup, def missing, mod list reset | `Player.log`, **first** exception (not the loudest) |
| STATIC | wrong field, bad xpath, patch matching nothing, duplicate comp | source + def dump + `validate_patch.py` + RimSage |
| BEHAVIOUR | a mechanic does the wrong thing in a running game | **the mod's script** (this proposal) |
| VISUAL | it works but looks wrong | screenshot + human / judge — never state-only |
| HARNESS | the bridge, the driver, a site, a tool shape is wrong | the driver's own selftest + schema lint |

The class decides the instrument. The north-star script is the instrument for
BEHAVIOUR and HARNESS; it is a consumer, not a leader, for the other three.

**Rung 1 — source first** (existing rule, unchanged: *a live run must be proven needed*).
Write the one line "what can source not tell me here?" If source settles it, fix it
there, and still go to rung 5 if the mod has a script.

**Rung 2 — known-error check: run the existing script** for that mod, narrowed to the
relevant chain (`--only <chain>` once built, §4). Three outcomes:
- it goes red on the reported symptom → you already have a reproduction; go to rung 4.
- it goes red on something else → that is a finding of its own; record it, carry on.
- it stays green while the symptom is real → **the script has a blind spot**; that blind
  spot is the bug in the harness to fix first, at rung 3.

**Rung 3 — reproduce as a check.** Before touching the mod, add the check that should
catch it, in the existing PROVE / EXPECT / LIES form (`rimworld-debug-testing` §7) — it
becomes a `@bar`/component or a **diagnostic** (§4.1: recorded evidence, never a
pass/fail bar the owner did not approve). Run it; it must go **red for the reported
reason**. A check written after the fix that was never seen red proves nothing.
Ad-hoc probing is allowed here to *find* the check — at most **two** throwaway probes;
the third probe is written as a diagnostic in the plan, not in `Transient/`.

**Rung 4 — fix** (mod, site, or harness — the classification says which). One cause
per rerun where attribution matters; a new assembly goes solo.

**Rung 5 — rerun until green, and read the whole result**, not just the line you
fixed: a check that passed before and fails now is a **stop** (CLAUDE.md, grading your
own work), and a changed predicate must carry its reason in the commit.

**Rung 6 — promote and commit.** The probe that found it lives in the plan; the live
response that surprised you is saved as a fixture (§4.3); the commit names the class
(MOD / SITE / HARNESS) and the check id. Nothing that found a bug stays only in
`Transient/` or conversation.

**Rung 7 — stuck → escalate to GPT** (owner addition, 2026-10-01). "Stuck" has a
concrete trigger — any one of:
- **three** hypotheses tested by rerun and refuted, with no new kind of finding; or
- **one** result nobody can explain after the script, its diagnostics and
  `Player.log`'s first exception are exhausted; or
- **45 minutes** of wall time on one symptom without a red check reproducing it.

Mechanism: the same Codex CLI route used for this proposal's review —
`codex.exe exec --sandbox read-only --skip-git-repo-check -o answer.md` with
`--cd Transient/debug_gpt/<ID>/`, the prompt in a file there, located as
`skills/generating-images/scripts/codex_image.py`'s `find_codex_cli()` does. The brief
must contain: **(a)** the symptom in one line and its class; **(b)** the script's result
JSON (or the failing rows of it); **(c)** what was ruled out and by which check;
**(d)** the relevant source excerpts (GPT reads nothing it is not given); **(e)** one
question. 🔑 **GPT's answer is a hypothesis to test in the script, never a verdict** —
each suggestion becomes a rung-3 check or is recorded as not tested; nothing GPT says
closes an item or reaches the owner as a finding unmeasured. Prompt and answer are
committed beside the item.

**Rung 8 — still stuck → the owner**, as a question card with the evidence path.

## 3. Boundaries

### 3.1 Where it applies — by what the mod already has

| tier | the mod has | the rule |
|---|---|---|
| **A — north-star plan** | a `northstar_plan.py` (today: Graffiti, Pyrelands) | full ladder, no discretion. Every live debug of a BEHAVIOUR/HARNESS symptom starts at rung 2. |
| **B — suite, no plan** | a modcheck `validation.py` (22 mods) | a plan is ~15 lines with `USE_SUITE = True` (Graffiti's is 16) plus a site recipe; **write it at the first live debug**, then tier A. |
| **C — no script** | nothing runnable | source first. On a live debug, the reproduction is still written as a check — in a new **regression script** (a plan with diagnostics and plain checks, no owner bars, no hash). Authoring is **owed** on the trigger below, not before. |

**Regression script ≠ north star.** A tier-C script's checks are the debugger's own,
never owner-approved bars; they bind nothing and cannot green a mod. It graduates to
a north star only when the owner validates a walk. This keeps the owner's hash
ceremony out of debugging and keeps debugging checks out of his checklist.

**Authoring trigger for tier C** — a regression script is owed when **any** holds:
the mod needs its **second** live debugging session; one bug needs **more than two**
live reruns; or the mod is about to ship. Not worth it: a mod about to be cut or
absorbed; a one-line def fix source fully proves; a mod whose whole experience is
visual (the judge, not a script, is its instrument).

**Authoring cost, from what exists:** Graffiti plan 16 + site 32 lines on top of an
existing suite (about an hour); Pyrelands site 544 + preflight 858 lines (most of a
day — biome-scale site building). A tier-C script for a small mechanic lands between;
a site needing a whole generated map is the expensive case.

### 3.2 Where it does NOT apply (the script consumes the lesson, it does not lead)

| case | instrument instead | what returns to the script afterwards |
|---|---|---|
| **LOAD** — game will not load, startup NRE, ModsConfig reset | `Player.log` **first** exception; `rimworld-load-round` | a preflight log gate (as `preflight_pyrelands.py` has) if the class can recur |
| **STATIC** — def/patch/xpath/field | source, def dump, `validate_patch.py`, RimSage | nothing unless it was only visible live |
| **VISUAL** — looks wrong | screenshot + judge / owner; `rimworld-live-review` | a framing check on captured frames (§4 #7) |
| **Flyers in flight** | state read of `Pawn_FlightTracker` only — **never** unattended live flight (ruled 3×) | the state read, as a check |
| **Cold load / mod list** | `rimworld-start-prep`, `rimworld-load-round` | a tier fingerprint in preflight |
| **World and map authoring, art** | iterate by LOOKING | nothing |
| **Owner present at the bench** | his eyes; interactive is the point | what was learned is promoted after (rung 6) |
| **New companion `[Tool]` development** | `rimbridge-companion`'s one-minute build loop | the tool's schema into the lint, one fixture |

### 3.3 Minimised exceptions — criteria and audit trail

Ad-hoc live debugging on a tier-A/B mod is allowed only when one of these holds:
1. **probe budget** — up to two throwaway probes to *find* the check (rung 3);
2. **tuning by feel with the owner watching** — a number whose right value is his eye;
3. **the harness itself is down** (driver/selftest red, bridge tool missing) — fix the
   harness; the fix is a HARNESS check, not a licence to skip the mod check;
4. **emergency** — the owner's live game is broken and he is waiting.

Not exceptions: "the script is slow", "it's a one-off", "I'll add it later".
Audit trail: one ledger note on the item —
`debug-exception: <1-4>; promoted: <check id> | none because <reason>`.
Two `promoted: none` on the same mod trigger tier-C authoring.

## 4. Harness work it implies — priority order

Exists already: `src/RimMandrake/Utils/northstar_driver/` (cli, session, transport with
`MockTransport`/`MockGame` + fault injection, preflight, site, bars, judge_cli,
selftests); `rimbridge_client.py`'s **runtime** guard refusing an argument key a tool's
schema does not declare (`--list-tools`, `selftest_unknown_params.py`); modcheck's
suite/floor/northstar/status; `rimworld-debug-testing` §7's PROVE/EXPECT/LIES plan.
**None of the items below exists today** (checked 2026-10-01: the driver's flags are
`--mod --mock --fault --god --rect --fix --expect-id --allow-unmeasured
--mock-skip-site --pipeline --plan --out`; no fixtures, no classification).

| # | item | cost | benefit | why this rank |
|---|---|---|---|---|
| 1 | **Static schema lint** — AST-walk every bridge call in plans, sites and `validation.py` against a committed `--list-tools` snapshot; runs in `run_selftests.py` | ~half a day; `cceea3071` did it once by hand | catches 10-01's largest class (22 call sites, `draft=`) with the game down | cheapest per finding; offline |
| 2 | **`@diagnostic`** in plans — records evidence rows (value, expected, LIES note), never a bar; may declare `stop=` | small | gives rungs 3 and 6 a home; ends `Transient/` probes | makes the policy executable at all |
| 3 | **Classification on every non-pass row** — `class: HARNESS / SITE / MOD / UNMEASURED` + `next_evidence:`; run summary counts *new kinds* | small | the progress metric the owner's own rule asks for; harness work stops reading as mod progress | needed for §7 |
| 4 | **Prior-pass-now-fail stop** — results diffed against the last run of the same plan; a regression makes the run report STOP | small | "a check that passed before and fails now is a stop", enforced | cheap guard against predicate drift |
| 5 | **Fast re-entry** — `--only <chain>`, `--resume-from <chain>`; site kept, game stays up | medium | rerun the failing chain in seconds, not the plan | the "rerun" premise depends on it for big plans |
| 6 | **Recorded fixtures** — `--record` writes live responses; mock replays them; stamped with tool-list hash + companion DLL version, stale when either moves | medium | offline selftest exercises real shapes (several 10-01 findings were shape mistakes) | after #1, which catches much of the same class |
| 7 | **Judge framing preflight** — refuse frames with the subject clipped or the crop under a minimum | small-medium | stops a state PASS hiding a blind visual half (76/79) | specific to visual bars |
| 8 | **Saves at chain boundaries** | medium-high | resume after a crash | lowest: loading over a live game NREs (`6271d0aba`), so reload must come from the main menu — defer until a run needs it |

## 5. Roles and briefs

- **One driver at a time** — the bridge lock, unchanged (`rimflow bridge take/release`).
  A subagent that drives the bridge drives it **through the driver** (`cli.py run`,
  plan edits, diagnostics) — never raw bridge-call loops outside a plan file.
- **Model:** driving the bridge is a *live bridge write*, where Agent_Policy forbids a
  cheaper tier — so **opus**. Lint, fixtures, classification code: **sonnet**
  (checkable outcome). A call-site census: haiku.
- **A bridge-driving brief must contain:** the mod, plan path and tier; the symptom in
  one line and its class; the check that must go red; the probe budget (2); stop
  conditions (prior-pass-now-fail · three refuted hypotheses → report, do not keep
  going · `success: true` with no visible effect); forbidden acts (`ModsConfig.xml`,
  deploy unless named, `git stash` / `reset --hard` / `checkout --`); the output file
  created as a skeleton **first** (600 s watchdog); "commit the promoted check, not
  the probe".
- **Who closes:** whoever proves it, as now. Evidence is a red→green pair in the
  results JSON plus the commit; a green never seen red is not a reproduction.

## 6. Failure modes of the policy itself

| failure | how it shows | guard |
|---|---|---|
| **predicates bent to pass** | a check edited in the same commit as the fix | #4 stop; a predicate edit says why in its commit; owner bars are hash-locked already |
| **false confidence from green** | 10/10 state PASS with a blind visual half | visual bars stay UNMEASURED until judged (already true); #7 |
| **harness bugs read as mod bugs, and vice versa** | a MOD "fix" for a shape error; a HARNESS fix hiding a mod defect | #3; a MOD classification must cite the wrong def/source line |
| **only tests what it was written to find** | the owner finds bugs the script never sees | count escapes (§7); each becomes a blind-spot check |
| **script rot** | tool renames, site recipe drift, tier changes | #1 lint + #6 fixture stamps in the pre-commit selftest run |
| **authoring cost swallows small fixes** | an hour of site-building for a one-line def | §3.1: source-proven fixes need no script |
| **bridge tool fragility** | a setter says `success: true` and nothing moved | every write read back inside the plan (driver practice already) |
| **"rerun" costs a cold load** | a mod-list or assembly change between runs | the ladder stops at LOAD; batch per `rimworld-load-round`; the script reruns only on a live game |
| **ritual without findings** | runs logged, nothing new found | the metric is new *kinds* of finding, never runs or greens |

## 7. Measuring it — trial and kill criterion

Trial: **two weeks or ten live debugging sessions** on the pilot, whichever is later.
Measured from results JSON + ledger notes, never prose tallies:

1. **script-first rate** — live debug sessions that began with a script run (target ≥ 90 %);
2. **promotion rate** — findings whose evidence lives in a committed check (target 100 %);
3. **time to red** — minutes from symptom to a red check (median);
4. **new kinds of finding per run, by class** — the HARNESS share should fall;
5. **escapes** — bugs the owner found that the script did not;
6. **exceptions taken**, by criterion.

**Kill or rework if**, at trial end: HARNESS is still > 80 % of findings; or median
time-to-red is > 2× the ad-hoc baseline; or exceptions cover > ⅓ of sessions; or the
script found no MOD defect that source alone would have missed. Then it falls back to
guidance in the skill; the harness work already done stays.

## 8. Where it lives, and rollout

- **CHARTER**: one line, replacing part of "Instruments, in order" (the charter does
  not grow): *"Live debugging of a mod with a script starts with the script; a probe
  that finds something becomes a check; ladder in `rimworld-debug-testing`."*
- **The ladder**: `skills/rimworld-debug-testing`, replacing §6 — in a fresh-context
  curation session, as skills require.
- **Enforcement** (CHARTER: an enforced rule is a hook): a `PreToolUse` **warn** on a
  raw `rimbridge_client.py` call naming a mod that has a plan. Warn, not block.
- **Rollout:** phase 0 — harness #1–#4 (about a day). Phase 1 — pilot on **Pyrelands**
  (active, biome-scale) with Graffiti as the control that already runs clean. Phase 2 —
  tier-B mods get plans at their first live debug. Phase 3 — tier C by trigger only.
  No backfill sweep.

## Appendix — GPT review: adopted / rejected
(pending)
