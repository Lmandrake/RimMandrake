#!/usr/bin/env python3
"""prove_beskar_armorer.py -- BESKAR_ARMORER_QUEST_1's functional script, one verdict per criterion.

    python3 src/RimUtinni/BeskarArmorer/prove_beskar_armorer.py          offline: L2 (static half) and L3
    python3 src/RimUtinni/BeskarArmorer/prove_beskar_armorer.py --live   L2 (log) and L4..L10, game loaded with the mod

--live needs the bridge held, the deployed mod current, and a list holding the mod (modset_builder tier beskar_armorer). It starts a
quicktest colony if none is up and refuses the canonical save by never loading one. The hands are the debug actions in
Source/ArmorerProbe.cs; each writes its rows to <save data>/BeskarArmorerProbe.jsonl, and this script joins them to the criteria. A
criterion with no row, or with any failing row, is not a PASS: it exits nonzero. Results go to the JSON path it prints.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
UTILS = os.path.join(REPO, "src", "RimMandrake", "Utils")
sys.path.insert(0, UTILS)
LOCALLOW = "/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios"
PROBE = os.path.join(LOCALLOW, "BeskarArmorerProbe.jsonl")
WIN_PROBE = os.path.expandvars(r"%USERPROFILE%\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\BeskarArmorerProbe.jsonl")
PLAYER_LOG = os.path.join(LOCALLOW, "Player.log")
OUT = "/mnt/d/ClaudeWork/rimmandrake/scratch/beskar_armorer_proof.json"
CRITERIA = {
    "L4": ["L4.other_pawn_no_quest", "L4.hunter_is_prisoner", "L4.quest_offered", "L4.no_covert_yet", "L4.delay_2_to_5_days",
           "L4.covert_on_orbit", "L4.quest_success", "L4.three_pawns", "L4.gravship_gate"],
    "L5": ["gravship.built", "gravship.gate_open", "gravship.landed", "L5.recipes_listed", "L5.melt_mass_read", "L5.colonist_refused_melt", "L5.colonist_refused_reforge",
           "L5.armorer_allowed", "L5.melted_4_in_5", "L5.reforged"],
    "L6": ["L6.mando_recipes_gone", "L6.stuff_bill_refuses_beskar", "L6.stuff_bill_takes_steel", "L6.smelter_bill_takes_beskar_gear",
           "L6.gear_smeltable", "L6.smelt_steel_slag"],
    "L7": ["visit.map", "cast.same_three", "leave.map_removable_object_stays", "leave.object_survives", "gravship.back_home",
           "gravship.map_discarded_object_stays"],
    "L8": ["L8.neutral_until_harm", "L8.hostile_after", "L8.object_stays_during_visit", "L8.gone_on_departure", "L8.reveal_refused_after_loss",
           "L8.route1_refused_after_loss", "L8.route2_refused_after_loss"]
          + ["L8.%s.%s" % (h, k) for h in ("guard", "building", "forge", "capture", "kill") for k in ("lost", "heat_max", "raid")],
    "L9": ["L9.not_before_day_30", "L9.not_while_revealed", "L9.not_while_lost", "L9.offered", "L9.site_is_empire", "L9.map_made",
           "L9.detainee_with_you", "L9.no_heat_yet", "L9.plate_in_locker", "L9.large_heat", "L9.pursuit_delay_running", "L9.pursuit_raid",
           "L9.covert_revealed", "L9.quest_success", "L9.he_went_home", "L9.heat_tool_reads_it", "L9.death_fails", "L9.death_no_covert", "L9.timeout_armed", "L9.timeout_fails"],
    "L10": ["L10.route1_off", "L10.route2_off", "L10.harm_raid_off", "L10.mod_off_no_gate", "L10.mod_off_no_quest", "L10.mod_off_smelt_is_not_ours"],
}


def offline():
    fails = []
    r = subprocess.run([sys.executable, os.path.join(REPO, "skills", "rimworld-quests", "scripts", "validate_quest.py"),
                        "--dir", os.path.join(HERE, "Defs", "QuestScriptDefs")], capture_output=True, text=True)
    print("L2 validate_quest:", r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr[-200:])
    if r.returncode or "0 error(s)" not in r.stdout or "2 QuestScriptDef(s)" not in r.stdout:
        fails.append("L2 validate_quest")
    r = subprocess.run([sys.executable, os.path.join(HERE, "validation.py")], capture_output=True, text=True)
    print("L2 static:", r.stdout.strip()[:300])
    if r.returncode:
        fails.append("L2 mod_static")
    r = subprocess.run([sys.executable, os.path.join(UTILS, "selftest_beskar_armorer.py")], capture_output=True, text=True)
    last = (r.stdout.strip().splitlines() or ["no output"])[-1]
    print("L3 selftests:", last)
    if r.returncode or not last.startswith("PASS"):
        fails.append("L3 selftests")
    return fails


class Game:
    def __init__(self):
        import rimbridge_client as rb
        for attempt in range(40):          # the bridge binds some way into the load, and writes its token file then
            try:
                host, port, token = rb.resolve_endpoint()
                self.s = rb.RimBridge(host=host, port=port, token=token, timeout=280.0)
                self.s.connect()
                break
            except rb.RimBridgeError:
                if attempt == 39:
                    raise
                time.sleep(5)

    def call(self, t, **p):
        r = self.s.call(t, p) or {}
        if isinstance(r, dict) and r.get("content"):
            try:
                r = json.loads(r["content"][0]["text"])
            except ValueError:
                pass
        return r

    def act(self, name):
        r = self.call("rimworld/execute_debug_action", path="Actions\\" + name)
        if isinstance(r, dict) and r.get("success") is False:
            print("  action refused:", name, str(r)[:200])
        return r

    def ticks(self, n):
        self.call("rimworld/step_game_ticks", ticks=n)


STEPS = ["Probe reset", "Probe L4 route one", 120, "Probe L4 read", "Probe L6 colony benches",
         "Probe visit by map path", "Probe L5 forge setup", "WAIT_REFORGE", "Probe L5 read", "Probe cast read", "Probe leave",
         "Probe visit by map path", "Probe leave", "Probe visit by map path", "Probe leave",
         "Probe L8 fresh covert", "Probe L8 harm guard", "Probe L8 fresh covert", "Probe L8 harm building",
         "Probe L8 fresh covert", "Probe L8 harm forge", "Probe L8 fresh covert", "Probe L8 harm capture",
         "Probe L8 fresh covert", "Probe L8 harm killed",
         "Probe L9 offer", 120, "Probe L9 breakout", 240, "Probe L9 out read", 120, "Probe L9 done read", "HEAT_TOOL",
         "Probe L9 failure paths", 240, "Probe L9 death read", 120, "Probe L9 timeout read", "Probe L10 toggles", "Probe gravship build"]


def drive():
    """Runs under Windows Python: RimBridge binds Windows loopback, and WSL2 cannot reach it."""
    t0 = time.time()
    g = Game()
    st = g.call("rimworld/get_game_info")
    print("game:", str(st)[:160])
    if st.get("status") != "game_loaded":
        g.call("rimworld/start_debug_game_ready", timeoutMs=250000)
        for _ in range(60):
            if g.call("rimworld/get_ui_state").get("programState") == "Playing":
                break
            time.sleep(2)
    for s in STEPS:
        if isinstance(s, int):
            g.ticks(s)
        elif s == "WAIT_REFORGE":
            wait_reforge(g)
        elif s == "HEAT_TOOL":
            heat_tool(g)
        else:
            print("  ", s, flush=True)
            g.act(s)
    print("  flying from %.0f s" % (time.time() - t0), flush=True)
    for leg in ("Probe gravship launch out", "Probe gravship read covert", "Probe gravship launch home", "Probe gravship read home",
                "Probe gravship launch out", "Probe gravship read covert"):
        if "read" in leg:
            g.act(leg)
            continue
        print("  ", leg, flush=True)
        g.act(leg)
        fly(g)
    print("  driven in %.0f s" % (time.time() - t0), flush=True)


def probe_rows(path=None):
    with open(path or WIN_PROBE) as f:
        return [json.loads(line) for line in f if line.strip()]


def wait_reforge(g):
    """step_game_ticks gives back what the frame budget allowed, not the ticks asked: poll the bills, never count on a tick total."""
    for _ in range(30):
        g.ticks(600)
        g.act("Probe L5 status")
        st = [r for r in probe_rows() if r["row"] == "L5.status"]
        if st and "meltLeft=0 reforgeLeft=0" in st[-1]["detail"]:
            return


def heat_tool(g):
    """Spec 6: the bridge read the blackboard takes, against the rows the game holds. Written as a probe row, from this side."""
    r = g.call("jawa/heat_events")
    ev = r.get("events") or []
    ok = r.get("modLoaded") is True and any(e["amount"] == 30 and e["faction"] == "Empire" for e in ev)
    with open(WIN_PROBE, "a") as f:
        f.write(json.dumps({"row": "L9.heat_tool_reads_it", "pass": ok, "detail": str(ev)[:300]}) + "\n")


def fly(g):
    """The cutscene runs on wall clock, travel on ticks: alternate until the marker waits, then confirm."""
    for _ in range(60):
        st = g.call("jawa/gravship_status")
        print("     state cutscene=%s travelling=%s landing=%s" % (st.get("cutsceneInProgress"), st.get("travelling"), st.get("landingConfirmationPending")), flush=True)
        if st.get("landingConfirmationPending"):
            g.act("Probe gravship pick spot")
            print("     land:", str(g.call("jawa/gravship_land"))[:200], flush=True)
            time.sleep(3)
            g.ticks(120)
            return
        g.ticks(900)
        if st.get("cutsceneInProgress"):
            time.sleep(1)
    print("     NEVER LANDED", flush=True)


def win_python():
    for p in ("python.exe", "/mnt/c/Users/Mandrake/AppData/Local/Microsoft/WindowsApps/python.exe"):
        if shutil.which(p) or os.path.exists(p):
            return p
    sys.exit("no Windows python found; the bridge cannot be reached from WSL")


def generator_log():
    """L2's live half: both startup lines are present and no error line names this mod's defs. A log with neither line is UNMEASURED."""
    with open(PLAYER_LOG, errors="replace") as f:
        lines = f.read().splitlines()
    gen = [l for l in lines if l.startswith("[BeskarArmorer] generated ")]
    patched = [l for l in lines if l.startswith("[BeskarArmorer] Harmony: patched ")]
    errs = [l for l in lines if any(w in l for w in ("RM_Reforge_", "RM_Armorer", "RM_Quest_Armorer", "RM_Quest_ImperialPrisonBreak", "RM_ImperialDetentionPost"))
            and any(w in l for w in ("rror", "xception", "Could not"))]
    if not gen or not patched:
        return "UNMEASURED", "startup lines not in the log"
    ok = not errs and patched[-1].endswith("missing 0") and " 0 reforge" not in gen[-1]
    return ("PASS" if ok else "FAIL"), "; ".join([gen[-1], patched[-1]] + errs[:5])


def live():
    me = subprocess.run(["wslpath", "-w", os.path.abspath(__file__)], capture_output=True, text=True).stdout.strip()
    r = subprocess.run([win_python(), me, "--drive"], timeout=525)
    if r.returncode:
        return ["drive"]
    rows = {}
    with open(PROBE) as f:
        for line in f:
            r = json.loads(line)
            rows.setdefault(r["row"], []).append(r)
    verdicts, bad = {}, []
    for crit, want in CRITERIA.items():
        missing = [w for w in want if w not in rows]
        failing = [r["row"] + ": " + r["detail"] for w in want for r in rows.get(w, []) if not r["pass"]]
        verdicts[crit] = "UNMEASURED" if missing and not failing else ("FAIL" if failing else "PASS")
        print(crit, verdicts[crit], "; ".join(failing + ["missing " + m for m in missing])[:1500])
        if verdicts[crit] != "PASS":
            bad.append(crit)
    verdicts["L2"], detail = generator_log()
    print("L2", verdicts["L2"], detail[:500])
    if verdicts["L2"] != "PASS":
        bad.append("L2")
    stray = [r["row"] + ": " + r["detail"] for rs in rows.values() for r in rs if not r["pass"] and not any(r["row"] in w for w in CRITERIA.values())]
    for s in stray:
        print("STRAY", s[:400])
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        json.dump({"verdicts": verdicts, "rows": rows, "at": time.strftime("%Y-%m-%dT%H:%M:%S")}, f, indent=1)
    print("rows ->", OUT)
    return bad + (["stray"] if stray else [])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--live", action="store_true")
    ap.add_argument("--drive", action="store_true", help="internal: the Windows-Python half of --live")
    a = ap.parse_args()
    if a.drive:
        return drive() or 0
    bad = live() if a.live else offline()
    print("FAIL: %s" % bad if bad else "PASS")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
