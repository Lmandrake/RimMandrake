#!/usr/bin/env python3
"""A swap marker that a dead run left behind must not stop the next list write
(RIMMANDRAKE_CLEAR_STALE_SWAP_MARKER_NOBODY_OWNS_ARCHSMALL_LIST).

Five runs on 2026-11-25 deleted such a marker by hand (ArchBig, ArchSmall, Steve2). The Conductor's design: the marker
names the process that holds the swap; take_before_copy sets a marker aside (renamed, with a note) when that process is
dead, or when an old marker names no holder; it still refuses when the holder lives, and names it; when it cannot see
the holder's process (another host, another pid namespace, a Windows process) it refuses and says "could not look",
never "dead". The preflight on SteveDesktop must not move aside a marker whose holder lives. Temp dirs only.
"""
import contextlib
import glob
import io
import json
import os
import socket
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import modset_builder as mb  # noqa: E402

OWNER = "<ModsConfigData><activeMods><li>ludeon.rimworld</li><li>a.b</li></activeMods></ModsConfigData>"
TIER = "<ModsConfigData><activeMods><li>ludeon.rimworld</li><li>t.t</li></activeMods></ModsConfigData>"
ELSE = "<ModsConfigData><activeMods><li>ludeon.rimworld</li><li>somebody.else</li></activeMods></ModsConfigData>"
FAILS = []


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


