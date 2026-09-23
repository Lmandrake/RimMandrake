"""
COLD_LOAD_RUN_SHEET_4 finish pass -- live bridge test helpers.
FOUNDRY, 2026-09-23. Run with python.exe from Windows (WSL: /mnt/d/... -> D:\\...).

Usage (from a `python.exe -c` one-liner or `python.exe this_file.py <stage>`):
    python.exe D:\\Luke\\dev\\Rimworld\\Transient\\foundry_livetest_2026-09-23.py <stage>

Stages: load, manywaters, ninefold, wyyyschokk, tilegen, cathedral, miasma
"""
import sys, json, time

sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint  # noqa: E402


def conn():
    host, port, token = resolve_endpoint()
    return RimBridge(host, port, token)


def pp(label, obj):
    print("===", label, "===")
    try:
        print(json.dumps(obj, indent=2)[:4000])
    except Exception:
        print(obj)


def stage_load(rb):
    r = rb.call("rimworld/load_game", {"saveName": "Autosave-10"})
    pp("load_game", r)
    for i in range(60):
        info = rb.call("rimworld/get_game_info", {})
        ps = info.get("programState") or info.get("Result", {}).get("programState")
        pp("get_game_info poll %d" % i, {"programState": ps, "raw_keys": list(info.keys())})
        if ps == "Playing":
            break
        time.sleep(3)
    return info


if __name__ == "__main__":
    stage = sys.argv[1] if len(sys.argv) > 1 else "load"
    with conn() as rb:
        if stage == "load":
            stage_load(rb)
        else:
            print("stage not implemented in this skeleton:", stage)
