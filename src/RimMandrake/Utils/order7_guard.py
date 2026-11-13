#!/usr/bin/env python3
"""order7_guard.py - keep the WSL kernel able to hand out order-7 blocks (DRVFS_ENOMEM_FIX_ORDER_SEVEN_RUNS_DRY).

The failure: `page allocation failure: order:7` in dmesg, from vmbus_alloc_ring <- hvs_probe (every new hv_sock
channel, which /mnt drvfs and Windows interop open, wants a 512 KiB contiguous ring). MemFree sat at the low
watermark (~100 MB of 28 GB, min_free_kbytes 45056) because the page cache fills everything, so no free pool
existed to build an order-7 block from. Measured 2026-11-06 (D:\\ClaudeWork\\rimmandrake\\DRVFS_ENOMEM_FIX_ORDER_SEVEN_RUNS_DRY):
  compact_memory alone       no change (Normal zone order 7+ stayed 0)
  drop_caches + compact      order 7+ 0 -> 468, but the cache ate 18 GB of free memory again within 6 minutes
  the sysctls in 90-rm-order7.conf   order 7+ between 24 and 1040 every minute for 7 minutes, MemFree ~2.5 GB, 0 failures
So the fix is the watermark sysctls, persisted in /etc/sysctl.d (applied at every boot by systemd-sysctl), and
this script on rm-order7.timer records the reading and re-applies them if something resets them.

    order7_guard.py run [--no-apply]   the timer: read the sysctls (re-apply as root through wsl.exe on drift),
                                       count free order-7+ blocks and new order:7 dmesg failures, write READING
    order7_guard.py status             exit 0 when every sysctl is at its target, else 1; one line each
    order7_guard.py install            as root (wsl.exe -u root): copy the conf to /etc/sysctl.d and apply it

Root comes from `wsl.exe -u root` (no sudo without a password here). RM_ORDER7_PROC and RM_ORDER7_STATE move
/proc and the state dir (tests only).
"""
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
CONF = HERE / "systemd" / "90-rm-order7.conf"
ETC_CONF = "/etc/sysctl.d/90-rm-order7.conf"
PROC = Path(os.environ.get("RM_ORDER7_PROC", "/proc"))
STATE = Path(os.environ.get("RM_ORDER7_STATE", os.path.expanduser("~/.local/state/rm-order7")))
READING = STATE / "reading.json"
FAIL_RX = re.compile(r"^\[\s*(\d+\.\d+)\].*page allocation failure: order:7\b")


def targets(conf=CONF):
    """{'vm.min_free_kbytes': '1048576', ...} from sysctl.d syntax."""
    out = {}
    for line in Path(conf).read_text().splitlines():
        line = line.split("#", 1)[0].strip()
        if not line or "=" not in line:
            continue
        k, v = (s.strip() for s in line.split("=", 1))
        out[k] = v
    if not out:
        raise SystemExit("order7_guard: no sysctl in %s" % conf)
    return out


def current(keys, proc=None):
    proc = proc or PROC
    got = {}
    for k in keys:
        p = proc / "sys" / k.replace(".", "/")
        try:
            got[k] = p.read_text().strip()
        except OSError as e:
            got[k] = "UNREADABLE: %s" % e.__class__.__name__
    return got


def drift(want, have):
    return {k: (have.get(k), v) for k, v in want.items() if have.get(k) != v}


def order7_blocks(proc=None):
    """Free blocks of order >= 7 per zone, from /proc/buddyinfo (columns are orders 0..10)."""
    proc = proc or PROC
    zones = {}
    for line in (proc / "buddyinfo").read_text().splitlines():
        f = line.split()
        if len(f) < 5 or f[2] != "zone":
            continue
        counts = [int(x) for x in f[4:]]
        zones[f[3]] = sum(counts[7:])
    return zones


def uptime(proc=None):
    proc = proc or PROC
    return float((proc / "uptime").read_text().split()[0])


def dmesg_failures(text, after):
    """Kernel timestamps of order:7 failures strictly after `after` seconds of uptime."""
    out = []
    for line in text.splitlines():
        m = FAIL_RX.match(line)
        if m and float(m.group(1)) > after:
            out.append(float(m.group(1)))
    return out


