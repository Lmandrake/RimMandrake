"""codex_cli.py — find the Codex CLI and its home, for callers that run Codex as a text agent.

gpt_consult.py and `codex_side.py` (the shell wrapper) use this. It is a copy of the finder half of
codex_image.py, which now lives in `~/dev/MandrakeWorkflows/skills/generating-images/scripts/`: the ask-GPT
tool must not depend on an image skill outside this repo (RIMMANDRAKE_MOVE_IMAGE_SKILLS_TO_WORKFLOWS_GPT_TOOL_BORROWS).
Image work keeps using codex_image.py through `image_skills.py`. A fix to the finder belongs in both copies.

Codex defaults to the Linux CLI on Archmagi/WSL; RM_CODEX_SIDE=win selects the Windows CLI (`codex_side.py`).
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from codex_side import codex_side, in_wsl  # noqa: E402,F401
from rmpaths import rm_str  # noqa: E402  (data root: rmpaths.py)

# CODEX_MODEL overrides, and `--model inherit` restores the config.toml choice. Same pin as codex_image.py.
DEFAULT_MODEL = os.environ.get("CODEX_MODEL", "gpt-5.6-sol")


# codex.exe FAILS with an ext4 cwd and HANGS reading \\wsl.localhost paths (MEASURED,
# git_workflow_plan_2026-10-01.md §2.3), so the Windows side works under the data root's scratch.
def scratch_root() -> Path:
    default = (str(Path.home() / ".local/state/rimmandrake/scratch/codex")
               if codex_side() == "wsl" else rm_str("scratch", "codex"))
    return Path(os.environ.get("CODEX_SCRATCH", default)).expanduser()


CODEX_SCRATCH = scratch_root()


def select_codex(side: str | None):
    """Apply a CLI override before resolving any homes, paths or executable."""
    if side is not None:
        os.environ["RM_CODEX_SIDE"] = codex_side(side)
        global CODEX_SCRATCH
        CODEX_SCRATCH = scratch_root()


def codex_path(p: Path) -> str:
    return str(Path(p).resolve()) if codex_side() == "wsl" else wsl_to_win(Path(p))


class EnvError(RuntimeError):
    """The Codex toolchain is not usable; the message says what to fix."""


def windows_home() -> Path | None:
    """Best guess at the Windows user profile, seen from WSL."""
    users = Path("/mnt/c/Users")
    if not users.is_dir():
        return None
    # USERPROFILE is not exported into WSL, so fall back to the newest profile
    # directory that actually contains a .codex install.
    candidates = [p for p in users.iterdir() if (p / ".codex").is_dir()]
    if not candidates:
        return None
    return max(candidates, key=lambda p: (p / ".codex").stat().st_mtime)


def base_codex_home() -> Path:
    """The machine's real Codex home: $CODEX_HOME, or the discovered one."""
    env = os.environ.get("CODEX_HOME")
    if env:
        p = Path(env)
        if p.is_dir():
            return p
    if codex_side() == "wsl":
        return Path.home() / ".codex"
    for base in (windows_home(), Path.home()):
        if base and (base / ".codex").is_dir():
            return base / ".codex"
    raise EnvError(
        "Cannot find CODEX_HOME. Looked at $CODEX_HOME, /mnt/c/Users/*/.codex "
        "and ~/.codex. Is the Codex app installed?"
    )


def child_env(home: Path) -> dict[str, str]:
    """Environment for codex, with CODEX_HOME actually reaching it.

    MEASURED 2026-09-06: a WSL process does NOT pass arbitrary environment variables to a Windows child;
    CODEX_HOME arrives EMPTY on the Windows side unless it is also named in WSLENV.
    """
    env = dict(os.environ)
    env["CODEX_HOME"] = codex_path(home)
    if in_wsl() and codex_side() == "win":
        names = [n for n in env.get("WSLENV", "").split(":") if n]
        if not any(n.split("/")[0] == "CODEX_HOME" for n in names):
            names.append("CODEX_HOME")
        env["WSLENV"] = ":".join(names)
    return env


def find_codex_cli() -> Path:
    """Locate codex: the Linux CLI, or codex.exe (config.toml -> PATH -> the app's install root)."""
    if codex_side() == "wsl":
        local = Path.home() / ".local/bin/codex"
        if local.is_file():
            return local
        on_path = shutil.which("codex")
        if on_path and not on_path.lower().endswith(".exe"):
            return Path(on_path)
        raise EnvError("Cannot find Linux codex. Checked ~/.local/bin/codex and $PATH.")
    home = base_codex_home()

    cfg = home / "config.toml"
    if cfg.is_file():
        # CODEX_CLI_PATH = 'C:\...\codex.exe'  (single or double quoted)
        m = re.search(r"CODEX_CLI_PATH\s*=\s*['\"](.+?)['\"]", cfg.read_text(errors="replace"))
        if m:
            p = win_to_wsl(m.group(1))
            if p.is_file():
                return p

    on_path = shutil.which("codex")
    # On WSL, selecting Windows must never fall through to the Linux npm CLI.
    if in_wsl() and on_path and not on_path.lower().endswith(".exe"):
        on_path = None
    on_path = on_path or shutil.which("codex.exe")
    if on_path:
        return Path(on_path)

    wh = windows_home()
    if wh:
        root = wh / "AppData/Local/OpenAI/Codex/bin"
        if root.is_dir():
            exes = sorted(root.glob("*/codex.exe"), key=lambda p: p.stat().st_mtime, reverse=True)
            if exes:
                return exes[0]

    raise EnvError(
        "Cannot find codex.exe. Checked CODEX_CLI_PATH in config.toml, $PATH, "
        "and AppData/Local/OpenAI/Codex/bin/*/codex.exe. Install or update the "
        "Codex app, or set CODEX_CLI_PATH."
    )


def wsl_to_win(p: Path) -> str:
    """WSL path -> Windows path, for handing to codex.exe."""
    p = p.resolve()
    if not in_wsl():
        return str(p)
    try:
        out = subprocess.run(["wslpath", "-w", str(p)], capture_output=True, text=True, timeout=10)
        if out.returncode == 0 and out.stdout.strip():
            return out.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        pass
    # Fall back to the /mnt/<drive>/ convention wslpath would have used.
    s = str(p)
    if s.startswith("/mnt/") and len(s) > 6:
        return f"{s[5].upper()}:\\{s[7:].replace('/', chr(92))}"
    raise EnvError(f"Cannot express {p} as a Windows path; codex.exe needs one.")


def win_to_wsl(p: str) -> Path:
    """Windows path -> WSL path."""
    if not in_wsl():
        return Path(p)
    s = p.strip().strip("'\"")
    s = s.replace("\\\\?\\", "")
    m = re.match(r"^([A-Za-z]):[\\/](.*)$", s)
    if m:
        return Path(f"/mnt/{m.group(1).lower()}/{m.group(2).replace(chr(92), '/')}")
    return Path(s)
