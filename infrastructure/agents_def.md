# agents_def.md — the rules five seats share

**In force.** It holds only what sits *between* seats and lives nowhere else, and it is
authoritative on what seats owe each other. Rule numbers are preserved because other
docs cite them. A seat's own identity — mission, refusals, voice — is
`infrastructure/agents/<SEAT>.md`, authoritative on its scope and injected by the
SessionStart hook; its queue is `infrastructure/state/queue/<SEAT>.md`. **Also not
here:** how an instruction rots, was rule 0.6 → `infrastructure/DOC_BUDGET.md`;
filings, addressing, the doctrine delta and WRAP → `skills/agent-messaging/SKILL.md`
§§1a, 3, 6, 9; the traffic light, commit, deploy and mod-list rules in full →
`CLAUDE.md`.

## The five seats

| seat | you are a… | its question |
|---|---|---|
| **BRIDGE** | live-systems engineer | *has it been seen working in the running game?* |
| **OPS** | reliability engineer | *what is the evidence, and what is the smallest test?* |
| **CREATE** | mod author and game artist | *does it load, and read right at game scale?* |
| **VISION** | game designer | *does the player ever notice this?* |
| **PROJECT** | technical writer + information architect, MVP seat | *can the next session find this and trust it?* |

**Any seat may decline out-of-scope work** — one line in the right seat's queue with
what it already checked, and the owner told; never a decline into silence.
**PROJECT holds the MVP seat**, setting the v1/v2 line in
`infrastructure/state/V1_SCOPE.md` and publishing an honest burn-down while the other
four own execution. **PROJECT may not halt work; a peer may not add to v1
unilaterally** — disagreement goes to **the owner**; VISION argues scope, never sets it.

## Rules

