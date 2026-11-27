# WreckedMachines

_Authored mod. `packageId: mandrake.rm.wreckedmachines`, namespace `RimMandrake.WreckedMachines`, prefix `RM_WM_`._

Ancient machines are found wrecked, carried home, studied and repaired where they stand, in two steps: Wrecked to
Kludged, Kludged to Refurbished. No repaired machine works as well as the Original, which is the donor mod's own machine.

The Design Version, its bars and its tests are in `design/concepts/WreckedMachines/` (`version/VERSION.json`,
`version/test_table.md`, `journal.md`).

## What lives where

| Path | What it is |
|---|---|
| `About/About.xml` | Mod metadata. Depends on Vanilla Furniture Expanded - Factory. |
| `DESIGN.md` | The build's contract: names, files and behaviours that the code, the defs and the tests agree on. Read it first. |
| `MACHINES.md` | The picture lane: which machines get pictures and how each picture is made. |
| `Defs/`, `Patches/` | The onboarding table (`Defs/MachineLines`), the level defs, the projects, the jobs. |
| `Textures/` | The Wrecked and Kludged pictures, in the layout the game loads. |
| `Source/*.cs` | The C# (`python3 src/RimMandrake/Utils/winbuild.py WreckedMachines`). |
| `Source/onboard.py` | Stamps a machine's level defs and projects from its row and the donor, and lands a line. |
| `Source/grab_source_art.py`, `briefs.py`, `facing.py`, `fit_sprite.py`, `check_sprite.py`, `judge_packet.py` | The picture tools (`MACHINES.md`). |
| `Source/onboarding_staged/` | Rows and stamped defs of machines whose pictures have not passed the art judge yet. The game never loads it. |
| `art_source/` | The picture workshop of the smelter. Later machines are made in a work folder outside the repo (`--root`). |
| `selftest_*.py`, `validation.py` | The offline tests and the live scenes (`version/test_table.md` lists them). |

`Source/`, `art_source/` and `*.md` are not deployed: the game receives `About/`, `Assemblies/`, `Defs/`, `Patches/` and
`Textures/`. Deploy with `python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod WreckedMachines` (a plan; `--apply`
writes).
