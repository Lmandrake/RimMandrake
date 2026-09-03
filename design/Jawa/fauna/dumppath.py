"""Resolve the live def dump, whichever layout it is in.

The dumper moved from <DefDump>/defs/ to <DefDump>/captures/<id>/defs/ on 2026-08-22
(DUMP_PRODUCER_DATED_CAPTURES_1). Scripts that hardcoded the old path fail with
FileNotFoundError - which is the good outcome. The bad one would have been a stale copy
still sitting at the old path and being read as current.
"""
import os, sys, glob

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, "src", "RimMandrake", "Utils"))
from game_paths import DUMP_ROOT  # noqa: E402

BASE = DUMP_ROOT

def dump_root():
    caps = sorted(glob.glob(os.path.join(BASE, 'captures', '*')))
    for c in reversed(caps):                    # ids are ISO timestamps, so lexical == newest
        if os.path.isdir(os.path.join(c, 'defs')):
            return c
    if os.path.isdir(os.path.join(BASE, 'defs')):
        return BASE
    raise FileNotFoundError(f"no def dump with a defs/ dir under {BASE}")

def defs_dir():   return os.path.join(dump_root(), 'defs')
def animals():    return os.path.join(dump_root(), 'animals.json')

def captures_newest_first():
    """Every capture dir that has a defs/, newest first.

    ⚠️ `dump_root()` returns only the newest, which is right for "what does the
    game have NOW" and wrong for "what is this def's owning mod" - a capture taken
    during a load that discarded defs answers the second question with a hole.
    """
    caps = sorted(glob.glob(os.path.join(BASE, 'captures', '*')))
    out = [c for c in reversed(caps) if os.path.isdir(os.path.join(c, 'defs'))]
    if os.path.isdir(os.path.join(BASE, 'defs')):
        out.append(BASE)
    return out
