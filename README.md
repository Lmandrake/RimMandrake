# RimMandrake

**This is an agentic experimental software factory, and the thing it is building is a game.**
Both halves matter. Read **[`PURPOSE.md`](PURPOSE.md)** before you read anything else in this repo.
Nothing here reads correctly without `PURPOSE.md`.

In short:

- The project intends to produce **the most comprehensive remake of RimWorld ever attempted**.
  - The product is a coherent hand-authored world: biomes, creatures, physics, factions and lore.
  - The measure is whether the player's experience is right, not whether the code matches a spec.
- The project is equally an **experiment in whether agentic factory pipelines can expand a *creative*
  project**, rather than merely execute requirements-driven software production. The experiment uses these parts:
  - seats and roles;
  - an append-only ledger as memory;
  - blind judges;
  - written-down intent before the build;
  - Design Versions;
  - refusals that carry a path to pass;
  - explicit delegation boundaries.
- The project is **Lukas Mandrake's passion project and his laboratory**. There he tries new ideas for agents,
  factories, orchestration strategies and workflows. The ideas that survive inform his research elsewhere.
- The domain is the experimental design, not a hobby that needed tooling.
  - A colony sim is **low-consequence**. An agent given real autonomy cannot hurt anyone here.
  - A colony sim is **deeply, intuitively understandable at every step**. A human can look at a screen and know
    instantly that something is wrong.
  - Together, the two properties make agentic behaviour more understandable, more interpretable, and more
    **trustable**. Watching earns that trust; nobody merely asserts it.

The project is not merely "a game." If you judge the project as merely a game, you miss the experiment. If you judge
the project as pure agent research, you miss that the game must genuinely be good. The reason: an experiment whose
output nobody cares about cannot test taste.

**The full declaration, the experiments being run, what this is *not*, and where to go next are in
[`PURPOSE.md`](PURPOSE.md).**

This is a private passion project, built on RimWorld 1.6 (© Ludeon Studios) with all expansions
assumed. The current campaign is a Jawa scavenger clan on a desert world.

---

## The game and the factory

The project is a RimWorld 1.6 campaign, run as an agent-built, agent-moderated game.

- Its parts are Python tooling, C# mods, and a ledger-driven workflow (`rimflow`).
- `rimflow` coordinates seats (the Conductor and the helpers it launches) around the live game.
- The rules that every agent obeys are in `CLAUDE.md` and `infrastructure/agents/CHARTER.md`.
- The protected vocabulary is `LEXICON.md`.

## First run

### Environment

- The repo root has no `.venv`, `pyproject.toml`, `requirements.txt` or `package.json`.
- The `./game`, `./bridge`, `./mirror` and `./publish` wrapper scripts are Bash. They call Python 3 programs, among
  them `src/RimMandrake/rimflow/cli.py`, and `publish.py` and `mirror.py` in `src/RimMandrake/Utils/`. Besides sibling
  modules of this repo, the three programs import only the standard library (read 2026-11-23). Nobody read the imports
  of the sibling modules.
- `src/` also holds C#/.NET mod projects: `Directory.Build.props`/`.targets`, and individual `.csproj`s. The mod
  projects build against RimWorld's own Harmony DLL on Windows. The `.csproj`s are in `src/RimMandrake/`,
  `src/RimStarWars/` and `src/RimUtinni/`. `src/Jawa/` holds none (measured 2026-11-23).
- Inside WSL, **`dotnet` is not installed on this machine**. Windows on Archmagi has `dotnet.exe` (measured 2026-11-23).
  Build the C# with `python3 src/RimMandrake/Utils/winbuild.py`, which uses it.
- Mod work targets a Windows box with the Steam RimWorld install.

### Console scripts

- There is no console script from a Python package. The entry points are the root wrapper scripts themselves
  (`game`, `bridge`, `mirror`, `publish`).
- All four scripts are present and executable in the repo root. The root also holds `pipe`, `sync` and `pages`.

### Login/token

- An in-game LLM call runs `claude -p "<prompt>"`. The call authenticates via the normal Claude Code / `claude.ai`
  login, **never a hosted API key** (owner ruling, 2026-09-05).
- `rimflow/login_watch.py` (in `src/RimMandrake/`) watches the health of that login but holds no credential.
  `infrastructure/agents/` holds no credential either.
- `mcp__rimsage__*` (RimSage) is a Windows-only MCP tool for def and About.xml lookups, used from the Windows side.
  `.mcp.json` declares RimSage as an HTTP endpoint at `https://mcp.rimsage.com/mcp`.
- The login or auth mechanism for that endpoint is Unknown (not found in this repo's files).

### The job

- No `*.plist` file exists in this repo, so nothing here installs a LaunchAgent.
- Files here do install background services: systemd units and Windows scheduled tasks. Examples, not the full list:
  - the tracked unit files are in `src/RimMandrake/Utils/systemd/` and `infrastructure/stevedesktop/mutation/`;
  - `src/RimMandrake/Utils/ops_clocks.py install` installs the units of `src/RimMandrake/Utils/systemd/`;
  - the `install*.sh` file `infrastructure/stevedesktop/mutation/install_mutation.sh` installs the mutation timer, and
    does not enable the timer;
  - `infrastructure/stevedesktop/bootstrap_wsl.sh` writes and enables a timer on SteveDesktop.
- `./game` and the seat windows are run interactively, or from seat-specific tooling.
  `src/RimMandrake/Utils/launch_fleet.ps1` opens the fleet's windows from this repo.
- Pipeline helpers run in their own systemd units (`src/RimMandrake/rimflow/detached_helper.py`).

*First-run section detected 2026-11-10, not verified by running it. The facts of this section were read again, or checked
against the files, on 2026-11-23. The exceptions are the in-game LLM call and the RimSage lines.*
