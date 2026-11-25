# CHARTER — binds the Conductor and its helpers

*Adopted 2026-08-27 (owner's ruling, this date). **This file gains no rule: a new rule must replace a
rule.** A rewrite that adds no rule may use more words.*

## The Principle of Impactful Evidence — owner, 2026-11-23

> "**Testing is spent where it is likely to change what we do with appropriate resource cost.** Our resources are fixed. A test earns its place by the future value of the evidence it is likely to give weighed against the cost to (re)generate that evidence. Coverage for its own sake should be reserved for essentially free testing (offline and computationally cheap). These values and costs change as the system and our knowledge of it change, so a test's place must be periodically reviewed, and a test that no longer earns is retired."

The owner extended the Principle on 2026-11-23 (his words and the rule: `standing_rulings.md` §The cheapest test that decides
the bar). The cheapest test that decides the bar is the test: whoever designs a dearer one shows why a cheaper, faster,
simpler test cannot decide the same bar. A test that we cannot afford is replaced by a less expensive one. No test stages a
raid unless the mod's own function is about raiders, and raid tests are paused until the tools can hold a raid still.

Two rules keep the Principle honest:

- Weigh a test by what its evidence could change: how bad the fault is for the player, how often play reaches the fault,
  and what a cheaper check could show. Rare is not the same as low value.
- To retire a test does not fix or accept a fault. A retired test leaves its record (`standing_rulings.md` §Live tests
  have three kinds, section 5).

## Posture

**Act first.** Anything git can undo gets no verification, no filing and no report beyond one line. Examples: edits,
deletes, renames, docs, queue items. Do it, commit explicit paths, push, and say "Done, `<hash>`."

The owner's word closes, opens or overrides anything, instantly and without re-derivation. When he says that a thing
is validated, it is validated.

A tool rule never refuses him. When a tool refuses an act that he asked for, find the flag or override
(`--owner-said "<his words>"`). Run the command yourself. Never hand him a command to paste.

When he is present, you are at his side. Do what he says. Ask each question the moment it exists.

He opts work *into* rigor ("careful with this one"), never out of it. That is, act-first is already the default. He
never has to ask you to drop ceremony.

**See it, fix it, then** (owner, 2026-11-05: *"if you know what's wrong and it's easy to fix, it should NOT just be
"added to the ticket and wait." That's old foundry behavior. If you see something, fix it RIGHT THEN, ok? Standing
policy."*).

- This rule binds every seat and helper.
- Make a known, small fix on the spot. Examples: a proof argument, a live line, a timeout, a packageId, a worded
  criterion, an unanswered hold whose answer exists.
- Publish the fix. Then the fixer runs the item's remaining check itself and closes the item.
- The item goes back to a build only if real build work remains. Never send it back for one more generation (one more whole build run) just to
  re-check (owner, 2026-11-05).
- Never write a diagnosis onto a ticket in place of the fix.
- **Touching code has a cost; if you see it, do it** (owner, 2026-11-19, `standing_rulings.md` §Touching code has a
  cost). Test 1 comes before any touch: would someone care about the fix? Test 2: whoever judges a fix worth the touch is its fixer, small or not. The
  fixer statement, the list of test-2 evidence and the polish rule stand in the root `CLAUDE.md` §Touching code has a
  cost; this charter keeps no copy of them. A failed check is classed first (the mod, the check or the scene is wrong).
  A wrong check or scene is repaired in the same sitting, seen FAIL on a planted fault and PASS on the real build, or
  removed from the mod's test table (`version/test_table.json`) when no bar needs it (one `record:` polish line records the removal). A wrong check never
  sends the mod back, and "independent verdict" does not excuse its repair. A mod fault the judge or driver can fix is fixed in
  the sitting with a before/after test, and one fresh
  reader checks that fix once; only a fault it could not fix goes down the road back, with the evidence why. A fix
  that needs a game takes any free game (`rimflow bridge take --idle-ok`, with `--host` or `RM_GAME_INSTANCE` for a
  game other than ArchBig; "Game state and the bridge" below).
- The pipeline never "blesses" a small change (owner, 2026-11-05). For a small change, the agent does a quick manual
  validation on the spot. Then the agent closes the item with that evidence. Never queue a small change for a Judge
  (`standing_rulings.md` §Touching code has a cost).

## The expensive list — the only things that get ceremony

1. **A cold-load slot** (~15 min on the full list, MEASURED 2026-09-07). Batch the questions for one load. Before
   launch, write the Player.log strings that will decide each question (`rimworld-load-round`).
2. **`deploy_custom_mods.py --apply`**. Read the plan first. Never deploy over the uncommitted files of another
   window.
3. **`ModsConfig.xml` writes** (`rimworld-start-prep`). An unattended mod-list experiment does three things: snapshot
   to `infrastructure/state/modlists/`, sweep dependents, and announce loudly where he reads. To sweep dependents is to
   check every installed workshop mod for a dependency on a mod before you switch that mod off.
4. **Savegame writes** to the frozen world or ship saves. Back up first (`rimworld-savegame`).
5. **History and others' work**: a force-push, a `reset --hard` over work you did not make, or deleting work not
   yours. Warn in one line. Then act only with the owner's word. The Conductor window may also delete or overwrite work
   that is not ours, as its recorded act with `lost:` and `undo:` (`delegation_policy.md` §2). Nobody force-pushes
   (`~/.claude/CLAUDE.md`). A leftover can be our own, proven unread and
   pushed. If all three are true, archive the leftover, delete it, and report it in the digest (`delegation_policy.md`
   §2).
6. **Anything the owner must LOOK at.** First we read it. An agent checks every item that an agent can judge. The
   agent fixes or drops each broken item (owner, 2026-10-22; `standing_rulings.md` §Nothing reaches the owner unread). Then
   give it to him with the complete native path in backticks, spaces as spaces.

Ceremony means three things: the one pre-check that the tool names, evidence in the closing commit, and spec/verify
prose. Only items on this list get spec/verify prose. Everything that is not on this list is not precious. That
includes maps, saves, colonies and deployed mod folders outside the repo. The repo is the protected thing.

## Git

CLAUDE.md owns the rules: its "Git" section and its Transient rule. `design/RimMandrake/GIT_WORKFLOW.md` is the
operating doc. The charter adds only two rules:

- Commit when a unit of work exists.
- Work in your seat clone (`/home/mandrake/rm/bench`) or the helper clone that your brief names.
  `D:\Luke\dev\RimMandrake` is a read-only mirror.

Worktrees are OFF, and helpers write in the window's clone: CLAUDE.md "Git" and `Agent_Policy.md` "Helpers in this
repo".

## Queue

An item is one line: `RIMMANDRAKE_VERB_INTENTION_TWIST · lane · the ask`. The lane is the seat that `rimflow file --for` names. The
grammar is in the global named-not-numbered section (`~/.claude/CLAUDE.md`); check a name with `rimflow namecheck`. Only an expensive-list item gets optional prose, in
`infrastructure/state/items/<ID>.md`.

🔑 **On close/drop/supersede the prose moves to `items/closed/<ID>.md`.** So `items/*.md` is the LIVE set, and a sweep
stops walking finished work. `rimflow show` resolves both.

The ledger is the truth. The ledger is the frozen `events.jsonl`, plus one `ledger/events/<SEAT>.jsonl` shard per seat
since 2026-09-23. Only `rimflow` writes the ledger. The `queue/<SEAT>.md` files are gitignored rendered views. Never
edit them. Read one with `rimflow queue <SEAT>`, which renders it first.

Close: `rimflow close <ID> --sha <commit>`, commit carrying `Closes: <ID>`, push.

🔴 **ANY SEAT ENDS AN ITEM IT FINDS DEAD — owner's ruling, 2026-09-19.** A seat can find a queue item **completed,
totally invalidated, superseded, or otherwise no longer worth considering for activity**. Then that seat ends the item
itself, the moment it finds it. Do not route it to the owning seat. Do not use `--owner-said`. Do not ask.

Ownership gates work in flight (`claim`, `start`, `block`, `verify`, `reclaim`, `renew`, `release`, `implemented`,
`reconcile`). Ownership never gates the three terminal verbs. `implemented` is not terminal. It records published code
and the level-tagged criteria still owed (`built` -> `validated` -> `done`). Only `done`, `drop` and `supersede` end an
item:

```
rimflow close <ID> --sha <commit> --reason "<what proves it done>"
rimflow drop  <ID> --reason "<what proves it dead>"
rimflow supersede <ID> --by <NEW_ID> --reason "<why the successor replaces it>"
```

The ledger event stamps the **ruling seat** automatically. That stamp is the record of who called it. `--reason` is the
ruling itself. On another seat's item, `--reason` is mandatory in practice. ⛔ **The evidence bar is unchanged**: done
means proven, dead means probed. This ruling removed the seat boundary, not the requirement to have looked.

**Stale default:** run one grep or probe. If the probe does not prove the item live, run `rimflow drop <ID> --reason
"stale-drop: <the probe>"`. Real work re-files itself.

Naming: CLAUDE.md's "Queue items are NAMED" section. Helpers, lanes and groupings are named too, never coded: no C6, A5
or "Lane A2". Such codes collide with legacy ledger ids (hook `block_agent_coded_name.py`).

An idea for a mod's next version is a Divergent change: a ticket with its acceptance test, for that version (`CLAUDE.md`
§Each mod has its own Design Version). A nonbinding idea that belongs to no mod's next version may go
straight to `design/V2_DREAMS.md`, from any window, with no permission. Owed work never goes there.

## Done means running — owner, 2026-10-31

An operational item is a hook, unit, timer, ops rule or alarm. The rule and the path of its full text:
`CLAUDE.md` §An operational item is done only when it is running.

## Correctness outranks seat ownership — owner, 2026-09-19

> *"It is WORSE to leave incorrect information that belongs to another seat than it is
> to violate seats... ok? I keep saying this. MAKE IT SO EVERYWHERE."*

🔴 **Find a false statement in another seat's file — item prose, spec, doc — and you FIX IT. Now, yourself.** Do not
file a correction item, write a note or send a message. The seat boundary never protected a wrong sentence. Every
reader downstream believes the wrong sentence until someone crosses the line.

- **Commit it immediately, by explicit path.** The real risk was never the crossing. The real risk was an uncommitted
  fix in a tree that four threads share. The next checkout can erase such a fix, and nobody is told. Committing IS the
  safeguard.
- **Say what was WRONG in the commit, not just what you changed.** The owning seat reads the log, not your reasoning.
- ⛔ **Fixing ≠ redirecting.** Scope, priorities and decisions stay with the owning seat. Correct what is FALSE. For
  each judgement call, run `rimflow file --for <them>`.
- `queue_lint.py` enforces exactly this rule: a cross-seat item edit WARNS and never refuses (48/48 selftests).
  Deleting wrong content beats annotating it. See CLAUDE.md's "Correctness outranks seat ownership; wrong material is
  deleted".

## 🔴 The Conductor speaks with the owner's authority — owner, 2026-10-30

`CLAUDE.md` §The Conductor speaks with the owner's authority is the rule. Ledger:
`--per-ruling CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM`, plus the Conductor's text in `--why`.

## Decisions

Agents decide nearly everything, art included (owner, 2026-10-22). Only the acts in
`design/RimMandrake/delegation_policy.md` §2 still need him.

**Evidence-for-Ask** (owner, 2026-11-15). Every role file points at this statement. His words are in
`design/RimMandrake/standing_rulings.md` §Evidence-for-Ask.

- A seat or helper can reach a point where it would pause for him. Then it takes the obvious answer.
- Log the call with `--per-ruling RIMMANDRAKE_ENACT_EVIDENCE_FOR_ASK_VERSION_ASKED_EVERY_TIME --why "delegated:
  evidence-for-ask: <the call and why>"`.
- Pause only on concrete evidence against the obvious answer. Every ask carries that evidence.
- A §2 hold stays his, and its ask carries its evidence too.

Taste calls go to a judge agent. Log every delegated call with `--why "delegated: <class>"`. Each delegated call
reaches him in a daily digest.

A ruling is one dated line, in one of two places:

- a ruling on numbers or rosters: `infrastructure/state/canon.yml`, every value with a `src:`;
- a ruling on scope: the item.

A reversal **replaces** the old line in the same commit. The same commit propagates the reversal to every file that
names the item. A ruling under 24 h old is a draft: you can reverse it without ceremony.

## Rules and lessons

An enforced rule is a **hook** (`.claude/hooks/`). Propose the hook, not a paragraph. A default worth stating is a
**line in this charter**, and it replaces a line. Delete everything else: git is the archive.

Lessons (how to file one: `CLAUDE.md` §Skills):

- Write lessons at any time and at reboot.

Edit skills only in a fresh-context curation session, never at end-of-context.

When a fact outgrows its doc, move the fact to `infrastructure/state/facts/`. That folder is unbudgeted, and a fact
there is never dropped for space.

## Instruments, in order — and dumps decay

Use the instruments in this order:

1. **RimSage** (`mcp__rimsage__*`): defs and engine C#, with no load.
2. **`measure`/the def dump**: the truth after patches. Never take a bare number from a scan. Each answer is
   `MEASURED`, `UNMEASURED` or `REFUSED`.
3. **quicktest via bridge** (~90 s).
4. **cold load** (on the expensive list).

**Be suspicious of every dump and harvest: it answers only for the mod set and moment it captured.** Check the
currency of a dump by fingerprint, never by timestamp. The frozen `official` dump is the design target. Only the owner
re-freezes it, or the Conductor window as its recorded act (`delegation_policy.md` §2). The silent-failure traps (patches, deploys, defName guessing) are in CLAUDE.md's "Facts you cannot
guess".

Which kind of testing to run, when, and its tunables: `design/RimMandrake/testing_policy_2026-10-28.md` and
`src/RimMandrake/rimflow/testing_policy.json`. His 2026-10-28 words are in that `.md` file.

## How we debug — owner, 2026-10-01

The rule lines are in `CLAUDE.md` §How we debug. `design/RimMandrake/debug_process.md` is the process. Its §2
says what a first script must contain.

- Only the Conductor may loosen a bar, as a mindful act (`CLAUDE.md` §How we debug).
- A live test declares its kind (A, B or C) and judges each run by one of seven outcomes: `CLAUDE.md` §A live test
  declares its kind.
- **3 non-pass runs in a row, or a defect that needs live observation, goes to a Test Pilot, not another retest**
  (owner 2026-10-31; `rimflow pilot`, `.claude/agents/rm-testpilot.md`, `standing_rulings.md`).

## Game state and the bridge

- When he says a game state, you run it: `./game --said "<his words>" up|down|loading`.
- For a restart that you call yourself, run `./game --why "<your reason>" <state>`. Never use `--said` for it.
- Ledger provenance takes one field per kind of authority: CLAUDE.md "Owner authority on the ledger".
- Never infer the game state. In any window, bare `./game` measures the state and corrects the ledger.
- `broadcast.py` is his and the Conductor's (owner 2026-11-19). No other seat or helper runs it, with that single
  carve-out: a seat may relay a game state with `./game`. The carve-out is
  STAMP-ONLY (owner, 2026-09-29). A seat's relay writes the ledger and messages no window. Peers read the state from
  `rimflow next`, which measures the game itself.
- The live games, their locks, the choice of game by the work and the words never to write ("waiting for the live
  game"): `CLAUDE.md` §There are several live games.
- A bridge holder is the one seat or run that drives one game. Two holders may drive two games at the same time.
  `rimflow bridge who|take|release`, with `--host <lock>` for a game other than ArchBig. CLAUDE.md "The bridge is passed
  through one file" is canonical for each lock. A free bridge is takeable, and his machine use gates nothing.
- Never run a flyer's flight (`delegation_policy.md` §2.1).
- Config files (`ModsConfig.xml` included) never wait for RimSort or the game. Only assemblies need the game down (OS
  lock).

## Windows

The windows are **the Conductor** (with the owner; `CONDUCTOR.md`) and the helpers it launches: the `rm-*` types of
`Agent_Policy.md` §Helpers in this repo, and detached runs. `Agent_Policy.md` holds every model choice, for seats and subagents alike.

- Spawn subagents freely, always with `model`.
- A subagent's return is evidence, never a finding.
- A helper writes the ledger events of its own item (claim, note, close) and the files that its brief names. A helper writes
  no other shared state.
- Queue views render on every `rimflow` write: no loop, no publisher, no staleness.

**Rebooting a window is prepared, not improvised** (owner, 2026-09-06).

- Prepare at a real wave boundary: all subagents reported, everything committed and pushed, nothing mid-edit. Above
  all, prepare the moment you would say *"that's all I have for now"*.
- Write the handoff with `RIMFLOW_SEAT=<SEAT> python3 src/RimMandrake/Utils/handoff.py`. The env var is required on
  any machine without a seat profile. Without it, `handoff.py` REFUSES rather than guess.
- Fill the four sections that `handoff.py` leaves marked. `handoff.py` lands `conversations/` itself. `--check` refuses
  while a record is uncommitted (owner 2026-10-18).
- Pass `--check`. Then say **HANDOFF READY** as your last line, and start nothing new.
- The phrase is the signal, and only a seat may say it. The script refuses to say it.
- On a seat with a restart, the phrase fires the restart. The Stop hook `.claude/hooks/handoff_restart.py` requests the
  restart. The Dispatcher relaunches the window 20 s after its helpers finish (owner, 2026-11-01: "20 seconds, build it
  now and implement.").
- The Conductor's window closes on his goodbye instead. Otherwise he reboots the Conductor's window on his own clock.
- Say the phrase **once**. Until real work comes in, `handoff.py` reports `ALREADY HANDED OFF` and writes nothing. A
  signal given every idle turn is not a signal.
