"""image_skills.py — where the generating-images and editing-images skills live.

Both moved out of this repo to `~/dev/MandrakeWorkflows/skills/` (D:\\Luke\\dev\\MandrakeWorkflows\\skills) on
2026-11-19 (owner, by card: "Move to MandrakeWorkflows"; RIMMANDRAKE_MOVE_IMAGE_SKILLS_TO_WORKFLOWS_GPT_TOOL_BORROWS).
Every tool here that runs their scripts (codex_image.py, pnglib.py, chroma_key.py, ...) resolves them through this
module. `$RM_IMAGE_SKILLS_ROOT` overrides the folder holding the two skills; shell scripts use
`${RM_IMAGE_SKILLS_ROOT:-$HOME/dev/MandrakeWorkflows/skills}`.

Paths are computed at import and never checked there (the art daemon builds its worker path at import);
`require()` and `add_to_path()` fail by name when the folder is absent.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

ENV = "RM_IMAGE_SKILLS_ROOT"
DEFAULT = "~/dev/MandrakeWorkflows/skills"
ROOT = Path(os.environ.get(ENV, "").strip() or os.path.expanduser(DEFAULT))
GENERATING = ROOT / "generating-images"
EDITING = ROOT / "editing-images"
GENERATING_SCRIPTS = GENERATING / "scripts"
EDITING_SCRIPTS = EDITING / "scripts"
CODEX_IMAGE = GENERATING_SCRIPTS / "codex_image.py"


def require(path: Path) -> Path:
    if not Path(path).exists():
        raise FileNotFoundError(f"{path} is absent: the image skills live in {DEFAULT} (MandrakeWorkflows); "
                                f"clone it or set ${ENV} to the folder holding generating-images/")
    return Path(path)


def add_to_path(scripts: Path = GENERATING_SCRIPTS) -> Path:
    """Put a skill's scripts dir first on sys.path (for `import codex_image`, `import pnglib`)."""
    s = str(require(scripts))
    if s not in sys.path:
        sys.path.insert(0, s)
    return Path(s)
