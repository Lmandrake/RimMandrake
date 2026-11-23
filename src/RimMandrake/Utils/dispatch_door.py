"""dispatch_door.py: load Dispatch's GPT door (`providers/chatgpt/bin/gpt_door.py`), the one entry for asking GPT.

Every RimMandrake consult goes through it: gpt_consult.py (the CLI shim) and codex_side.py (the shell launcher).
`$RM_DISPATCH_ROOT` overrides where Dispatch lives (default `~/dev/Dispatch`). A missing Dispatch fails by name.
Design: `~/dev/Dispatch/design/specs/2026-11-22-gpt-door.md`.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

ENV = "RM_DISPATCH_ROOT"
ROOT = Path(os.environ.get(ENV, "").strip() or os.path.expanduser("~/dev/Dispatch"))
BIN = ROOT / "providers" / "chatgpt" / "bin"


class DoorMissing(RuntimeError):
    """Dispatch (and so the GPT door) is not on this machine."""


def load():
    """The gpt_door module, or DoorMissing naming the path and the override."""
    if not (BIN / "gpt_door.py").is_file():
        raise DoorMissing("Dispatch's GPT door is absent: no %s. Clone Dispatch to ~/dev/Dispatch or set $%s."
                          % (BIN / "gpt_door.py", ENV))
    if str(BIN) not in sys.path:
        sys.path.insert(0, str(BIN))
    import gpt_door  # noqa: E402
    return gpt_door
