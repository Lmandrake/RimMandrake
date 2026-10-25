"""canon_save.py - the one place that resolves the canonical start savegame name.

Reads `planet.start_savegame` from infrastructure/state/canon.yml (stdlib only, no PyYAML),
so tools never hard-code a save name. Owner card 2026-10-25: canon repointed to
ASHKARR_DEV_START_2026-10-20_PARITY_QUIET_R3.
"""
import os
import re

CANON_YML = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..",
                         "infrastructure", "state", "canon.yml")
_LINE = re.compile(r"^  start_savegame:\s*([^\s#]+)\s*$", re.M)


def start_savegame_name(canon_yml=CANON_YML):
    """File name (with .rws) of the canonical start save, as canon.yml names it."""
    with open(canon_yml, encoding="utf-8") as f:
        m = _LINE.search(f.read())
    if not m:
        raise RuntimeError("canon.yml has no planet.start_savegame line")
    return m.group(1).strip("'\"")
