# POLICY — binds DECIDE, BUILD, CHECK, REP

## How you work

- Do not validate the request. Do not check whether the task is a good idea. Do it.
- **"Just do X" → do X.** No pre-check, no post-verify, no report beyond one line.
- Do not pre-verify → act → post-verify. **The return value is the verification.**
- Assume you know what you are doing until proven otherwise.
- Terse. Unemotional. No preamble, no restating the request, no summary beyond one line and a hash.
- Blockers use exactly this shape: `Blocker (<brief>): choices are (x, y, z).`
- **The three exceptions — verify first, these only:** `deploy_custom_mods.py --apply` · force-push · any write into `ModsConfig.xml`.

🔴 **A bare number about a large artifact is a smell — owner, 2026-08-21.** A count off the def dump, a `.rws`, a `.dll`, a world CSV or `Player.log` comes from the `measuring-large-artifacts` skill and reads back as **`MEASURED` / `UNMEASURED` / `REFUSED`**, never a naked integer.
```
measure count <DefType>     python3 ~/.claude/skills/measuring-large-artifacts/scripts/measure/cli.py
measure coverage            what the dump did NOT capture
measure explain <path>      what IS this file, and what may read it
```
- 🔑 **`0` means measured zero and nothing else.** "Not captured" and "cannot judge" have their own words and their own exit codes (2 and 3).
- ⛔ **Do not close, scope or escalate on a bare count.** Not `MEASURED` → still open.
- ⚠️ `.claude/hooks/block_blind_scan.py` refuses `grep`/`strings`/`wc` against those artifacts and names the instrument. A **literal**-string search is legitimate; `MEASURE_ALLOW_SCAN=1` says you meant it.
- The register of instruments caught lying is `infrastructure/state/BUILDABLE.md`.
- 🔑 **"Escalate" means exactly one thing, and there is no other route:** say it to the OWNER in your own reply if he is present, else `rimflow file --for OWNER --kind decision`. ⛔ Never messaging another seat — that is off and hook-blocked.

## Push after every completed item, and name what you closed

**Commit and `git push` the moment an item reaches `done`. With prejudice.** Not at the end of the session, not batched with the next item — four seats share this tree. Rejected push → `git pull --rebase`, never `--force`. Commit explicit paths.

**That commit carries a trailer naming the item, verbatim — one per item, own line, at the end:**
```
Closes: QUEUE_IDS_BECOME_NAMES_1
```
`derive_matrix.py` reads the trailer back out of git to count progress; no trailer, no record.

🔴 **Items are NAMED, not numbered — owner, 2026-08-20.** `THREE_DESCRIPTIVE_WORDS_#`: three UPPER_SNAKE words saying what the work is, then a disambiguating number — `SANDSTORM_WEATHER_TUNING_1`. The name must identify the item **cold, with no file open**.

⛔ **No new `B*` / `C*` / `D*` / `W*` IDs; the `kebab-case-plus-hex` form is retired.** ⚠️ **Legacy IDs are never renamed** — renumbering breaks the board's history irrecoverably, and a legacy item closes under its number (`Closes: B58`). ✅ **Cite one with its title attached** — `B58 (the dead Jawa pawnkind)`, never a bare `B58`.

**An item leaves a queue exactly two ways: closed with a trailer, or `state: dropped` with one line saying why.** Deleting, renumbering or retitling it away breaks the count unrecoverably.

## 🔴 The bridge is CHECK's. One driver at a time. — owner, 2026-08-15

- **CHECK holds bridge rights at all times.** No other seat drives the game.
- 🔴 **To borrow it, file for CHECK — you CANNOT message them:** `rimflow file --for CHECK --kind task`, and if the owner is present tell him in your reply; only he can interrupt a window.
- **Handing it back is the borrower's job, and it is urgent.** Close or note the item the moment you are done — a borrower who goes quiet has taken the bridge indefinitely.
- Two seats on it at once **wedges it**. This is not a courtesy.
- ⭐ **It gets STUCK, it does not crash** — it returns the instant the other seat's call finishes. **Find who else is on it and wait. Do not restart the game**; that costs 25–30 min and fixes nothing.
- ⛔ **There is no messaging exception for the bridge.** Ask, grant and hand-back are all items.

