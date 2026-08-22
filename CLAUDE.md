# RimWorld 1.6 — Jawa scavenger clan on a desert world

Read `infrastructure/agents/POLICY.md` and your own `infrastructure/agents/<SEAT>.md`.
They are short. This file is only what neither of them covers.

## 🔴 There is no worldgen feature, in any version — owner, 2026-08-15

*"There is no auto worldgen we are building. The world will be user-made and frozen.
We are NOT enabling worldgen, we will provide players a savegame with a fixed world,
period. True worldgen is OUT of any version, even v2."* — plus, moments later,
*"(but designing worldgen by hand and design documents to guide that are in)"*

- **OUT, permanently, not deferred:** any automated or programmatic worldgen; worldgen
  as a player-facing capability; any v2 worldgen item. ⛔ **v2 is not a parking space
  for it** — mark such work dead rather than moving it to `design/V2_DREAMS.md`.
- **IN:** the owner building the world **by hand, once**, and the design documents that
  guide him. Keep writing those.
- 🔑 **Players never generate anything. They receive a savegame holding the fixed
  world.** One hand-made world, frozen, shipped — so **a faction, ideoligion or setting
  absent when he builds it is absent from every player's game forever**, with no
  regenerate behind it.

### 🔴 ONE MAP, NOT A GENERATOR — owner, 2026-08-18

*"We aren't trying to make random generators that produce alternative planet maps…
that's way out of scope and produces unacceptably unreal solutions. I just want ONE
planetary map that is as realistic as possible, following the guidelines I told you
from design and discussion."*

- ⛔ **Do not build, extend or tune anything that produces ALTERNATIVE planets.** No
  seed sweeps, no "try N variants and pick one", no parameters exposed so a different
  world could be rolled. A knob that can produce a second planet is out of scope even
  if we only ever turn it once.
- ✅ **Author THE map.** Direct, one-off edits to the one world are the whole job, and
  they are judged by **realism first** — does it read as a photograph of a real
  planet — then by whether it follows `design/Jawa/worldbuilding/`.
- 🔑 **Iterate by LOOKING.** `worldview.py` renders the save; change, render, look,
  change again. A number that says the world is fine while the picture shows compass
  circles is the number being wrong.
- The visual target and the reference photographs are
  `design/Jawa/worldbuilding/the_one_map.md`.

## Facts you cannot guess

- **The game reads `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods`,
  never this repo.** Writing a file is not deploying it.
- **A cold load is ~25 minutes.** A quicktest map is ~90 s and answers most things.
  Never say "restart and see".
- **`ModsConfig.xml` is the live mod list**, at
  `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Config\ModsConfig.xml`.
  Read it for the active count; never a number written in a doc.
- **No config file waits for anything.** Owner, 2026-08-15: *"You NEVER have to ask
  if RimSort is open. It does not autosave, and I will never save without asking.
  Nobody blocks on RimSort or game close for config files of any kind."* Write it,
  game up or down. Only **assemblies** need the game down, because the OS locks them.
- **Never guess a defName, field, or namespace.** Read the def, the `About.xml`, or
  ask `measure`. ⚠️ **Corrected 2026-08-21: `strings -a -el` on an assembly is NOT a
  census and this file used to say it was.** Measured against the companion DLL it
  found **16 of 115** tool names — .NET keeps attribute strings in metadata blobs a
  byte scan never reaches, and it reports the shortfall as a clean answer. `strings`
  proves a name is PRESENT; it can never prove one is absent.
- 🔴 **A number about a large artifact comes from `measure`, never from a scan.**
  `grep`, `strings` and `wc` return a plausible number with no error when they cannot
  read the encoding — that cost seven wrong counts in one session, and
  `.claude/hooks/block_blind_scan.py` now refuses the scan and names the instrument.
  ```
  measure count <DefType>     MEASURED 24904 / UNMEASURED + why
  measure coverage            what the dump did NOT capture
  measure explain <path>      what may read this file
  ```
  📦 **The instrument is a SKILL and lives OUTSIDE this repo**, because it is
  generic and this project merely uses it:
  `D:\Luke\dev\measuring-large-artifacts`, installed machine-wide at
  `~/.claude/skills/measuring-large-artifacts`. Run it as `measure …` if `bin/`
  is on PATH, else
  `python3 ~/.claude/skills/measuring-large-artifacts/scripts/measure/cli.py …`.
  🔑 **`0` now means measured zero and nothing else** — ignorance answers `UNMEASURED`,
  a question the instrument cannot judge answers `REFUSED`, and both say what to run
  instead. The register of instruments caught lying is
  `infrastructure/state/BUILDABLE.md`.
- **A patch that matches nothing logs nothing.** `PatchOperationConditional` and
  `PatchOperationFindMod` both return true on no match.

## 🔴 Queue items are NAMED, not numbered — owner's ruling, 2026-08-20

> *"When queue actions are created, they are named `THREE_DESCRIPTIVE_WORDS_#` rather
> than B104 or D5. It's killing me having to guess what D55 is."*

