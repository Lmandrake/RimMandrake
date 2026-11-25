# LEXICON — this project's terminology

This file is the project tier. It narrows or extends the fleet's `~/dev/Lodestar/LEXICON.md`.

- If a term here and a term in the fleet file collide, the term here **wins on
  collision**. Then say so loudly.
- A term here is authorization to use the term when you talk to Mandrake.
- In the tables, "he", "him" and "his" mean Mandrake.

## Who does the work

| Term | Means |
|---|---|
| **Conductor** | The one window he talks to: it decides, routes the work and starts helpers. Also provides collaborative live-game development and testing for smaller items or generates excellent tickets for large work orders. |
| **Maturation Pipeline** | The one pipeline that carries each mod, stage by stage, from design to his walk. |
| **Judge** | An agent that did not build the work and decides whether it passes or is refused against what the work promised. |
| **Designer** | The Maturation Pipeline role that argues a mod idea into a well-defined design before any code, and again when an inconsistency needs refining. |
| **Operations** | The role that watches the production system's health and raises the alarm. |
| **Dispatcher** | The clock that starts scheduled roles; there is no AI in it. |
| **Test Pilot** | One live debugging sitting on one stuck item/ticket, ending in measured cause and check that it produces the fail (the check goes red for the reported reason before the fix). Also called Test Drive. |
| **Fable Rescue** | A Fable run sent to a stuck mod when ordinary building could not finish it. "Rescuer" and "Rescue agent" mean it. |
| **Foundry** | The old builder window; retired, folded into the Conductor now. |
| **Bench** | The old name for the window he talks to; retired, it is the Conductor now. |
| **Relentless** | The retired pipeline era before the Maturation Pipeline; some live paths and names still say it. |

## The game and the proof

| Term | Means |
|---|---|
| **Bridge** | The connection that lets a script drive the running game; one driver at a time. |
| **Live** | In the running game. |
| **Offline** | Needing no running game. |
| **Deployed** | Copied into the game's own mod folder; until then the game cannot see the change. |
| **Minimal mod list** | The handful of mods that loads in seconds; a pass on it proves nothing about his real game. |
| **Full mod list** | His real game's mod list; slow to load, and the only place a final pass counts. |
| **Lightspeed** | The test lane with no AI in it: scripts stage, run and decide every verdict. |
| **North star** | A mod's written list of what the player must see in the game, set down before the build and tested after. |
| **UNMEASURED** | The proof could not ask the question; never a soft pass. |
| **Blocked** | Cannot move until a named other thing is finished or fixed. |
| **Ruling** | A decision of his that stands until he reverses it. |
| **Bar** | A key capability a mod promises the player, judged as an experience; never a tuning number. |
| **Walk** | His own sitting in the game that passes or refuses a mod; only he does it. |
| **Hold** | His stop on a mod: nothing launches on it until he or the Conductor lifts it. |

## Mods, layers and machines

| Name | Is |
|---|---|
| **FlowWorks** | The liquid engine: dig a channel and a liquid flows into it — canals, pits, ponds, tanks, hoses. |
| **Gimme Some Slack (GSS)** | Power cables with slack in them: loose cords on the floor and overhead lines between masts. |
| **Huge Things** | Huge plants and animals that behave like their size. |
| **Pyrelands** | A hot savanna biome that burns on a cycle of its own. |
| **Graffiti** | (his to write) |
| **Explosive Knockback** | Every blast throws everything light near it away from its centre. |
| **Baroque Biomes** | Our family of exotic biomes, each a mod of its own. |
| **Star Wars layer** | Everything that would suit any Star Wars scenario unchanged: races, droids, weapons. |
| **Utinni layer** | Everything that belongs to this one campaign only: its clan, its story, its lore. |
| **Archmagi** | The main machine: his desk, the Conductor, and the games ArchBig and ArchSmall. |
| **SteveDesktop** | The second machine: two games, Steve1 and Steve2, that run test jobs unattended. |

## Machinery words of the rule files

These words are for the files that agents read, not for talk with Mandrake. Each row points at the home of the word.

| Term | Means |
|---|---|
| **Seat** | A name that signs ledger writes: BENCH (the Conductor), OWNER, RUNNER, DISPATCHER. "A seat" in a rule is the window, role or helper that signs with that name (`src/RimMandrake/rimflow/cli.py`, `--seat`). |
| **Helper** | A run that the Conductor or the pipeline starts with `src/RimMandrake/rimflow/detached_helper.py`. |
| **Item** | One entry of the rimflow ledger, shown by `rimflow show <ID>`; "ticket" is the same thing. |
| **Card** | A question to the owner with options that he picks from; the pick is in the card store (`src/RimMandrake/rimflow/card_capture.py`). |
| **His five acts** | A live flight test of a flyer, a replacement of art that he kept, the pass at his walk, a money spend, publication outside the private repos (`CLAUDE.md` §Only five acts stay his). |
| **Tick** | One timed run of the pipeline: `maturation_dispatch.py tick`. In a game sentence, a tick is the game's own time step. |
| **Clone pool** | The reused helper clones under `/home/mandrake/rm/relentless/clones` (`src/RimMandrake/Utils/scratch_clone.py`). |
| **Disk floor** | The free space below which no new clone is made: `ops.disk_brake_free_gb` in `src/RimMandrake/Utils/slot_rules.json`. |
| **Leave line** | The percent left on an account at which work moves to the next account (the `leave` of that account's step in the account plan; `./acct plan` prints it, `./acct line <account> <percent>` sets it). |
| **Companion** | The JawaBench DLL that adds tools to the bridge (`skills/rimbridge-companion/SKILL.md`). |
| **Calibrated brief** | A judge brief whose planted cases ran on its present text and came out as planted (`infrastructure/state/judge_calibration.json`). |
| **Design Version** | The numbered version of a mod's design that the mod is built towards (`CLAUDE.md` §Each mod has its own Design Version). |
| **Operational item** | An item whose result must stay running: a hook, unit, timer or alarm. Its close names its live promise (`CLAUDE.md` §An operational item is done only when it is running). |
| **Live promise** | The `--live` text of a close: what must stay alive and its last reading (`src/RimMandrake/rimflow/live_line.py`). |
| **Boundary page** | The page of promises of a piece of pipeline code, `design/specs/<component>/boundary.md`. |
| **Official dump** | The frozen dump of the game's defs, `observed/inventory/DefDump_OFFICIAL/`. |
| **Naming tiers** | RimMandrake, RimStarWars and RimUtinni, with the prefixes `RM_`, `RSW_` and `RUT_` (`design/NAMING_SCHEME_PLAN.md`). |
| **Direct Sun** | The one heat of the sun, a function of the sun's angle (`design/RimMandrake/unified_direct_sun_heat_2026-10-19.md`). |

## Retired names

A rule file never uses these names. `src/RimMandrake/Utils/guiding_prose.py` returns each one to the writer.

| Name | Write instead |
|---|---|
| **the belt** | The queue of builders of the retired Relentless era. Name the step that does the work now, for example the clone's return step at the end of a run. |
