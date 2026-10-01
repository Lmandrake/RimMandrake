# Debug process proposal — debug through the script, leave the harness behind

status: PROPOSAL, not policy until the owner approves · drafted 2026-10-01 by a FOUNDRY
subagent · revised after a GPT adversarial review (appendix) · nothing here edits
CHARTER, FOUNDRY, CLAUDE.md or a skill

## 0. The rule in five lines

1. **Source first, unchanged.** A live run must still be proven needed.
2. When a live **behaviour** bug is in a mod that has a script, **run the script first**.
3. If the script is blind to the bug, explore briefly, then **make the script see it** —
   a check that goes red for the reported reason — **before the final fix**.
4. Fix, rerun until green, and **commit the check**. Nothing that found a bug lives
   only in `Transient/` or a conversation.
5. Stuck → GPT for **hypotheses to test**, never a verdict; still stuck → the owner.

## 1. Problem and evidence

**The owner's intent:** stop debugging mods interactively and impromptu. Debug by
rerunning one fast verification script per mod and watching it get further each run;
when it cannot see a known error, extend the script until it can. The script left
behind is the testing harness. Exceptions for rapid iteration exist but are minimised.

**What 2026-10-01 showed** (each line traced to a commit, re-checked on the day):

| found | how | commit |
|---|---|---|
| Graffiti full live run: 723 calls, ~100 s | the driver | ledger note; `f4428e8f1` |
| `set_draft` called with `draft=`, tool declares `drafted=` | script red | `f4428e8f1` |
| `waitTicks` a no-op on a paused site (ticksElapsed 0) | script red | `afcd048bd`, `8b1029f7b` |
| `step_game_ticks` gives up at ~10 s; client timeout was 30 s | script | `f4428e8f1` |
| preflight read wrong result fields (dlc, weather, modal, devMode); deploy check ignored the deploy tool's skip rules | script | `f4428e8f1`, `63d1771f1` |
| **a 10/10 PASS was state-only; the judge then found 76 of 79 frames UNJUDGEABLE** (marks clipped, 544×75 px crops) | judge pass | `757ee7521` |
| 22 Pyrelands call sites passed undeclared params or named tools that do not exist — found by an ad-hoc AST walk; no committed tool | hand probe | `cceea3071` |
| a bridge-made map that is not a player home is culled on save | live, ad hoc | `1be6f727e` |
| loading over a live game NREs in `GlowGrid.GlowPool.Take`; cell temp 41.6 vs 50.4 °C until ticks run; closing the naming dialog hops to the colony map | live, ad hoc | `6271d0aba`, `cceea3071` |
| burnedDef gate allowance was 12 lines, not 4 | script red | `795c1b008` |
| one-tick-per-frame waits made a Pyrelands run take ~4 h until fixed | script | `e2879e83a` |
| MOD defect: `RUT_Barbslinger` carried two turret comps (duplicate load IDs, corrupt save) | tier load + site | `710208b9d` |
| 158 ConfigErrors in the pyrelands tier, ~111 of them one advisory | log triage | (2026-10-01 triage note) |

**Three lessons, honestly weighed.**
1. **It works, and it is fast.** A rerunnable script turned a day of findings into
   commits; most were caught because a check went red and was rerun.
2. **Most of what it found was the HARNESS, not the mods** — params, result shapes,
   timeouts, the site recipe. One row above is a mod defect. That is the expected cost
   of a young harness, and the trap: fixing the instrument can read as progress on the mod.
3. **What lived outside the script vanished.** The scratch probes used that day
   (`ns_probe_*`, `ns_load_site*`) are on disk in neither the shared tree nor this
   worktree; what they learned survives only where a commit message carried it.

**Counter-evidence that bounds the policy.** The fast driver has plans for **two**
mods (`src/RimMandrake/Graffiti/northstar_plan.py`, `src/RimMandrake/Pyrelands/northstar_plan.py`);
**22** mods have a modcheck `validation.py`; the rest have no script at all. And not every
bug has a machine oracle — visual, intermittent, emergent-AI and performance defects can
make a Boolean check actively misleading. So the rule is **narrow and mandatory** where it
fits (§3.1) and silent elsewhere, rather than broad and routinely excepted.

