#!/usr/bin/env python3
"""LabWorld "bends" rows to lab_sharp_sheet.py's input. python3 ralph/live/lab_bends_rows.py OUT.json SHARP.json"""
import json, sys
B = json.load(open(sys.argv[1]))["bends"]
json.dump([dict(apex=[r["x"], r["z"]], forced=None if r["why"] == "unforced" else r["why"], cls="end" if r["fromEnd"] < 0.75 else "mid", piece=r["piece"], turn=r["turn"]) for r in B["rows"]], open(sys.argv[2], "w"))
