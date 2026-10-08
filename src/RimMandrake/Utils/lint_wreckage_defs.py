#!/usr/bin/env python3
"""Offline lint of the Wreckage mod (defs/patches vs C#): see lint_mod_defs.py for the checks.

    python3 src/RimMandrake/Utils/lint_wreckage_defs.py [--mod-dir <dir>] [--quiet]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lint_mod_defs  # noqa: E402

if __name__ == "__main__":
    sys.exit(lint_mod_defs.run("Wreckage", sys.argv[1:]))
