# Work bundles: one worker takes all ready tickets of one system (draft for the owner, 2026-11-24)

Status: the owner decided the four open choices on 2026-11-24 (section 7). Nothing here is built yet.
Evidence: `design/RimMandrake/batch_worker_runs_compared_2026-11-24.md` (the batch-worker report) and the night of
2026-11-24. Related ticket: `RIMMANDRAKE_BATCH_ONE_MODS_OPEN_WORK_INTO_ONE_RUN_PIPELINE_SPLITS_PER_TICKET`.

His order (2026-11-24, about 10:00 PM PST): "I'm tired of single tickets. It's hideously inefficient, especially when
there's a bunch of small tickets lying around such as testing often produces." ... "help me design this capability to
formalize it into Maturation & Workshop pipelines!"

## 1. What we learned

| finding | evidence |
|---|---|
| Most open tickets need no code. | 22 of 34 (Explosive Knockback sweep), 12 of 18 (Gimme Some Slack close-out) [measured] |
| One context ends a list cheaply. | 30 of 34 tickets in 109 min; 18 of 18 in 73 min; no death, no compaction [measured] |
| One ticket's investigation helps the next. | Slack: the shared cord code was read once for many fixes. FlowWorks visit 11: two faults were in one staging file, found by two separate runs [measured] |
| A sort keeps too much. | Of 3 Knockback tickets the sweep kept, later runs dropped 2 as not worth the touch [measured] |
| The live proof is the expensive part. | Knockback: 20 runs after the sweep. Slack: 3 runs after the batch [measured] |
| A skipped proof comes back as cost. | Slack only: no red-first run, one wrong gate check, 2.35M weighted tokens to record the pass [measured] |
| A batch run writes few progress notes. | Slack: 0 notes in 73 min. A late death would have lost the whole context [measured] |
| One run per ticket reloads the system each time. | Tonight, FlowWorks visit 11 left 4 small faults. 4 separate runs fixed them between 9:00 PM and 9:56 PM PST, and each loaded FlowWorks again. Their token cost is UNMEASURED here. |
| Context grows with the list. | 18 tickets ended at 480k of context (81k at start) [measured] |

## 2. The capability, in one paragraph

A **work bundle** is all the ready tickets of one system, worked by one run in one context, from the reality check to
the live proof. A system is one mod, or one pipeline component (the files that one boundary page names). The pipelines
stop launching one run per ticket. They launch one run per system that has ready work. A single ticket is a bundle
of one: there is no second path.

## 3. Fix when you find it comes first

The filing gate is built and live since 7:59 PM PST 2026-11-24 (`RIMMANDRAKE_REFUSE_FILING_WITHOUT_EVIDENCE_WHY_NOT_FIX_IT_NOW`,
closed at `90cda010d8`, live hook `filing_refusal_before_stop.py`). In a helper run, `rimflow file` and `rimflow spawn`
are the one door, and they refuse a work ticket that gives no evidence why the run cannot do the work itself. Since
it landed: 14 filings, 6 with a stated "not now" reason [measured, a crude count over the ledger shards]. Runs tonight
reported "I fixed it in this run" and "I did not file it". NOT YET SEEN: an in-game tester run under the gate. The
visit-11 tester filed its 4 tickets at about 6:37 PM, before the gate landed.

The bundle takes what the gate lets through: the work that the finder truly could not do.

## 4. What a bundle run does (the role: `roles/bundle_worker.md`, to be written)

| step | who | what | why |
|---|---|---|---|
| 0. Reality sort | a program, no tokens | Run each member's acceptance test on the current build. A green test closes the member as already fixed, with the commit named. | most tickets need no code |
| 1. Read once, class all | the worker | Read the system once. Class each member: real, already fixed, or not worth the touch. Group members with one cause. Put investigations first. | one investigation informs the next |
| 2. Tests first, together | the worker | Each real member has its acceptance test. One red run for the whole set, recorded. | a skipped proof comes back as cost |
| 3. Fix in order | the worker | After each member or one-cause group: green run, a progress note, a publish. | a death loses one group at most |
| 4. One fresh reader | a fresh run | Reads the changed files once, at the end, not once per fix. | the reviewer rule, at bundle size |
| 5. One live pass | the worker, on a free game | Runs the in-game checks that the changes touch. Also tries the members that the sort kept but doubted: the game settles them. For a pipeline component, the live pass is the component running for real. | the live proof is the expensive part; do it once |
| 6. Close each member | the worker | Each member closes with the commit that fixed it. A member is refused only with a reason (it cannot be proven, it is not about this system, or another surprise). Without a reason the bundle keeps going. One table in the report. | tickets keep their identity and their test |

## 5. Right size: a guard on progress, not a count

- **Membership.** Same system, and shared files or one cause. Tickets of two systems are never in one bundle.
- **No fixed count.** A count would be a limit with no measured danger. The danger is a full context: the worker
  loses what it learned. The evidence is 480k of context after 18 tickets.
- **The guard.** After each group the run reads its own context size. Above half of its window it finishes the group
  and saves its state: what is done, what it learned about the system, what is next. The bundle then restarts in a
  fresh context from that state and keeps going, as many times as the bundle needs. The state file is the bundle's
  memory; the progress notes and the publishes after each group are its checkpoints.
