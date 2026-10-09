#!/usr/bin/env python3
"""selftest_render_refine.py — render_subjects.refine(): the deterministic rules for renders token matching left open
(vanilla reskin family, sibling, primary-body, rename, deleted, donor-name), and that each leaves bound renders alone."""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import def_history as H  # noqa: E402
import render_subjects as RS  # noqa: E402

FAILS = []


def check(cond, msg, detail=""):
    print(("PASS " if cond else "FAIL ") + msg + ("" if cond else f"  [{str(detail)[:300]}]"))
    if not cond:
        FAILS.append(msg)


class FakeWorld:
    defs = {n: {} for n in ("RM_Hollu", "RM_HolluCatch", "RM_Vurra", "VAEWaste_Megatardi", "RM_Dewgourd", "RSW_Korrum")}


def rec(job, res=None, via=None, subjects=()):
    fam = RS.S.FAM_RE.sub("", job)
    return {"job": job, "family": fam, "resolution": res, "via": via, "subjects": list(subjects), "evidence": ""}


H.load = lambda: {"renames": {"RSW_Ashworm": ["RM_Vurra"], "RSW_Stoneback": ["RSW_Bokka", "RSW_Korrum"]},
                  "rename_commit": {"RSW_Ashworm>RM_Vurra": "abc123 NONCANON rename"},
                  "deleted": {"RM_Kudda": "def456 cut", "RSW_Stoneback": "x", "RSW_Ashworm": "y"}}
out = {k: rec(*v) for k, v in {
    "a": ("RSW_Junk_AncientTank_03", "unresolved"),
    "b": ("RSW_Junk_AncientNotReal_03", "unresolved"),
    "c": ("bluedesert_Thunderbeast_v2_east", "bound", "binding", ["AA_Thunderbeast"]),
    "d": ("bluedesert_Thunderbeast_v2_north", "unresolved"),
    "e": ("twilightsea_hollu_v2", "ambiguous", "token", ["RM_Hollu", "RM_HolluCatch"]),
    "f": ("desertportb_ashworm", "unresolved"),
    "g": ("RM_Kudda", "unresolved"),
    "h": ("facingrepair_megatardi_v1", "unresolved"),
    "i": ("RSW_Stoneback", "unresolved"),
    "j": ("spec_scene_kudda", "unresolved"),
    "k": ("hollu_catch_v1", "ambiguous", "token", ["RM_Hollu", "RM_HolluCatch"]),
}.items()}
before_bound = dict(out["c"])
RS.refine(out, FakeWorld())
check(out["a"]["via"] == "vanilla-reskin" and out["a"]["subjects"] == ["AncientTank"], "RSW_Junk_AncientTank_NN -> vanilla AncientTank", out["a"])
check(out["b"]["resolution"] == "unresolved", "a RSW_Junk name outside the spec table stays unresolved", out["b"])
check(out["c"] == before_bound, "a bound render is untouched")
check(out["d"]["via"] == "sibling" and out["d"]["subjects"] == ["AA_Thunderbeast"], "sibling inherits the family's single target_def", out["d"])
check(out["e"]["via"] == "primary-body" and out["e"]["subjects"] == ["RM_Hollu"], "body + Catch -> body", out["e"])
check(out["k"]["resolution"] == "ambiguous", "a family that names the catch is not collapsed to the body", out["k"])
check(out["f"]["via"] == "rename" and out["f"]["subjects"] == ["RM_Vurra"], "recorded rename to a live def resolves", out["f"])
check(out["g"]["resolution"] == "dead" and out["g"]["subjects"] == ["RM_Kudda"], "removed def is dead, not bound", out["g"])
check(out["h"]["via"] == "donor-name" and out["h"]["subjects"] == ["VAEWaste_Megatardi"], "donor name without its mod prefix", out["h"])
check(out["i"]["resolution"] == "ambiguous" and out["i"]["via"] == "rename", "a name handed to two things over time is never guessed", out["i"])
check(out["j"]["resolution"] == "unresolved", "spec_* scenes never take a removed-def match", out["j"])
print("FAILED %d" % len(FAILS) if FAILS else "ALL PASS")
sys.exit(1 if FAILS else 0)