## 2. The process — a decision ladder

"How do we debug X?" Walk the rungs in order; stop at the first that settles it.

**Rung 0 — classify the symptom** (one line, before anything runs). Classify only enough
to choose the instrument:

| class | example | first instrument |
|---|---|---|
| LOAD | startup NRE, ConfigError, ModsConfig reset | `Player.log`, **first** exception |
| STATIC | wrong field, bad xpath, patch matching nothing, duplicate comp | source, def dump, `validate_patch.py`, RimSage |
| BEHAVIOUR | a mechanic does the wrong thing in a running game | **the mod's script** |
| VISUAL | works, looks wrong | screenshot + judge / owner |
| HARNESS | bridge tool, driver, site recipe, result shape | the driver's selftest + schema lint |

**Rung 1 — source first** (existing rule). Write "what can source not tell me here?"
If source settles it, fix it there — no script needed.

**Rung 2 — run the existing script**, the relevant part of it. Outcomes:
- red on the reported symptom → you have a reproduction; go to rung 4.
- **a check that passed before now fails** → **STOP**; that regression is the finding.
- red on something new, unrelated → record it; carry on unless it invalidates the
  reproduction or threatens state.
- green while the symptom is real → the script is blind; go to rung 3.

**Rung 3 — explore, then reproduce as a check.** One **exploration window** (§3.3):
up to 20 minutes of raw probing to understand the symptom. When it ends, write the
check that should catch the bug, in `rimworld-debug-testing` §7's PROVE / EXPECT / LIES
form, and see it go **red for the reported reason** before the final fix. "For the
reported reason" means the check reads the same quantity the symptom is about — not a
correlate. A check never seen red proves nothing.

**Rung 4 — fix** the mod, the site or the harness, as the class says. Independent
fixes may share a rerun; isolate only where fixes could interact (a new assembly
still goes solo).

**Rung 5 — rerun until green, and read the whole result.** A changed predicate
carries its reason in the commit.

**Rung 6 — commit the check.** The commit names the class (MOD / SITE / HARNESS)
and the check id. The probe that found it is thrown away; the check stays.

**Rung 7 — stuck → GPT** (owner addition, 2026-10-01). Stuck is **any one** of:
- **20 minutes** without new evidence that tells hypotheses apart;
- **two genuinely different** causal hypotheses refuted;
- a result that **contradicts the current model** of the system after the script,
  its checks and `Player.log`'s first exception are exhausted.

