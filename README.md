# RimMandrake

**This is an agentic experimental software factory, and the thing it is building is a game.**
Both halves matter. Read **[`PURPOSE.md`](PURPOSE.md)** before anything else in this repo —
nothing here reads correctly without it.

In short:

- It is intended to produce **the most comprehensive remake of RimWorld ever attempted** — a
  coherent hand-authored world (biomes, creatures, physics, factions, lore), judged on whether
  the player's experience is right, not on whether code matches a spec.
- It is equally an **experiment in whether agentic factory pipelines can expand a *creative*
  project** rather than merely execute requirements-driven software production: seats and
  roles, an append-only ledger as memory, blind judges, written-down intent before the build,
  Design Versions, refusals that carry a path to pass, and explicit delegation boundaries.
- It is **Lukas Mandrake's passion project and his laboratory** — where he tries new ideas for
  agents, factories, orchestration strategies and workflows, and where the survivors inform his
  research elsewhere.
- The domain is the experimental design, not a hobby that needed tooling. A colony sim is
  **low-consequence** (an agent given real autonomy cannot hurt anyone here) and **deeply,
  intuitively understandable at every step** (a human can look at a screen and know instantly
  that something is wrong). Together that makes agentic behaviour more understandable, more
  interpretable, and more **trustable** — trust earned by watching, not asserted.

This is not merely "a game." Judging it as one misses the experiment; judging it as pure agent
research misses that the game must genuinely be good, because an experiment whose output nobody
cares about cannot test taste.

**Full declaration, the experiments being run, what this is *not*, and where to go next:
[`PURPOSE.md`](PURPOSE.md).**

Private passion project, built on RimWorld 1.6 (© Ludeon Studios) with all expansions
assumed. Current campaign: a Jawa scavenger clan on a desert world.

---

## The game and the factory

A RimWorld 1.6 campaign run as an agent-built, agent-moderated game: Python tooling, C# mods,
and a ledger-driven workflow (`rimflow`) that coordinates seats (the Conductor and the helpers
it launches) around the live game. The rules every agent obeys are in `CLAUDE.md` and
`infrastructure/agents/CHARTER.md`; the protected vocabulary is `LEXICON.md`.

## First run

- **Environment**: no `.venv`, `pyproject.toml`, `requirements.txt` or `package.json` at the
  repo root — the `./game`, `./bridge`, `./mirror`, `./publish`, `./pulse` wrapper scripts are
  Bash that shell out to stdlib-only Python 3 (`src/RimMandrake/rimflow/cli.py`,
  `src/RimMandrake/Utils/pulse/pulse.py`, `publish.py`, `mirror.py` — no imports beyond the
  standard library found). `src/` also holds C#/.NET mod projects
  (`Directory.Build.props`/`.targets`, individual `.csproj`s under `src/Jawa/` and
  `src/RimMandrake/`) that build against RimWorld's own Harmony DLL on Windows; **`dotnet` is
  not installed on this machine**, so the C# side cannot be built here — mod work targets a
  Windows box with the Steam RimWorld install.
- **Console scripts**: none via a Python package — the entry points are the root wrapper
  scripts themselves (`game`, `bridge`, `mirror`, `publish`, `pulse`), all present and
  executable in the repo root.
- **Login/token**: in-game LLM calls shell out to `claude -p "<prompt>"` and authenticate via
  the normal Claude Code / `claude.ai` login — **never a hosted API key** (owner ruling,
  2026-09-05). `infrastructure/agents/` and `rimflow/login_watch.py` watch that login's health
  but do not themselves hold a credential. A Windows-only MCP tool, `mcp__rimsage__*`
  (RimSage, declared in `.mcp.json` as an HTTP endpoint at `https://mcp.rimsage.com/mcp`), is
  used from the Windows side for def/About.xml lookups — login/auth mechanism for that
  endpoint: Unknown (not found in this repo's files).
- **The job**: no `*.plist`, `install*.sh` or systemd unit exists in this repo. Nothing here
  installs a LaunchAgent or background service; `./game`, seat windows and pipeline helpers are
  run interactively or from seat-specific tooling outside this repo's own files.

*First-run section detected 2026-11-10, not verified by running it.*
