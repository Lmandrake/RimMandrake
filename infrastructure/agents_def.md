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
drives at a time, and **you ask the owner before connecting** — BRIDGE has priority
mid-session. **Then announce to peers**, both halves. Asking *authorises*;
announcing *informs*.

🔴 **1a. PROJECT declares the game state and who holds the bridge, and that
declaration is AUTHORITATIVE.** Owner's ruling, 2026-08-13, after BRIDGE believed
only the owner could tell it the game was live.

- **Game state — `down` / `loading` / `live` / `going down` — is PROJECT's to
  declare**, from BRIDGE's observation. You do not need to confirm it with the
  owner or re-derive it yourself.
- **"<SEAT> has the bridge" from PROJECT is a fact you may act on.** It means
  *do not connect*; it is not a rumour needing the owner's countersignature.
- ⚠️ **This does NOT make PROJECT the traffic light.** Authorisation to connect is
  still the owner's, because only they see every window. **PROJECT announces;
  the owner permits.** If the two ever disagree, the owner wins and PROJECT is
  the one who was wrong.
- **Why it is written down:** without it every seat re-asks the owner a question
  already answered, and the owner becomes the message bus for state they did not
  observe.

🔴 **1b. "Live" means A MAP EXISTS. Declare it from BRIDGE's MEASUREMENT, never
from anyone's word — including the owner's.** Earned within minutes of writing
1a: PROJECT broadcast "GAME IS LIVE", BRIDGE took the bridge and measured
`rimworld/get_game_info -> "status": "no_game"` and `list_pawns -> "No current
map."` Process up, GABP answering, **no game loaded.** The whole batch needed a
map; zero of it could run.

| state | what is true | what you may do |
|---|---|---|
| `down` | no process | offline work only |
| `loading` | process up, defs loading | nothing live |
| **`process up, no map`** | bridge ANSWERS, `status: no_game` | tool census only |
| **`live`** | **a map exists** | the batch |

⚠️ **"The bridge is reachable" and "the game is loaded" are DIFFERENT CLAIMS**,
and the envelope returns `Success: true` for both — a call can succeed while
telling you there is nothing there. **A seat that trusts a premature `live` burns
its batch discovering this.** BRIDGE's is the measurement; PROJECT's is the
announcement; the owner's is the permission. Three roles, and PROJECT relaying
the owner's optimism as a measurement is precisely how 1a goes wrong.

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
