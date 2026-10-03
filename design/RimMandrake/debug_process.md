# How we debug — debug through the script, leave the harness behind

status: **OFFICIAL**, owner rulings 2026-10-01 · binds BENCH, FOUNDRY and every subagent

## 0. The rule

1. **Every mod has a functional script.** Bugs in a mod are debugged by rerunning it and
   watching it get further each run. The script grows with the code.
2. **Source first, still.** A live run must be proven needed.
3. A live **behaviour** bug starts with **the mod's script**.
4. If the script cannot see the bug, poke live as long as it takes. **The session ends
   by writing what it learned into the script**: a check that goes red for the
   reported reason before the final fix, plus guards for the theories that proved
   false but are worth knowing. Nothing that found a bug lives only in `Transient/`
   or a conversation.
5. Stuck → GPT, **early**, for hypotheses to test, never for a verdict. Still stuck
   → the owner.

The owner, 2026-10-01, typed: *"Initial debugging will always be debugging new code as
well as new validation scripts. And that's good. They evolve together."* And on poking:
*"It's more a sense of writing the final acceptance from a poking session. Capture what
you learned in terms of tests to detect this from now on. Including other theories that
proved false but would be informative to know."*

## 1. The build pause — 2026-10-01, LIFTED 2026-10-02

**Lifted by the owner 2026-10-02, typed: *"Build pause is lifted."*** The rest of this section is
the record of what the pause was; the first-script contract (§2) still applies to every mod.

Owner, typed: *"It's worth slowing or stopping all current build to get this in place
everywhere and really exercise northstar. I really do mean stop and start working a new
way. This would be as big a need as rerunning clean dirty code is now."*

**Stopped** (decision taken by question card, 2026-10-01): **all new content**. That
means new mods, new defs, new mechanics, biome work, roster sittings, and art jobs for
content that is not built yet. Work in flight is brought to a committable state,
committed, and its remainder filed as an item. Then it stops.

**Allowed during the pause:**
- **Bug fixes** to existing mods, done by this process.
- **First scripts** (§2) and the harness they need: `modcheck`, `northstar_driver`,
  site recipes, companion `[Tool]`s, and these four items in order: (1) the static schema
  lint over bridge calls; (2) the prior-pass-now-fail diff; (3) the GPT-consult wrapper
  (§5); (4) `northstar_driver run` writing its result through `modcheck.status.record_run`
  (the driver does not record into `modcheck_status.json` today).
- Load rounds that run first scripts. They are batched per `rimworld-load-round` and
  remain on the Charter's expensive list.
- **Exceptions:** only by the owner's own word, quoted on the item. A BENCH request is
  not one until he says it.

**DONE: what lifts the pause.** The pause lifts when **both** of these hold:

- **(a) Every mod has a committed first script.** "Every mod" means every folder
  matching `src/*/*/About/About.xml`; the glob is the set, not a number in a doc. It
  held 164 on 2026-10-01, 48 of them `*ArtOverride`. "Has a script" means it meets §2:
  its own `validation.py` or membership in a family script, plus a walk whose
  `## must be true` declares coverage.
- **(b) Every mod has a recorded live run.** In
  `infrastructure/state/modcheck_status.json`, every mod (or its family key) holds a
  run entry at its current hash. That entry is not `NEVER RUN` and not `REFUSED`. Every
  `RED` component is either fixed or filed as a named item that says which it is: a
  MOD, SITE or HARNESS defect.

A RED that is filed does not hold the pause; it is bug work, which continues anyway. When
`modcheck status` plus the glob census show (a) and (b), the seat that saw it tells the
owner in one line with the census output, and the pause is over. Umbrella item:
`NORTHSTAR_EVERYWHERE_PROGRAM_1`.

