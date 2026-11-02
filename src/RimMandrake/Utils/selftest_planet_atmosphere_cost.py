#!/usr/bin/env python3
"""Selftest for planet_atmosphere_cost.py: loader arithmetic, sample judging, A/B pairing. Offline."""
import datetime as dt
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import planet_atmosphere_cost as pac  # noqa: E402

FAILS = []


def check(name, cond):
    if not cond:
        FAILS.append(name)
        print("FAIL " + name)


# loader arithmetic
t = pac.texture_bytes(8192, 4096)
full = sum(max(1, 8192 >> i) * max(1, 4096 >> i) for i in range(14))
kept = sum((8192 >> i) * (4096 >> i) for i in range(9))
check("8k is DXT5, 9 levels (log2(4096/16)+1)", t["format"] == "DXT5" and t["mips"] == 9)
check("8k resident = 1 B/px over kept levels", t["resident"] == kept)
check("8k decode = 4 B/px over the full chain", t["decode"] == 4 * full)
check("8k off-compression is RGBA32 full chain", pac.texture_bytes(8192, 4096, compression=False)["resident"] == 4 * full)
check("8k no-compute keeps full chain", pac.texture_bytes(8192, 4096, compute=False)["mips"] == 14)
s = pac.texture_bytes(5000, 5000)
check("5000^2 keeps 2 DXT levels", s["mips"] == 2 and s["resident"] == 5000 * 5000 + 2500 * 2500)
r = pac.texture_bytes(2048, 125)
check("odd side stays RGBA32 with full chain on compute", r["format"] == "RGBA32" and r["mips"] == 12)
check("odd side clamps to 1 level without compute", pac.texture_bytes(2048, 125, compute=False)["mips"] == 1)
check("dxt_mips 2048x128", pac.dxt_mips(2048, 128) == 6)
check("2048x128 keeps 4 levels (log2(128/16)+1)", pac.texture_bytes(2048, 128)["mips"] == 4)
check("min side 16 stays RGBA32", pac.texture_bytes(64, 16)["format"] == "RGBA32")
check("1x1 is one RGBA32 texel", pac.texture_bytes(1, 1)["resident"] == 4)

# load time parse
log = ("[RimBridge] STARTUP_TIMING phase=a durationMs=0 elapsedMs=180\n"
       "[RimBridge] STARTUP_TIMING phase=late-input-patches durationMs=19 elapsedMs=93994\n"
       "[RimBridge] STARTUP_TIMING phase=tools.construct durationMs=0 elapsedMs=98200\n")
check("load_ms = max elapsed", pac.load_ms(log) == 98200)
check("load_ms none", pac.load_ms("nothing here") is None)

# sample judging
start = dt.datetime(2026, 11, 2, 9, 0, tzinfo=dt.timezone.utc)
proc = {"running": True, "pid": 7, "start": "2026-11-02T09:00:00.1234567Z", "private": 2 * 1024 ** 3,
        "working": 1024 ** 3, "gpu_dedicated": 3 * 1024 ** 3, "gpu_shared": 1024 ** 2, "gpu_counters": 2}
mods = ["ludeon.rimworld"] + pac.DLC + [pac.PKG]
ok_row, bad = pac.judge_sample(proc, mods, start - dt.timedelta(seconds=60), log, start + dt.timedelta(hours=1))
check("good sample has no reasons", bad == [] and ok_row["with"] is True and ok_row["load_ms"] == 98200)
_, bad = pac.judge_sample(proc, mods, start + dt.timedelta(seconds=pac.LAUNCH_SLACK_S + 5), log,
                          start + dt.timedelta(hours=1))
check("ModsConfig written after launch refuses", any("next load" in b for b in bad))
_, bad = pac.judge_sample(proc, mods[:2] + [pac.PKG], start, log, start + dt.timedelta(hours=1))
check("missing DLC refuses", any("DLC missing" in b for b in bad))
_, bad = pac.judge_sample(proc, mods, start, "", start + dt.timedelta(hours=1))
check("no timing refuses", any("UNMEASURED" in b for b in bad))
_, bad = pac.judge_sample(dict(proc, gpu_counters=0), mods, start, log, start + dt.timedelta(hours=1))
check("no GPU counter refuses", any("GPU" in b for b in bad))
_, bad = pac.judge_sample(proc, mods, start, log, start - dt.timedelta(seconds=10))
check("stale Player.log refuses", any("older" in b for b in bad))
_, bad = pac.judge_sample({"running": False}, mods, start, log, start)
check("not running refuses", bad != [])

# pairing
w = dict(ok_row)
o = dict(ok_row, mods=[m for m in mods if m != pac.PKG])
o["with"] = False
other = dict(o, mods=o["mods"] + ["someone.else"])
check("pair finds with/without", pac.pair([w, o]) == (w, o))
check("pair refuses lists differing by more", pac.pair([w, other]) is None)
check("pair refuses one side", pac.pair([w]) is None)

# record(): the --require condition gate, with the impure readers stubbed
import contextlib  # noqa: E402
import io  # noqa: E402
import tempfile  # noqa: E402
import types  # noqa: E402

with tempfile.TemporaryDirectory() as tmp:
    now = dt.datetime.now(dt.timezone.utc)
    cfg = os.path.join(tmp, "ModsConfig.xml")
    plog = os.path.join(tmp, "Player.log")
    samples = os.path.join(tmp, "out", "samples.jsonl")
    with open(cfg, "w") as fh:
        fh.write("<ModsConfigData/>")
    with open(plog, "w") as fh:
        fh.write(log)
    os.utime(cfg, (now.timestamp() - 120, now.timestamp() - 120))
    os.utime(plog, (now.timestamp(), now.timestamp()))
    live_proc = dict(proc, start=(now - dt.timedelta(seconds=60)).isoformat().replace("+00:00", "Z"))
    saved = (pac.sample_process, pac.active_mods, pac.MODSCONFIG, pac.PLAYER_LOG, pac.samples_path)
    pac.sample_process = lambda: dict(live_proc)
    pac.MODSCONFIG, pac.PLAYER_LOG, pac.samples_path = cfg, plog, (lambda: samples)
    try:
        def run(mod_list, require):
            pac.active_mods = lambda: list(mod_list)
            before = os.path.getsize(samples) if os.path.exists(samples) else 0
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = pac.record(types.SimpleNamespace(require=require))
            after = os.path.getsize(samples) if os.path.exists(samples) else 0
            return rc, buf.getvalue(), after > before
        without_mods = [m for m in mods if m != pac.PKG]
        rc, out, wrote = run(mods, "with")
        check("record: 'with' launch + --require with records (exit 0)", rc == 0 and wrote and "SAMPLE with" in out)
        rc, out, wrote = run(without_mods, "without")
        check("record: 'without' launch + --require without records (exit 0)",
              rc == 0 and wrote and "SAMPLE without" in out)
        rc, out, wrote = run(without_mods, "with")
        check("record: 'without' launch refuses --require with", rc == 1 and not wrote
              and "'without' condition, not 'with'" in out)
        rc, out, wrote = run(mods, "without")
        check("record: 'with' launch refuses --require without", rc == 1 and not wrote
              and "'with' condition, not 'without'" in out)
    finally:
        pac.sample_process, pac.active_mods, pac.MODSCONFIG, pac.PLAYER_LOG, pac.samples_path = saved

print("selftest_planet_atmosphere_cost: %s (%d failed)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
sys.exit(1 if FAILS else 0)