def put(path, text):
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def get(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def read(path):
    try:
        with open(path) as f:
            return f.read().strip()
    except OSError:
        return None


def start_of(pid):
    """Field 22 of /proc/<pid>/stat (start time in clock ticks since boot), as the marker records it."""
    s = read("/proc/%d/stat" % pid)
    return int(s[s.rindex(")") + 2:].split()[19]) if s else None


def holder(pid, **over):
    h = {"host": socket.gethostname(), "pid": pid, "kind": "posix",
         "boot": read("/proc/sys/kernel/random/boot_id"), "pidns": os.readlink("/proc/self/ns/pid"),
         "start": start_of(pid)}
    h.update(over)
    return h


def dead_pid():
    p = subprocess.Popen(["true"])
    pid = p.pid
    p.wait()
    return pid


def stranded(d, hold=None, old_s=0, live=ELSE, drop_before=False):
    """A swap a run left: the owner list aside, a tier stamped, then the live list moved on (`live`).
    -> (config, backups, marker)"""
    cfg, bk = os.path.join(d, "ModsConfig.xml"), os.path.join(d, "bk")
    os.makedirs(bk, exist_ok=True)
    put(cfg, OWNER)
    before = os.path.join(bk, "ModsConfig.before-tier-old.xml")
    put(before, OWNER)
    m = {"tier": "old", "before": os.path.basename(before), "md5": mb._md5(before)}
    put(cfg, TIER)
    m["tier_md5"] = mb._md5(cfg)
    if hold is not None:
        m["holder"] = hold
    marker = os.path.join(bk, mb.SWAP_MARKER)
    with open(marker, "w") as f:
        json.dump(m, f)
    if old_s:
        t = time.time() - old_s
        os.utime(marker, (t, t))
    put(cfg, live)
    if drop_before:
        os.remove(before)
    return cfg, bk, marker


def attempt(cfg, bk, tier="new"):
    """-> (stamp or None, refusal text or None, stdout)"""
    out = io.StringIO()
    try:
        with contextlib.redirect_stdout(out):
            return mb.take_before_copy(cfg, bk, tier), None, out.getvalue()
    except mb.RestoreRefused as e:
        return None, str(e), out.getvalue()


def set_aside(cfg, bk, marker, what):
    stamp, why, out = attempt(cfg, bk)
    check(why is None and stamp is not None, "%s: the list write goes on (refusal: %s)" % (what, why))
    check(bool(glob.glob(marker + ".stale-*")), "%s: the old marker is set aside, kept for the record" % what)
    check("set aside" in out.lower(), "%s: a note says so (stdout %r)" % (what, out.strip()[:160]))
    if stamp:
        check(get(stamp) == ELSE, "%s: the fresh before-copy is the live list" % what)
        with open(marker) as f:
            m = json.load(f)
        check((m.get("holder") or {}).get("pid") is not None, "%s: the new marker names its holder" % what)


def refuses(cfg, bk, marker, what, *words):
    stamp, why, _ = attempt(cfg, bk)
    check(why is not None and all(w in why for w in words),
          "%s: refused, naming %s (refusal: %s)" % (what, " / ".join(words), why))
    check(os.path.exists(marker) and not glob.glob(marker + ".stale-*"), "%s: the marker stays in place" % what)
    check(get(cfg) == ELSE, "%s: the live list is untouched" % what)


with tempfile.TemporaryDirectory() as d:
    pid = dead_pid()
    set_aside(*stranded(os.path.join(d, "dead"), holder(pid, start=12345)), what="holder pid %d dead" % pid)
with tempfile.TemporaryDirectory() as d:
    set_aside(*stranded(d, holder(dead_pid(), start=1), drop_before=True), what="dead holder, before-copy gone")
with tempfile.TemporaryDirectory() as d:
    set_aside(*stranded(d, holder(os.getpid(), start=(start_of(os.getpid()) or 0) + 1)),
              what="holder pid alive but started later (pid reused)")
with tempfile.TemporaryDirectory() as d:
    set_aside(*stranded(d, holder(os.getpid(), boot="00000000-0000-0000-0000-000000000000")),
              what="holder from an earlier boot")
with tempfile.TemporaryDirectory() as d:
    set_aside(*stranded(d, None, old_s=3 * 86400), what="no holder field, 3 days old")

with tempfile.TemporaryDirectory() as d:
    refuses(*stranded(d, holder(os.getpid())), "holder alive", "pid %d" % os.getpid(), "alive")
with tempfile.TemporaryDirectory() as d:
    refuses(*stranded(d, holder(os.getpid()), drop_before=True), "holder alive, before-copy gone", "alive")
with tempfile.TemporaryDirectory() as d:
    refuses(*stranded(d, None), "no holder field, 1 min old", "could not tell")
with tempfile.TemporaryDirectory() as d:
    refuses(*stranded(d, holder(dead_pid(), host="SomeOtherHost")), "holder on another host", "could not look")
with tempfile.TemporaryDirectory() as d:
    refuses(*stranded(d, holder(dead_pid(), pidns="pid:[1]")), "holder in another pid namespace", "could not look")
with tempfile.TemporaryDirectory() as d:
    refuses(*stranded(d, holder(dead_pid(), kind="nt")), "holder is a Windows process", "could not look")

with tempfile.TemporaryDirectory() as d:      # a fresh swap records its holder: RM_MODSET_HOLDER_PID, else the caller
    cfg, bk = os.path.join(d, "ModsConfig.xml"), os.path.join(d, "bk")
    put(cfg, OWNER)
    os.environ["RM_MODSET_HOLDER_PID"] = str(os.getpid())
    attempt(cfg, bk)
    del os.environ["RM_MODSET_HOLDER_PID"]
    with open(os.path.join(bk, mb.SWAP_MARKER)) as f:
        h = json.load(f).get("holder") or {}
    check(h.get("pid") == os.getpid() and h.get("start") == start_of(os.getpid()) and h.get("host"),
          "a fresh marker names its holder pid, start and host (%s)" % h)

# the SteveDesktop preflight moves a refusing marker aside: never one whose holder lives
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "infrastructure", "stevedesktop"))
sys.path.insert(0, os.path.join(HERE, "testq"))
try:
    import preflight as P
except Exception as e:      # noqa: BLE001
    check(False, "infrastructure/stevedesktop/preflight.py imports (%s)" % e)
    P = None
if P is not None:
    with tempfile.TemporaryDirectory() as d:
        cfg, bk, marker = stranded(d, holder(os.getpid()))
        why, note = P.check_swap_marker({"profile": "tier:new"}, mb, cfg, bk, fix=True)
        check(why is not None and note is None and os.path.exists(marker),
              "preflight: a live holder's marker is refused, not moved aside (%r, %r)" % (why, note))
    with tempfile.TemporaryDirectory() as d:
        cfg, bk, marker = stranded(d, holder(dead_pid()))
        why, note = P.check_swap_marker({"profile": "tier:new"}, mb, cfg, bk, fix=True)
        check(why is None, "preflight: a dead holder's marker does not refuse the job (%r)" % why)

print("\n%s" % ("FAIL: %d" % len(FAILS) if FAILS else "PASS"))
sys.exit(1 if FAILS else 0)