*Mechanism:* the Codex CLI route used for this proposal's own review — `codex.exe exec
--sandbox read-only --skip-git-repo-check -o answer.md "Read prompt.md …"`, run from
`Transient/debug_gpt/<ID>/` with stdin closed, binary located by `find_codex_cli()` in
`skills/generating-images/scripts/codex_image.py`. It reasons at xhigh (~5–10 min).
⚠️ Measured today: Codex read the UTF-8 prompt through Windows PowerShell and saw
`°` and `§` as mojibake, then judged the text "corrupt". The prompt must say "read as
UTF-8" or be ASCII. A small maintained wrapper (§4 #2) should own both.

*The brief must contain:* the symptom in one line and its class; expected vs actual;
last-known-good state and what changed since; the mod / tier / companion versions; the
script's result JSON (the failing rows); `Player.log`'s first exception; what was ruled
out and by which check; the relevant source excerpts (GPT reads nothing it is not
given); and one question: **"rank the hypotheses and give the cheapest test that tells
each apart."**

🔑 **GPT's answer is a hypothesis, never a verdict.** Each material claim is tested
with the strongest fitting instrument — a script check, source, the log, a mod-set
bisection — and nothing GPT says closes an item or reaches the owner as a finding
until it is tested. Prompt and answer stay in `Transient/` (14-day shelf); what
survived testing goes in the commit and the item.

**Rung 8 — two GPT rounds without new evidence → the owner**, as a question card with
the evidence path.

## 3. Boundaries

### 3.1 Where it is mandatory — all five must hold

1. Source and static checks are exhausted; the bug needs live evidence.
2. The symptom is **machine-observable behaviour** — not appearance, not tuning by feel.
3. The mod has a runnable script and a site recipe that already passes its selftest.
4. Running it needs no cold load, no mod-list change, no unattended flight, and does
   not touch the owner's saves.
5. A faithful check can reasonably be written in **30 minutes**.

When any fails, the rule does not bind; the agent says which one in a line on the item.

### 3.2 Where it does not lead

| case | instrument instead | what comes back to the script |
|---|---|---|
| LOAD failures | `Player.log` first exception; `rimworld-load-round` | a preflight log gate, if it can recur |
| STATIC defects | source, def dump, `validate_patch.py`, RimSage | nothing unless only visible live |
| VISUAL quality, tuning by feel | screenshot + judge / owner; `rimworld-live-review` | a framing check on captured frames |
| intermittent, statistical, performance | none yet — until a seed or sampling method exists | the seed, once found |
| flyers in flight | `Pawn_FlightTracker` state read only — **never** unattended live flight (ruled 3×) | the state read, as a check |
| cold load, mod list, save migration | `rimworld-start-prep`, `rimworld-load-round`, `rimworld-savegame` | a tier fingerprint in preflight |
| world, map, art authoring | iterate by LOOKING | nothing |
| owner at the bench | his eyes; interactive is the point | **a check afterwards when the lesson is machine-observable** |
| new companion `[Tool]` | `rimbridge-companion`'s build loop | the tool's schema into the lint |

### 3.3 The exploration window — the one exception, and how it is audited

Raw live probing on a mod in scope is allowed in **one window of up to 20 minutes**,
opened by a ledger note **before the first call** carrying one factual code:

| code | means |
|---|---|
| `BLIND_SCRIPT` | the script ran green while the symptom is real (rung 3) |
| `NO_RELEVANT_PLAN` | the mod has no script covering this area |
| `NON_MACHINE_ORACLE` | the symptom can only be judged by eye |
| `HARNESS_FAILED:<selftest id>` | the driver itself is broken — named, not asserted |
| `OWNER_SUPERVISED` | he is watching and steering |
| `EMERGENCY_RECOVERY` | his live game is broken and he is waiting |

The window ends at 20 minutes or at a stable reproduction, whichever comes first. It
then closes with one of: **promoted** `<check id>` · **returned to source** · **stopped**
with evidence. **FOUNDRY cannot renew a window on its own**; a second window on the
same symptom needs BENCH or the owner. Not codes: "the script is slow", "one-off",
"I'll add it later".

### 3.4 Mods with no script

No north star is built pre-emptively. A mod's **second** live incident forces a
recorded decision on the item: write a **regression script** (a plan with checks only,
no owner bars) — the default when the reproduction is stable — or record why not
(cut soon, purely visual, one-line def fix). Cost to expect, from what exists: Graffiti's
plan is 16 lines and its site 32 on top of an existing suite (about an hour); Pyrelands'
site is 544 lines and its preflight 858 (most of a day, biome-scale).

**Regression checks are not north-star bars.** They bind nothing, cannot green a mod,
and never enter a hashed `## north star` section; they become bars only if the owner
validates them into a walk. Owner bars stay his; debugging checks stay ours.

## 4. Harness work

**Day one** (needed for the rule to be executable or already proven valuable):

| # | item | cost | why now |
|---|---|---|---|
| 1 | **Static schema lint** — AST-walk every bridge call in plans, sites and `validation.py` against a committed `--list-tools` snapshot; runs in `run_selftests.py` | ~half a day | 10-01's largest finding class (22 call sites, `draft=`) with the game down; `cceea3071` did it once by hand. Worth building whatever the owner rules on the rest |
| 2 | **A place for a promoted check that is not a bar** — a plain `@check` in plans (same PROVE/EXPECT/LIES fields, reported separately from bars) — plus the small **GPT-consult wrapper** (UTF-8-safe, read-only, prompt and answer files) | small | without #2 a promoted check would have to be a bar, which the owner's hash ceremony rightly refuses |
| 3 | **Prior-pass-now-fail STOP** — diff against the last run of the same plan | small | the one existing rule a script can enforce for free |

