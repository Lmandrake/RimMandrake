#!/usr/bin/env python3
"""Selftest for order7_guard.py against a FAKE /proc (no root, no wsl.exe, no real dmesg).

Planted breaks it must catch: a sysctl one off its target (drift), a missing sysctl file, buddyinfo order-7+
summed from the wrong column, a failure line at or before the last reading counted again, a reboot (uptime fell)
that must count from zero, a non-order-7 failure counted, and the shipped conf losing a key.
"""
import json
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import order7_guard as G  # noqa: E402

FAILS = []


def ok(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


BUDDY = ("Node 0, zone    DMA32   1   2   3   4   5   6   7   8   9  10  11 \n"
         "Node 0, zone   Normal  10  20  30  40  50  60  70   0   2   1   0 \n")
DMESG = ("[100.000001] kworker/0:1: page allocation failure: order:7, mode:0xdc0(GFP_KERNEL|__GFP_ZERO)\n"
         "[200.500000] kworker/0:2: page allocation failure: order:7, mode:0xdc0(GFP_KERNEL|__GFP_ZERO)\n"
         "[250.000000] python3: page allocation failure: order:3, mode:0xdc0\n"
         "[300.000000] kworker/0:3: page allocation failure: order:7, mode:0xdc0(GFP_KERNEL|__GFP_ZERO)\n")


def fake_proc(root, vals):
    (root / "sys" / "vm").mkdir(parents=True, exist_ok=True)
    for k, v in vals.items():
        (root / "sys" / k.replace(".", "/")).write_text(v + "\n")
    (root / "buddyinfo").write_text(BUDDY)
    (root / "uptime").write_text("400.12 1000.0\n")


def main():
    want = G.targets()
    ok(set(want) == {"vm.min_free_kbytes", "vm.watermark_scale_factor", "vm.compaction_proactiveness"},
       "shipped conf names the three sysctls: %s" % sorted(want))
    ok(want.get("vm.min_free_kbytes") == "1048576", "min_free_kbytes target is the measured 1 GiB")
    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "proc"
        fake_proc(root, want)
        have = G.current(want, proc=root)
        ok(G.drift(want, have) == {}, "all at target -> no drift")
        bad = dict(want, **{"vm.watermark_scale_factor": "10"})
        fake_proc(root, bad)
        d = G.drift(want, G.current(want, proc=root))
        ok(list(d) == ["vm.watermark_scale_factor"] and d["vm.watermark_scale_factor"] == ("10", "200"),
           "one key off -> exactly that drift: %s" % d)
        (root / "sys" / "vm" / "compaction_proactiveness").unlink()
        d = G.drift(want, G.current(want, proc=root))
        ok("vm.compaction_proactiveness" in d and str(d["vm.compaction_proactiveness"][0]).startswith("UNREADABLE"),
           "missing sysctl file reads as UNREADABLE drift, never as OK")
        z = G.order7_blocks(proc=root)
        ok(z == {"DMA32": 8 + 9 + 10 + 11, "Normal": 0 + 2 + 1 + 0}, "order 7+ per zone from columns 7..10: %s" % z)
        ok(G.uptime(proc=root) == 400.12, "uptime parsed")
        ok(G.dmesg_failures(DMESG, 0.0) == [100.000001, 200.5, 300.0], "all three order:7 lines, the order:3 one ignored")
        ok(G.dmesg_failures(DMESG, 200.5) == [300.0], "a line at the last reading's uptime is not counted again")
        r = G.build_reading(want, want, z, 400.12, {"uptime_s": 200.5, "boot_id": "b1"}, DMESG, None, None, "b1")
        ok(r["new_order7_failures"] == 1 and r["sysctl_ok"] is True, "same boot: only the new failure counts")
        r = G.build_reading(want, want, z, 150.0, {"uptime_s": 9999.0, "boot_id": "b1"}, DMESG, None, None, "b1")
        ok(r["new_order7_failures"] == 3 and r["counted_after_uptime_s"] == 0.0, "reboot (uptime fell) counts from 0")
        r = G.build_reading(want, want, z, 400.12, {"uptime_s": 200.5, "boot_id": "b0"}, DMESG, None, None, "b1")
        ok(r["new_order7_failures"] == 3, "new boot_id with a larger uptime still counts from 0")
        r = G.build_reading(want, bad, z, 400.0, None, None, "dmesg rc=1", None)
        ok(r["new_order7_failures"] is None and r["sysctl_ok"] is False, "unreadable dmesg is None, not 0; drift is not ok")
        out = Path(td) / "state" / "reading.json"
        G.write_reading(r, out)
        ok(json.loads(out.read_text())["order7_free_total"] == sum(z.values()), "reading written and parseable")
        cmd = G.apply_cmd(want)
        ok(cmd.startswith("sysctl -q -w ") and "vm.min_free_kbytes=1048576" in cmd, "apply command: %s" % cmd)
    print("%d failure(s)" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
