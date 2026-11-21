# RIMMANDRAKE_DEPLOY_BEFORE_GAME_VISIT_PYRELANDS_REFUSED_THRICE

Written by the Conductor at 6:50 PM PST 2026-11-20, from what it saw live. The ticket title was filed before the drift
was read. **The title's premise is partly wrong; this file is the truth.** Read all of it before you design the fix.

## What happened (measured)

- 5:47 PM PST: Pyrelands blind cycle 4 met its exit. 6:03 PM: its steward advanced Pyrelands to `in_game` (7a6a833965).
- The Dispatch tick filed `RIMMANDRAKE_DRIVE_PYRELANDS_IN_GAME_VISIT_TWO` and called the launch. `maturation.py`
  `launch()`, in_game branch, calls `mod_deployed()` (line ~2427). It returned not-current. The launch returned
  `REFUSED: ... would play a game copy not checked against the repo`.
- The tick retried on its next firings. Three refusals counted as 3 system faults. `OPS_MATURATION_SYSTEM_FAULT_LOOP`
  paused Pyrelands at about 6:15 PM. It stays paused until someone runs `maturation_dispatch.py clear Pyrelands --why`.
- Game a was UP and the bridge was FREE the whole time. Nothing else wanted the game.

## The drift was NOT a stale Pyrelands build (measured 6:48 PM PST)

Pyrelands is composed into Baroque Biomes (`src/RimMandrake/Biomes.compose.json`), so `mod_deployed` runs
`deploy_custom_mods.py --compose biomes` (plan only). Only the text "Everything in sync." reads current. The plan said
"Drift found." for these lines, and no others:

- `~ Biomes/Cauldron/mutants_cauldron_trunk_deposits.sh`: a dev test script of CAULDRON, a mod under the owner's hold.
  It is not game content. It changed in the repo (commit e6ffd743bf, image skills moved). `src/DEPLOY_HOLD.txt` holds
  other dev scripts out of the deploy; this one is not held.
- nine `-` lines: textures that are in the game folder and not in the repo, all under
  `Biomes/Pyrelands/Textures/Things/Filth/` (`RM_FE_AshCoverRipple.png`, `RM_FE_AshCoverStreak.png`, seven
  `RM_FE_LooseAsh/LooseAsh*.png`). `git log --diff-filter=D` finds no commit that deleted them: their origin is
  UNKNOWN. The game folder may hold the only copy.

So no Pyrelands def, DLL or shipped texture differed. The visit was stopped by one dev script of another mod and by
nine extra files.

## Why a plain "deploy, then launch" does not fix it

- `--apply` writes the `~` file. It does NOT remove `-` files ("kept; use --prune to delete, or --pull to rescue").
  After `--apply`, the plan still says "Drift found.". An auto-deploy that re-reads `mod_deployed` would refuse
  again, forever. Test this case first.
- Do not `--prune` those nine textures blind. Generated art is not disposable (owner rule; an agent once deleted real
  generated images as cleanup). Find where they came from. If they are real art, `--pull` them into the repo through the
  art ledger. If they are leftovers of a retired asset, prune them, and say which evidence shows it.
- The check is on the whole composed mod. One drifting file in any of the member biome mods stops the visit of any
  other member. Six member mods are under the owner's hold (`src/RimMandrake/rimflow/mod_owner_hold.json`); a helper
  may still write their design text and scripts, so this will recur.

## What the fix must decide (the design questions)

1. What must match for a visit of mod M? Options: (a) the whole composed mod, as now; (b) only files the game loads
   (Defs, Patches, Assemblies, Textures, Languages, About), for the whole composed mod; (c) only M's files. The danger
   the check guards: in-game verdicts on a copy that is not the committed one (2026-11-19, GimmeSomeSlack visit 2 was
   owed with an old DLL and `.srchash`). A dev `.sh` cannot cause that. A stale def of another member biome can change
   what M's scenes see. The Conductor's lean: (b). Decide with the evidence, say why.
2. `-` lines: extra game files. Are they drift for this check? A texture no def names cannot change a verdict. A stray
   def XML can. Decide per file kind.
3. Self-repair: when real drift exists and the bridge is takeable, the launch path deploys. Things that bind:
   - Pyrelands ships `Assemblies/FireEcologyHook.dll`. A DLL cannot be written while the game runs: game down first
     (`./game --idle-ok --why ... down`), deploy, then up. A deployed def or texture is only played after a reload, so
     a restart is needed for XML too.
   - Load time: the full mod list takes many minutes; a minimal list about 22 s (`skills/rimworld-load-round/SKILL.md`).
     The visit's tier decides which.
   - Two games: `mod_deployed(game=...)` and `--instance b` already target game b's own install
     (`D:\ClaudeWork\rimmandrake\instances\b\game`). Deploy to the game the visit will drive, never the other.
   - His hold on game a (`./pipe off game:a`): deploy and restart tools refuse game a without `--despite-hold`. A visit
     then goes to game b. Do not pass `--despite-hold`.
   - His OWNER bridge hold and "never fullscreen or focus the game" still bind.
   - The companion check beside it (`companion_current`, `COMPANION_FIX`) has the same refuse-only shape.
4. A deploy that fails is the only refusal left, and it names the deploy's cause.

## How it meets the other open ticket

`RIMMANDRAKE_STOP_COUNTING_DRAIN_REFUSALS_AS_SYSTEM_FAULTS` is in the same launch and tick code: a launch refused for
a planned, self-ending reason (the account drain) counted as a system fault and paused FlowWorks. The common fault: the
tick treats every refused launch as a system fault and retries the same launch unchanged. Fix both in one run. A
refusal whose cause the tick can repair, or that ends by itself, must not count toward the fault loop.

## Acceptance test (not yet written, not yet seen failing)

A selftest with `MATURATION_DEPLOY_PLAN` stubs (the env var `mod_deployed` already reads). Expected 6 of 6:

1. plan = this evening's real output (one `~` dev script of another member, nine `-` textures): the visit launches,
   with no deploy and no game restart. On the base commit this refuses: the red run.
2. plan = a `~` on a Pyrelands def: the launch path deploys once, restarts the game, re-reads, launches.
3. plan = a `~` on a DLL with the game up: game down before the deploy, up after.
4. the deploy exits non-zero: REFUSED, the message names the deploy failure; counted as a real fault.
5. plan could not run (could not look): REFUSED as could-not-look, never read as current.
6. bridge held by another seat, or game a under his hold with no game b: no deploy, the tick waits, fault count 0.

Cover the input kinds, not only these examples (an empty plan, a plan with only `+` lines, a `-` line on a def XML).

## After the fix

Clear Pyrelands (`maturation_dispatch.py clear Pyrelands --why`), watch the tick launch visit 2 by itself, and put the
run id on this item. That live launch is the proof; the selftest alone is not.

## What is not known

- The origin of the nine extra textures.
- Whether other member biomes carry the same kind of non-game drift today (only this plan was read).
- Which game the refused visit targeted (the default is a).