**Backlog, built only when a pilot incident needs it** (GPT's point, adopted: it is a
product backlog, not a prerequisite): `--only <chain>` / `--resume-from`; recorded
fixtures stamped with tool-list hash and companion DLL version; a judge framing
preflight (the 76/79 case); saves at chain boundaries (expensive: reloading over a
live game NREs, `6271d0aba`, so a resume needs a main-menu load); a HARNESS/SITE/MOD
field on result rows. What exists and is reused, not rebuilt: `northstar_driver/`
with its mock transport and fault injection, `rimbridge_client.py`'s runtime guard on
undeclared params, modcheck's suite and north-star machinery.

## 5. Roles and briefs

- **One driver at a time** — the bridge lock, unchanged. A subagent that drives the
  bridge drives it **through the driver** and its plan; its exploration window is
  opened and closed in the ledger like anyone's.
- **Model:** driving the bridge is a *live bridge write*, where Agent_Policy forbids a
  cheaper tier. Lint, wrapper and check code with a checkable outcome are cheaper-tier
  work. (Model names live in Agent_Policy and nowhere else.)
- **A bridge-driving brief contains:** mod, plan path, tier; the symptom and its class;
  the check that must go red; the window rule (20 min, one, code first); stop
  conditions (prior-pass-now-fail · two refuted hypotheses → report · `success: true`
  with no visible effect); forbidden acts (`ModsConfig.xml`, deploys unless named,
  `git stash` / `reset --hard` / `checkout --`); the output file created as a skeleton
  first; "commit the check, not the probe".
- **Who closes:** whoever proves it. Evidence is a red→green pair and the commit.

## 6. Failure modes of the policy itself

