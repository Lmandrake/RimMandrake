#!/usr/bin/env python3
"""Live proof of jawa/patch_switch on ArchSmall, a fresh quicktest with Explosive Knockback loaded.
Page: design/specs/2026-11-23-bridge-v2/boundary.md, section THE PATCH SWITCH.

    python.exe prove_patch_switch.py                 the rows on the Explosive Knockback job-override prefix
    python.exe prove_patch_switch.py --patch <id>    the rows on another patch id from action=list

The off step taints the game process until restart (the switch is an overlay entry of class PUT BACK).
It writes design/specs/2026-11-23-bridge-v2/live/mutants/patch_switch_result.md; its last line is
VERDICT PASS, VERDICT FAIL <rows> or VERDICT COULD NOT LOOK <why>.
Exit 0 = every row PASS, 1 = a FAIL, 2 = could not look.
"""
import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "Utils"))
import scene
from scene import cond as c

TOOL = "jawa/patch_switch"
MOD = "mandrake.rm.explosiveknockback"
# The proof target: a prefix on a method that every pawn's job tracker calls, so a short run reaches it.
WANT = "RimMandrake.ExplosiveKnockback.RM_Patch_JobTracker_KnockbackLandingNoSearch.Prefix"
CANONICAL = "ASHKARR_DEV_START_2026-10-20"  # the first name of JawaBenchCanonicalSaves.Names
REPO = Path(__file__).resolve().parents[3]
RESULT = REPO / "design/specs/2026-11-23-bridge-v2/live/mutants/patch_switch_result.md"
TICKS = 1200  # 20 game seconds: CheckForJobOverride runs many times per pawn in that span (to be confirmed by row 2)
ROWS = []


class CouldNotLook(Exception):
    pass


def row(name, ok, detail):
    ROWS.append((name, "PASS" if ok is True else "FAIL" if ok is False else "UNMEASURED", str(detail)[:400]))
    print("%-58s %-10s %s" % ROWS[-1], flush=True)


