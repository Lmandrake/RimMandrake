"""dispatch_door.py: load Dispatch's Codex door (`providers/chatgpt/bin/`), the one way this repo starts Codex.

`load()` is the question door (gpt_door.py: gpt_consult.py, canon_check.py), `load("door_agent")` runs an agent in a
folder (agent_runner.py), `load("door_image")` and `load("image_guard")` make and check a picture (the image command
line codex_image.py in MandrakeWorkflows uses them too). One sign-in folder serves all three.
`$RM_DISPATCH_ROOT` overrides where Dispatch lives (default `~/dev/Dispatch`). A missing Dispatch fails by name.
Design: `~/dev/Dispatch/design/specs/2026-11-23-one-codex-door/boundary.md`.
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


def load(module: str = "gpt_door"):
    """One module of the door, or DoorMissing naming the path and the override."""
    if not (BIN / (module + ".py")).is_file():
        raise DoorMissing("Dispatch's Codex door is absent: no %s. Clone Dispatch to ~/dev/Dispatch, pull it, or set $%s."
                          % (BIN / (module + ".py"), ENV))
    if str(BIN) not in sys.path:
        sys.path.insert(0, str(BIN))
    import importlib
    return importlib.import_module(module)
