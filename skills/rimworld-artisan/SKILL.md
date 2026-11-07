---
name: rimworld-artisan
description: The RimMandrake facts on top of the general artisan, artisan-head and artisan-judge skills, for Artisan loops on a RimWorld mod. Use when starting, watching, stopping, gating or landing an rm-ralph unit, reading ARTISAN_NOW or artisan_now.py, working in a ralph/ folder under rm/scratch, giving a loop the game, game B or SteveDesktop through steve.sh, or updating a mod's scoreboard row.
---

# Artisan loops on RimWorld

The method is in `artisan`, `artisan-head` and `artisan-judge`. This file adds only what is true here. Rule for a new
line: if it would still be true with RimWorld removed, it belongs in those skills.

Scoreboard per mod: [references/scoreboard.md](references/scoreboard.md). Update it on every claim, verdict and owner's look; the
`Acceptances` line that `artisan_now.py` reads is in the general skill's `references/learned.md`.

## Where things are

| | |
|---|---|
| Units | `rm-ralph-*` (`systemctl --user list-units 'rm-ralph*'`) |
| Clones and `ralph/` | `/home/mandrake/rm/scratch/BENCH/ralph_<mod>/`. Read only unless you are the head writing `OWNER_NOTE`, `PROMPT.md` or `STOP` |
| Logs, shots, verdicts | `D:\ClaudeWork\rimmandrake\ralph_<mod>\` |
| The page | `D:\ClaudeWork\rimmandrake\conductor\ARTISAN_NOW.md`, and `ARTISAN_NOW_PHONE.md` beside it (`src/RimMandrake/Utils/artisan_now.py`, `rm-artisan-now.timer`, every minute, no model) |
| The frozen statement | The mod's `## north star` in `design/validation_walks/RimMandrake/<Mod>.md` |
| Second-machine design | `design/RimMandrake/two_rimworld_instances_2026-11-07.md` (the steps for a loop on game B are its section "How a loop goes on game B") |

## Writing the prompt here

- Name the telemetry database and its history as a resource (`telemetry` skill): *"The artisan loops have access to the full telemetry we
  built into BRIDGE, right? That's a very robust database of performance and useful extractions, as well as its historical database should
  they wish to understand current trends vs. past trends. That's important to provide."*
- Name what it may not touch ("Stay inside <Mod>"), and keep a loop's writable mods disjoint from any other loop's on the same machine: every
  game on a machine loads one `Mods` folder, and a deploy with two games up is unmeasured.
- A good offline list to name: the mod's selftests and kernel fuzz. A shape lab or an offline geometry solve beats a pass of screenshots.

## The game gate

`ralph/game_gate.py` is the gate. Its pattern matches the playtest runner's and proof scripts' filenames anywhere in a local command, a `grep`
included, so tell a loop to open those files with Read.

Long bridge scripts: write output to a file and background them with a long timeout, since piping through `cut` hides everything. A killed
script leaves the game running, so pause it.

## SteveDesktop, a second game

A loop's unit and agent run on Archmagi; only the game and its tools run on SteveDesktop, through `ralph/steve.sh`. No credential moves. So
`systemctl --user is-active` over ssh there reads such a unit as inactive.

- 🔴 **Never reboot that machine for a game problem** (owner): *"Even with CPU faults, rebooting the game often clears any damage caused sufficient
  for this kind of testing. Don't keep rebooting it. It's slow and hard on the machine."* `ralph/steve.sh reboot` is the last resort, only when the
  game won't come up at all after a retry.
- It has a CPU fault nobody has cured, showing some minutes after boot. If `ralph/steve.sh status` shows `bad_cpus` other than `[]`, or a result
  surprises you, restart the game and rerun before acting on it. Uptime alone isn't a reason to do anything.
- A dead game or a dropped ssh there is weather, not the mod's bug. Log how often.
- `src/RimMandrake/Utils/testq/` is its no-model test queue; its lane pauses while a loop holds the game.
- `src/RimMandrake/Utils/game_instance.py` (`RM_GAME_INSTANCE=b`) says which game a process means. A loop on older tools still picks the first game,
  so every loop sharing a machine carries this code before game B goes up.

## Landing

- The pre-push guard wants source committed first, then the rebuilt DLLs with their `.srchash`. A module shared between mods (`SlackGeometry` into
  FlowWorks) needs both rebuilt first.
- Art goes through the art ledger's `art install`, not around it. The guard refuses textures that went around.
- Prove on the full mod list last, after small lists.
- A loop's mod-specific findings go in that mod's own doc or selftest at landing.
