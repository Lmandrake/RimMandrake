#!/usr/bin/env python3
"""Four ./publish runs of trivial commits started at once from four scratch clones; samples, every 0.5 s, how many of
the four hold a full check tree (rm-treecheck-* in their git dir) and how many machine slots are locked (/proc/locks)."""
import glob, json, os, subprocess, sys, time
base = sys.argv[1]
clones = [os.path.join(base, "tcg-proof-%d" % i) for i in range(1, 5)]
slots = "/home/mandrake/rm/.treecheck-slots"
out = sys.argv[2]
def slot_inodes():
    return {os.stat(p).st_ino: p for p in glob.glob(slots + "/slot.*")}
def locked():
    ino = slot_inodes(); n = 0
    for ln in open("/proc/locks"):
        f = ln.split()
        try:
            i = int(f[5].split(":")[2]) if "->" not in ln else int(f[7].split(":")[2])
        except (IndexError, ValueError):
            continue
        if i in ino and "->" not in ln:
            n += 1
    return n
procs = []
for i, c in enumerate(clones, 1):
    rel = "design/specs/2026-11-24-treecheck-slots/proof/clone%d.md" % i
    os.makedirs(os.path.join(c, os.path.dirname(rel)), exist_ok=True)
    open(os.path.join(c, rel), "w").write("Four-publish proof of the tree-check line, clone %d, %s.\n" % (i, time.strftime("%Y-%m-%d %H:%M %Z")))
for i, c in enumerate(clones, 1):
    rel = "design/specs/2026-11-24-treecheck-slots/proof/clone%d.md" % i
    log = open(os.path.join(os.path.dirname(out), "proof4_clone%d.log" % i), "w")
    procs.append(subprocess.Popen(["./publish", "-m", "RIMMANDRAKE_THROTTLE_TREECHECKS_WHEN_DISK_SATURATES_HANG_GUARDS_FIRE: four-publish proof, clone %d\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\n" % i, rel],
                                  cwd=c, stdout=log, stderr=subprocess.STDOUT))
t0 = time.time(); samples = []
while any(p.poll() is None for p in procs):
    trees = [len(glob.glob(os.path.join(c, ".git", "rm-treecheck-*"))) for c in clones]
    samples.append((round(time.time() - t0, 1), trees, locked()))
    time.sleep(0.5)
rcs = [p.returncode for p in procs]
mine = max(sum(1 for x in t if x) for _s, t, _l in samples)
res = dict(rcs=rcs, wall_s=round(time.time() - t0, 1), max_of_four_in_checks=mine, max_slots_locked=max(l for *_x, l in samples),
           samples=len(samples), at=time.strftime("%Y-%m-%d %H:%M:%S %Z"))
json.dump(dict(res, timeline=samples), open(out, "w"))
print(json.dumps(res))
