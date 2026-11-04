#!/usr/bin/env python3
"""ops_clocks_check.py check - the same as `ops_clocks.py check` (OPS_CLOCKS_DEPLOY_ONE_PINNED_COPY's contract names it)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ops_clocks  # noqa: E402

if __name__ == "__main__":
    sys.exit(ops_clocks.main(sys.argv[1:] or ["check"]))
