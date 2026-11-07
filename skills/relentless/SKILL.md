---
name: relentless
description: Operate, read, stop, debug or work inside the Relentless Pipeline (src/RimMandrake/rimflow/relentless.py, rm-relentless.timer, relentless_rules.json) and its Builder and Judge workers. Use when setting or repairing a contract, running boxrun or finish, reading why an item is held, churning, blind-failed or checker_lost, writing a proof the walled Marker must run, staging a live proof, changing the supervisor or its rules, stopping or restarting it, or deciding whether work belongs in it at all. The pipeline is STOPPED by the owner as of 2026-11-06 and may change at his sitting, so read this before assuming it is running or restarting anything. For a shell-loop agent on one whole piece of work, use artisan instead.
---

# Relentless

🔴 **Status, 2026-11-07: STOPPED by the owner.** *"Stop the pipeline immediately. This is broken."*
(2026-11-06 18:22 PST). Item `PIPELINE_RETHINK_OWNER_STOPPED_BURN`, which holds the undo list; undo
only at his sitting. `rm-relentless.timer` read inactive and `D:\ClaudeWork\rimmandrake\dispatcher\PAUSE`
exists. **Everything here describes a stopped system that may change or go away when he sits down.**
Check the item and the timer first. Don't restart it, enrol into it, or file work on the assumption it
will pick that up.

What it had delivered when he stopped it: about 360 items closed a day at about 1.1M tokens each, 0 of
135 mods accepted, 67 pass, 40 fail and 169 no answer from live proofs in 24 hours. He asked: *"Why are
you so intelligent when I ask questions, but so foolish in this automated loop?"*
(`D:\Luke\dev\MandrakeWorkflows\artisan\RESEARCH.md`). So a green here means a contract was met, never that
he accepts the work.

**Traps from about 130 filed lessons are in [references/traps.md](references/traps.md).** Read its section for
what you're doing before you set a contract, write a proof, finish an item or touch the supervisor.

## What it is

Two parts named apart, so one can change without the other (owner, 2026-11-03):

- **The Relentless Pipeline:** `src/RimMandrake/rimflow/relentless.py` and its `relentless_*.py` modules, a
  program with no AI. `tick` runs from `rm-relentless.timer` out of one pinned release a day
  (`<root>/release/current`), and reads data from its own clone (`<root>/books`). `<root>` is
  `/home/mandrake/rm/relentless`.
- **The workers in its places:** Relentless-style Builders and Judges, defined in
  `D:\Luke\dev\MandrakeWorkflows\relentless\workers\BUILDER_JUDGE.md` (the blindness contract lives there), run
  as the agents `worker_agent` and `checker_agent` in the rules.

**The item is the owner, workers are replaceable.** *"just don't let go until it's done."* The record on disk
holds the goal, proof, attempts, learned notes and a fencing generation; a worker may die and the next one
sits in the same clone.

**What belongs in it** (owner, 2026-11-06): *"It's a builder/test-builder/judge pipeline, not an everything
pipeline...."* It's for work that needs building, a built test and a judge. Approved art, deploys, one-off
commands and readings are done directly. For a single defect that needs live observation, use a Test Pilot
sitting; for whole work judged by the owner's eye, `artisan`.

## Where things are

| | |
|---|---|
| Limits and rules, as data | `src/RimMandrake/rimflow/relentless_rules.json` |
| One item's record | `<root>/store/items/<ID>/` (`state.json`, `attempts.jsonl`, `learned.md`, `receipts/`) |
| Run results and launch errors | `<root>/store/runs/roles/rm-relentless-check-*.{json,err}` |
| Host journal | `<root>/store/journal.jsonl`; live rows `<root>/live/runs.jsonl` |
| Item clones | `<root>/clones/<ID>/` |
| Pipeline design | `design/RimMandrake/relentless_owner_design_2026-10-31.md` |
| Worker design | `design/RimMandrake/relentless_agent_design_2026-11-01.md` |
| Daily release | `design/RimMandrake/relentless_daily_release_2026-11-06.md` |