- **First estimate, to be measured:** about 25k to 65k of context per member, so 10 to 15 real fixes fit one context
  [guess ~60%]. The first three bundles record context after each group; then this line gets a measured number.
- **Model.** Opus by default (the Conductor's call: the Opus sweep cost 2.40M weighted tokens, the Fable close-out
  6.44M, on unlike work). `./pipe model <Mod> fable` stays for a mod he wants on Fable.

### Who restarts a bundle

A program restarts a bundle. No seat, no window and no person restarts a bundle.

- **The restarter** is `src/RimMandrake/rimflow/left_open_continue.py`. The systemd unit of each detached run calls
  it when the run ends (`finish`, the unit's ExecStopPost), on every kind of end.
- **When the bundle machinery is built** (boundary page, promise *restart-until-each-member-has-an-outcome*): a bundle
  run that ends with a member still open is restarted in a fresh context, from the state file and the first brief.
  The end can be a saved state at a full context, a spend stop, or a death. The 3-a-day count of single runs does not
  apply to a bundle.
- **What stops a bundle:** only a stop that someone ordered (a kill by hand, a void, a pipeline pause, an owner hold,
  `pipe off`), or a restart that ended no member. A restart that ended no member writes one ALARM line in the
  Conductor log. The Conductor then acts; the bundle reads `raised`, never silently ended.
- **Until that machinery is built**, a bundle that is launched by hand is a plain detached run. The same program
  restarts a plain detached run, with three weaker rules:
  - the run must end with exit 0, and with a `LEFT OPEN:` note or an open item;
  - a spend stop is continued only when the launch carried `--continue-on-cap N`;
  - at most 3 restarts for one item in 24 hours. The next one is the alarm `DETACHED_CONTINUE_LIMIT_REACHED` in the
    Conductor log, with no launch.
  A run that dies (a non-zero exit) is not restarted by the program. The Conductor's run-end wake reports that death,
  and the Conductor relaunches the run by hand.
- **The build of this machinery follows the weaker rules too.** So the builder writes a `PROGRESS:` note and
  publishes after each part, and the Conductor holds an owed item to relaunch the build after a death or the alarm.
- **How to see it:** `work_bundle.py` status (boundary promise) shows each bundle with its step, its restarts and its
  open members. A bundle that is not `ended` and has no live run and no `restarting` state is a defect.

## 6. Where it goes in the two pipelines

- **Workshop Pipeline.** Its systems are the parts of the pipeline itself (a rimflow component, a tool, a machine)
  and the game-wide subjects. Tickets already have a home (`list_home.py`: `game:art-canon` holds 30,
  `machine:SteveDesktop` 4). The launcher (`list_dispatch.py`) launches one bundle per home with ready work, not one
  run per ticket. A home that is too wide splits by shared files. A ticket with a `mod:` home (`mod:FlowWorks` holds
  65) is one mod's work: it stays off the Workshop Pipeline and joins that mod's bundle in the Maturation Pipeline.
- **Maturation Pipeline.** A tester fixes what it finds (section 3). What it cannot fix goes to the mod's one bundle,
  not to one fixer run per fault. The steward routes a visit's failures back as one bundle. The offline builder
  already takes several bars in one run; it follows the same six steps.
- **Codex lane.** A group sent to Codex is a bundle with Codex as the builder and Claude as the reader and lander.
- **One command for a hand launch:** `./pipe bundle <Mod | home | ticket ids> --why "..."`.
- **The pipeline page** shows each bundle: its members, each member's outcome, the step it is on.

## 7. Decided by the owner (question card, 2026-11-24 about 10:20 PM PST)

1. **The form: a record that a program makes at launch.** The launcher writes one bundle record that lists its member
   tickets. Each ticket keeps its own test and closes with its own commit. Nobody files a bundle by hand.
2. **The live proof runs inside the bundle run.**
3. **How it works and how it starts.** His words: "They fix together, offline test together, then live test together.
   When they run out of context they save their state, restart, and keep going. It's the relentless agent in spirit. It
   works because the correct unit of work is a system not a bug. Same lesson we learned for mods for the maturation
   pipeline. Learning it again for the workshop pipeline and also to extend it not just to advancing a mod or system
   but to embrace all the tickets at once that make up a version."
   - So the bundle is the way both pipelines work, not a trial and not a hand command.
   - A bundle outlives a context. At a full context the worker saves its state, restarts and goes on (section 5).
   - The members of a bundle are all the tickets that make up the current version of that mod or system.
4. **No member is left unfinished without a reason.** His words: "Either they just reboot and keep fixing or they have
   a reason to not do the ticket and say so. Refused tickets may not be provable, or do not represent the system they
   were told to modify, or any number of other surprises. But there must be a reason or else the bundle keeps going."
   - A bundle ends only when each member is fixed and proven, closed as already fixed, or refused with its reason.
   - A full context, a cap or a death is never a reason. The bundle restarts.
   - Each refusal reaches the Conductor with its reason, and his daily digest.

## 8. How we will know it works

Count each bundle to the version tag (or, for a component, to its green live reading): weighted tokens and wall time
per member ended, the share proven live, the share reopened later. Compare with the 8 one-ticket runs of the same week
(2.27M weighted tokens and 102 min per ticket fixed, 2 of 10 proven live [measured]). If a bundle with its proofs
inside is not cheaper per member at the tag, keep only step 0 and step 1.
