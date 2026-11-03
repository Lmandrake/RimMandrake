#!/usr/bin/env python3
"""Offline check of the FOREIGN_GUARD_WIDEN_MIRROR_CROP census calibration.

calib.tsv beside this file is the frozen output of calib.py (run over the 2,204 artpipe census outputs and
11,321 codex cache renders on D:\\ClaudeWork, which a checker may not reach): every pair the NEW transforms
(mirrored placement; centre square of a non-square candidate) bring inside FOREIGN_NEAR that the plain
16x16 check did not, with its detail correlation and the artpipe spec facts of the placed output.

This re-judges each recorded pair against codex_image.py's bars AT THIS SHA and exits 0 only when
  - every row's would_refuse agrees with today's FOREIGN_NEAR / FOREIGN_DETAIL_CORR,
  - every row's class follows from its recorded facts (no UNCLASSED, no hand label),
  - no pair of two independent codex generations (the only legitimate pair the guard can see) is refused.
Classes: independent_generation (both sides plain codex generates: refusing it is a false positive),
source_file_import (output placed from source_file, a path the guard never runs on), copy_channel
(channel=copy, a deliberate copy, never through the guard), foreign_crop_stowaway (a real cropped foreign
copy the old guard passed; filed ARTEVAL_CROPPED_COPIES_AUDIT_TWO_STOWAWAYS), detail_rejected (coarse hit
that detail confirmation lets through).
"""
import csv
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
sys.path.insert(0, str(REPO / "skills/generating-images/scripts"))
import codex_image as ci  # noqa: E402


def derive_class(r):
    if r["both_independent_generate"] == "True":
        return "independent_generation"
    if r["would_refuse"] == "False":
        return "detail_rejected"
    if r["out_source_file"] == "True":
        return "source_file_import"
    if r["out_channel"] == "copy":
        return "copy_channel"
    if r["centre"] == "True" and r["out_channel"] == "codex":
        return "foreign_crop_stowaway"
    return "UNCLASSED"


def main():
    rows = list(csv.DictReader(open(HERE / "calib.tsv"), delimiter="\t"))
    bad, counts = [], {}
    for r in rows:
        corr = None if r["detail_corr"] == "None" else float(r["detail_corr"])
        coarse = float(r["dist"]) <= ci.FOREIGN_NEAR
        refuse = coarse and (corr is None or corr >= ci.FOREIGN_DETAIL_CORR)
        if not coarse:
            bad.append(f"{r['output']}: dist {r['dist']} is outside FOREIGN_NEAR {ci.FOREIGN_NEAR}")
        if str(refuse) != r["would_refuse"]:
            bad.append(f"{r['output']}: recorded would_refuse={r['would_refuse']}, bars at this sha say {refuse}")
        c = derive_class(r)
        if c != r["class"]:
            bad.append(f"{r['output']}: class {r['class']!r} does not follow from its facts ({c!r})")
        if c == "UNCLASSED":
            bad.append(f"{r['output']}: unclassed")
        if c == "independent_generation" and refuse:
            bad.append(f"{r['output']}: LEGITIMATE independent pair newly refused <- {r['candidate']}")
        counts[c] = counts.get(c, 0) + 1
    if not rows:
        bad.append("calib.tsv has no rows: instrument blind")
    print(f"bars FOREIGN_NEAR={ci.FOREIGN_NEAR} FOREIGN_DETAIL_CORR={ci.FOREIGN_DETAIL_CORR}; "
          f"{len(rows)} new coarse pairs; " + ", ".join(f"{k}={v}" for k, v in sorted(counts.items())))
    for b in bad:
        print("FAIL", b)
    print("PASS" if not bad else f"FAIL ({len(bad)})")
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