| failure | guard |
|---|---|
| **checks bent to pass**, or a convenient proxy written to get a fast red | "red for the reported reason" (rung 3); predicate edits explain themselves; owner bars hash-locked |
| **false confidence from green** (10/10 state PASS, blind visual half) | visual bars stay UNMEASURED until judged — already true in the driver |
| **harness bugs read as mod bugs, and vice versa** | the commit names the class; a MOD claim cites the wrong def or source line |
| **the script tests only what it was written to find** | escapes are counted in the pilot; each one becomes a check |
| **harness work swallows the mod work** | the 30-minute test (§3.1 #5); harness minutes measured in the pilot |
| **script rot** — tool renames, site drift | #1 lint in the pre-commit selftest run |
| **the exception becomes the norm** | codes are factual, windows are capped, FOUNDRY cannot self-renew |
| **"rerun" costs a cold load** | out of scope by §3.1 #4; batch per `rimworld-load-round` |
| **ritual without findings** | the pilot measures time and reuse, never run counts or greens |

## 7. Pilot, measurement, kill criterion

**Scope:** Graffiti (mature, ~100 s plan) and **two bounded Pyrelands chains**, only
after their site passes its selftest — Pyrelands alone would confound the process
with building its instrument. Eligible incidents only (§3.1); excluded classes stay
out of the denominator.

**Length:** 10 eligible incidents or 14 days, whichever is longer; four-week cap.

**Per incident, recorded in the item's ledger notes:** hands-on minutes to a
trustworthy reproduction; total minutes to resolution; bridge occupancy and cold loads;
harness minutes vs mod minutes; whether a faithful red-before-green check resulted;
window code and duration; recurrence within 14 days; whether the check ran again later
and found anything.

**Baseline:** reconstructed from the 2026-10-01 commits and notes where timestamps
allow; where they do not, the pilot reports absolute cost and says it is not a speed
comparison.

**Adopt** if ≥ 70 % of eligible incidents get a faithful red check within 30 minutes,
median resolution is ≤ 1.5× baseline (or acceptable to the owner in absolute terms),
and harness work is < 40 % of pilot effort.
**Kill or rework** if any two hold: < 50 % get a faithful red check · median > 1.5×
baseline · harness > 50 % of effort · windows needed in > ⅓ of incidents · a promoted
check later passes its own original symptom · no check is reused in the pilot or the
14 days after. The harness work already done stays either way.

## 8. Where it lives, and rollout

- **CHARTER**: one line, replacing part of "Instruments, in order" (the charter does
  not grow): *"A live behaviour bug in a mod with a script starts with the script; the
  probe that finds it becomes a check; ladder in `rimworld-debug-testing`."*
- **The ladder**: `skills/rimworld-debug-testing`, replacing §6 — in a fresh-context
  curation session, as skills require.
- **Enforcement** (CHARTER: an enforced rule is a hook) — after the pilot, not before:
  a `PreToolUse` **warn** on a raw bridge call naming a mod with a plan and no open
  window note.
- **Rollout:** day-one harness #1–#3 → pilot (§7) → owner ruling on adopt/kill →
  CHARTER line + skill section → tier-B mods get a plan at their first in-scope
  incident; no-script mods by §3.4 only. No backfill sweep.

## Appendix — GPT review: adopted / rejected

Codex CLI, gpt-5.6-sol, read-only sandbox, 2026-10-01. The prompt and raw answer
were committed in the same commit as this file (Transient, 14-day shelf; git keeps them).

**Adopted**
- *It confuses debugging with harness development* → rung 3 now allows exploration
  first; the check must precede the **final fix**, not all investigation.
- *"Two probes" is unenforceable* → one coded, 20-minute exploration window that
  FOUNDRY cannot renew (§3.3).
- *"Red for the reported reason" lacks an oracle* → defined (same quantity as the
  symptom, not a correlate), and non-machine oracles excluded (§3.1 #2).
- *Sharper scope* → the five-condition test (§3.1), including the 30-minute feasibility test.
- *Intermittent / statistical / performance defects* → excluded until a seed or
  sampling method exists.
- *Unrelated failures conflict with the regression stop* → split: prior-pass-now-fail
  stops; a new failure stops only if it invalidates the reproduction.
- *"One cause per rerun" wastes bridge time* → independent fixes batch.
- *Owner-present BENCH is a loophole* → exempt from the script, not from leaving a check behind.
- *Tier B is falsely cheap; don't force a harness on a second incident* → the second
  incident forces a **decision**, defaulting to a regression script; the costs are stated.
- *Harness roadmap is a backlog, not a prerequisite* → day one is lint, a non-bar
  check type with the consult wrapper, and the regression stop; the rest waits for a pilot need.
- *Metrics reward labels and are gameable; there is no baseline* → time and outcome
  metrics, reconstructed baseline or an honest "absolute only".
- *Do not require the pilot to find a mod defect source would miss* → dropped from
  the kill list: the process preserves reproductions; discovery is a separate claim.
- *Pyrelands is a bad sole pilot* → Graffiti plus two bounded Pyrelands chains.
- *GPT rung* → 20-minute / two-hypotheses / contradicts-the-model trigger; a richer
  brief; ask for ranked hypotheses with discriminating tests; test with the strongest
  instrument, not only the script; two rounds then the owner; a maintained wrapper;
  transcripts stay in Transient and only tested conclusions are committed.

**Rejected**
- *"The proposal text contains encoding corruption"* — false for the file: it is
  clean UTF-8 (checked: zero mojibake sequences). Codex read it through Windows
  PowerShell's default codepage and corrupted `°`/`§` itself (visible in its own
  transcript as `41.6 vs 50.4 A�C`). Kept as evidence for the wrapper requirement,
  not as a defect in the proposal.
- *Defer the non-bar check type* — without it, the owner's core instruction ("additions
  are made to the north-star script") has nowhere to go except his hash-locked bars.
  It stays on day one, kept minimal.
- *Commit nothing of the GPT exchange* — partially: the brief and answer of **this**
  policy review are committed in Transient as the record the owner asked for;
  debugging consults follow the Transient-only rule above.
