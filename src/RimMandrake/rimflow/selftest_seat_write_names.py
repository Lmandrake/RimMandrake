#!/usr/bin/env python3
"""SEAT_BENCH_RENAME_WORD_OUTLIVED_ITS_WORKSHOP step 2 (owner 2026-11-03: "1+2 yes"): new ledger events say CONDUCTOR or
RELENTLESS, never BENCH; BENCH stays a read alias, so old lines replay and the shared key in memory is unchanged.
Runs the real cli on a throwaway ledger; touches nothing real."""
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
RIM = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, RIM)
CLI = os.path.join(HERE, "cli.py")
FAILS = []


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


def main():
    import model
    # Pure functions first: the whole name space.
    check(model.write_name("BENCH", {}) == "CONDUCTOR", "the Conductor's window writes CONDUCTOR")
    check(model.write_name("BENCH", {"RIMFLOW_BRIDGE_SEAT": "RELENTLESS"}) == "RELENTLESS",
          "a Relentless process writes RELENTLESS")
    for s in model.SEATS:
        if s != "BENCH":
            check(model.write_name(s, {"RIMFLOW_BRIDGE_SEAT": "RELENTLESS"}) == s, "%s is written as itself" % s)
            check(model.read_name(s) == s, "%s reads as itself" % s)
    for n in ("BENCH", "CONDUCTOR", "RELENTLESS"):
        check(model.read_name(n, "note") == "BENCH", "%s reads as the shared key on a note" % n)
    check(model.read_name("RELENTLESS", "bridge") == "RELENTLESS", "a bridge line keeps the RELENTLESS holder")
    check(model.read_name("CONDUCTOR", "bridge") == "BENCH", "a Conductor bridge hold reads as BENCH")
    # Readers that cannot import model keep an inline copy of the fold: it must agree with model.from_disk on every case.
    import importlib.util
    root = os.path.dirname(os.path.dirname(RIM))
    folds = {}
    for name, path in (("queue_lint", os.path.join(root, ".claude", "hooks", "queue_lint.py")),
                       ("handoff", os.path.join(RIM, "Utils", "handoff.py"))):
        sys.path.insert(0, os.path.dirname(path))
        spec = importlib.util.spec_from_file_location("_fold_" + name, path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        folds[name] = mod._seat_keys
    names = ("BENCH", "CONDUCTOR", "RELENTLESS", "FOUNDRY", "OWNER", None)
    for verb in ("note", "bridge", "file", "spawn", "reassign", "close", "needs"):
        for seat in names:
            for other in names:
                ev = {"event": verb, "id": "X"}
                if seat:
                    ev["seat"] = seat
                if other:
                    ev["for"] = ev["to"] = other
                want = model.from_disk(dict(ev))
                for name, fold in folds.items():
                    if fold(dict(ev)) != want:
                        check(False, "%s's fold disagrees with model.from_disk on %r" % (name, ev))
    check(True, "the queue_lint and handoff folds agree with model.from_disk on %d cases" % (7 * len(names) ** 2))

    tmp = tempfile.mkdtemp(prefix="rf_names_")
    try:
        os.makedirs(os.path.join(tmp, "items"))
        base = {k: v for k, v in os.environ.items() if k not in (
            "RIMFLOW_SEAT", "AGENT_SEAT", "CLAUDE_SESSION_ID", "CLAUDECODE", "RIMFLOW_RAN_BY", "RM_DRIVER_PID",
            "RIMFLOW_BRIDGE_SEAT", "RIMFLOW_BRIDGE_SEAT_IN_TEST", "RELENTLESS_SUPERVISOR", "RM_HOST_GUARD_GEN")}
        ledger = os.path.join(tmp, "events.jsonl")
        base.update(RIMFLOW_LEDGER=ledger, RIMFLOW_ITEMS=os.path.join(tmp, "items"), RIMFLOW_PROBE="no-reading",
                    RIMFLOW_SHARED_BRIDGE=os.path.join(tmp, "shared.json"),
                    RIMFLOW_DISPATCH_LOCK=os.path.join(tmp, "dispatch.lock"),
                    RIMFLOW_BRIDGE_LOCK=os.path.join(tmp, "bridge.lock"),
                    RIMFLOW_OWNER_ACT_STAMP=os.path.join(tmp, "act.json"), RIMFLOW_DRIVER_LOCK="")
        # An old line, written before the rename, must still replay as BENCH's.
        shard = os.path.join(tmp, "events", "BENCH.jsonl")
        os.makedirs(os.path.dirname(shard))
        with open(shard, "w") as f:
            f.write(json.dumps({"ts": "2026-11-01T00:00:00Z", "tsn": 1, "seat": "BENCH", "event": "file",
                                "id": "OLD_LINE_KEEP_ITS_BENCH", "title": "an old BENCH line", "kind": "task",
                                "for": "BENCH", "target": "v1", "needs": "offline"}) + "\n")

        def rf(relentless, *a):
            e = dict(base, RIMFLOW_SEAT="BENCH")
            if relentless:
                e.update(RIMFLOW_BRIDGE_SEAT="RELENTLESS", RIMFLOW_BRIDGE_SEAT_IN_TEST="1")
            r = subprocess.run([sys.executable, CLI, *a], env=e, capture_output=True, text=True, timeout=120, cwd=tmp)
            return r.returncode, r.stdout + r.stderr

        rc, out = rf(False, "file", "SEAT_NAMES_RENAME_ON_DISK_ONLY", "--title", "filed by the Conductor",
                     "--kind", "task", "--for", "BENCH", "--why", "selftest")
        check(rc == 0, "the Conductor files an item (rc=%s %s)" % (rc, out.strip()[-200:]))
        rc, out = rf(True, "note", "SEAT_NAMES_RENAME_ON_DISK_ONLY", "--text", "a worker's note", "--why", "selftest")
        check(rc == 0, "a Relentless worker notes it (rc=%s %s)" % (rc, out.strip()[-200:]))

        raw = []
        for root, _, names in os.walk(tmp):
            for n in names:
                if n.endswith(".jsonl") and os.path.basename(root) == "events":
                    with open(os.path.join(root, n)) as f:
                        raw += [(n, json.loads(x)) for x in f if x.strip()]
        new = [(n, e) for n, e in raw if e.get("id") == "SEAT_NAMES_RENAME_ON_DISK_ONLY"]
        check(len(new) >= 2, "both new events reached a shard (%d)" % len(new))
        filed = [e for _, e in new if e["event"] == "file"]
        noted = [e for _, e in new if e["event"] == "note"]
        check(bool(filed) and filed[0]["seat"] == "CONDUCTOR", "the file line says seat CONDUCTOR (%s)"
              % (filed and filed[0].get("seat")))
        check(bool(filed) and filed[0]["for"] == "RELENTLESS", "the file line says for RELENTLESS (%s)"
              % (filed and filed[0].get("for")))
        check(bool(noted) and noted[0]["seat"] == "RELENTLESS", "the worker's note says seat RELENTLESS (%s)"
              % (noted and noted[0].get("seat")))
        check(all(n == "BENCH.jsonl" for n, _ in new), "the shard file is still BENCH.jsonl (held: a path)")
        check(not any("BENCH" in (e.get("seat"), e.get("for"), e.get("to")) for _, e in new),
              "no new line says BENCH in seat, for or to")

        # Reading folds every name back to the shared key.
        evs = model.read(ledger)
        evs = model.read_clone(ledger)
        mine = [e for e in evs if e.get("id") in ("SEAT_NAMES_RENAME_ON_DISK_ONLY", "OLD_LINE_KEEP_ITS_BENCH")]
        check(len(mine) >= 3 and all(e["seat"] == "BENCH" for e in mine), "every line reads as seat BENCH")
        w = model.replay(evs)
        it, old = w.items.get("SEAT_NAMES_RENAME_ON_DISK_ONLY"), w.items.get("OLD_LINE_KEEP_ITS_BENCH")
        check(it is not None and it.owner == "BENCH", "the new item is owned by the shared key")
        check(old is not None and old.owner == "BENCH", "the old BENCH line still replays")
        rc, out = rf(True, "show", "SEAT_NAMES_RENAME_ON_DISK_ONLY")
        check(rc == 0 and "a worker's note" in out, "show reads the renamed lines (rc=%s)" % rc)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("\n%s" % ("ALL PASS" if not FAILS else "%d FAIL" % len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
