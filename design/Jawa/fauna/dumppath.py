"""Resolve the live def dump, whichever layout it is in.

The dumper moved from <DefDump>/defs/ to <DefDump>/captures/<id>/defs/ on 2026-08-22
(DUMP_PRODUCER_DATED_CAPTURES_1). Scripts that hardcoded the old path fail with
FileNotFoundError - which is the good outcome. The bad one would have been a stale copy
still sitting at the old path and being read as current.
"""
import os, glob
BASE = "/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/DefDump"

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
