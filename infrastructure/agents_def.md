# agents_def.md — the rules five seats share

_Dissolved 2026-08-13: what is left is only what sits **between** seats and lives
nowhere else. Rule numbers are preserved because other docs cite them._

| what left | where it went |
|---|---|
| each seat's mission, refusals, thinking style, voice | `infrastructure/agents/<SEAT>.md`, injected by the SessionStart hook |
| Rule 0.6 — how a written instruction rots | `DOC_BUDGET.md` |
| how to write a filing · addressing · the doctrine delta · rule 10 | `skills/agent-messaging/SKILL.md` §§1a, 3, 3a, 6 |
| the traffic light, commit, deploy and mod-list rules in full | `CLAUDE.md` |

## The five seats

Identity in `infrastructure/agents/<SEAT>.md` (authoritative on scope and refusals), queue in
`infrastructure/state/queue/<SEAT>.md`. This file is authoritative on what seats owe each other.

| seat | you are a… | its question |
|---|---|---|
| **BRIDGE** | live-systems engineer | *has it been seen working in the running game?* |
| **OPS** | reliability engineer | *what is the evidence, and what is the smallest test?* |
| **CREATE** | mod author and game artist | *does it load, and read right at game scale?* |
| **VISION** | game designer | *does the player ever notice this?* |
| **PROJECT** | technical writer + information architect, MVP seat | *can the next session find this and trust it?* |

**Any seat may decline out-of-scope work** — one line in the right seat's queue with
what it already checked, and the owner told. Never a decline into silence.

**PROJECT holds the MVP seat:** it sets the v1/v2 line in `V1_SCOPE.md` and publishes
an honest burn-down, including "no progress this session". The other four own
execution. **PROJECT may not halt work; a peer may not add to v1 unilaterally** —
disagreement goes to **the owner**, and VISION argues for scope without setting it.

## Rules

**0. Open the seat's own Windows Terminal tab. That is the whole startup** —
`AGENT BRIDGE` … `AGENT PROJECT` in the tab dropdown. The profile exports
`AGENT_SEAT` and launches `claude --name 'AGENT <SEAT>'`; the SessionStart hook
records the role, titles window and session, and injects `infrastructure/agents/<SEAT>.md`.
**Nothing typed.** Fallback, for a tab opened without a profile or a seat
changing role: `./src/RimMandrake/Utils/set_agent_window.sh <SEAT>` — only
`BRIDGE|OPS|CREATE|VISION|PROJECT`, and the role it writes beats `AGENT_SEAT`.
Profiles are (re)installed with `python3 src/RimMandrake/Utils/install_wt_seat_profiles.py --apply`.

⛔ **Being addressable comes from `--name` at launch, from nothing else.** The
hook's `sessionTitle` names the *conversation*; the name `SendMessage` accepts is
a separate field only `--name`, `/rename` and the agent-name setter ever write —
measured 2026-08-13 with three seats live, all three carrying correct role files
and none addressable by seat. So the fallback script **cannot** make a running
session reachable by name, and no mid-session command can. A tab opened outside a
profile is addressable only by its generated name until it is relaunched.
**Always resolve an address with `python3 src/RimMandrake/Utils/peers.py`** — it joins role to
registry and prints both: send to `NAME`, read `SEAT` to know who that is.

**0.5. Never ignore a problem, especially one that is not yours.** Ownership decides
*who fixes it*, never *whether it is recorded*. Do not fix it, do not drop it — file
it at the owning seat's queue, `[?]` if you cannot tell (PROJECT drains those). What
the entry must contain, and the live-hazard exception: the messaging skill §6.

**0.6. A written instruction rots, and it rots while still being true.** → moved to
`DOC_BUDGET.md`.

**1. The live game is a single resource; the owner is the traffic light.** One seat
drives at a time, and **you ask the owner before connecting** — there is no channel
between windows, so the human is the only arbiter; BRIDGE has priority mid-session.
**Then announce to peers**, both halves. Asking *authorises*; announcing *informs*.

**2. Nobody touches another seat's tools.** Request capabilities; only the owner of a
tool writes it.

**3. Anyone may deploy, but only their own files.** `deploy_custom_mods.py` prints a
plan — read it. `--apply` only if every listed file is yours; a `-` line means
someone hand-edited the deployed copy, so `--pull` first.

**4. Lessons go in the tool owner's trap file, whoever learned them.** Append, and
correct wrong text in place; do not restructure someone else's file.

**5. Commit explicit paths only.** Per `CLAUDE.md`.

**6. `git status` before editing a shared doc.** If it is modified, someone is in it.

**6a. Edit a shared file in ONE PASS: append, then commit.** Your `M` is everyone
else's locked door — rule 6 tells them to back off, so holding a file for hours
*actively instructs peers not to write*. Measured: `NEXT_RELOAD.md` held 14:28→18:01
blocked the load queue for three and a half hours. Minutes, not hours; think in your
own file and paste the finished item in. **Corollary — do not write into another
seat's territory just because their file is free.** Append to their queue.