def read_dmesg():
    try:
        r = subprocess.run(["dmesg"], capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.TimeoutExpired) as e:
        return None, "dmesg: %s" % e.__class__.__name__
    if r.returncode != 0:
        return None, "dmesg rc=%d %s" % (r.returncode, r.stderr.strip())
    return r.stdout, None


def as_root(cmd):
    """Run a shell command as root through wsl.exe (interop); returns (rc, text)."""
    try:
        r = subprocess.run(["wsl.exe", "-u", "root", "--", "sh", "-c", cmd],
                           capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.TimeoutExpired) as e:
        return 99, "wsl.exe: %s" % e.__class__.__name__
    return r.returncode, (r.stdout + r.stderr).strip()


def apply_cmd(want):
    return "sysctl -q -w " + " ".join("%s=%s" % (k, v) for k, v in sorted(want.items()))


def boot_id(proc=None):
    proc = proc or PROC
    try:
        return (proc / "sys" / "kernel" / "random" / "boot_id").read_text().strip()
    except OSError:
        return None


def last_reading(path=None):
    path = path or READING
    try:
        return json.loads(Path(path).read_text())
    except (OSError, ValueError):
        return None


def build_reading(want, have, zones, up, prev, dmesg_text, dmesg_err, applied, boot=None):
    since = 0.0
    same_boot = bool(prev) and prev.get("boot_id") == boot and boot is not None
    if same_boot and isinstance(prev.get("uptime_s"), (int, float)) and prev["uptime_s"] <= up:
        since = float(prev["uptime_s"])    # same boot: count only what is new; a reboot counts from 0
    fails = None if dmesg_text is None else dmesg_failures(dmesg_text, since)
    return {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "uptime_s": up,
        "boot_id": boot,
        "sysctl_target": want,
        "sysctl_live": have,
        "sysctl_ok": not drift(want, have),
        "reapplied": applied,
        "order7_free_blocks": zones,
        "order7_free_total": sum(zones.values()),
        "new_order7_failures": None if fails is None else len(fails),
        "dmesg_error": dmesg_err,
        "counted_after_uptime_s": since,
    }


def write_reading(reading, path=None):
    path = Path(path or READING)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(reading, indent=1, sort_keys=True) + "\n")
    os.replace(tmp, path)


def cmd_run(no_apply):
    want = targets()
    have = current(want)
    applied = None
    d = drift(want, have)
    if d and not no_apply:
        rc, text = as_root(apply_cmd(want))
        applied = {"rc": rc, "drift": d, "out": text}
        have = current(want)
    text, err = read_dmesg()
    reading = build_reading(want, have, order7_blocks(), uptime(), last_reading(), text, err, applied,
                            boot_id())
    write_reading(reading)
    print("order7_guard: sysctl_ok=%s order7_free=%d new_failures=%s%s" % (
        reading["sysctl_ok"], reading["order7_free_total"], reading["new_order7_failures"],
        " reapplied rc=%s" % applied["rc"] if applied else ""))
    return 0 if reading["sysctl_ok"] else 1


def cmd_status():
    want = targets()
    have = current(want)
    bad = drift(want, have)
    for k, v in sorted(want.items()):
        print("%s %s live=%s target=%s" % ("OK  " if k not in bad else "DRIFT", k, have.get(k), v))
    try:
        print("order7_free_blocks %s" % order7_blocks())
    except OSError as e:
        print("order7_free_blocks UNMEASURED: %s" % e.__class__.__name__)
    return 1 if bad else 0


def cmd_install():
    want = targets()
    body = CONF.read_text()
    # the conf is passed on stdin-free argv: printf with the literal text (no quote characters allowed in it)
    if "'" in body:
        raise SystemExit("order7_guard: conf may not hold a single quote")
    rc, text = as_root("printf '%%s' '%s' > %s && sysctl -q -p %s" % (body, ETC_CONF, ETC_CONF))
    print("install rc=%d %s" % (rc, text))
    return cmd_status() if rc == 0 else 1


def main(argv):
    if not argv or argv[0] not in ("run", "status", "install"):
        print(__doc__)
        return 2
    if argv[0] == "run":
        return cmd_run("--no-apply" in argv[1:])
    if argv[0] == "status":
        return cmd_status()
    return cmd_install()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
