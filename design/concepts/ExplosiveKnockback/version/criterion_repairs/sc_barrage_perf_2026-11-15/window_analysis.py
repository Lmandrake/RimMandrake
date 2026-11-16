#!/usr/bin/env python3
"""Step 1 of the sc_barrage_perf criterion repair: where do the >50 ms frames fall against the barrage-and-chain window?

Reads the nine RM_FrameProbe CSVs of visit 2 (copied into probe_csv/; each row is one rendered frame: ms since the previous
frame, paused, things in the air). A frame's probe time is the running sum of ms. The event window comes from the scene's own
schedule (RM_KnockbackProof_StageThree.cs BarragePerf: shells at stagedTick+60+30i, ignite at +300) and the run journal (last
gas_burst at stagedTick+476..496); the mod-on runs' in_air column (first 0.94-0.96 s, last 7.57-8.02 s) confirms tick time
tracks probe time to ~0.06 s. Usage: python3 window_analysis.py
"""
import csv
import os

HERE = os.path.dirname(os.path.abspath(__file__))
RUNS = [  # (visit-2 run, selfcheck, barrage_perf_off, barrage_perf), scene order of knockback_runner --scenes
    ("first", "172102", "172127", "172152"),
    ("settled", "172255", "172320", "172345"),
    ("third", "172430", "172455", "172520"),
]
EVENT = (0.9, 8.25)    # first shell (1.0 s) to the last gas burst / landing (<= 8.1 s), with margin
SHELLS = (0.9, 3.6)    # the six shells only: 1.0-3.5 s
BAR = 50.0


def frames(stamp):
    t, out = 0.0, []
    with open(os.path.join(HERE, "probe_csv", "RM_FrameProbe_20261115T%s.csv" % stamp)) as f:
        for r in csv.DictReader(f):
            ms = float(r["ms"])
            t += ms
            out.append((t / 1000.0, ms, int(r["in_air"])))
    return out


def worst(fr, lo, hi):
    inside = [ms for (s, ms, _) in fr if lo <= s <= hi]
    return max(inside) if inside else 0.0, sum(1 for ms in inside if ms > BAR)


def main():
    print("run      case  worst_all  worst_event[0.9-8.25s] n>50  worst_shells[0.9-3.6s] n>50  spikes>50 (s:ms)")
    outside_s = outside_n = 0.0
    for name, sc, off, on in RUNS:
        for case, stamp in (("self", sc), ("off", off), ("on", on)):
            fr = frames(stamp)
            wa = max(ms for _, ms, _ in fr)
            we, ne = worst(fr, *EVENT)
            ws, ns = worst(fr, *SHELLS)
            spikes = " ".join("%.2f:%.0f" % (s, ms) for s, ms, _ in fr if ms > BAR)
            print("%-8s %-5s %8.1f  %10.1f %18d  %10.1f %16d  %s" % (name, case, wa, we, ne, ws, ns, spikes))
            if case in ("off", "on"):  # background: after the window, to the end of the probe
                total = fr[-1][0]
                outside_s += max(0.0, total - EVENT[1])
                outside_n += sum(1 for s, ms, _ in fr if s > EVENT[1] and ms > BAR)
    print("background (off+on, after the window): %d frames over %.0f ms in %.1f s = %.2f per second"
          % (outside_n, BAR, outside_s, outside_n / outside_s))


if __name__ == "__main__":
    main()
