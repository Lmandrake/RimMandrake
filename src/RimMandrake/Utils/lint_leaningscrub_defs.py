#!/usr/bin/env python3
"""Offline lint of the LeaningScrub mod (defs/patches vs C#): see lint_mod_defs.py for the checks.
The pilgrim's token has no art yet (its def says so: placeholder until generated), so it is a WARN, not an ERROR.

    python3 src/RimMandrake/Utils/lint_leaningscrub_defs.py [--mod-dir <dir>] [--quiet]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lint_mod_defs  # noqa: E402

if __name__ == "__main__":
    sys.exit(lint_mod_defs.run("LeaningScrub", sys.argv[1:], known_missing_art=("Things/Item/Resource/RM_SweetlineToken",)))
