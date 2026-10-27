#!/usr/bin/env python3
"""TPS/FPS/heap census from JawaBench tps records (C-suite evidence, 2026-10-26).

Reads <SaveData>/JawaBench/tps/tps_*.jsonl (7-day retention), joins each sample to its
session's mod count, and prints per day x list-class (full >=200 mods, minimal <=60, mid)
x speed multiplier: running-sample count, median TPS, median ratio (tps/target),
median FPS, max heapMB. Only samples with dTicks>0 (game actually ticking) count for TPS.
"""
import glob, json, os, statistics as st, sys, collections

D = os.environ.get("JB_TPS", "/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/"
                   "RimWorld by Ludeon Studios/JawaBench/tps")


def cls(n):
    if n is None or n < 0:
        return "?"
    return "full" if n >= 200 else ("minimal" if n <= 60 else "mid")


def main():
    mods = {}
    rows = collections.defaultdict(list)
    sess_seen = collections.defaultdict(set)
    for f in sorted(glob.glob(os.path.join(D, "tps_*.jsonl"))):
        with open(f, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                try:
                    r = json.loads(line)
                except ValueError:
                    continue
                k = r.get("kind")
                if k == "session":
                    mods[r["session"]] = r.get("mods")
                elif k == "sample":
                    day = r["utc"][:10]
                    c = cls(mods.get(r.get("session")))
                    sess_seen[(day, c)].add(r.get("session"))
                    rows[(day, c, r.get("mult"))].append(r)
    print("day        class    mult  n_run  medTPS  medRatio  medFPS(all)  maxHeapMB  sessions")
    for (day, c, m), rs in sorted(rows.items(), key=lambda x: (x[0][0], x[0][1], str(x[0][2]))):
        run = [r for r in rs if (r.get("dTicks") or 0) > 0 and r.get("tps")]
        fps = [r["fps"] for r in rs if r.get("fps") is not None]
        heap = [r["heapMB"] for r in rs if r.get("heapMB") is not None]
        rat = [r["ratio"] for r in run if r.get("ratio") is not None]
        if not run and m not in (0, None):
            continue
        print(f"{day} {c:8} {str(m):5} {len(run):6} "
              f"{(st.median([r['tps'] for r in run]) if run else float('nan')):7.1f} "
              f"{(st.median(rat) if rat else float('nan')):8.2f} "
              f"{(st.median(fps) if fps else float('nan')):11.1f} "
              f"{(max(heap) if heap else float('nan')):9.0f}  {len(sess_seen[(day, c)])}")


if __name__ == "__main__":
    sys.exit(main())
