#!/usr/bin/env python3
"""Acceptance for RIMMANDRAKE_KEEP_STAGE_JSON_DESIGNERS_LEDGER_READS_HOMONYM_NAMED (DESIGN DECISION 2026-11-18 on
RIMMANDRAKE_CUTOVER_PILOT_MODS_TO_LEDGER_SAME_DAY): design/concepts/<Mod>/stage.json stays the Designer stage machine's
own state store, written by designer_stage.py; it is not archived and not a generated view. The mod ledger READS it:
`modledger.packet(root, mod)` carries one line, `Designer step: <0-5> (<status>)`, read from stage.json when the packet
is made, and never calls it a "stage" (the pipeline stage is the ledger's; the same word for both is the trap the
cutover spec names). The four answers stay apart: a step read, `none (no stage.json)`, `UNMEASURED (<cause>)`.
The cutover test stops asking for stage.json to be a view or archived.
Red on b28e0d697 (watched). The Conductor's delegate wrote this; a wrong clause goes to the Conductor."""
import json
import os
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import modledger as M                                            # noqa: E402

ROOT = M.REPO_ROOT
PILOT = "ExplosiveKnockback"
FAILS = []
LINE = re.compile(r"^Designer step: (.+)$", re.M)


def check(name, ok, got=""):
    print("%s %s%s" % ("ok  " if ok else "FAIL", name, "" if ok else "  got: %s" % (got,)))
    if not ok:
        FAILS.append(name)


def step_line(root, mod):
    """-> the packet's Designer step text, None when the packet has no such line, or "CRASH ..."."""
    try:
        text = M.packet(root, mod)[0]
    except Exception as e:
        return "CRASH %s: %s" % (type(e).__name__, e)
    m = LINE.findall(text)
    return m[0] if len(m) == 1 else (None if not m else "TWICE %s" % m)


def main():
    if not M.read(ROOT, PILOT):
        print("UNMEASURED: %s has no mod ledger in this clone" % PILOT)
        return 2
    tmp = tempfile.mkdtemp(prefix="designer_state_accept_")
    try:
        shutil.copytree(M.ledger_dir(ROOT, PILOT), M.ledger_dir(tmp, PILOT))
        sp = os.path.join(tmp, "design", "concepts", PILOT, "stage.json")

        def put(obj):
            with open(sp, "w") as f:
                f.write(obj if isinstance(obj, str) else json.dumps(obj))

        put({"schema": 1, "mod": PILOT, "stage": 5, "status": "locked"})
        check("a locked Designer reads `5 (locked)`", step_line(tmp, PILOT) == "5 (locked)", step_line(tmp, PILOT))
        put({"schema": 1, "mod": PILOT, "stage": 0, "status": "ready"})
        check("step 0 is a step, not a missing one", step_line(tmp, PILOT) == "0 (ready)", step_line(tmp, PILOT))
        put({"schema": 1, "mod": PILOT, "stage": 3, "status": "blocked", "blocked_on": "waits on the coverage judge"})
        got = step_line(tmp, PILOT) or ""
        check("a blocked Designer reads its step, status and what it is blocked on",
              got.startswith("3 (blocked)") and "waits on the coverage judge" in got, got)
        os.remove(sp)
        check("no stage.json reads `none (no stage.json)`", step_line(tmp, PILOT) == "none (no stage.json)",
              step_line(tmp, PILOT))
        for name, bad in (("a stage.json that does not parse", "{not json"), ("an empty stage.json", ""),
                          ("a stage.json that is a list", "[]"), ("a stage.json with no step", '{"status": "ready"}'),
                          ("a stage.json whose step is not 0-5", '{"stage": "five", "status": "ready"}')):
            put(bad)
            got = step_line(tmp, PILOT) or ""
            check("%s reads UNMEASURED with its cause" % name, re.match(r"UNMEASURED \(.+\)$", got) is not None, got)
        put({"schema": 1, "mod": PILOT, "stage": 2, "status": "running"})
        try:
            text = M.packet(tmp, PILOT)[0]
        except Exception as e:
            text = "CRASH %s" % e
        head = text.split("\n## ")[0]
        check("the packet's head never says `stage 2` for the Designer's step",
              LINE.search(head) is not None and not re.search(r"\bstage 2\b", head), head[:300])
        with open(sp) as f:
            before = f.read()
        M.packet(tmp, PILOT)
        with open(sp) as f:
            check("making a packet does not write stage.json", f.read() == before)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    # the real pilot mods agree with their real stage.json
    for mod in ("ExplosiveKnockback", "GimmeSomeSlack", "FlowWorks"):
        try:
            with open(os.path.join(ROOT, "design", "concepts", mod, "stage.json")) as f:
                st = json.load(f)
            want = "%s (%s)" % (st["stage"], st["status"])
        except (OSError, ValueError, KeyError) as e:
            print("UNMEASURED %s: its stage.json could not be read (%s)" % (mod, e))
            FAILS.append("%s stage.json unread" % mod)
            continue
        got = step_line(ROOT, mod) or ""
        check("%s: the packet's Designer step is its stage.json's" % mod, got.startswith(want), got)
    # the cutover test no longer asks for stage.json to be a view or archived
    with open(os.path.join(HERE, "modledger_cutover_accept.py")) as f:
        src = f.read()
    m = re.search(r"^OLD = \((.*?)\)\s*$", src, re.M | re.S)
    check("modledger_cutover_accept.py's OLD stores no longer list stage.json",
          m is not None and "stage.json" not in m.group(1).replace("stage_record.json", ""), m and m.group(1))
    print("%s: %d failure(s)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
