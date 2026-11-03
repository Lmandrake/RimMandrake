#!/usr/bin/env python3
"""Selftest for heavy_textures_vram.py: reply unwrapping, texture and process judging, the textureless excuse. Offline."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import heavy_textures_vram as h  # noqa: E402

FAILS = []
MB = 1048576


def check(name, cond):
    if not cond:
        FAILS.append(name)
        print("FAIL " + name)


W = list(h.MODS)


def mod(pid, count=10, gpu=5 * MB, ba=0, prof=None):
    return {"packageId": pid, "count": count, "gpuBytes": gpu, "cpuBytes": 0, "profilerBytes": prof, "readable": 0,
            "bundleAssets": ba, "fromContent": count, "fromBundle": 0,
            "top": [{"name": "t", "w": 64, "h": 64, "format": "RGBA_DXT5_UNorm", "gpuBytes": gpu}]}


def res(mods, textures=1000, gpu=900 * MB, missing=()):
    return {"success": True, "textures": textures, "totals": {"gpuBytes": gpu, "cpuBytes": 0, "profilerBytes": None},
            "mods": mods, "missing": list(missing), "buckets": {}}


GB = "fourtoo.glowingbush"
good = res([mod(p) for p in W])

# unwrap: bare, result-wrapped, GABP content envelope, garbage
check("unwrap bare", h.unwrap(good) is good)
check("unwrap result", h.unwrap({"result": good}) == good)
check("unwrap content", h.unwrap({"content": [{"type": "text", "text": json.dumps(good)}]}) == good)
check("unwrap garbage", h.unwrap({"content": [{"text": "not json"}]}) is None and h.unwrap("x") is None)

# textures
c, rows, why = h.judge_textures(good, W)
check("all four measured -> 0", c == 0 and len(rows) == 4 and not why)
check("MB conversion", rows[0]["gpuMB"] == 5.0 and rows[0]["profilerMB"] is None)
c, _, why = h.judge_textures(res([mod(p) for p in W[:3]], missing=[W[3]]), W)
check("a mod not running -> 2 (unmeasurable), never a FAIL", c == 2 and W[3] in why[0])
c, _, why = h.judge_textures(res([mod(p) for p in W[:3]]), W)
check("a mod absent from mods[] -> 2 even when missing[] is empty", c == 2)
c, _, why = h.judge_textures(res([mod(p) for p in W], textures=0, gpu=0), W)
check("blind census (0 textures, 0 bytes) -> 1", c == 1 and "blind" in why[0])
zero = [mod(p) if p != GB else mod(p, count=0, gpu=0) for p in W]
check("a zero mod with files -> 1", h.judge_textures(res(zero), W)[0] == 1)
check("a zero mod the census found textureless -> 0", h.judge_textures(res(zero), W, {GB})[0] == 0)
bundled = [mod(p) if p != W[1] else mod(p, count=0, gpu=0, ba=40) for p in W]
check("bundle assets listed but none loaded -> not blind", h.judge_textures(res(bundled), W)[0] == 0)
check("unsuccessful reply -> 2", h.judge_textures({"success": False}, W)[0] == 2 and h.judge_textures(None, W)[0] == 2)

# textureless: only clean, empty census rows
rows_off = [{"packageId": "a", "error": None, "texFiles": 0, "bundleFiles": 0},
            {"packageId": "b", "error": "no folder", "texFiles": 0, "bundleFiles": 0},
            {"packageId": "c", "error": None, "texFiles": 3, "bundleFiles": 0},
            {"packageId": "d", "error": None, "texFiles": 0, "bundleFiles": 1}]
check("textureless = clean rows with no files", h.textureless(rows_off) == {"a"} and h.textureless(None) == set())

# process
proc = {"running": True, "pid": 1, "private": 30000 * MB, "working": 18000 * MB, "gpu_dedicated": 4000 * MB,
        "gpu_shared": 300 * MB, "gpu_counters": 2}
health = {"unityAllocMB": 9000.0, "unityReservedMB": 9500.0, "monoUsedMB": 5000.0, "monoHeapMB": 5200.0, "gfxMB": 0}
c, fig, why = h.judge_process(proc, health)
check("process measured -> 0", c == 0 and fig["privateMB"] == 30000.0 and fig["gpuDedicatedMB"] == 4000.0)
check("gfx driver 0 is UNKNOWN, not zero", fig["gfxDriverMB"] is None)
c, fig, _ = h.judge_process(dict(proc, gpu_counters=0, gpu_dedicated=0), None)
check("no GPU counter -> UNKNOWN, and no health -> UNKNOWN, still 0", c == 0 and fig["gpuDedicatedMB"] is None
      and fig["unityAllocMB"] is None)
check("private bytes unread -> 1", h.judge_process(dict(proc, private=0), health)[0] == 1)
check("no process -> 2", h.judge_process({"running": False}, health)[0] == 2
      and h.judge_process({"error": "x"}, health)[0] == 2 and h.judge_process(None, None)[0] == 2)

# the report renders on a full answer
md = h.markdown("T", h.judge_textures(good, W)[1], h.judge_process(proc, health)[1], good,
                [{"packageId": W[0], "texMB": 76.1}])
check("markdown carries estimate and UNKNOWN", "76.1" in md and "UNMEASURED" in md and "UNKNOWN" in md)

print("FAILED %d" % len(FAILS) if FAILS else "OK selftest_heavy_textures_vram")
sys.exit(1 if FAILS else 0)