**6b. Addressing and replying: messaging skill §3.** Reply by copying the incoming
`from=` verbatim; confirm any other name in a `ListAgents` listing first. Publish
your own address on every resume — §3a.

**7. OPS is the sole writer to the mod list** — `ModsConfig.xml`, load order and
RimSort's `userRules.json`. Load-order bugs land in OPS's lap, so OPS owns their
cause; others request. Run `python src/RimMandrake/Utils/refresh.py` after any change.

**8. Whoever needs the restart calls it, harvests the log, and writes up for
everyone.** A cold load is ~23–30 min and carries everyone's pending work, so harvest
the **whole** log, not just your own concerns. Checks: `NEXT_RELOAD.md` §"After the
load"; anything surprising goes to the matching traps file.

**8a. The cold load carries a doctrine refresh** — `python3 src/RimMandrake/Utils/whats_new.py`,
called by PROJECT at game launch. Why, and the flags: messaging skill §1a.

**9. A mixed-subject directory is owned twice** — ratified by the owner 2026-08-12.

> The **doc** is owned by whoever owns the **subject**; the **directory** is owned by
> PROJECT for shape and staleness.

`runtime/` forced it: a decision-doc drawer whose entries belong to different
domains, so "who owns `runtime/`?" is a malformed question. PROJECT reshapes, indexes
and chases staleness there and **files findings on the subject owner rather than
fixing the content**. Applies to any directory collecting by *format* not *subject* —
and is not a licence to make more of them.

**10. Messaging: `skills/agent-messaging/SKILL.md`.** Ten lines is the ceiling; if
they cannot act on it now, it is a file, not a message.

## Handoffs — what crosses, and what "done" means on each side

**A handoff is not a message; it is an artifact plus a stated done-condition.** If
the receiver has to ask what it is being given, the handoff did not happen.

| stage | what crosses | sender's done-condition | receiver rejects it if… |
|---|---|---|---|
| **VISION → CREATE** | a written spec in `design/Jawa/worldbuilding/` | every field a builder must know is **decided** — no "X or Y", nothing left to infer | it would have to **invent** anything. Adding detail is fine; guessing is not |
| **CREATE → OPS** | a built, deployable mod | validates at full stack, deploys, and CREATE names the log strings that will show it worked | not deployable — no `About.xml`, no packageId, or never validated |
| **OPS → BRIDGE** | a capability request | the measurement OPS needs, and what it concludes from each outcome | no stated decision is attached to it |

VISION decides *what should exist and why*; CREATE decides *how it is built*. A spec
dictating implementation is VISION overreaching; a build inventing a design decision
is CREATE overreaching. **The middle row validates against the NEWEST backup, never a
pinned one**, and never against a small spike config — there every xpath legitimately
matches nothing and the wall of false failures burns a day:

```bash
validate_patch.py <file> --mods-config "$(ls -t deployed/config/ModsConfig.full-*.xml | head -1)"
```

**BRIDGE owns verification** — *was the truth reported?* **OPS owns validation** —
*was the true value also the predicted value?* A wrong number is BRIDGE's instrument;
a right number meaning something unexpected is OPS's call.

## Who draws, who fixes

**The split is LIVE versus NEW — not art versus code.** Medium is irrelevant; what
matters is whether the thing is already in the world.

| | |
|---|---|
| **OPS** | everything already **live**, art included — auditing it, inspecting it, judging whether it renders correctly, mechanically repairing it |
| **CREATE** | **originating** assets that do not exist yet — new images, redraws, restyling, and the pipeline that produces and validates them |

So auditing a live mod's art is OPS's even though it is art; drawing the replacement
that audit calls for is CREATE's. **Originating pixels → CREATE. Finding out what the
live game actually does → OPS.**

## Queues, and one state file per seat

**Every seat owns `infrastructure/state/queue/<SEAT>.md` and writes to it freely. Nobody blocks on
anybody.** Filing *at* a seat means appending to **theirs**; a shared queue held `M`
is an instruction to the other four not to file. `[v1]`/`[v2]` tag scope against
`V1_SCOPE.md`, `[?]` means unclaimed, two seat names mean shared work and the first
owns it. **`NEXT_RELOAD.md` is the one exception** — a single document about a single
event, assembled by PROJECT from the five queues before each load, so do not stage
load-round work directly in it. ⚠️ **`TODO.md` is being retired**
(`infrastructure/state/queue/PROJECT.md` P3): readable, but file new work in `infrastructure/state/queue/`.

**Each seat keeps one `AGENT_<SEAT>_state.md`**, rewritten when its context resets or
it hands off, carrying its cross-session address (messaging skill §3a). **Each seat
migrates and deletes its own, never another's** — flag a stale one belonging to
another role rather than removing it.
