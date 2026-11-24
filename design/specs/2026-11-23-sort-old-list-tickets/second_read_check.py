#!/usr/bin/env python3
"""second_read_check.py NAME: the outcome check of one second-read item (sort_batch_accept.py check_second). A file of its
own, because list_dispatch.pick_model gives an item whose check names an `_accept.py` a Sonnet run, and a second read is
Opus work. Exit 0 holds, 1 fails, 2 could not look."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sort_batch_accept as S  # noqa: E402

sys.exit(S.main(["check_second"] + sys.argv[1:]))
