#!/usr/bin/env python3
"""flier_guard.py - refuse flier flip-book inputs in tools that register / crop / centre / scale on the alpha bbox.

FLIER_FRAMES_AUDIT_BODY_NOT_WING_EXTREMES (owner 2026-10-20): a flier's body stays static while its wings flap, so a
flip-book (`<Name>_Flying_<N>_<facing>.png`, the sets `flyingAnimationFramePathPrefix` names) must never be registered
on the alpha bounding box - the wing extremes would move the body. Rewriting tools call `refuse_fliers(tool, *paths)`
on every input/output path they would read-and-rewrite; read-only measuring tools (flier_frame_registration.py,
flyer_lock.check, facing_scale_lint lint) do not call it. Use flyer_lock.py / flyer_plate_from_master.py instead; see
design/RimMandrake/flier_frame_registration_audit_2026-10-20.md (section 'Tool guards').
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

FLIER_RE = re.compile(r"_flying_", re.I)
AUDIT_DOC = "design/RimMandrake/flier_frame_registration_audit_2026-10-20.md"


def is_flier(x) -> bool:
    """True if a path / name / texPath names a flier flip-book frame or prefix. A directory counts if a frame lies directly in it."""
    s = str(x).replace("\\", "/")
    if FLIER_RE.search(s):
        return True
    try:
        p = Path(s)
        if p.is_dir():
            return any(FLIER_RE.search(c.name) for c in p.iterdir())
    except OSError:
        pass
    return False


def message(tool: str, hits) -> str:
    return (f"REFUSED: {tool} registers on the alpha bounding box and would couple a flier's wings to its body "
            f"(owner 2026-10-20: bodies stay static while wings flap). Flip-book input: {', '.join(map(str, hits))}. "
            f"Use src/RimMandrake/Utils/art/flyer_lock.py / flyer_plate_from_master.py; see {AUDIT_DOC}.")


def refuse_fliers(tool: str, *items) -> None:
    """sys.exit with the refusal message if any item (str/Path, or an iterable of them; None ignored) is a flier flip-book."""
    flat = []
    for it in items:
        if it is None:
            continue
        flat.extend(it if isinstance(it, (list, tuple, set)) else [it])
    hits = [x for x in flat if is_flier(x)]
    if hits:
        sys.exit(message(tool, hits[:3]))