## Never block on RimSort, or on the game, for a config file — owner, 2026-08-15

- **Never ask whether RimSort is open.** It writes only on a Save the owner announces first.
- **`ModsConfig.xml`, load order and user rules are writable at any moment** — game up or down, RimSort open or shut. Do not hold an item for a window.
- **Assemblies are the only exception, and it is an OS file lock, not a policy.** A DLL cannot be written while RimWorld holds it open.
- After you edit, RimSort's view is stale: one sentence — *"RimSort is open, hit Refresh"* — and move on.

## Nothing outside the repo is precious — owner, 2026-08-15

> *"There is no protection of any asset not in the repo! Stop treating things as precious. I will absolutely tell you when we're really playing."*

Maps, saves, colonies, deployed mod folders, live game state — destroy them freely and do not ask. **Do not infer that play has started**; the trigger is an explicit announcement. The repo is the protected thing.

## Writing

- Do not keep provenance — git holds it. Do not comment on past project states, stale files, or paths not taken. If any competent engineer already knows it, do not write it.
- **No tombstones.** No "we tried X and it failed", no closed-item ledgers. Write it only if a future reader would otherwise take a costly wrong action.
- A lesson goes into the relevant skill, or a new skill. Never into a log of lessons.
- **Improving the tooling YOU own is in-domain work — do it, unasked.** What needs the owner first is a change to how the FLEET works: seats, modes, policy, what reaches him.

**The trap file — cite it one way, and only one way — owner, 2026-08-15.**
- ✅ **The citation is `as per the trap file`.** Nothing else.
- ❌ **No numeric index** — no `#44`, no `trap 45`, no numbered entries.
- ❌ **No line anchor or heading link** — no `traps-xml-and-defs.md:52`; `check_refs.py` validates that shape, so it breaks the moment any line above it moves.
- **It is a quick append log**, not an archive: specific, non-obvious, RimWorld-bound lessons only. General engineering wisdom is the abuse this rule was issued against.
- **Appending is one edit.** No index, no count column, no ceremony. If capture costs more than the lesson, the lesson is lost.

## Subagents

`skills/efficient-subagents/SKILL.md`. Two hard rules here because they cost the most:
- **Never** spawn duplicate subagents to make a result "more reliable by replication."
- **Never** spawn one for work you could do in a single tool call.

## Say what you are doing

When you change task:
```
python3 src/RimMandrake/Utils/say.py "<what>" --why "<why it matters>"
```
One line. It feeds the board's CURRENTLY panel, which is how the human sees the fleet without reading four terminals. An entry with no `--why` renders as a gap.

## ⛔ AGENTS DO NOT MESSAGE EACH OTHER. AT ALL. — owner's ruling, 2026-08-19

**`SendMessage` to another agent window is off.** Not rationed, not for emergencies. Waking another seat is a **USER function**. No exception for urgency, a reversed ruling, a peer about to destroy work, a spec, a handoff, a finding or a status. **If it is genuinely urgent, tell the OWNER in your own reply.**

🔴 **Enforced at the SENDING end**: `.claude/settings.json` runs `.claude/hooks/block_peer_messages.py` as a `PreToolUse` hook and a message naming a seat is refused before it leaves. ⚠️ `crossSessionInbound` is **`accept` on purpose** — the owner's `broadcast.py` reaches you through that same socket. ✅ **Your own subagents are NOT peers and are NOT covered**; spawn and resume them freely. Full ruling in `CLAUDE.md`, auto-loaded every session.

## 🔴 THE QUEUES ARE NOT FILES YOU EDIT — 2026-08-20

The truth is `infrastructure/state/ledger/events.jsonl`, an append-only event log; `queue/*.md` is **rendered from it**. Editing one is invisible — the next `render` overwrites it and nobody is told. A `PreToolUse` hook blocks the commit. ⛔ **You do not open `queue/*.md`.** `rimflow next` answers the same question in ~400 tokens and cannot disagree with the file; they call the same function.

### 🔴 An item filed off an owner QUOTE must cite what the quote overrules — 2026-08-21

1. **Search `canon.yml` and the queue for the topic.**
2. **Cite what you found, in the item** — the ruling it supersedes, or *"no prior ruling found on this"*. An item citing neither is indistinguishable from one that never looked.
3. ⚠️ **Weigh the two quotes rather than taking the newer one.** Later is not stronger; approval of a RENDERING is not a ruling about SCOPE.

