#!/usr/bin/env python3
"""Cross-check STEVE_DISK_MEASURE_ONLY_FORTY_GIGS_LEFT against the raw SteveDesktop outputs committed with it.

The checker sandbox cannot ssh SteveDesktop, so the raw readings (taken over ssh by
the worker, verbatim tool output) live in infrastructure/state/facts/steve_c_drive_fill_2026-11-03/.
Exit 0 only if: C: free >= 55e9 in the post-clear reading and the report quotes a raw
reading verbatim; every swap.vhdx folder del_swaps.out deleted is absent afterwards;
diskpart reported a compact and ext4.vhdx is now smaller than before it.
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
REPORT = ROOT / "infrastructure/state/facts/steve_c_drive_fill_2026-11-03.md"
RAW = ROOT / "infrastructure/state/facts/steve_c_drive_fill_2026-11-03"
MIN_FREE = 55_000_000_000
READING = re.compile(r"^(20\d\d-\d\d-\d\dT\d\d:\d\d:\d\dZ) free_bytes=(\d+) size_bytes=(\d+)$")


def main() -> int:
    bad = []
    report = REPORT.read_text(encoding="utf-8")
    for head in ("## What fills C:", "## Cleared (ours)"):
        if not re.search(r"^" + re.escape(head), report, re.M):
            bad.append(f"report lacks section {head!r}")

    after = (RAW / "state_after_0545Z.txt").read_text(encoding="utf-8").splitlines()
    m = READING.match(after[0]) if after else None
    if not m:
        bad.append("state_after_0545Z.txt line 1 is not a Get-PSDrive reading")
    else:
        free = int(m.group(2))
        if free < MIN_FREE:
            bad.append(f"C: free {free} < {MIN_FREE}")
    readings = [ln for f in ("c_free_reading_0430Z.txt", "state_after_0545Z.txt")
                for ln in (RAW / f).read_text(encoding="utf-8").splitlines() if READING.match(ln)]
    if not any(r in report for r in readings):
        bad.append("report quotes no raw reading verbatim")

    deleted = re.findall(r"^DELETED (\S+) (\d+)$", (RAW / "del_swaps.out").read_text(encoding="utf-8"), re.M)
    if not deleted:
        bad.append("del_swaps.out records no deletion")
    left = set(re.findall(r"^swapdir (\S+) ", "\n".join(after), re.M))
    if again := left & {g for g, _ in deleted}:
        bad.append(f"deleted swap dirs still present: {sorted(again)}")

    log = (RAW / "compact.log").read_text(encoding="utf-8")
    start = re.search(r"start vhdx_GB ([\d.]+)", log)
    if "DiskPart successfully compacted the virtual disk file." not in log or not start:
        bad.append("compact.log shows no successful diskpart compact")
    vhdx = re.search(r"^ext4vhdx .* bytes=(\d+)$", "\n".join(after), re.M)
    if not vhdx:
        bad.append("state_after_0545Z.txt has no ext4.vhdx size")
    elif start and int(vhdx.group(1)) >= float(start.group(1)) * 2**30:
        bad.append(f"ext4.vhdx {vhdx.group(1)} B is not below the pre-compact {start.group(1)} GiB")

    for b in bad:
        print("FAIL", b)
    if bad:
        return 1
    print(f"OK free_bytes={m.group(2)} at {m.group(1)}; {len(deleted)} swap dirs deleted and gone; "
          f"ext4.vhdx {int(vhdx.group(1)) / 2**30:.2f} GiB < {start.group(1)} GiB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
