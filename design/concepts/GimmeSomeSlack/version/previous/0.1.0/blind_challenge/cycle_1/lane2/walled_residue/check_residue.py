#!/usr/bin/env python3
"""Exit code for the walled residue: run judge_the_judge/diag.py all N --base (optionally on another GSS tree) and exit 1 unless slack under, stray miss and
unforced bends all read 0 (the twins are RIMMANDRAKE_PART_GSS_TWIN_LEADS_EACH_DRAWN_ALONE's). Usage: check_residue.py [N] [--src <GSS dir>] [--stage <dir>]"""
import os, re, subprocess, sys
here = os.path.dirname(os.path.abspath(__file__))
args = [a for a in sys.argv[1:]]
n = args.pop(0) if args and args[0].isdigit() else "1000"
out = subprocess.run([sys.executable, os.path.join(here, "../judge_the_judge/diag.py"), "all", n, "--base"] + args, capture_output=True, text=True).stdout
got = {k: re.search(p, out, re.M) for k, p in (("slack", r"^SLACK .* under (\d+)"), ("stray", r"^EXC .* miss (\d+)"), ("bends", r"^BENDS .* unforced (\d+)"))}
if not all(got.values()): print("UNMEASURED: diag output lacks a SLACK/EXC/BENDS line\n" + out[-1500:]); sys.exit(2)
v = {k: int(m.group(1)) for k, m in got.items()}
print(f"RESIDUE slack under {v['slack']}, stray miss {v['stray']}, unforced bends {v['bends']} over {2 * int(n)} scenes per sweep: " + ("PASS" if not any(v.values()) else "FAIL"))
sys.exit(0 if not any(v.values()) else 1)