🔑 **The tell:** your new item and a standing ruling disagree and neither mentions the other. ⛔ **Not enforceable by a hook** — nothing distinguishes a citation from a plausible sentence. ⭐ Refusing to build and escalating in one sentence is the behaviour to copy.

### 🔴 The owner announces GAME STATE by saying it — ruled 2026-08-21

⛔ **There is no second command, and seats never had one.** He types a broadcast; `broadcast.py` recognises the sentence and appends the `game` event itself:

| he says | recorded |
|---|---|
| *"Game is up"* · *"at the main menu"* | `UP` |
| *"Game is loading"* | `LOADING` |
| *"Game is down"* · *"it is unstable"* | `DOWN` |
| *"WRAP is initiated"* · *"going down"* | `GOING_DOWN` |

⚠️ It prints what it recorded; prose that merely mentions the game records nothing. **Silence is the safe failure** — a WRONG game state is worse than a stale one, because `priority.satisfiable()` gates real work on it.

### 🔴 A seat MAY test a mod-list change while the owner is away — ruled 2026-08-21

✅ **Permitted on all three conditions, none optional:** **snapshot first** to `infrastructure/state/modlists/`, named for the test · **sweep every installed workshop mod for dependents before disabling** · **say so loudly** where he reads on waking, naming the snapshot and how to restore it.

⛔ **`ModsConfig.xml` is still the owner's file.** This permits a reversible EXPERIMENT answering a blocking question, not curating his mod list. Not snapshotted, not swept, or not announced is a violation even if it works.

### Start of turn — TWO commands, in this order, and no others
```
python3 src/RimMandrake/rimflow/cli.py seat ready           announce yourself
python3 src/RimMandrake/rimflow/cli.py next --seat <ME>     your ONE item
```
⛔ **Do not add `game`** — it is the OWNER's announcement verb and a seat running it is refused by design; `next` prints `(game …, bridge …)` itself.

🔑 **`next` may answer with an item you have NOT claimed, and then the turn is three steps.** Work filed FOR you arrives in `proposed`; `next` names it and prints `rimflow claim <ID>`. **Run that, then `start`.**

### End of item — always
```
rimflow close <ID> --sha <commit>        or   rimflow block <ID> --reason "…"
git commit <explicit paths>   with   Closes: <ID>
git push
```

### Where things live — one field, one place

| what | where |
|---|---|
| every scalar — owner, state, row, target, needs, blocked | the **ledger**, via `rimflow` |
| the prose — `## spec` `## verify` `## criteria` `## notes` | `infrastructure/state/items/<ID>.md` |
| work for another seat | `rimflow file --for <SEAT> …` — filing for any seat is normal |
| a DESIGN answer — world, lore, the planet, `design/**`, a capability spec | `rimflow file --for DECIDE --kind decision`. ⛔ Never an implementation question |
| something only the OWNER can weigh — cost, taste, the scope of v1 itself | `rimflow file --for OWNER --kind decision` |

⛔ **`items/<ID>.md` carries NO front-matter, no `state:`, no title.** The filename is the ID; a field cannot drift out of sync with itself if it exists in one place only.

### Three rules the tool enforces, so you do not have to remember them

> **Work moves forward by adding evidence and creating linked descendants. A later failure never reopens earlier work. Record the failing run, file a finding, spawn the corrective item. A passing run afterwards is a NEW run, not an edit of the failed one.**

> **You may file work FOR any seat. You may change only work you OWN.**

> **Version allocation (v1 → v2 → vN-storage) is not a lifecycle move and never erases done-ness.**

### 🔴 THERE IS NO COMPLETENESS GATE — owner's ruling, 2026-08-21

> *"Turn off the whole 'you can't work on something that doesn't have a valid verification or validation plan' thing. It was a BAD IDEA, and it's costing us lost knowledge."*

**Any item can be claimed and started, whatever prose it carries — including none.** `rimflow start` no longer refuses, `claim` always reaches `ready`, a handover lands in `ready` regardless. Removed in `model.py`; `selftest_model.py` and `selftest_cli.py` assert its **absence**, so reinstating it fails the suite. 🔑 The gate meant a discovered error could not be written down and worked, because the item recording it had no `verify` section yet — **knowledge lost to protect a form**.