**Every NEW item in `infrastructure/state/queue/*.md` and every new append to
`design/V2_DREAMS.md` gets a name that says what it is:**

```
## MECHANOIDS_STAY_ON_1 Keep the Mechanoid faction; it is the Forgotten Arsenal
## PAWN_KIND_ROSTER_2 Create 48 pawn types so raids field roles
```

- **Three UPPER_SNAKE words, then `_#`.** Three is the target, not a hard cap — but if
  you need six words to say it, the extra words belong in the title after the ID, not
  inside it. The trailing number disambiguates reuse of the same three words; start at
  `1` and only go up when the name is already taken.
- 🔑 **The name must be guessable cold.** The whole point is that a seat reading
  `Closes: SANDSTORM_WEATHER_TUNING_1` in a commit knows what happened without opening
  a queue file. Name it after **what the work is**, never after the seat, the file or
  the sprint.
- ⛔ **No new `B*` / `C*` / `D*` / `W*` IDs.** That scheme is closed. It reads as
  precedence it does not have, and nobody can remember what `D55` was.

**The tooling already accepts it — verified 2026-08-20, no change needed.**
`src/RimMandrake/Utils/derive_matrix.py` takes the first whitespace-delimited token
after `## ` as the ID, and its `Closes:` trailer regex is
`[A-Za-z][A-Za-z0-9._-]*`, which admits underscores and digits.

⚠️ **Legacy IDs stay exactly as they are. Do not rename them.** `POLICY.md` is right
that renumbering an item away breaks the board's count and cannot be recovered — a
legacy item still closes under its own ID (`Closes: B58`). ✅ **But whenever you WRITE
a legacy ID anywhere — a report, a commit body, a queue cross-reference — put its title
beside it:** `B58 (the dead Jawa pawnkind)`, never a bare `B58`.

## Superseding a doc means writing INTO the doc you superseded

**Owner's rule, 2026-08-20**, issued after an audit of two doc clusters. Across 14
files only three items had actually gone wrong, and all three were the same failure:
a doc was answered by a better one and never told.

- 🔑 **When you supersede, correct or measure against another file, put ONE line at
  the top of THAT file** naming the successor and what changed. The successor
  citing its predecessor is not enough — **nobody reads backwards.**
  `restraining_bolt_technical.md` cited the doctrine doc it overruled; the doctrine
  doc had never heard of it, so every reader arriving from the ideoligion rubric got
  the dead numbers.
- ⛔ **"Not my file" does not discharge it.** `droid_taxonomy.md` filed a correction
  that way on 2026-08-13; `droid_ruling.md` was then edited three times by
  reorganisation sweeps and kept the wrong mechanism until 2026-08-20.
- ✅ **Prose that agrees with itself is fine.** Restating a ruling in the doc whose
  argument depends on it is good writing, not duplication. Only a **number, roster or
  ruling that differs between two files** is a defect.
- 🔑 **Single-source only what a GENERATOR can enforce.** Four hand-kept copies of one
  text is a drift machine; one source plus a script is not. Where only discipline
  enforces it, expect decay and write the pointer instead.

## Git

- **Commit explicit paths. Never `git add -A`, `git add .`, or `git commit -a`.**
  Enforced by `.claude/hooks/block_blanket_git_stage.py`.
- **`git commit <path>` commits the working tree at that path, not your index** —
  including a peer's uncommitted edits. Read `git status --porcelain <paths>` first.
- **Push immediately after committing.** Rejected push → `git pull --rebase`, never
  `--force`.
- **Never commit a file over ~50 MB.** GitHub hard-rejects at 100.

## ⛔ AGENTS DO NOT MESSAGE EACH OTHER. AT ALL. — owner's ruling, 2026-08-19

**`SendMessage` to another agent window is off.** Not rationed, not for emergencies —
**off.** Waking another seat is a **USER function**, and the owner has taken it back.

🔴 **Enforced, not merely written — but at the SENDING end.** `.claude/settings.json`
runs `.claude/hooks/block_peer_messages.py` as a `PreToolUse` hook on `SendMessage`: a
message whose target names a seat (BUILD · CHECK · DECIDE · REP) is refused before it
is sent, with the queue files named in the refusal. `ListAgents` stays denied outright, so peers cannot be enumerated either.

⚠️ **`crossSessionInbound` is `accept`, and that is DELIBERATE — do not "fix" it to
`refuse`.** Corrected 2026-08-19 after three docs, this one included, claimed it read
`refuse`. It never did, and it must not: the owner's `broadcast.py` reaches every window
through that same inbound socket, which Claude Code runs through the same inbound
controls as any other peer message. `refuse` would silence **the owner's own game-state
announcements** — the one class of message that is supposed to get through.

🔑 **Why a hook and not a deny rule.** `permissions.deny: ["SendMessage"]` was the old
mechanism and it was too blunt: Claude Code's docs are explicit that *"denying
SendMessage also removes messaging to subagents, since the same tool serves both"*, and
there is no scoped syntax to separate them. It enforced "no peer messaging" by also
breaking every subagent resume — a seat could spawn a worker and never collect from it.
The owner ruled 2026-08-19: *"Sub-agents should function normally."*

