#!/usr/bin/env python3
"""wait_and_run.py: wait for ArchBig to be free, then run live_pass.sh under `game_lock.py run ArchBig` (one process holds
the game for the whole pass). A lost race (exit 75: another holder took it first) goes back to waiting. A PROGRESS note on
the item for each 30 minutes of waiting (bundle_worker.md step 5). No bound on the wait: a held game is a live run, not a
hang, and waitalive.py watches this process for a sign of life."""
import os, subprocess, sys, time
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 6))
ITEM = "RIMMANDRAKE_SHRINK_FLOWWORKS_SCENES_HUNG_BRIDGE_RAN_27_TIMES"
LOCK = [sys.executable, "src/RimMandrake/rimflow/game_lock.py"]
t0, noted = time.time(), 0
while True:
    q = subprocess.run(LOCK + ["query", "ArchBig"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    if "FREE" in q:
        print("free at %s: %s" % (time.strftime("%H:%M:%S"), q), flush=True)
        rc = subprocess.call(LOCK + ["run", "ArchBig", "--for", "FlowWorks shrunk scenes live pass (%s)" % ITEM, "--",
                                     "bash", os.path.join(os.path.dirname(os.path.abspath(__file__)), "live_pass.sh")], cwd=ROOT)
        if rc != 75:
            print("live pass exit %s" % rc, flush=True)
            sys.exit(rc)
        print("lost the race (75): waiting again", flush=True)
    waited = int((time.time() - t0) // 1800)
    if waited > noted:
        noted = waited
        subprocess.run([sys.executable, "src/RimMandrake/rimflow/cli.py", "note", ITEM, "--text",
                        "PROGRESS: waiting %d min for ArchBig for the live pass: %s | next: live_pass.sh the moment it frees"
                        % (waited * 30, q), "--seat", "BENCH", "--why", "detached run", "--publish"], cwd=ROOT,
                       capture_output=True)
        print("progress note at %d min: %s" % (waited * 30, q), flush=True)
    time.sleep(30)
