# BOUNDARY: the names of the games, Design Version 0.1.0

Code: `src/RimMandrake/rimflow/game_names.py` (all of it), and the places that read or type a game through it:
`src/RimMandrake/rimflow/game_lock.py` (`check_game`, `line`, `_res`, `_query_main`, `main`),
`src/RimMandrake/Utils/game_instance.py` (`check_name`, `brief`, `status_lines`, `launch`, `stop`, `main`),
`src/RimMandrake/rimflow/control.py` (`scope_of` for `game:`, `game_held`, `describe`, `game_lines`, `cmd_switch`),
`src/RimMandrake/rimflow/model.py` (`bridge_host_key`, `bridge_body`), `src/RimMandrake/rimflow/cli.py`
(`_who_lines`, `_bridge_other_host_locked`), `src/RimMandrake/rimflow/maturation_dispatch.py` (`pick_game`, the
tick's `put`), `src/RimMandrake/rimflow/maturation.py` (`FREE_GAME_RULE`, `deploy_repair`, `launch_mod`'s bridge
check, `bridge_idle`).
Item: `RIMMANDRAKE_RENAME_GAMES_ARCHBIG_ARCHSMALL_STEVE1_STEVE2_LETTERS_UNREADABLE`, written 2026-11-22. The owner, by
card, about 2:35 AM PST: *"A and b lower case are very hard to read and recognize."* · *"Let's go with ArchBig,
ArchSmall, Steve1 & Steve2."* Each promise has a test of its name in `src/RimMandrake/rimflow/selftest_game_names.py`,
which also runs every test on a planted wrong map (ArchSmall pointed at Steam's install) and fails unless that goes red.
This page covers only these parts of the files named; the rest of each file has its own page or none.

## ACCEPTS (the only inputs this is built for)

- **a-game-as-typed.** A game name in any letter case (ArchBig, ArchSmall, Steve1, Steve2); an instance letter (`a`,
  `b`, and on); a bridge key (`archmagi`, `archmagi.b`, `stevedesktop`, `stevedesktop.b`, `<machine>.a`); any of these
  after `game:`.
- **this-machine.** `RM_HOST`, else the host name. A host that is not a game machine reads as Archmagi, the default
  host, as in `model.DEFAULT_BRIDGE_HOST`.

## DOES NOT SURVIVE (not promised)

- **a-third-game-on-a-machine.** A letter past `b` has no name from the owner. It reads as its bridge key
  (`archmagi.c`), never as another game's name.
- **a-raw-reader-of-rm-game-instance.** `RM_GAME_INSTANCE` stays a letter. A shell that sets it to a name by hand is
  not read by `host_guard`, `model` or `game_paths`; `game_instance.py env <name>` exports the letter.
- **free-text-a-format-string-did-not-build.** `name_text` rewrites `game a` / `game b` / `game:a` in messages our code
  formats; "game a run" and "game a live run" are left, as English. Text from elsewhere is not promised.

## PROMISES (each one is owed a test of the same name)

- **every-reader-prints-the-games-name-never-a-bare-letter.** `game_lock` lines and refusals, `game_instance status`
  and the run brief, `./pipe show`'s game lines, a game switch's description, the tick's reasons per game and
  `rimflow bridge who --host` name each game ArchBig, ArchSmall (Steve1, Steve2 on SteveDesktop), and none of them
  prints `game a`, `game b` or `game:a`.
- **every-input-takes-a-name-in-any-case-and-the-old-keys-and-both-reach-one-lock.** `game_lock.check_game`,
  `game_instance.check_name`, `control.scope_of("game:...")` and `model.bridge_host_key` take each name in any letter
  case and each old key, and resolve both to the same letter, scope or key; every form of a game reaches one lock file,
  and ArchSmall's is `instances/b`'s, never Steam's.
- **an-unknown-name-is-refused-by-name-never-a-default-game.** An unknown name is refused by each input with the name
  in the refusal; a game of another machine (Steve1 on Archmagi) is refused as that machine's, never mapped to a game
  here.

Later lists beside this page: `polish.md` (none yet) and `next_version.md` (none yet).
