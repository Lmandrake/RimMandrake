#!/usr/bin/env python3
"""`rimflow bridge who` on a clone whose ledger copy is older than the shared lock
(BRIDGEWHO_FIX_STALE_CLONE_SAYS_HOUR_IDLE). The bench clone read RELENTLESS since 20:02:54Z, idle 59 min, while the live
hold was 21:01:08Z, idle 3 min, and no warning fired because the holder name was the same in both clones.

Every case runs the real cli against a throwaway ledger holding an hour-old take, with the shared lock written as
another clone would have left it."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
CLI = os.path.join(HERE, "cli.py")
FAILS = []


def check(cond, msg):
    print(("ok   " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


def stamp(ago):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() - ago))


class Fixture:
    def __init__(self):
        self.tmp = tempfile.mkdtemp(prefix="rf_who_")
        os.makedirs(os.path.join(self.tmp, "items"))
        self.shared = os.path.join(self.tmp, "shared.json")
        self.base = {k: v for k, v in os.environ.items()
                     if k not in ("RIMFLOW_SEAT", "AGENT_SEAT", "CLAUDE_SESSION_ID", "RIMFLOW_BRIDGE_SEAT")}
        self.base.update(RIMFLOW_LEDGER=os.path.join(self.tmp, "events.jsonl"), RIMFLOW_ITEMS=os.path.join(self.tmp, "items"),
                         RIMFLOW_SHARED_BRIDGE=self.shared, RIMFLOW_PROBE="no-reading", RIMFLOW_SEAT="FOUNDRY")

    def rf(self, *args):
        return subprocess.run([sys.executable, CLI] + list(args), env=self.base, capture_output=True, text=True, timeout=120)

    def age_ledger(self, seconds):
        """Rewrite every event as `seconds` older: the ledger this clone last synced."""
        shards = os.path.join(self.tmp, "events")
        for name in os.listdir(shards):
            path = os.path.join(shards, name)
            rows = []
            with open(path, encoding="utf-8") as f:
                for line in f:
                    ev = json.loads(line)
                    ev["ts"] = stamp(seconds)
                    ev["tsn"] = int(ev["tsn"]) - seconds * 10 ** 9
                    rows.append(json.dumps(ev))
            with open(path, "w", encoding="utf-8") as f:
                f.write("\n".join(rows) + "\n")

    def set_shared(self, **body):
        with open(self.shared, "w", encoding="utf-8") as f:
            json.dump(body, f)

    def who(self):
        r = self.rf("bridge", "who")
        return r.returncode, r.stdout + r.stderr


def main():
    fx = Fixture()
    try:
        taken = fx.rf("bridge", "take", "--for", "old proof")
        check(taken.returncode == 0, "the fixture take lands: " + taken.stderr[:200])
        fx.age_ledger(3600)
        old_since = stamp(3600)[:13]    # the hour is enough to tell the old reading from the new
        held = json.load(open(fx.shared, encoding="utf-8"))
        check(held.get("holder") == "FOUNDRY", "the take wrote the shared lock (the instrument can see): %s" % held)

        # (a) the reported failure: same holder, newer take in another clone
        new_since = stamp(180)
        fx.set_shared(holder="FOUNDRY", since=new_since, touched=stamp(180), purpose="live proof", clone="/books")
        rc, out = fx.who()
        check(rc == 0, "same holder, newer take: exits 0")
        check("⚠️" in out and "behind" in out and "/books" in out, "same holder, newer take: warns and names the clone: " + out)
        line = [x for x in out.splitlines() if x.startswith("bridge held by")]
        check(len(line) == 1, "one holder line: %s" % line)
        check(line and new_since in line[0], "the holder line carries the newer take's since: %s" % line)
        check(line and "for: live proof" in line[0], "the holder line carries the newer take's purpose: %s" % line)
        check(line and "(idle 3 min)" in line[0], "idle is the shared lock's, not the hour-old copy: %s" % line)
        check(old_since in out and "idle 60 min" in out, "the warning names the stale reading it replaces: " + out)

        # (b) same hold, another clone's event touched it: no alarm, idle still the fresher one
        fx.set_shared(holder="FOUNDRY", since=stamp(3598), touched=stamp(120), purpose="old proof", clone="/books")
        rc, out = fx.who()
        check("⚠️" not in out, "same take a few seconds apart does not warn: " + out)
        check("(idle 2 min)" in out, "a fresher touch still corrects idle: " + out)

        # (c) released in another clone, not yet in this one
        fx.set_shared(holder=None, touched=stamp(300), clone="/books")
        rc, out = fx.who()
        check("⚠️" in out and "released" in out and "/books" in out, "a release after the local hold warns: " + out)

        # (d) a release older than the hold says nothing
        fx.set_shared(holder=None, touched=stamp(7200), clone="/books")
        rc, out = fx.who()
        check("⚠️" not in out, "a release before the local hold does not warn: " + out)

        # (e) a different holder keeps its own warning
        fx.set_shared(holder="BENCH", since=stamp(60), touched=stamp(60), purpose="x", clone="/books")
        rc, out = fx.who()
        check("BENCH holds it from another clone" in out and "behind" not in out, "a different holder keeps its warning: " + out)

        # (f) a current clone: its own lock, nothing to say, and the ledger's reading stands
        fresh = Fixture()
        try:
            fresh.rf("bridge", "take", "--for", "current")
            rc, out = fresh.who()
            check(rc == 0 and "⚠️" not in out and "for: current" in out and "(idle 0 min)" in out, "a current clone prints no warning: " + out)
            os.remove(fresh.shared)
            rc, out = fresh.who()
            check(rc == 0 and "⚠️" not in out and "bridge held by FOUNDRY" in out, "no shared lock: the ledger's reading: " + out)
            fresh.set_shared(holder="FOUNDRY", since="garbage", touched="garbage", clone="/books")
            rc, out = fresh.who()
            check(rc == 0 and "⚠️" not in out and "(idle 0 min)" in out, "an unreadable stamp changes nothing: " + out)
        finally:
            shutil.rmtree(fresh.tmp, ignore_errors=True)
    finally:
        shutil.rmtree(fx.tmp, ignore_errors=True)
    print("\n%d failed" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
