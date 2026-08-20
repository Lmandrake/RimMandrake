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

## 🔴 DO NOT MESSAGE OTHER AGENTS — owner's ruling, 2026-08-19

`SendMessage` to a peer session is an **interrupt**. It lands in another seat's
context mid-turn and **bills their tokens exactly like a prompt the owner typed**.
It is not free, and it is not a courtesy.

**Send one only when BOTH hold:**

1. **The owner asked for it**, or it is a real emergency — the other seat is about
   to destroy work, is acting on a ruling that has been reversed, or is about to
   test something that is not live.
2. **One or two sentences.** If it needs a third, it was never a message.

⛔ **Never for:** a spec · a contract · a handoff · a status · a finding · a
summary · context · reasoning · "here is what I decided" · anything the other seat
will find in its inbox anyway. **All of that is a QUEUE ITEM.** A queue item can be
as long as it needs to be and costs nobody a token until they choose to read it.

⚠️ **There is no broadcast, and there never was.** `SendMessage` addresses exactly
one named target. The `@` typeahead is an affordance in the **owner's own prompt**
for naming one session so Claude need not call `ListAgents` first — it is not a
fan-out operator and there is no `@all`. So "I will broadcast it" is never the
plan; the only question is whether to interrupt **one named seat**, and the answer
is almost always no.

🔑 **A peer message cannot change configuration anyway.** Claude Code instructs a
receiving session never to alter permission settings, `CLAUDE.md` or other config
because another session asked. **Only the owner can.** So a message arguing for a
rule change is wasted tokens by construction — put it in the queue or in
`queue/HUMAN.md`.

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
```

Paths in prose are always full and native, in backticks:
`D:\Luke\dev\Rimworld\infrastructure\state\V1.md`.

## Skills

Load themselves off their description when the task matches. The roster is
`skills/README.md`. The ones you will actually reach for:
`rimworld-modding` · `rimworld-deploy` · `rimworld-load-round` · `rimbridge` ·
`efficient-subagents` · `generating-rimworld-sprites`.