**Keep the bridge busy** (owner, 2026-10-01, typed: *"Multitasking to keep the bridge active is a good
idea. That's what we want to maximize. Live bridge usage. In fact that's a great metric to track."*).
The pause is bounded by live-run throughput, not authoring. So the bridge holder always has a next
script to run: authors work offline in parallel behind the current live run, each delivering a
READY-TO-RUN script with a live-run sheet, and the holder never sits on the bridge between runs
(release it when truly idle). Nobody blocks on "writing everything first". The tracked metric is
bridge utilization (active driving and ticking time over held time): `NORTHSTAR_BRIDGE_UTILIZATION_1`.

## 2. What a first script must contain

**Use the existing machinery and build no parallel system.** A first script is a modcheck
`Suite` in `src/<tier>/<Mod>/validation.py`. Its chains run on a live site, and
`northstar_driver` runs the same suite fast (`USE_SUITE = True` in a
`northstar_plan.py`). A `@bar` in a plan is for the owner's validated bars only.
Functional checks belong in the suite.

1. **Intended-function bars.** Write one line per thing the mod is for, in the mod's walk
   `design/validation_walks/<tier>/<Mod>.md` under **`## must be true`**. That section is
   agent-owned and not hashed. Read the lines from the mod's design doc, its `About.xml`
   description and its defs and C#. Never invent them: a line with no source is a
   guess. A mod with no walk gets one; the walk is part of the first script.
2. **One cheap state check per line.** Each line gets a chain component that reads game
   state back: a def present with the right field, a thing spawned, a hediff applied, a
   job run, a setting toggled off with the effect gone. Use the `t.*` verbs and read
   `success`/`foundCount`/`notFound` fields; never substring a payload. A component
   that could not ask records `UNMEASURED`, never PASS. Prefer short, local, cheap
   chains; depth comes later, as bugs teach it.
3. **Coverage declaration.** Every `## must be true` line ends with `→ <chain>.<component>`
   or `→ UNCOVERED: <why>`. The why is a §4 boundary, or a missing tool named as an item.
   The arrows are the coverage; a line with neither counts as uncovered and missing.
   Every Mod Settings toggle goes in `suite.toggles` (CLAUDE.md "superb Mod Settings").
4. **Ruled-out theories** go in the walk's `## anti-guessing notes`, one line each:
   `RULED OUT: <theory> — <the check or source line that killed it>`. If a machine can
   watch it, it also gets a guard component that goes red if the ruled-out cause ever
   becomes true.
5. **Selftest offline first.** Run it under `--mock` and it must exit clean before it
   costs a bridge minute. A run recorded through `modcheck` is the record (§1 DONE (b)).

**The `*ArtOverride` family: one parametrized script, not 48.** A single family suite
covers every art-override mod. It reads its member list from the glob at run time, so a
new override is covered without an edit. Per member it checks that the overridden def's
graphic resolves to our texture path, not the donor's (the texture binds by texPath); that
`Player.log` has no missing-texture or magenta error for that path; and that every facing
the def needs is present. It records under one family key whose run entry lists the members. A member that needs a
behaviour check of its own graduates to its own `validation.py`.

**Folded mods.** A mod folded into a composed mod, such as a biome folded into
`RimMandrake.Biomes`, is covered by the composed mod's script only if that script's
`## must be true` names the member's lines.

**How passing is recorded.** `modcheck.status.record_run`, writing
`modcheck_status.json` under a lock, is the only record. It is hash-bound: any edit to
the mod makes it STALE (the `code_review_status.py` discipline). **The functional script
passed** = `GREEN` (no hashed north star), or `DRAFT-CHECKLIST` / `PENDING-OWNER-REVIEW`
(passed; only the owner's layer is incomplete). **Not passing** = `RED`, `REFUSED`,
`NEVER RUN`.

## 3. The debugging ladder

Walk it in order and stop at the first rung that settles the bug.

- **Rung 0: classify.** One line, only enough to choose the instrument. **LOAD** (startup
  NRE, ConfigError, ModsConfig reset) → `Player.log`'s **first** exception. **STATIC**
  (field, xpath, patch matching nothing, duplicate comp) → source, def dump,
  `validate_patch.py`, RimSage. **BEHAVIOUR** → the mod's script. **VISUAL** → screenshot
  plus judge, or the owner. **HARNESS** (bridge tool, driver, site, result shape) → the
  driver's selftest and the schema lint.
- **Rung 1: source first.** Write down what source cannot tell you. If source settles
  it, fix it there.
- **Rung 2: run the script**, the relevant chains. Act on the outcome:
  red on the symptom → a reproduction, rung 4 · **a check that passed before now fails →
  STOP**, that regression is the finding · a new unrelated red → record it, carry on
  unless it invalidates the reproduction or threatens state · green while the symptom is
  real → the script is blind, rung 3.
- **Rung 3: poke, then write it down.** No clock. Probe live freely, through
  `python.exe` and holding the bridge. The poking ends **when it has taught you the
  cause**, and it ends by writing a check that goes **red for the reported reason**
  before the final fix. That means the check reads the same quantity the symptom is
  about, not a correlate. A check never seen red proves nothing. Write the informative
  dead theories as §2.4 notes and guards. Scratch probes are thrown away and only the
  checks stay: on 2026-10-01 the `ns_probe_*` scratch files vanished, and what they
  learned survived only in commit messages.
- **Rung 4: fix** the mod, the site or the harness, as the class says. Independent fixes
  may share a rerun; isolate only fixes that could interact. A new assembly always goes
  alone.
- **Rung 5: rerun until green and read the whole result.** A changed predicate carries
  its reason in the commit. Never weaken a check to pass. Loosening one is a script
  defect unless the commit shows the old predicate was wrong.
- **Rung 6: commit the check.** The commit names the class (MOD / SITE / HARNESS) and the
  check id.
- **Rung 7: stuck → GPT** (§5). **Rung 8:** two GPT rounds, no new evidence → the owner.

**At the bench** (decision taken by question card): interactive work with the owner is the
point there, and the script does not lead. **Every bench session leaves a test behind
whenever a machine can check the lesson.** It is written that sitting or filed as a
named item before the session ends.

**Ablation is later and explicit.** Owner: *"We can ablate unnecessary testing later if it
becomes slow or onerous."* Until he or a review says so, coverage grows and nothing is cut
for speed.

## 4. Boundaries — where the script does not lead

| case | instrument instead | what still comes back to the script |
|---|---|---|
| engine load errors | `Player.log`, **first** exception (not the loudest); `rimworld-load-round` | a preflight log gate if it can recur |
| def / patch bugs | offline: source, def dump, `validate_patch.py`, RimSage | a state check only if it was visible only live |
| visual quality, tuning by feel | screenshot + judge / owner; `rimworld-live-review` | a framing check on captured frames |
| flyers in flight | `Pawn_FlightTracker` state read **only**; never unattended live flight (ruled 3×) | the state read, as a check |
| cold load, mod list, save migration | `rimworld-start-prep`, `rimworld-load-round`, `rimworld-savegame` | a tier fingerprint in preflight |
| world, map, art authoring | iterate by LOOKING | nothing |
| performance, intermittent, statistical | none yet; no Boolean check, which would mislead | the seed or sampling method, once one exists |

## 5. GPT consults — asked early

**Trigger** (decision taken by question card), any **one** of: 20 minutes without new
evidence that tells hypotheses apart; **two** genuinely different causal theories
refuted; a result that makes no sense against the current model of the system.

**Mechanism.** Use the Windows Codex CLI, read-only. Run
`codex.exe exec --sandbox read-only --skip-git-repo-check -o answer.md "<read prompt.md as UTF-8 …>"`
from `Transient/debug_gpt/<ITEM_ID>/` with stdin closed. Locate the binary the way
`find_codex_cli()` in `skills/generating-images/scripts/codex_image.py` does. ⚠️ Through
Windows PowerShell's codepage, Codex reads `°`/`§` as mojibake. Say "read as UTF-8" in
the prompt, or write it in ASCII. The maintained wrapper (§1 item 3) will own both.

**The brief contains:** the symptom and its class; expected vs actual; last-known-good
state and what changed since; mod, tier and companion versions; the failing result rows;
`Player.log`'s first exception; what was ruled out, by which check; the relevant source
excerpts (GPT reads nothing it is not given); and one question: **"rank the hypotheses and give the cheapest test that tells each apart."**

🔑 **GPT's answer is a hypothesis, never a verdict.** Test each material claim with the
strongest fitting instrument: a script check, source, the log, or a mod-set bisection.
Nothing GPT says closes an item or reaches the owner as a finding until it has been
tested.

**Retention** (decision taken by question card). The prompt and answer stay in
`Transient/` for the 14-day shelf. Only survivors are committed, into the script, the
walk and the commit: confirmed tests, and false theories worth knowing.

## 6. Who approves scripts, and the owner's bars

Owner, typed: *"Agents absolutely can build and approve validation scripts and declare
passing. I will periodically release adversarial agents and even gpt reviews to criticize
them or grow them."*

- **Functional scripts are agents' work, approved by agents.** A script runs green →
  the mod passes. No owner step.
- **The owner's validated north-star bars are a separate layer and are untouched.** These
  are the hash-bound `## north star` sections in walks with `state: VALIDATED`;
  `modcheck floor --all` re-derives which. CLAUDE.md's hash rule stands: a functional
  script never edits a hashed section. An agent may still draft north-star lines (DRAFT),
  but only his `modcheck validate --owner-said` binds them.
- **Periodic adversarial review.** The owner releases adversarial agents and GPT reviews
  against the scripts, on his clock (`NORTHSTAR_ADVERSARIAL_REVIEW_1`). A weakened, proxy
  or never-red check they find is a script defect. It is fixed and recorded like any bug.

## 7. Briefing a bridge-driving subagent

- **One driver at a time.** The holder takes the bridge lock; the subagent drives through
  the driver or `modcheck`, never around them.
- **The brief contains:**
  - the mod, its `validation.py` / plan path, the tier; the symptom and its class; the
    check that must go red;
  - stop conditions: prior-pass-now-fail; two refuted theories (report back, with the
    GPT trigger); `success: true` with no visible effect;
  - forbidden: `ModsConfig.xml`, deploys and `modcheck run` (it swaps the mod list)
    unless named; `stash` / `reset --hard` / `checkout --`; unattended flyer flight.
- **"End the poking by committing the check and the ruled-out notes; throw the probe
  away"**, and create the output file as a skeleton first.
- **Model:** a live bridge write follows `Agent_Policy.md`, which is never restated here.
- **Who closes:** whoever proves it. The evidence is a red→green pair and the commit.

## 8. Why — the evidence of 2026-10-01

One day of script-driven work on Graffiti and Pyrelands turned findings into commits:
`draft=` vs `drafted=` and a ~10 s `step_game_ticks` give-up (`f4428e8f1`); a no-op
`waitTicks` on a paused site (`afcd048bd`); a 10/10 state PASS hiding 76 of 79
unjudgeable frames (`757ee7521`); 22 call sites with undeclared params or missing tools
(`cceea3071`); one-tick waits stretching a run to ~4 h (`e2879e83a`); one mod defect,
`RUT_Barbslinger`'s two turret comps (`710208b9d`). Lessons: **rerunnable checks work and
are fast**; **most early findings are HARNESS, not MOD** (why the commit names the class);
**what lived outside a script vanished**.

GPT's adversarial review of the draft (prompt and answer: `Transient/debug_process_gpt/`,
kept in history) is adopted where it set: a red check before the *final* fix, not all
investigation; "red for the reported reason" defined; non-machine, intermittent and
performance defects out of scope (§4); prior-pass-now-fail separate from a new unrelated
red; independent fixes batch; the bench owes a test; GPT asked early, tested by the
strongest instrument, conclusions only committed. Superseded by the owner: the 20-minute
exploration window (now no clock), never-owner-approved non-bar checks (now
agent-approved functional scripts), and the pilot (now a full stop and a new way of
working).
