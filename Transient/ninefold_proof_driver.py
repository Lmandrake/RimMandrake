# Ninefold hook proof driver — BENCH 2026-09-05. Run with python.exe (Windows loopback).
# Stages so a failure is attributable:
#   stage1: preflight (census, devmode on, load Autosave-4, settle)
#   stage2: baseline pawn census + log offset
#   stage3: fire real raid, verify arrivals, run time, harvest [Ninefold] lines
import sys, time, json, os
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

PLAYER_LOG = r"C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Player.log"
STATE = r"D:\Luke\dev\Rimworld\Transient\ninefold_proof_state.json"

def log(msg):
    print(msg, flush=True)

def main(stage):
    host, port, token = resolve_endpoint()
    rb = RimBridge(host, port, token)
    rb.__enter__()
    try:
        if stage == "1":
            info = rb.call("rimworld/get_game_info", {})
            log(f"programState={info.get('programState')} status={info.get('status')} mapCount={info.get('mapCount')}")
            tools = rb.list_tools()
            names = [t.get("name", "") for t in (tools.get("tools", []) if isinstance(tools, dict) else tools)]
            jawa = [n for n in names if n.startswith("jawa/")]
            log(f"jawa tool count MEASURED: {len(jawa)}")
            if "jawa/prefs" in names:
                r = rb.call("jawa/prefs", {"devMode": True})
                log(f"prefs write: success={r.get('success')} after={json.dumps(r.get('after'))}")
            else:
                log("jawa/prefs MISSING — devmode unverified"); return 1
            # load the save
            r = rb.call("rimworld/load_game", {"saveName": "Autosave-4"})
            log(f"load_game: success={r.get('success')} code={r.get('code')} msg={str(r.get('message'))[:200]}")
            # poll postcondition: programState Playing + ticks answering
            deadline = time.time() + 600
            while time.time() < deadline:
                time.sleep(10)
                try:
                    gi = rb.call("rimworld/get_game_info", {})
                except Exception as e:
                    log(f"poll reconnect ({e})"); rb.__exit__(None, None, None)
                    rb = RimBridge(*resolve_endpoint()); rb.__enter__(); continue
                ps = gi.get("programState")
                log(f"  poll: programState={ps} status={gi.get('status')} ticks={gi.get('ticksGame')}")
                if ps == "Playing":
                    break
            else:
                log("TIMEOUT waiting for Playing"); return 1
            log("settling 45s (bridge-answers != game-reactive)")
            time.sleep(45)
            gi = rb.call("rimworld/get_game_info", {})
            log(f"settled: programState={gi.get('programState')} ticks={gi.get('ticksGame')} mapCount={gi.get('mapCount')}")

        elif stage == "2":
            pawns = rb.call("jawa/list_pawns", {})
            rows = pawns.get("pawns") or pawns.get("rows") or []
            byfac = {}
            for p in rows:
                byfac.setdefault(str(p.get("factionName")), []).append(p.get("id") or p.get("pawnId"))
            for f, ids in sorted(byfac.items()):
                log(f"faction {f}: {len(ids)} pawns")
            off = os.path.getsize(PLAYER_LOG)
            json.dump({"log_offset": off, "baseline_ids": sorted(str(i) for v in byfac.values() for i in v)}, open(STATE, "w"))
            log(f"log offset recorded: {off}")

        elif stage == "3":
            st = json.load(open(STATE))
            r = rb.call("jawa/fire_raid", {"points": 2000})
            log(f"fire_raid: success={r.get('success')} executed={r.get('executed')} blockedByDialog={r.get('blockedByDialog')} windowsOpened={r.get('windowsOpened')}")
            time.sleep(3)
            pawns = rb.call("jawa/list_pawns", {})
            rows = pawns.get("pawns") or pawns.get("rows") or []
            new = [p for p in rows if str(p.get("id") or p.get("pawnId")) not in set(st["baseline_ids"])]
            facs = {}
            for p in new:
                facs[str(p.get("factionName"))] = facs.get(str(p.get("factionName")), 0) + 1
            log(f"ARRIVALS (census, not echo): {json.dumps(facs)}")
            if not new:
                log("NO ARRIVALS — do not proceed to time run"); return 1
            # run real time: speed via jawa/set_game_speed, verify by tick delta
            t0 = rb.call("rimworld/get_game_info", {}).get("ticksGame")
            r = rb.call("jawa/set_game_speed", {"speed": 3})
            log(f"set_game_speed: success={r.get('success')}")
            for i in range(24):  # up to ~4 min wall
                time.sleep(10)
                gi = rb.call("rimworld/get_game_info", {})
                t1 = gi.get("ticksGame")
                nf = count_ninefold(st["log_offset"])
                log(f"  t+{(i+1)*10}s ticks={t1} (delta {t1 - t0 if t1 and t0 else '?'}) ninefold_lines={nf}")
                if nf >= 3 and t1 and t0 and t1 - t0 > 5000:
                    break
            rb.call("jawa/set_game_speed", {"speed": 0})
            gi = rb.call("rimworld/get_game_info", {})
            log(f"paused-request sent; ticks now {gi.get('ticksGame')}")
            dump_ninefold(st["log_offset"])
        return 0
    finally:
        try:
            rb.__exit__(None, None, None)
        except Exception:
            pass

def count_ninefold(offset):
    try:
        with open(PLAYER_LOG, "rb") as f:
            f.seek(offset)
            data = f.read().decode("utf-8", "ignore")
        return data.count("[Ninefold]")
    except Exception:
        return -1

def dump_ninefold(offset):
    with open(PLAYER_LOG, "rb") as f:
        f.seek(offset)
        data = f.read().decode("utf-8", "ignore")
    lines = [l for l in data.splitlines() if "[Ninefold]" in l]
    log(f"NINEFOLD LINES ({len(lines)}):")
    for l in lines[:40]:
        log("  " + l.strip())

if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "1"))
