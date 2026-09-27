"""GREENTIDE_PLANT_SIGHT_BLOCK_ENGINE_1 -- live verification via the deterministic
dev-action probe RM_SightBlockProbe already ships (RimMandrake > "Sight-block probe"
/ "Sight-block stress"). Run with python.exe (bridge is Windows-loopback only).

    python.exe D:\\Luke\\dev\\Rimworld\\.claude\\worktrees\\agent-ab807a29ef8f12901\\Transient\\sight_block_verify.py

Loads the canonical save if no map is current, brings the game to foreground
(runInBackground trap), locates the two debug-action leaves by walking
list_debug_action_children (never search_debug_actions on the full stack),
fires each, and reads the result back from Player.log tail (the actions log
via Log.Message/Log.Warning).
"""
import sys
import time

sys.path.insert(0, r"D:\Luke\dev\Rimworld\.claude\worktrees\agent-ab807a29ef8f12901\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint  # noqa: E402
import game_focus  # noqa: E402

SAVE_NAME = "CANONICAL_ASHKARR_START_2026-09-12"
LOG_PATH = r"C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Player.log"


def log_tail_since(byte_offset):
    with open(LOG_PATH, "r", encoding="utf-8", errors="replace") as f:
        f.seek(byte_offset)
        return f.read()


def log_size():
    import os
    return os.path.getsize(LOG_PATH)


def find_leaf(rb, root_path, want_substring):
    """Walk list_debug_action_children looking for a leaf whose path's last
    component contains want_substring. Returns the path or None."""
    stack = [root_path]
    seen = set()
    while stack:
        node = stack.pop()
        if node in seen:
            continue
        seen.add(node)
        resp = rb.call("rimworld/list_debug_action_children", {"path": node})
        children = resp.get("children", [])
        for c in children:
            p = c.get("path", "")
            last = p.split(chr(92))[-1]
            if want_substring.lower() in last.lower():
                return p
            if c.get("hasChildren"):
                stack.append(p)
    return None


def main():
    prev_focus = None
    try:
        prev_focus = game_focus.preflight()
    except RuntimeError as e:
        # runInBackground is already True for this launch (checked Prefs.xml),
        # so the game's main thread keeps ticking even unfocused; the focus
        # steal is the fallback for when that pref is False, not a hard
        # requirement. Proceed without it rather than yank focus from a live
        # BENCH/owner window.
        print("focus steal skipped (non-fatal, runInBackground=True):", e)
    host, port, token = resolve_endpoint()
    print("endpoint:", host, port, bool(token))

    with RimBridge(host, port, token) as rb:
        info = rb.call("rimworld/get_game_info", {})
        print("game_info:", info)
    has_map = isinstance(info, dict) and info.get("status") != "no_game"

    if not has_map:
        print("no live game -- load_game_ready:", SAVE_NAME, "(long timeout connection)")
        try:
            with RimBridge(host, port, token, timeout=180.0) as rb_load:
                r = rb_load.call("rimworld/load_game_ready", {
                    "saveName": SAVE_NAME,
                    "timeoutMs": 150000,
                    "ignoreModCompatibility": True,
                })
                print("load_game_ready ->", r)
        except Exception as e:
            # Per rimbridge skill: a timeout kills the CONNECTION, not the call --
            # never retry on the same socket, open a fresh one and poll instead.
            print("load_game_ready call itself timed out/errored (expected on a slow load):", e)
        # Poll a FRESH connection each time for the post-condition.
        for i in range(24):  # up to ~4 minutes of polling
            time.sleep(10)
            try:
                with RimBridge(host, port, token, timeout=15.0) as rb_poll:
                    gi = rb_poll.call("rimworld/get_game_info", {})
                print("poll", i, "->", gi)
                if isinstance(gi, dict) and gi.get("status") != "no_game":
                    break
            except Exception as e:
                print("poll", i, "error (continuing):", e)
        time.sleep(45)  # the ~40s drivability settle, not just the bridge answering
    else:
        print("already on a live map, reusing it")

    with RimBridge(host, port, token) as rb:
        info2 = rb.call("rimworld/get_game_info", {})
        print("game_info after load:", info2)

        print("locating debug-action leaves under Actions\\RimMandrake ...")
        probe_path = find_leaf(rb, "Actions", "Sight-block probe")
        print("probe_path:", probe_path)
        stress_path = find_leaf(rb, "Actions", "Sight-block stress")
        print("stress_path:", stress_path)

        if not probe_path:
            print("ABORT: could not locate the 'Sight-block probe' debug action leaf.")
            return 2

        off = log_size()
        print("firing probe, log offset before:", off)
        resp = rb.call("rimworld/execute_debug_action", {"path": probe_path})
        print("execute_debug_action(probe) ->", resp)
        time.sleep(2)
        tail = log_tail_since(off)
        print("----- Player.log tail after probe -----")
        print(tail[-4000:])

        if stress_path:
            off2 = log_size()
            print("firing stress, log offset before:", off2)
            resp2 = rb.call("rimworld/execute_debug_action", {"path": stress_path})
            print("execute_debug_action(stress) ->", resp2)
            time.sleep(2)
            tail2 = log_tail_since(off2)
            print("----- Player.log tail after stress -----")
            print(tail2[-2000:])
    if prev_focus:
        game_focus.restore_focus(prev_focus)
    return 0


if __name__ == "__main__":
    sys.exit(main())