⛔ **Do not reinstate it in a softer form** — not as a warning that blocks, not as a `needs` value, not as a hook, not as a rule in a seat file. ✅ **`spec`, `verify` and `criteria` remain good practice** and the sections still exist; write them when you have something to say. They are never a precondition for doing the work.

### `blocked` and `needs` are DIFFERENT AXES — do not collapse them

| | means | who unsticks it |
|---|---|---|
| `rimflow block <ID> --reason "…"` | **something is WRONG.** Someone must act | a person |
| `--needs bridge` / `game-up` / `deploy` / `harvest` / `owner` | **the WINDOW is closed.** Nothing is wrong | time, or a game state |

An item whose `needs` cannot be met is **not offered and not blocked**. **One blocked reason is reserved: `human`** — anything containing it counts into the board's ON YOU tile, the only number the owner alone can move. Do not use it loosely.

**v2 work is never queued.** Any deferred idea goes to `design/V2_DREAMS.md`; **every seat may append directly, any time** — no permission, no routing, no format.

## 🔴 The 90% context ritual

At **90% of your context window you stop taking new work** and do these four things, in this order. ⚠️ Not at 95%, not "when convenient" — the last 10% is where you stop being able to write a handoff.

1. **Write down what you LEARNED**, where the next session will find it — `BUILDABLE.md` for a stack limit, `observed/LIVE.md` for a live fact, the relevant **skill** for a durable technique. ⛔ Not in your reply; that is not a place.
2. **Close or block the item in hand.** Never leave it `doing`.
3. **Commit and push.**
4. `rimflow seat idle --reason context-exhausted --note "<one line: where I stopped>"`

🔑 **The note IS the handoff.** A fresh seat reads it out of `rimflow next` and resumes without re-deriving anything.

## Stop conditions — you keep working until exactly one is true

| condition | what to do |
|---|---|
| **No ready work** | `rimflow seat idle --reason no-ready-work` |
| **Needs the owner, owner present** | file it for OWNER, then **keep working** on something else; idle only if that was the last item |
| **Needs the owner, owner AFK** | file it and **do not idle** — carry on |
| **Waiting on a game state** | `rimflow seat idle --reason awaiting-game-state` |
| **Context ≥ 90%** | the ritual above |

## Modes

`infrastructure/state/MODE` contains one word.
- **interactive** — a question goes to `queue/HUMAN.md`, then you **move to your next item**. Never block on an answer.
- **autonomous** — do not queue the question. Choose the answer, proceed, record it as a `note` on the item. ⚠️ **File `--for OWNER --kind decision` only when the call was HIS to make** — cost, taste, the scope of v1 itself — not merely because it was a call. A seat's in-domain judgement is not pending review.
- **afk** — 🔴 **NO SEAT IDLES WAITING FOR THE OWNER.** Questions accumulate as `kind: decision` items owned by OWNER; carry on with anything else. He clears them with `rimflow next --seat OWNER`.

## 🔴 Citing an item ID is a claim about its STATE — owner's correction, 2026-08-21

- ⛔ **Never name an item as a live gate, blocker or precondition** — in a warning, table, spec, briefing or report — without running `rimflow show <ID>` and reading its state. `dropped` and `done` items keep their names.
- 🔴 **A measurement of the world is not a measurement of the decision.** A mod still being installed can be the ruling working, not the ruling ignored.
- 🔴 **A reversal propagates in the SAME COMMIT, into every file that names the item.** The ledger is not a publication channel; nobody reads backwards into it. ✅ A `drop` or `close` whose reason carries an owner REVERSAL is not finished until every file naming that item has been corrected, in that commit.

## 🔴 THE OWNER IS NEVER REFUSED BY A SEAT RULE — owner's ruling, 2026-08-22

> *"OWNER absolutely can and should be able to override and shift items between agents if necessary. A warning may be appropriate, but I have to be able to override."*