🔴 **Read a number from the rules, not the design.** The owner design's table still says
`same_failure_limit` 3; the rules said 2 on 2026-11-07. Token limits are advisory (owner, 2026-11-02: *"make
token limits advisory at this time everywhere. Nothing gets killed or stopped for that"*).

## The state machine

```
queued → running → candidate → checking → closing → done
            │ snag, lost, stale, full         │ FAIL, or live check broken
            └──────── stopping ───────────────┘   (gen += 1 first, then stop, then confirm gone)
                         └→ back to queued, ahead of fresh items
held: out of line until unhold. retired: the ledger closed it from outside. blocked: waits on a named item.
```

- **Fencing:** every worker verb names `--gen`. A wrong gen exits 3, FENCED, and writes nothing. It stops a
  *stale* worker by accident; it isn't a sandbox.
- **Changing tack:** `same_failure_limit` returns of one class, or `unchanged_returns_limit` returns of any,
  change the approach (`build` → `pilot` or `redesign`). A `contract_*` snag goes to redesign at once. After
  `max_approach_changes`, the item is held for the Conductor (`relentless_strikes.py`).
- **Who hears about a hold:** tooling holds (`proof_weak`, strikes, a non-flyer game hold) are the Conductor's.
  Only an `owner_call` naming a section of `delegation_policy.md` §2, or a flyer's flight, sets needs=owner.
- **An inability to measure is not a fail** (owner, 2026-11-04). UNMEASURED sends no work back and changes no
  approach; it's reported up for repair.

## Being a worker

Your brief gives your item and generation. Run the verbs with `python3 src/RimMandrake/rimflow/relentless.py
<verb> --help`: `beat`, `learn`, `contract`, `rebind`, `boxrun`, `snag`, `finish`, `help`, `challenge`.

**The contract is set once, so spend your care before the first call.** Only a redesign or proof-only worker
may change it. Any worker may add a missing live line or adapter, since that only asks more, and may propose a
binding repair with `rebind`, which an independent judge rules on. Before `contract`:

1. Decide the `--live` line and the `--game` clauses, and write `infrastructure/state/live_proofs/<ID>.txt`.
2. Write the test first. Run the exact proof command green. Then run `relentless.py boxrun`, which runs it in
   the Marker's box at HEAD.
3. Spell the proof the way the extractor reads it, and aim it only at what the box can reach (traps file).
4. A worker who finds the set contract factually unsatisfiable snags `contract_*`, and doesn't edit the named
   instrument to get through.

**Landing and finishing:** publish first, and start every commit subject with `<ID>:`. Finish on a commit that
did the work. The box replays the ledger and code review from the candidate's *parent*, so land those one commit
earlier and finish on a later commit outside them. Fire a `reading=` service after publish and before finish.

**Never decide his ruling.** An item whose title says "decide" about the meaning of something he said is a §2
call: a worker read one narrowly and wrote "Decided" into a spec, and he reversed it the same day. Snag it as
`owner_call`.

## The blind check

The Marker runs walled, in `/home/mandrake/walled/<id>`: an exported tree at the sha with no `.git`, no
`conversations/` or `infrastructure/state/items/`, no store, nothing under `/home/mandrake/rm` or
`D:\ClaudeWork`. It gets the contract and the diff, never the attempts or notes. Verdicts: PASS, WEAK (done, but
the proof has a gap), FAIL, REJECT-PACKET, UNJUDGEABLE. A too-easy contract is a FAIL. `relentless_rules.json`
`walls.marker` is the current list.

**Done means the contract was met, not that the contract was complete.** A missing requirement passes every
stage by construction. Report "accepted against contract", and see `mutate-your-checker` for whether a proof
can see anything.

## The live round

`relentless_game.py` stages, `relentless_live_round.py` reruns read-only proofs, and one game serves one user at
a time. A live proof line drives the bridge through `python.exe`, and the mods it needs come from the built
sha's game files unless named. Flyers' flight is refused by word (`flyer_word`), never live-tested. There's no
step that writes the live world: a deliverable that is a bridge write plus a save can't pass blind, so it snags
with the one command a bridge holder runs. **A FAIL may be the harness or the site.** Read the evidence log
before counting it as the mod's. A showing for his look is pre-built before the item reaches him (design §8.1).

## Reading a stuck item

Read before you redesign anything. Each of these has cost generations.

1. `relentless.py show <ID>` for the state and last ending; `relentless.py causes` for the cause book of open
   follow-up items that failures were explained by.
2. `checker_lost` or "no verdict": read the check unit's `.err` in `store/runs/roles/` first. It may never have
   been judged. A full `/tmp`, a mode error at launch.
3. `state.json`: `tomb_since` for an aged close, `live_iter` and the bridge holder for a game hold.
4. Many items put down at once: suspect the supervisor's reach, not the items.
5. A fix that seems not to have taken: `relentless_release.py status`. A landed code fix waits for 04:30, and
   a data change reaches launches one tick after books shows it.
6. Fresh eyes: `relentless.py help --item <ID>`, which sends a fresh agent the failed approaches.

## Operating it

- **Reading the system:** `relentless.py reading`, the `rm-relentless.service` journal,
  `D:\ClaudeWork\rimmandrake\conductor\RELENTLESS_NOW.md`. Only the Conductor sets expedite.
- 🔴 **Stopping takes more than its units and the Dispatcher PAUSE.** `relentless_live_round.py` is a bare
  `Popen` from the tick, in no unit. On 2026-11-06 it kept calling `game_next` and launched the game 11 minutes
  after the stop, and the owner caught it. Kill it by pid and check the journal. `dispatcher stop-runs` also
  leaves `rm-dispatcher.timer` off, which disables Conductor restarts.
- **Pausing a timer for a while:** `python3 src/RimMandrake/Utils/timers_guard.py pause --hours H <timer>`, so
  guards read a planned stop. Stopping by hand raises `RELENTLESS_BLIND` after 10 minutes.
- **A release:** `relentless_release.py cut --emergency --why "..."`, `rollback`, `status`. Limits in the rules,
  including `share`, arrive the same way.

## Changing it

The main supervisor is about 8,400 lines, and the owner's stop was partly about that. Prefer deleting to adding.
A full-file GPT review doesn't converge on it (traps file), so don't re-run one hoping for CLEAN. A new alarm
kind needs its route in the same commit. A new lane needs its own queue cap and a look at the journal for its
first enrol.

Add a new trap to `references/traps.md` directly when you're editing skills; otherwise
`python3 src/RimMandrake/Utils/lessons.py add "..." --home skills/relentless`.