**0. Open the seat's own Windows Terminal tab. That is the whole startup** — `AGENT
BRIDGE` … `AGENT PROJECT` in the tab dropdown. The profile exports `AGENT_SEAT` and
launches `claude --name 'AGENT <SEAT>'`; the SessionStart hook records the role, titles
window and session, and injects the seat file. **Nothing typed.** For a tab opened
without a profile, or a seat changing role:
`./src/RimMandrake/Utils/set_agent_window.sh <SEAT>` — `BRIDGE|OPS|CREATE|VISION|PROJECT`
only, and the role it writes beats `AGENT_SEAT`. Reinstall:
`python3 src/RimMandrake/Utils/install_wt_seat_profiles.py --apply`. **The profile
launches the seat memory-BOUNDED** — one seat's runaway kills that tab, not the VM.
Running and triaging the fleet: `skills/agent-fleet-windows/SKILL.md`.

⛔ **Being addressable comes from `--name` at launch, from nothing else** — the hook's
`sessionTitle` names the *conversation*, a separate field. No mid-session command, the
fallback script included, makes a running session reachable by seat name; a tab opened
outside a profile keeps its generated name until relaunched. **Resolve every address
with `python3 src/RimMandrake/Utils/peers.py`** — send to `NAME`, read `SEAT`.

**0.5. Never ignore a problem, especially one that is not yours.** Ownership decides
*who fixes it*, never *whether it is recorded*. Do not fix it, do not drop it — file
it at the owning seat's queue, `[?]` if you cannot tell (PROJECT drains those). What
the entry must contain, and the live-hazard exception: messaging skill §6.

**1. The live game is a single resource; the owner is the traffic light.** One seat
drives at a time, and **you ask the owner before connecting** — BRIDGE has priority
mid-session. **Then announce to peers**, both halves. Asking *authorises*;
announcing *informs*.

🔴 **1a. PROJECT declares the game state and who holds the bridge, and that
declaration is AUTHORITATIVE.**

- **Game state — `down` / `loading` / `live` / `going down` — is PROJECT's to
  declare**, from BRIDGE's observation. Do not re-derive it or re-ask the owner.
- **"<SEAT> has the bridge" from PROJECT is a fact you may act on.** It means *do not
  connect*; it is not a rumour needing the owner's countersignature.
- ⚠️ **This does NOT make PROJECT the traffic light.** Connecting is authorised by the
  owner, who alone sees every window. **PROJECT announces; the owner permits**, and
  the owner wins any disagreement.

🔴 **1b. "Live" means A MAP EXISTS. Declare it from BRIDGE's MEASUREMENT, never from
anyone's word — including the owner's.**

| state | what is true | what you may do |
|---|---|---|
| `down` | no process | offline work only |
| `loading` | process up, defs loading | nothing live |
| **`process up, no map`** | bridge ANSWERS, `status: no_game` | tool census only |
| **`live`** | **a map exists** | the batch |

⚠️ **"The bridge is reachable" and "the game is loaded" are DIFFERENT CLAIMS**, and the
envelope returns `Success: true` for both — a call can succeed while telling you there
is nothing there, and a seat trusting a premature `live` burns its batch on it.
**BRIDGE measures; PROJECT announces; the owner permits.**

🔴 **1c. WHOEVER HOLDS THE BRIDGE MAY CREATE AND DESTROY DEV COLONIES AT WILL.**

- **You do not need a map; you can make one.** `rimworld/start_debug_game_ready` starts
  a dev quicktest colony through the bridge — no permission, no queue entry, no
  worldgen wait. Make them freely, destroy them freely: a quicktest colony is scratch.
- ⭐ **So "blocked on a map" almost never means it.** Batch needs a map and there is
  none? **Start one** — a 30-second call, not a 25-minute load.
- ⏸️ **Map protection is SUSPENDED, not repealed.** Owner: *"NO AGENT SHOULD TRY TO
  PRESERVE MAP CONTENTS OR CAMPAIGN INTEGRITY AT THIS TIME… YOU WILL BE INFORMED WHEN
  WE GET TO THAT PHASE."* Test destructively until the owner announces play has
  started — that announcement is the reactivation trigger. **Still say which map a
  result came from**: evidence hygiene, not preservation.
- ⚠️ **Paid-for trap:** `start_debug_game_ready` **exceeds the 30 s client timeout and
  succeeds anyway** — the response is merely late. **Do not retry** (connection
  desynced), **do not re-issue** (you get a second map). Open a fresh connection, poll
  `jawa/list_pawns` until it stops saying *"No current map"*. Method:
  `skills/rimbridge/references/capability-matrix.md`.
- **Rule 1 still holds**: taking the bridge is announced; making a colony once you hold
  it needs nobody's say-so.

**2. Nobody touches another seat's tools.** Request capabilities; only the owner of a
tool writes it.

**3. Anyone may deploy, but only their own files.**
`src/RimMandrake/Utils/deploy_custom_mods.py` prints a plan — read it. `--apply` only if
every listed file is yours; a `-` line means someone hand-edited the deployed copy, so
`--pull` first.

**4. Lessons go in the tool owner's trap file, whoever learned them.** Append, and
correct wrong text in place; do not restructure someone else's file.

**5. Commit explicit paths only.** Per `CLAUDE.md`.

**6. `git status` before editing a shared doc.** If it is modified, someone is in it.

**6a. Edit a shared file in ONE PASS: append, then commit.** Your `M` is everyone
else's locked door — rule 6 tells them to back off, so holding a file for hours
*actively instructs peers not to write*. Minutes, not hours; think in your own file and
paste the finished item in.

**6b. Addressing and replying: messaging skill §3.** Reply by copying the incoming
`from=` verbatim; confirm any other name in a `ListAgents` listing first. Publish
your own address on every resume — §3b.

**7. OPS is the sole writer to the mod list** — `ModsConfig.xml`, load order and
RimSort's `userRules.json`. Load-order bugs land in OPS's lap, so OPS owns their
cause; **other seats file enable/order *requests* at `infrastructure/state/queue/OPS.md`**
and a deployed mod stays inert until OPS acts. Run
`python src/RimMandrake/Utils/refresh.py` after any change.

**8. Whoever needs the restart calls it, harvests the log, and writes up for everyone.**
A cold load is ~23–30 min and carries everyone's pending work, so harvest the **whole**
log, not just your own concerns. Run sheet: `infrastructure/state/NEXT_RELOAD.md`;
anything surprising goes to the matching traps file.

**8a. The cold load carries a doctrine refresh** —
`python3 src/RimMandrake/Utils/whats_new.py`, called by PROJECT at game launch. Why,
and the flags: messaging skill §1a.

**9. A mixed-subject directory is owned twice** — the **doc** belongs to whoever owns
the **subject**, the **directory** to PROJECT for shape and staleness. Applies wherever
a directory collects by *format* rather than *subject*, so "who owns this directory?"
is malformed: PROJECT reshapes, indexes and chases staleness there and **files findings
on the subject owner rather than fixing the content**. Not a licence to make more.

**10. Messaging: `skills/agent-messaging/SKILL.md`.** Ten lines is the ceiling; if
they cannot act on it now, it is a file, not a message. **WRAP — the shutdown order —
is §9, and PROJECT alone issues it on the owner's word.**

## Handoffs — what crosses, and what "done" means on each side

**A handoff is an artifact plus a stated done-condition, not a message** — if the
receiver must ask what it is being given, the handoff did not happen.

| stage | what crosses | sender's done-condition | receiver rejects it if… |
|---|---|---|---|
| **VISION → CREATE** | a written spec in `design/Jawa/worldbuilding/` | every field a builder must know is **decided** — no "X or Y", nothing left to infer | it would have to **invent** anything. Adding detail is fine; guessing is not |
| **CREATE → OPS** | a built, deployable mod | validates at full stack, deploys, and CREATE names the log strings that will show it worked | not deployable — no `About.xml`, no packageId, or never validated |
| **OPS → BRIDGE** | a capability request | the measurement OPS needs, and what it concludes from each outcome | no stated decision is attached to it |

VISION decides *what should exist and why*; CREATE decides *how it is built*. A spec
dictating implementation is VISION overreaching; a build inventing a design decision
is CREATE overreaching. **The middle row validates against the NEWEST backup, never a
pinned one and never a small spike config** — there every xpath legitimately matches
nothing and the wall of false failures burns a day:

```bash
skills/rimworld-modding/scripts/validate_patch.py <file> \
  --mods-config "$(ls -t deployed/config/ModsConfig.full-*.xml | head -1)"
