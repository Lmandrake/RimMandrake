#!/usr/bin/env python3
"""Acceptance test for RIMMANDRAKE_REGISTER_UNLISTED_SELFTESTS_THREE_MODS_157_UNSEEN: every on-disk selftest of the mod is
named by a command or file in its version/test_table.json, or listed in the table's top-level `unlisted_suites` map with
a non-empty why. Prints one line per mod and exits 1 when any suite is unaccounted for, 2 when a table cannot be read."""
import glob, json, os, sys
PATS = {"Pyrelands": ["src/RimMandrake/Pyrelands/**/selftest*.py", "src/RimMandrake/Utils/selftest_pyre*.py"],
        "GimmeSomeSlack": ["src/RimMandrake/GimmeSomeSlack/**/selftest*.py", "src/RimMandrake/Utils/selftest_gimme*.py",
                           "src/RimMandrake/Utils/selftest_gss*.py"],
        "FlowWorks": ["src/RimMandrake/FlowWorks/**/selftest*.py", "src/RimMandrake/Utils/selftest_flowworks*.py"]}
bad = unreadable = 0
for mod in sys.argv[1:] or PATS:
    try:
        t = json.load(open("design/concepts/%s/version/test_table.json" % mod, encoding="utf-8"))
    except (OSError, ValueError) as e:
        print("%s UNREADABLE: %s" % (mod, e)); unreadable += 1; continue
    named = " ".join(json.dumps(v.get("command")) + " " + json.dumps(v.get("file")) for v in t["tests"].values())
    why = t.get("unlisted_suites") if isinstance(t.get("unlisted_suites"), dict) else {}
    disk = sorted({p for g in PATS[mod] for p in glob.glob(g, recursive=True)})
    miss = [os.path.basename(p) for p in disk if os.path.basename(p) not in named
            and not (isinstance(why.get(os.path.basename(p)), str) and why[os.path.basename(p)].strip())]
    print("%s: %d on disk, %d unaccounted%s" % (mod, len(disk), len(miss), (": " + ", ".join(miss)) if miss else ""))
    bad += bool(miss)
sys.exit(2 if unreadable else 1 if bad else 0)