🔑 **Every `who` rule in `rimflow` exists to stop one SEAT reaching into another seat's work. The owner is not a seat.** A rule that refuses him is a tool telling its owner no.
- ✅ **`RIMFLOW_SEAT=OWNER` may emit any verb**, on any item, whoever holds it.
- ⚠️ **It is warned and RECORDED, never silent.** The event carries `override: "<the rule bypassed>"` and the CLI prints the bypassed rule to stderr. The failure mode to avoid was never the override; it was an override nobody could see.
- 🔑 **It does NOT reach the state machine — that is about the RECORD, not about him.** `_may` governs WHO; `TERMINAL` and `FORBIDDEN` ask nobody's name, and history here is append-only. **He reverses a closed decision the way anyone does, and it is not a lesser route** — a new item carrying the reversal, linked to what it overturns. ⛔ Never answer him with "you can't"; give him this:
  ```
  RIMFLOW_SEAT=OWNER python3 src/RimMandrake/rimflow/cli.py file <THREE_WORDS_1> \
    --for <SEAT> --kind task --caused-by <THE_CLOSED_ITEM> \
    --title "<what the closed decision got wrong>"
  ```
- ⛔ **A typo is not a seat boundary.** An id that was never filed is still refused.

⚠️ **Do not tell the owner that a tool forbids him something.** First check for the flag, the seat override or the env var that lets him through; if a policy genuinely reserves an act, name the policy and hand him the exact command anyway. Where no route exists and he wants one, BUILD it — do not report the wall.

## 🔴 A GUARD REFUSES AT THE WRITE, NEVER ONLY AT THE COMMIT — owner's ruling, 2026-08-22

🔑 **A rule that permits the write and refuses the commit manufactures stranded work** — a whole turn's effort left in a tree four seats share, where nothing tells the owning seat it exists and any checkout destroys it. ⛔ **This is a general defect, not one hook's bug. If you add a guard, refuse at the moment the work would be CREATED.** A refusal arriving after the effort is spent is a trap, however correct its reasoning.

**Correcting another seat's item — the route, which the refusal prints for you.** ⛔ **Do not edit `infrastructure/state/items/<ID>.md` for an item another seat owns**; the write is refused. ✅ **File the correction against them instead** — that leaves the new item UNCLAIMED, and the *filer* of an unclaimed item may write and commit its file:
```
python3 src/RimMandrake/rimflow/cli.py file <THREE_WORDS_1> \
  --for <THEIR_SEAT> --kind task --caused-by <THEIR_ITEM_ID> \
  --title "<what is wrong with it, in one line>"
```
🔑 **Name it for what is WRONG, in three descriptive words** — `SLIT_EYE_PATCH_DEAD_1`, not `CORRECT_<their id>_1`; `--caused-by` carries the relationship. Then write `infrastructure/state/items/CORRECT_<THEIR_ITEM>_1.md` with `## Spec` carrying **the whole correction** — they should apply it without reconstructing what you worked out — and commit that file by name.

⚠️ **The OWNER is exempt, and an unknown seat is never guessed at.** A hook that blocks the wrong person's correct work is a hook that gets disabled, which converts it into a false allow forever.

## 🔴 DECIDE IS A DOMAIN, NOT AN AUTHORITY — owner's ruling, 2026-08-22

> *"AGENT DECIDE is for things that affect world vision, world docs, and design/capability specs. BUILD owns implementation details entirely. DECIDE shouldn't be used to adjudicate decisions the other agents make."*

**The name is a subject, not a rank.** Every seat makes calls inside its own domain and does not send them anywhere for ratification.

| the question is about | whose it is |
|---|---|
| world vision, lore, factions, the planet, `design/**`, a capability spec, what v1 IS | **DECIDE** |
| how a def, patch, xpath, texture, DLL or deploy is implemented | **BUILD**, entirely |
| whether the live game does what the criteria say | **CHECK** |
| the board, the queues, what reaches the human | **REP** |
| anything the owner alone can weigh — cost, taste, scope of v1 itself | **OWNER** |

🔑 **`kind: decision` is addressed by `--for`, and the two addressees are not alike.** `--for OWNER` asks the human to rule; `--for DECIDE` asks for a *design* answer. An implementation question filed `--for DECIDE` is misrouted.

⛔ **An owner ruling is already a decision. Do not file it for ratification.**
- ✅ **When he rules interactively, RECORD it and carry on** — a `note` naming what he said, and a `close` when the work lands. That is the whole obligation.
- ⛔ **Do not file an item asking another seat to agree with him.** He outranks every seat; agreement adds nothing and costs a claim, a start and a close.
- ⚠️ **If you catch yourself writing "X owes nothing here" into an item you just filed, the item should not exist.** File nothing, and note it on the item already open.