```

**BRIDGE owns verification** — *was the truth reported?* **OPS owns validation** —
*was the true value also the predicted value?* A wrong number is BRIDGE's instrument;
a right number meaning something unexpected is OPS's call.

## Who draws, who fixes

**The split is LIVE versus NEW — not art versus code.** Everything already in the world
is **OPS's** to audit, inspect, judge and mechanically repair, art included;
**originating** what does not exist yet — new images, redraws, restyling, and the
pipeline that produces and validates them — is **CREATE's**. So auditing a live mod's
art is OPS's; drawing the replacement that audit calls for is CREATE's.

## Queues, and one state file per seat

**Every seat owns `infrastructure/state/queue/<SEAT>.md` and writes to it freely.
Nobody blocks on anybody.** Filing *at* a seat means appending to **theirs**. `[v1]`/
`[v2]` tag scope against `infrastructure/state/V1_SCOPE.md`, `[?]` means unclaimed, two
seat names mean shared work and the first owns it.
**`infrastructure/state/NEXT_RELOAD.md` is the one exception** — one document about one
event, assembled by PROJECT from the five queues before each load, so do not stage
load-round work directly in it. **`infrastructure/state/TODO.md` is RETIRED**, a
pointer stub; nothing is fileable there.

**Each seat keeps one `infrastructure/state/AGENT_<SEAT>_state.md`**, rewritten when its
context resets or it hands off, carrying its cross-session address (messaging §3b).
**Each seat migrates and deletes its own, never another's** — flag a stale one
belonging to another role rather than removing it.
