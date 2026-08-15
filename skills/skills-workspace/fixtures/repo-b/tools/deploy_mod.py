#!/usr/bin/env python3
import argparse
ap = argparse.ArgumentParser()
ap.add_argument("--apply", action="store_true", help="actually write (default: dry run)")
ap.add_argument("--mod", action="append", default=[])
ap.add_argument("--prune", action="store_true")
a = ap.parse_args()
print("dry run" if not a.apply else "APPLYING", a.mod)
