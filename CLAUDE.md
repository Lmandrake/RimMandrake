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
  `strings -a -el` the assembly. Plain `strings` misses UTF-16 method bodies.
- **A patch that matches nothing logs nothing.** `PatchOperationConditional` and
  `PatchOperationFindMod` both return true on no match.

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

🔴 **Enforced, not merely written.** `.claude/settings.json` sets
`crossSessionInbound: "refuse"`, and a `refuse` in project settings applies over every
other source. **Every agent window in this repo now DROPS inbound peer messages without
delivering them.** So a message you send is not "an interrupt they might forgive" — it
is tokens spent on something the receiver will never see. There is no notice back to
you when a message is refused on arrival, so **you will not even learn that it failed.**

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
python3 skills/rimworld-modding/scripts/validate_patch.py <path> --defs ...
./src/RimMandrake/Utils/show.sh <path>             open it in Explorer
python3 src/RimMandrake/Utils/broadcast.py --list  🔴 OWNER ONLY - see below
```

🔴 **`broadcast.py` is the OWNER's tool and agents do not run it.** It reaches every
agent window at once, by writing the peer socket directly — which permission rules do
not gate. That is the point, and it is also why **an agent running it is breaking the
no-messaging ruling by the back door.** It exists so the owner can announce a change of
GAME STATE (*game is up* · *game is loading* · *WRAP is initiated*) in one command.
```
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
