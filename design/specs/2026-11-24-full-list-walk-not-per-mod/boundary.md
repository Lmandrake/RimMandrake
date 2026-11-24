# BOUNDARY: a mod is developed, tested and walked on its small list (small_list.py; build_match.walk_letter; maturation.walk_small_list_why, walk_letter; maturation_autonomy.walk_game), Design Version 0.1.0

Code: `src/RimMandrake/Utils/small_list.py`, `src/RimMandrake/rimflow/build_match.py` (`walk_letter`, `walk_paths`),
`src/RimMandrake/rimflow/maturation.py` (`walk_small_list_why`, `walk_letter`) and
`src/RimMandrake/rimflow/maturation_autonomy.py` (`walk_game` and the `autodeploy` act). Tests:
`src/RimMandrake/rimflow/selftest_walk_small_list.py`.

The rule: `design/RimMandrake/standing_rulings.md` §Mod development runs on small lists (owner, 2026-11-24, "go").
The failure: 65 hours of ArchBig in a week, 31% of it on the full list, and four mods in a line (`proposal.md`).

## ACCEPTS

- **a-small-list-file.** `design/concepts/<Mod>/version/small_list.json`: `mod`, `tier` (a `modset_builder` tier), `why`, `also`.
- **a-mod-folder.** `src/<tier>/<Mod>` with `About/About.xml`, and `Defs` and `Patches` at any depth.
- **a-walk-savegame-path.** A Windows or WSL path of an `.rws` file.

## DOES NOT SURVIVE (not handled)

- **a-mod-that-only-the-code-reaches.** A type that the C# looks up by name is not read. Declare it in `also`.
- **a-patch-of-a-def-by-name.** An xpath that names a def of another mod, with no FindMod and no MayRequire, is
  `modcheck/patch_targets.py`'s work.
- **the-order-of-the-list.** The walk savegame is compared as a set.

## PROMISES (each one is owed a test of the same name)

- **a-patched-mod-absent-from-the-list-fails.** A mod that the source depends on, patches behind FindMod or names in MayRequire, and
  that is on the whole list he plays, must be on the small list.
- **a-mod-he-does-not-play-is-named-not-failed.** Such a mod that is not on the whole list reads OFF LIST.
- **one-of-a-findmod-group-is-enough.** FindMod and MayRequireAnyOf match on any of their mods.
- **a-findmod-name-that-no-mod-has-fails.** The patch can never match, and the game logs nothing.
- **a-folded-mod-is-held-by-baroque-biomes.**
- **every-list-holds-all-five-expansions.**
- **every-list-holds-the-zoom-mod.**
- **a-mod-the-code-reaches-is-needed-when-declared.**
- **an-unreadable-patch-is-could-not-look.** Never "not installed".
- **an-about-that-fails-once-is-read-again.**
- **could-not-look-exits-two.**
- **a-walk-save-on-the-small-list-passes.** A walk savegame with more or fewer mods is refused at the Stage 6 exit. The refusal
  names the tier to stage on.
- **a-visit-that-opened-before-the-ruling-keeps-its-save.**
- **the-walk-game-holds-the-save.** He walks on the game whose Saves folder holds the walk savegame, ArchSmall included. The walk build, its
  deploy and his hold are read on that game.
- **a-stale-walk-build-is-deployed-to-the-walk-game.**
- **his-hold-is-read-on-the-walk-game.**
- **the-exit-reads-the-list-too.** The Stage 6 exit of a visit that opened after the ruling is not met while the small list lacks a mod
  that the mod needs.
- **a-list-that-cannot-be-read-is-said.**
- **an-opening-time-that-cannot-be-read-is-said.**

## LIMITS

None. The one date, `SMALL_LIST_FROM`, is the ruling's: it keeps the rule off a visit that was live when he ruled.