**The only thing that legitimately crosses windows is the owner announcing a change of
GAME STATE** — *game is up* · *game is loading* · *WRAP is initiated* — and **the owner
sends those himself, to each window.** You do not relay them, and you do not send one
because you inferred it.

⛔ **There is no exception for:** urgency · a reversed ruling · "they are about to
destroy work" · a spec · a contract · a handoff · a finding · a status · a summary ·
context · reasoning · "here is what I decided". If a peer must know something, it goes
where they already read:

| what you have | where it goes |
|---|---|
| work for another seat | `infrastructure/state/queue/<SEAT>.md` |
| something the owner must decide or relay | `infrastructure/state/queue/HUMAN.md` |
| a correction to doctrine | the file that says otherwise, plus a commit |
| something genuinely urgent | 🔑 **tell the OWNER, in your own reply.** He is reading you, and he is the one with the authority to interrupt anyone |

⚠️ **There is no broadcast and there never was.** `SendMessage` addresses exactly one
named target; the `@` typeahead is an affordance in the **owner's own prompt** for
naming one session, not a fan-out operator, and there is no `@all`.

✅ **Your own subagents are NOT peers and are NOT covered.** `crossSessionInbound` does
not touch them. Spawning subagents and resuming them with `SendMessage` to collect their
findings stays fully authorized and encouraged — that is your own worker in your own
context, costing no one else anything.

🔑 **And a peer message could never change configuration anyway** — Claude Code instructs
a receiving session never to alter permission settings, `CLAUDE.md` or other config
because another session asked. Only the owner can.

## What is where

```
src/                    mods, defs, C#, art          BUILD owns
design/                 campaign specs (Utinni)      DECIDE owns
skills/                 tooling + how-to           the seat that USES it owns it
                                                   broadly shared -> REP
infrastructure/state/   queues, V1.md, facts/        see POLICY.md
```

## Tools

```
python3 src/RimMandrake/Utils/status_server.py     the board -> http://localhost:8787
python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod <name>    dry run; --apply writes
python3 src/RimMandrake/Utils/refresh.py           rebuild the offline def dump
measure count <DefType>       one line; never a bare number  (skill: see below)
python3 skills/rimworld-modding/scripts/validate_patch.py <path> --defs ...
./src/RimMandrake/Utils/show.sh <path>             open it in Explorer
node --check <file.js>        ⭐ Node 22 IS installed, user-local, 2026-08-22 — no sudo,
                              ~/.local/node symlinked into ~/.local/bin. Lint every board
                              view before serving it. REP shipped the board twice in one
                              session saying "no JS engine here", when installing one took
                              40 seconds and found the answer.
./game up|down|loading|deploying|going-down   announce to every window + stamp the ledger
python3 src/RimMandrake/Utils/broadcast.py --list  🔴 OWNER ONLY - see below
```

### 🔑 Declaring game state: just say it

**Owner, 2026-08-22 — he no longer types anything to stamp the board.** Say *"game is up"*,
*"game is loading"*, *"game is going down"* to whichever agent you are talking to, and it
stamps the ledger immediately, recording your words as the authorization:

```
python3 src/RimMandrake/rimflow/cli.py game UP --owner-said "game is up"
```

⛔ **A seat still may not INFER game state** — that is guessing on everyone's behalf, and
it is what the rule always banned. Quoting you is not inferring. ✅ **And neither is
MEASURING it** — owner, 2026-08-22: *"Any agent is absolutely able to check what it
literally is."* `./game` takes the reading and corrects the ledger from it, from any seat.
⛔ **So never write "X says up but the owner said down"** — run it and there is nothing to
report. The full ruling is `infrastructure/GAME_STATE_WORKFLOW.md`.

⚠️ **That stamps the LEDGER, which is what makes `rimflow next` start offering or
withholding `needs: game-up` / `bridge` / `deploy` work.** It does NOT wake the other
windows. **`./game up` does both**, in one word, and is still the better move when other
seats are running:

🔴 **`broadcast.py` is the OWNER's tool and agents do not run it.** It reaches every
agent window at once, by writing the peer socket directly — which permission rules do
not gate. That is the point, and it is also why **an agent running it is breaking the
no-messaging ruling by the back door.** It exists so the owner can announce a change of
GAME STATE (*game is up* · *game is loading* · *WRAP is initiated*) in one command.
```
./game up                      # same thing, one word - announces AND stamps the ledger
./game                         # no argument: what the board thinks vs what is running
python3 src/RimMandrake/Utils/broadcast.py "Game is up"
python3 src/RimMandrake/Utils/broadcast.py --to CHECK,BUILD "Game is loading"
```

Paths in prose are always full and native, in backticks:
`D:\Luke\dev\Rimworld\infrastructure\state\V1.md`.

## Skills

Load themselves off their description when the task matches. The roster is
`skills/README.md`. The ones you will actually reach for:
`rimworld-modding` · `rimworld-deploy` · `rimworld-load-round` · `rimbridge` ·
`efficient-subagents` · `generating-rimworld-sprites`.
