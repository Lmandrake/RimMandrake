# RimMandrake

A RimWorld 1.6 campaign (Jawa scavenger clan on a desert world) run as an agent-built,
agent-moderated game: Python tooling, C# mods, and a ledger-driven workflow (`rimflow`) that
coordinates seats (Conductor, Relentless builder/judge pipeline) around the live game.

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
  installs a LaunchAgent or background service; `./game`, seat windows and the Relentless
  pipeline are run interactively or from seat-specific tooling outside this repo's own files.

*Detected 2026-11-10, not verified by running it.*