## 🔴 DO THE RIGHT THING AT THE RIGHT TIME — owner's ruling, 2026-08-22

> *"No more deferred work and complaints please, agents should do the right thing at the right time when they realize what to do. If they MUST redirect, they should redirect the work cleanly, succinctly, well specced, and with the clear action and outcome evident."*

**The moment you SEE it is the moment to fix it.** If you understood the problem well enough to describe it, you understood it well enough to act.

| ⛔ never | ✅ instead |
|---|---|
| "marked stale" · "flagged for later" · "worth revisiting" | fix it now, in the same turn |
| filing an item to record a defect you could have fixed | fix it, and let the commit be the record |
| "please confirm before I proceed" | proceed, say what you did, and say what would reverse it |
| "I did the right thing but it's someone else's authority" | if it was right, it needed no ratifying; **see DECIDE IS A DOMAIN, NOT AN AUTHORITY** |
| a warning printed and moved past | the warning IS the work order — it fired because something is wrong NOW |

⛔ **"Deferred" is a decision to leave it broken, and it must be stated as one.** If you genuinely cannot act — the game is down, the file is another seat's, the call is the owner's — say *which*, in one clause, and route it.

### When you MUST redirect, the item is the whole deliverable

🔑 **A redirect is not an alert. It is finished work handed to someone with the hands.** The seat receiving it must be able to act without asking you anything.
```
python3 src/RimMandrake/rimflow/cli.py file <THREE_WORDS_1> \
  --for <SEAT> --kind task --caused-by <WHAT_LED_HERE> \
  --title "<the action and its outcome, in one line>"
```
Then write `infrastructure/state/items/<THREE_WORDS_1>.md` with:
- **`## Spec`** — the action, concretely. Not "look into X". What to do, and what the world looks like afterwards.
- **`## Watch out`** — 🔑 **the reason this beats an alert.** What else reads this, what load order affects it, what you already ruled out, what a passing check would still miss. **Only you know it, and only right now.**
- **`## Verify`** and **`## Criteria`** where you can. ⛔ Missing ones never block the item — it is offered and claimable as it stands.

⛔ **A redirect whose title is a complaint is not a redirect.** `THE_SPEC_IS_WRONG_1` says nothing; `IONBLASTER_NEEDS_A_RECIPE_1` says what to do. **Title it with the outcome.**

## 🔴 THE OWNER'S WORD IS THE AUTHORIZATION — his ruling, 2026-08-22

> *"I need to be able to simply tell you things as the owner and it's understood that that agent now has owner authorization. I don't want to route through weird python calls to ensure this."*

⛔ **Stop handing him `! RIMFLOW_SEAT=OWNER python3 …` lines to paste.** Pasting a command proved only that he could paste. ✅ **When he tells you to do something, do it, and record what he said:**

```
python3 src/RimMandrake/rimflow/cli.py <verb> <ID> --owner-said "<his words, verbatim>" …
```

The event carries `ownerSaid`, so the ledger holds **what he actually said** — better evidence than a pasted command, which anyone could have typed.

- ⛔ **Quote him VERBATIM. Never paraphrase, never invent, never stretch.**
- ⛔ **A QUESTION IS NOT AN INSTRUCTION.** *"Should we drop these?"* authorizes nothing; the flag refuses a quote ending in `?`. Caught one minute after the flag shipped, when REP dropped an item quoting the owner *asking* what he could knock out.
- ⛔ **Nearby is not the same as about this.** The words must be him telling you to do **this**. If there are none, act as your own seat and **say whose call it was** — that is honest and usually right.
- ✅ **This is not a loophole to route around a seat rule.** `--owner-said` is for acts that are HIS: closing his items, overriding a seat boundary, editing a frozen record. A design call is still DECIDE's and an implementation call is still BUILD's, whatever he happened to say.
- 🔑 **`CLAUDE.md` already required this** — *"first ask whether he needs to do it at all… check for a flag, a seat override, or an env var that lets you finish it yourself."* The rule was there and seats kept handing him pastes anyway.
