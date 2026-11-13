#!/usr/bin/env python3
"""RAILING_TOGGLE_FIX_KEEPS_DECONSTRUCT: paused player off/on, real designation and identity reads.

Run under Windows Python on a held bridge, after published DLL deploy and preflight.
Uses registered disposable calm save, guarded new scene-begin snapshot, exact rectangle/debug-settings restore.
No pawn scheduling/completed-deconstruction or full-list claim; no worldgen, canonical writes or art changes.
"""

import argparse
import hashlib
import json
from pathlib import Path
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
for p in (ROOT / "src/RimMandrake/Utils", ROOT / "src/RimMandrake/Utils/modcheck"):
    sys.path.insert(0, str(p))
SUSP = "RimMandrake.FlowWorks.Pits.RM_SuspensionProofs"
PRISON = "RimMandrake.FlowWorks.RM_PitPrisonProof"
RECT = "30,30,24,18"
RAIL = "RM_SuspensionRailing"


def require(ok, why):
    if not ok:
        raise AssertionError(why)


def run(B, T, saves, res, expected_sha):
    calls = res.setdefault("calls", [])

    def call(tool, **kw):
        r = B.call(tool, **kw)
        calls.append(dict(tool=tool, args=kw, result=r))
        require(isinstance(r, dict) and r.get("success") is not False, str((tool, r)))
        return r

    def sc(typ, method, arg):
        r = call("jawa/static_call", type=typ, method=method, args=arg)
        require("result" in r, "missing static result")
        text = str(r["result"])
        require(not text.startswith("REFUSED"), text)
        return text

    def rect():
        return sc(PRISON, "Rect", RECT)

    def flags():
        return {
            r["name"]: r["value"]
            for r in call("jawa/debug_settings", action="list")["fields"]
        }

    def rails():
        r = call("jawa/list_things", defName=RAIL, rect=RECT, limit=100)
        require(
            r.get("countMatched") == len(r.get("things", []))
            and r.get("isCompleteList") is True,
            "incomplete railing list",
        )
        return sorted(
            [
                {
                    k: t[k]
                    for k in ("id", "def", "x", "z", "spawned", "stuff", "hitPoints")
                }
                for t in r["things"]
            ],
            key=lambda t: t["id"],
        )

    def designations():
        r = call("jawa/designate_batch", action="query", limit=1000)
        require(
            r.get("truncated") is False and r.get("total") == len(r["designations"]),
            "incomplete designations",
        )
        return r

    def rail_marks(r):
        return sorted(
            (d["x"], d["z"])
            for d in r["designations"]
            if d["def"] == "Deconstruct"
            and d.get("thing") == RAIL
            and 30 <= d["x"] < 54
            and 30 <= d["z"] < 48
        )

    def controls(r):
        return sorted(
            (d["def"], d["x"], d["z"], d.get("thing") or "")
            for d in r["designations"]
            if d["def"] == "Plan"
            or (d["def"] == "Deconstruct" and d.get("thing") == "Wall")
        )

    def toggle(on):
        text = sc(SUSP, "ProofRails", "38,36;" + ("on" if on else "off") + ";player")
        span = sc(SUSP, "ProofSpan", "38,36")
        require(
            ("on=" + str(on)) in text and ("railings=" + str(on)) in span,
            "switch disagrees " + text + " " + span,
        )
        require(flags()["godMode"] is False, "player toggle leaked god mode")
        return dict(rails=text, span=span)

    res["identity"] = sc(PRISON, "Identity", "probe")
    require("sha256=" + expected_sha in res["identity"], "wrong loaded FlowWorks DLL")
    res["site"] = T.load_site(call, "calm")
    require(res["site"]["verified"], "calm load failed")
    old = flags()
    saved = False
    name = "WHITTLE_RailingToggle_Begin_" + time.strftime("%Y%m%dT%H%M%S")
    res["settings_before"] = old
    try:
        res["snapshot"] = T.save_site(call, name, saves)
        require(res["snapshot"].get("bytes", 0) > 0, "snapshot absent")
        saved = True
        require(
            T.load_site(call, "calm", name=name, check=False)["verified"],
            "begin reload failed",
        )
        call("rimworld/pause_game", pause=True)
        res["before"] = rect()
        call("jawa/set_roof_batch", ops="None:" + RECT)
        call("jawa/destroy_batch", rects=RECT, categories="All")
        sc(
            "RimMandrake.FlowWorks.RM_NorthstarProofs",
            "ProofResetRect",
            RECT.replace(",", ";"),
        )
        call("jawa/set_terrain_batch", ops="Soil:" + RECT)
        call("jawa/set_fog", action="unfog", rect=RECT)
        for x in range(37, 41):
            call(
                "jawa/flowworks_excavation_drive", x=x, z=36, deepenLevels=4, setBodyWaterM=0.0
            )
            d = call("jawa/flowworks_excavation_report", x=x, z=36)
            require(d.get("depth") == 4 and d.get("fill") == 0, "not dry D4")
        res["build"] = sc(SUSP, "ProofBuild", "36,36;41,36;timber;god")
        require(
            "ok=True" in res["build"] and "decks=4" in res["build"],
            "bridge fixture failed " + res["build"],
        )
        sc(SUSP, "ProofRails", "38,36;on")
        call("jawa/debug_settings", action="set", field="godMode", value=False)
        baseline = rails()
        require(
            len(baseline) == 4 and all(t["spawned"] and t["stuff"] for t in baseline),
            "four real stuffed railings required",
        )
        res["railings_before"] = baseline
        # Controls: Plan on a bridge cell, and a separate wall's Deconstruct. Neither belongs to the rail toggle.
        build = call(
            "jawa/build_batch", ops="Wall:48,40", faction="player", wipeExisting=False
        )
        require(build.get("placed") == 1, "control wall build failed")
        call("jawa/map_commit")
        call("jawa/designate_batch", action="add", designation="Plan", rect="38,36,1,1")
        call(
            "jawa/designate_batch",
            action="add",
            designation="Deconstruct",
            rect="48,40,1,1",
        )
        before = designations()
        ctrl = controls(before)
        require(
            ("Plan", 38, 36, "") in ctrl and ("Deconstruct", 48, 40, "Wall") in ctrl,
            "controls absent",
        )
        require(not rail_marks(before), "railings already marked")
        res["off"] = toggle(False)
        off = designations()
        res["designations_off"] = off
        expected = sorted((t["x"], t["z"]) for t in baseline)
        require(rail_marks(off) == expected, "off must mark each actual railing")
        require(rails() == baseline, "off changed railing identities/material/HP")
        # Capture the actual visible off designation marks before enabling again; game time remains paused.
        call("jawa/clear_ui")
        call(
            "rimworld/frame_cell_rect", x=34, z=33, width=17, height=10, paddingCells=1
        )
        time.sleep(1)
        res["off_screenshot"] = call(
            "jawa/take_screenshot",
            fileName="WHITTLE_RailingToggle_Off_" + time.strftime("%Y%m%dT%H%M%S"),
        )
        res["on"] = toggle(True)
        on = designations()
        res["designations_on"] = on
        require(not rail_marks(on), "on retained Deconstruct")
        require(rails() == baseline, "on replaced or removed railings")
        res["repeated_on"] = toggle(True)
        repeat = designations()
        res["designations_repeat"] = repeat
        require(not rail_marks(repeat) and rails() == baseline, "repeated on unsafe")
        require(
            controls(off) == controls(on) == controls(repeat) == ctrl,
            "unrelated designations changed",
        )
        require(
            off["ticksGame"] == on["ticksGame"] == repeat["ticksGame"],
            "before-work proof unexpectedly ticked",
        )
        res["railings_after"] = rails()
        res["staged_rect"] = rect()
        call("jawa/clear_ui")
        call(
            "rimworld/frame_cell_rect", x=34, z=33, width=17, height=10, paddingCells=1
        )
        time.sleep(1)
        res["screenshot"] = call(
            "jawa/take_screenshot",
            fileName="WHITTLE_RailingToggle_" + time.strftime("%Y%m%dT%H%M%S"),
        )
        res["assertions"] = (
            "real player off queues four Deconstruct; on/repeated on clear all; identical railing IDs/stuff/HP; Plan and wall Deconstruct unchanged; no ticks elapsed"
        )
    finally:
        errors = []
        res["restore"] = {}
        if saved:
            try:
                r = T.load_site(call, "calm", name=name, check=False)
                res["restore"]["load"] = r
                require(r["verified"], "restore reload failed")
                res["restore"]["rect"] = rect()
                require(
                    res["restore"]["rect"] == res.get("before"),
                    "restored rectangle differs",
                )
            except Exception as e:
                errors.append(repr(e))
        try:
            current = flags()
            for k, v in old.items():
                if current.get(k) != v:
                    call("jawa/debug_settings", action="set", field=k, value=v)
            res["restore"]["settings"] = flags()
            require(res["restore"]["settings"] == old, "debug settings differ")
        except Exception as e:
            errors.append(repr(e))
        res["restore"]["status"] = "FAIL" if errors else "PASS"
        require(not errors, "restoration failed " + str(errors))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    import validation_core as V
    import test_site_saves as T
    from game_paths import SAVES

    res = dict(script=__file__, mode="live", started=time.time())
    try:
        run(
            V.Bridge(),
            T,
            SAVES,
            res,
            hashlib.sha256(
                (HERE.parent / "Assemblies/RimMandrakeFlowWorks.dll").read_bytes()
            ).hexdigest(),
        )
        res["status"] = "PASS"
    except Exception as e:
        res.update(status="FAIL", error=repr(e))
    finally:
        res["finished"] = time.time()
        Path(a.out).write_text(json.dumps(res, indent=2, default=str), encoding="utf-8")
        print(res["status"], a.out, res.get("error", ""), flush=True)
    return 0 if res["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
