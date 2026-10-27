#!/usr/bin/env python3
"""Query the Windows-side VictoriaMetrics (telemetryd) from WSL via powershell.exe.

WSL cannot reach Windows 127.0.0.1:8428 directly (NAT), so this shells out to
powershell Invoke-WebRequest. Used by the C-suite evidence census (2026-10-26).

  csuite_vm.py series 'rm_game_tps'                 -> label sets
  csuite_vm.py range 'avg(rm_game_tps)' --days 21 --step 1d
  csuite_vm.py instant 'max_over_time(rm_game_heap_mb[21d])'
"""
import argparse, json, subprocess, sys, time, urllib.parse

VM = "http://127.0.0.1:8428"


def get(path, params):
    url = VM + path + "?" + urllib.parse.urlencode(params)
    ps = f"(Invoke-WebRequest -UseBasicParsing '{url}').Content"
    r = subprocess.run(["powershell.exe", "-NoProfile", "-Command", ps],
                       capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        sys.exit(f"powershell failed: {r.stderr[-400:]}")
    return json.loads(r.stdout)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["series", "range", "instant"])
    ap.add_argument("expr")
    ap.add_argument("--days", type=float, default=21)
    ap.add_argument("--step", default="1d")
    a = ap.parse_args()
    now = time.time()
    if a.mode == "series":
        d = get("/api/v1/series", {"match[]": a.expr, "start": int(now - a.days * 86400)})
        for s in d["data"]:
            print(json.dumps(s))
    elif a.mode == "instant":
        d = get("/api/v1/query", {"query": a.expr})
        for s in d["data"]["result"]:
            print(json.dumps(s["metric"]), s["value"][1])
    else:
        d = get("/api/v1/query_range", {"query": a.expr, "start": int(now - a.days * 86400),
                                        "end": int(now), "step": a.step})
        for s in d["data"]["result"]:
            print(json.dumps(s["metric"]))
            for t, v in s["values"]:
                print("  ", time.strftime("%Y-%m-%d %H:%M", time.localtime(t)), v)


if __name__ == "__main__":
    main()
