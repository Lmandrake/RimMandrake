#!/usr/bin/env python3
"""The publish door's check of the tree's own test tables: scene_size.py check, whole tree. Exit 0 clean, 1 a new oversized
live test with no cheaper_why, 2 could not look."""
import sys

import scene_size

if __name__ == "__main__":
    sys.exit(scene_size.main(["check"]))
