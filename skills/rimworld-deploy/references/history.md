# History: evidence and old lines that left `SKILL.md`

The lessons are in `../SKILL.md`. This file holds only the old figures and the lines that are no longer true. Git holds the
rest. Each line below is a record, not a rule. The rewrite was on 2026-11-23.

## "Written" and "the game can see it" (§1)

- The source path was once `<repo>/custom_patches/<ModName>/`. The mods are now under `src/<tier>/`.
- §1 once said that the game names its own copy on every launch, with the line
  `Adding mandrake.jawa.patches(C:\...\RimWorld\Mods\Jawa_Patches)`. The `Player.log` of 2026-11-23 holds no line that starts
  `Adding mandrake` (0 matches; the log does name files under `RimWorld\Mods`). `Jawa_Patches` is not a mod any more.

## Plan first (§2, §9)

- §2 and §9 once said that five seats share one working tree. Each run now has its own clone.
- §2 once said to tell the owner before you write a file that you do not recognise. The Conductor decides that now.
- The example mod of the commands was `Jawa_Patches`.

## The `-` line (§3)

- §3 once said that a `-` file is an edit in `Mods/` that `--apply` is about to destroy. Plain `--apply` keeps such a file.

## Validate (§4)

- The three roots were once `"C:/Program Files (x86)/Steam/steamapps/common/RimWorld/Data"`,
  `"C:/Program Files (x86)/Steam/steamapps/workshop/content/294100"` and
  `"C:/Program Files (x86)/Steam/steamapps/common/RimWorld/Mods"`. On 2026-11-23 a WSL run with a `C:/` root printed
  `UNMEASURABLE` and no verdict.
- A run with no `--defs` once said `no --defs given; static checks only`. It still says so when `--live` is absent too.
- The command for the newest list was once `$(ls -t deployed/config/ModsConfig.full-*.xml | head -1)`. CHECK corrected it on
  2026-08-22. That day the glob gave `deployed/config/ModsConfig.full-574.2026-08-12.xml`: 574 mods, ten days old. That list
  still carried `thereallemon.factioncontrol`, which the owner removed on 2026-08-21 because it aborted three save loads. The
  live list was 578 and clean. The advice ("pass the newest
  backup, never a pinned filename") was right; the command globbed the wrong directory.
- The `--restore` source was cited as `modlist_swap.py:24`. The constant is now `FULL` in `modlist_swap.py`.
- §4 once said: if the line does not say 578, you validate against the wrong stack. The list held 315 mods on 2026-11-23. The line
  was cited as `N active mods → M def files`.
- §4 once said that `validate_patch.py` reads `Patches/` only, never `Defs/`. It has read both since 2026-08-13.

## Not every folder is deployable (§6)

- The folder that passed `[ -e "$dir" ]` with only `__pycache__` was `src/RimMandrake/Pits`. That folder is gone.
- Once the tool deployed a folder with no packageId, and RimWorld ignored it. The tool now refuses.

## Assemblies (§7, §9)

- §7 once said to tell CHECK before any shutdown. CHECK is a retired seat.
- §9 once said that nothing in the plan tells "same DLL" from "yesterday's DLL", and that md5 is the only way to know. The plan
  compares bytes. The old command read `src/<Mod>/Assemblies/<Name>.dll`.

## Is this artifact current (§7b)

- §7b once sent the reader to `observed/LIVE.md` for the dump's location and freshness. The dump section of that file is of
  2026-09-09 and earlier.
- On 2026-11-23 the newest capture held 481 def-type files, and 69 had `"count":0` near the top (a text read, not `measure`).
  `AbilityDef` was not empty in that capture.

- The `defs.sqlite` row once ended at the fingerprint: the verdict read current although the capture was gone. A probe on
  2026-11-23 of `DumpDB._staleness` with dated captures read STALE for a named capture that was gone.

## The companion DLL

- The tool list of a DLL was once a BYTE SCAN. Its "added" list was untrustworthy: encoding differences made tools that shipped
  weeks ago look new. The advice was: trust `LOST` being empty and a name being PRESENT, and corroborate a gap with file size
  and the build commit.
- A `jawa/` literal in a description once became a phantom tool name, and the guard of `build.py` then lied in both directions.
  The check after a description edit was `[x for x in surface if x.endswith('_')]`. `tool_metadata.py` replaced the scan on
  2026-09-06 (BUILD_PY_TOOLNAME_SCAN_FALSE_LOSS_1).
