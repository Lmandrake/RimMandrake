"""Live proof of the scene library's skeleton, written as a scene: open reports six phases done, a run of 120 ticks stops on
its tick, and the receipt names the game and the loaded DLLs. Item RIMMANDRAKE_BUILD_SCENE_LIBRARY_TEN_NAMES_FIVE_LAYERS_TODAY.

    python.exe src\\RimMandrake\\Utils\\scene.py accept src\\RimMandrake\\bridgetools\\scene_smoke_run.py
    python.exe src\\RimMandrake\\bridgetools\\scene_smoke_run.py          (not an acceptance run; SMOKE_GAME names another game)

Exit 0 = every row PASS, 1 = a FAIL."""
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Utils"))
import scene  # noqa: E402

c = scene.cond
GAME = os.environ.get("SMOKE_GAME", "ArchSmall")
ROWS = []


def row(name, ok, detail):
    ROWS.append(bool(ok))
    print("%-58s %s  %s" % (name, "PASS" if ok else "FAIL", str(detail)[:400]), flush=True)


with scene.open(GAME, needs={"map": "fresh:quicktest", "calm": "standard"}) as s:
    print(s.opened, flush=True)
    row("open reports six phases done", [p["state"] for p in s.opened] == ["done"] * 6, [p["phase"] for p in s.opened])
    b, t0 = s.receipt.build, s.state.tick
    row("the receipt names the game", s.receipt.game["name"].lower() == GAME.lower(), s.receipt.game)
    row("the receipt names the loaded DLLs", b["dlls"] and all(d["mvid"] and d["sha256"] for d in b["dlls"].values()), {n: d["sha256"][:12] for n, d in b["dlls"].items()})
    pawns = s.raw("jawa/map_info")          # a declared read: no stamp
    row("a declared read leaves no stamp", pawns.receipt.stamps == [], pawns.receipt.stamps)
    r = s.run(until=120, limit=400, speed="Normal")
    time.sleep(1.5)
    again = s.state                          # a second, independent reading, 1.5 s later
    row("a run of 120 ticks stops on its tick", r.hit and r.tick == t0 + 120, r)
    row("read again 1.5 s later: the same tick, paused", again.tick == t0 + 120 and again.paused is True, again)
    r2 = s.run(until=c.game.tick >= 10 ** 8, limit=60, speed="Ultrafast")
    row("a limit is a limit, at Ultrafast, on its tick", r2.why == "limit" and r2.hit is False and r2.tick == t0 + 180, r2)
    r3 = s.run(until=c.game.tick >= 1, limit=60)
    row("a condition that is true at the start plays no tick", r3.hit and r3.tick == t0 + 180 == s.state.tick, r3)
    refused = []
    for bad in (lambda: s.run(until=5), lambda: s.raw("rimworld/load_game", saveName="x"), lambda: s.raw("jawa/no_such_tool"), lambda: s.act):
        try:
            bad()
        except scene.Refused as e:
            refused.append(e.name)
    row("refusals are by name", refused == ["NO_LIMIT", "LIFE_CYCLE_TOOL", "UNKNOWN_TOOL", "NOT_BUILT"], refused)
    try:
        scene.open(GAME)
        second = "opened"
    except scene.Refused as e:
        second = e.name
    row("a second session on the game is refused", second in ("SESSION_OPEN", "GAME_HELD"), second)
    print("could not look: %s" % "; ".join(r.receipt.could_not_look), flush=True)
    print("run folder: %s" % s.run_dir, flush=True)
row("the session closed and put back", not [x for x in s.closed_report.did if x.startswith("NOT PUT BACK")], s.closed_report.did)
print("scene smoke run: %d of %d PASS" % (sum(ROWS), len(ROWS)))
sys.exit(0 if all(ROWS) else 1)