def proof(s, wanted):
    def call(**params):
        r = s.raw(TOOL, **params)
        if not isinstance(r, dict) or "success" not in r:
            raise CouldNotLook(f"{params.get('action')}: no reply shape: {r}")
        return r

    def ok(**params):
        r = call(**params)
        if r["success"] is not True:
            raise CouldNotLook(f"{params.get('action')}: {r.get('message')}")
        return r

    def counts():
        p = ok(action="count", patch=pid)["patch"]
        return p["patchCalls"], p["originalCalls"]

    def run():
        before = counts()
        if not s.run(c.ticks(TICKS), limit=TICKS).hit:
            raise CouldNotLook(f"{TICKS} ticks could not be run")
        after = counts()
        return after[0] - before[0], after[1] - before[1]

    listed = ok(action="list", mod=MOD)
    ours = listed["patches"]
    row("1 list shows at least 1 Explosive Knockback patch", len(ours) >= 1,
        f"{len(ours)} patches of {MOD}; jawaBenchPatches={listed['jawaBenchPatches']} otherPatches={listed['otherPatches']}")
    pick = [p for p in ours if p["id"] == wanted or p["patchMethod"] == wanted]
    if len(pick) != 1:
        raise CouldNotLook(f"{wanted} names {len(pick)} listed patches; ids: {[p['id'] for p in ours]}")
    target = pick[0]
    pid = target["id"]
    if target["kind"] == "transpiler" or target["originalsOfPatchMethod"] != 1 or target["offRefusal"] or target["state"] != "on":
        raise CouldNotLook(f"{pid} is not a countable patch of one original that is on: {target}")

    ok(action="arm_count", patch=pid)
    armed = run()
    if armed[1] <= 0:
        raise CouldNotLook(f"the original of {pid} did not run in {TICKS} ticks; pick another patch with --patch")
    row("2 after arm_count, ticks raise both counters", armed[0] > 0 and armed[1] > 0,
        f"patch +{armed[0]}, original +{armed[1]} in {TICKS} ticks (a patch counter at 0 means an inlined caller, E9)")

    off = call(action="off", patch=pid, driver=s.id)
    entries = (off.get("deviation") or {}).get("entries") or []
    mine = [e for e in entries if e.get("target") == pid]
    row("3a off succeeds and reads back off", off["success"] is True and off.get("state") == "off", off.get("message") or off.get("state"))
    row("5a the deviation record shows the entry as overlay PUT BACK process", len(mine) == 1 and mine[0].get("kind") == "overlay"
        and mine[0].get("class") == "PUT BACK" and mine[0].get("reach") == "process", mine or entries)
    again = call(action="off", patch=pid, driver=s.id)
    row("3b a second off is refused ALREADY_OFF", again["success"] is False and str(again.get("message")).startswith("ALREADY_OFF"), again.get("message"))
    gone = run()
    row("3c after off, the original counter rises and the patch counter does not", gone[0] == 0 and gone[1] > 0,
        f"patch +{gone[0]}, original +{gone[1]} in {TICKS} ticks")

    on = call(action="on", patch=pid, driver=s.id)
    row("4a on succeeds and reads back on", on["success"] is True and on.get("state") == "on", on.get("message") or on.get("state"))
    print(f"   order before off {on.get('orderBefore')}; after on {on.get('orderAfter')}; orderKept={on.get('orderKept')}")
    back = run()
    row("4b after on, both counters rise", back[0] > 0 and back[1] > 0, f"patch +{back[0]}, original +{back[1]} in {TICKS} ticks")
    receipt = on.get("deviation") or {}
    row("5b the entry is repaid and the receipt reads tainted", receipt.get("tainted") is True and receipt.get("clean") is False
        and not [e for e in receipt.get("entries") or [] if e.get("target") == pid], {k: receipt.get(k) for k in ("tainted", "clean", "overlay")})
    twice = call(action="on", patch=pid, driver=s.id)
    row("4c a second on is refused ALREADY_ON", twice["success"] is False and str(twice.get("message")).startswith("ALREADY_ON"), twice.get("message"))
    bench = call(action="off", patch="CountPatchPre", driver=s.id)
    row("4d a JawaBench patch is refused by name", bench["success"] is False and str(bench.get("message")).split(":")[0] in ("JAWABENCH", "AMBIGUOUS"),
        bench.get("message"))


def canonical_row():
    # The tool's own CANONICAL_SAVE refusal is the offline unit off-refusals: loading a canonical save to poke it is not allowed.
    # The live row reads the refusal that stands in front of it: a session on a canonical save does not open.
    try:
        scene.open("ArchSmall", needs={"map": CANONICAL}).close()
        got = "opened"
    except scene.Refused as e:
        got = e.name
    except scene.Fault as e:
        got = "fault " + e.name
    row("6 a canonical save is refused (scene layer; tool: unit off-refusals)", got == "CANONICAL_SAVE", got)


def write(verdict):
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    lines = ["# jawa/patch_switch live proof", "", "Written by src/RimMandrake/bridgetools/prove_patch_switch.py.", "",
             "| row | result | detail |", "|---|---|---|"]
    lines += ["| %s | %s | %s |" % (n, r, d.replace("|", "/").replace("\n", " ")) for n, r, d in ROWS]
    RESULT.write_text("\n".join(lines + ["", verdict, ""]))
    print(verdict)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--patch", default=WANT, help="a patch id or Type.Method from action=list")
    args = parser.parse_args()
    try:
        with scene.open("ArchSmall", needs={"map": "fresh:quicktest", "mods": ["ExplosiveKnockback"], "overlay": "none"}) as s:
            proof(s, args.patch)
        canonical_row()
    except (CouldNotLook, scene.CallFailed, scene.Refused, scene.Fault, OSError, KeyError, TypeError, ValueError) as exc:
        write(f"VERDICT COULD NOT LOOK {type(exc).__name__}: {str(exc)[:300]}")
        return 2
    bad = [n.split(" ")[0] for n, r, _ in ROWS if r != "PASS"]
    write("VERDICT PASS" if not bad else "VERDICT FAIL " + ",".join(bad))
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
