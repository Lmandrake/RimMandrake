"""Live proof of the scene library's promises about the game: the process mark, a driver that dies, a value that goes away in a
run, refusals that only a real game can give. Page: design/specs/2026-11-23-scene-library/boundary.md.

    python.exe prove_scene_mark.py              the rows; they MARK the game process EXPLORED until the game restarts
    python.exe prove_scene_mark.py --unmarked   one row, after a restart: the new process carries no stamp

Exit 0 = every row PASS, 1 = a FAIL, 2 = a row is UNMEASURED."""
import os
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Utils"))
import scene  # noqa: E402

c, GAME, ROWS = scene.cond, os.environ.get("SMOKE_GAME", "ArchSmall"), []
FRESH = {"map": "fresh:quicktest", "calm": "standard"}


def row(name, v, detail):
    ROWS.append("PASS" if v is True else "FAIL" if v is False else "UNMEASURED")
    print("%-62s %-10s %s" % (name, ROWS[-1], str(detail)[:500]), flush=True)


def refusal(**needs):
    try:
        scene.open(GAME, needs=needs).close()
        return "opened", ""
    except scene.Refused as e:
        return e.name, e.repair
    except scene.Fault as e:
        return "fault " + e.name, e.detail


def stamps_of_a_new_session():
    with scene.open(GAME) as s:
        return s.receipt.stamps


if sys.argv[1:] == ["--die"]:
    s = scene.open(GAME)
    print("DYING IN", s.id, flush=True)
    os._exit(9)

if sys.argv[1:] == ["--unmarked"]:
    with scene.open(GAME, needs=FRESH) as s:
        row("a restarted game carries no stamp", s.receipt.stamps == [], s.receipt.stamps)
else:
    for needs, want, word in (({"mods": ["Graffiti"]}, "MOD_NOT_LOADED", "Graffiti"), ({"map": "RM_NoSuchFixture"}, "FIXTURE_MISSING", "cp "),
                              ({"map": "ASHKARR_DEV_START_2026-10-20"}, "CANONICAL_SAVE", "canonical")):
        got = refusal(**needs)
        row("refused by the real game: %s" % want, got[0] == want and word in got[1], got)
    with scene.open(GAME, needs=FRESH) as s:
        before = s.receipt.stamps
        # a value that goes away inside a run: a fire on bare stone goes out by itself
        t = s.raw("jawa/set_terrain_batch", ops="PavedTile:20,20,5,5", layer="top")
        first = t.receipt.stamps
        s.raw("jawa/spawn_batch", ops="Fire:22,22")
        fires = s.raw("jawa/list_things", defName="Fire", rect="20,20,5,5").get("things") or []
        row("a changing raw call stamps EXPLORED at once", None if before else first == ["EXPLORED"], "before %s, after %s" % (before, first))
        r = s.raw("jawa/static_call", type="System.Environment", method="GetEnvironmentVariable", args=scene.GAME_STATE)
        row("a second reading: the mark is in the game's own process", '"EXPLORED"' in str(r.get("result")) and s.id in str(r.get("result")), r.get("result"))
        if not fires:
            row("a value that goes away ends the run as unknown", None, "no fire was made")
        else:
            fid = fires[0].get("id") or fires[0].get("thingId")
            run = s.run(until=c.value(fid, "fireSize") < -1, limit=5000, speed="Superfast", record=[c.track(fid, "fireSize")])
            row("a value that goes away ends the run as unknown", run.why == "unknown" and run.tick < run.tick_from + 5000, run)
            v = run.values["%s.fireSize" % fid]
            row("the gone value has a state and no number", v.state == "gone", v)
            try:
                hit = run.hit
            except scene.Fault as e:
                hit = e.name
            row("r.hit of an unknown run raises", hit == "CONDITION_UNKNOWN", hit)
        row("a run in a marked process carries the stamp", s.run(until=10, limit=50).receipt.stamps == ["EXPLORED"], "")
    row("a new session in the marked process carries the stamp", stamps_of_a_new_session() == ["EXPLORED"], "")
    p = subprocess.run([sys.executable, os.path.abspath(__file__), "--die"], capture_output=True, text=True, timeout=300)
    row("a driver was killed in an open session", "DYING IN" in p.stdout and p.returncode == 9, p.stdout + p.stderr[-200:])
    got = refusal()
    row("the dead driver's session is found, and its driver is dead", got[0] == "SESSION_OPEN" and "is dead" in got[1], got)
    rc = scene.main(["end-session", GAME])
    row("end-session ends it, and the mark stays", rc == 0 and stamps_of_a_new_session() == ["EXPLORED"], rc)
print("scene mark: %d PASS, %d FAIL, %d UNMEASURED" % tuple(ROWS.count(x) for x in ("PASS", "FAIL", "UNMEASURED")))
sys.exit(1 if "FAIL" in ROWS else 2 if "UNMEASURED" in ROWS else 0)
