#!/usr/bin/env python3
"""THROWAWAY (steward run RIMMANDRAKE_STEWARD_EXPLOSIVEKNOCKBACK_PREFLIGHT_STAGE, 2026-11-24): carry ExplosiveKnockback's
test-and-stage table from 0.1.0 (59 bars) to 0.2.0 (73 bars). The 59 rows of 0.1.0 stay as they are. Each of the 14 new
bars (VERSION.json bars_new) gets its deciding tests as its own record.json `proof_note` names them: a transcription of
the Designer's words, not a new placement. Every new test is `new: true` (specified; Stage 3 builds it, red first).
Usage: python3 extend_test_table_0_2_0.py <repo>   rewrites version/test_table.json and version/test_table.md.
Idempotent: a second run changes nothing but the measured runs_today of the built new tests.

Stage 3 (RIMMANDRAKE_AUTOBUILD_EXPLOSIVEKNOCKBACK_FOURTEEN_BARS_LEFT, 2026-11-24): a new test leaves `new: true` only when
its builder names it in BUILT below, with the evidence the maker reads (a line its run prints, or the scene file it
writes). The maker then MEASURES it: it runs a built offline test and records rc and seconds; it records a built live
scene UNRUN with its exact command and entry_exists true. A bar's every_decider_runnable_today is the pipeline's own rule
(maturation._bar_lines, make_test_table.py): each decider ran today, or is an in-game entry written and recorded UNRUN.
The first form of this file asked each decider to be `not new` and PASS, which no in-game scene can be offline: no 0.2.0
bar could ever read runnable."""
import datetime
import json
import os
import shlex
import subprocess
import sys
import time

REPO = os.path.abspath(sys.argv[1]); os.chdir(REPO)
C = "design/concepts/ExplosiveKnockback"; M = "src/RimMandrake/ExplosiveKnockback"
PROOF = M + "/Source/RM_KnockbackProof.cs"; MATH = M + "/Source/RM_KnockbackMath.cs"
MC = M + "/Source/RM_MapComponent_Knockback.cs"; MOD = M + "/Source/RM_KnockbackMod.cs"
PROG = M + "/Source/SelfTest/Program.cs"; KERNEL = M + "/selftest_explosiveknockback_kernel.py"
SCENES = C + "/scenes.json"; BLAST_SPEC = "design/specs/2026-11-24-knockback-blast-show/design.md"
ART = "design/RimMandrake/art_judge_brief.md"
FLING = "RIMMANDRAKE_FLING_KNOCKBACK_CARRY_ON_OWN_ARC"; BRUISE = "RIMMANDRAKE_BRUISE_KNOCKBACK_LANDING_ON_PAWN"
ABSORB = "RIMMANDRAKE_ABSORB_EXTRA_EXPLOSION_EFFECTS_OWN_FLECKS"
FOLD = "RIMMANDRAKE_FOLD_KNOCKBACK_POLISH_LINES_INTO_ZERO_TWO_THREE_JUDGED_IN"
NOTRUN = {"ran": False, "why": "specified for 0.2.0, not built: Stage 3 builds it, red first"}


def off(tid, file, observes, reads, item, marker=None):
    t = dict(id=tid, kind="offline", stage="4-5", file=file, new=True, item=item, observes=observes, reads=reads,
             command="python3 " + file, runs_today=NOTRUN)
    if marker:
        t["marker"] = marker
    return t


def live(tid, entry, observes, why_game, item, scene=None, reads=()):
    return dict(id=tid, kind="live_minimal", stage="6", file=PROOF, entry=entry, new=True, item=item,
                scene=scene or tid, observes=observes, reads=[PROOF, SCENES, MC] + list(reads), why_game=why_game,
                why_full_list=None, entry_exists=False, partial=None, runs_today=NOTRUN)


BS = "sc_blast_show"
BS_SCENE = M + "/proof/scene_blast_show.py"
# test id -> what shows it is built: ("prints", <text its run prints>) or ("scene", <the scene file>). Each Stage 3 batch
# adds the tests it built; nothing else leaves `new: true`.
BUILT = {
    "T_BLAST_SHOW_OFFLINE": ("prints", " blast show: "),
    BS: ("scene", BS_SCENE),
    # RIMMANDRAKE_AUTOBUILD_EXPLOSIVEKNOCKBACK_SIX_BARS_LEFT (2026-11-24): the six bars left
    "T_KERNEL_CARRY_OWN_PLAN": ("prints", "K_CARRY_OWN_PLAN sweep: "),
    "T_KERNEL_COLLISION_BRUISE": ("prints", "K_COLLISION_BRUISE sweep: "),
    "T_KERNEL_GAS_COVER_SHOVE": ("prints", "K_GAS_COVER_SHOVE sweep: "),
    "T_KERNEL_NO_CONTACT": ("prints", "K_NO_CONTACT sweep: "),
    "T_CARRY_STATIC": ("prints", " carry static: "),
    "T_SETTINGS_SWEEP_SHOW": ("prints", " settings sweep show: "),
}
# the live scenes of the six bars: each on the scene library (CLAUDE.md: scenes and verdicts stay in Python), its own file
SCENES6 = {
    "sc_pawn_arc_carried_thing": "scene_pawn_arc_carried_thing.py",
    "sc_pawn_arc_bruise_sizes": "scene_pawn_arc_bruise_sizes.py",
    "sc_pawn_arc_sandbag_no_contact": "scene_pawn_arc_sandbag_no_contact.py",
    "sc_gas_chain_pawn_on_cover": "scene_gas_chain_pawn_on_cover.py",
    "sc_storeroom_mortar_rebound_legs": "scene_storeroom_mortar_rebound_legs.py",
    "sc_settings_sweep_show_switches": "scene_settings_sweep_show_switches.py",
}
for _tid, _f in SCENES6.items():
    BUILT[_tid] = ("scene", M + "/proof/" + _f)
# the settings sweep's file holds two deciders, one half each (an unbuilt show part must not turn the 0.1.0 half red)
HALF = {"T_SETTINGS_SWEEP_OFFLINE": "offline", "T_SETTINGS_SWEEP_SHOW": "show"}
BS_WHY = ("the blast's look is drawn by the game (flecks, camera, paint, overlays, weather); only a live frame shows "
          "what the player sees, and the look itself is the art judge's call (%s)" % ART)
JUDGED = "; each capture goes to the art judge (%s), whose keep is part of this verdict" % ART
TESTS = [
    off("T_KERNEL_CARRY_OWN_PLAN", KERNEL,
        "kernel case K_CARRY_OWN_PLAN: a thrown colonist's carried thing gets a flight plan of its own, apart from the "
        "colonist's; a carried thing too heavy to fly lands on the colonist's start cell; a colonist carrying nothing "
        "plans as before", [MATH, PROG], FLING, marker="K_CARRY_OWN_PLAN"),
    off("T_CARRY_STATIC", M + "/selftest_explosiveknockback_carry_static.py",
        "static: the pawn throw no longer flies with its carried thing (no MakeFlyer(..., flyWithCarriedThing: true) "
        "on the throw path of RM_MapComponent_Knockback.cs)", [MC], FLING),
    off("T_KERNEL_COLLISION_BRUISE", KERNEL,
        "kernel case K_COLLISION_BRUISE over pairs of masses: a thrown pawn landing on a pawn bruises it by their sizes "
        "(a small one on a large one is a light bruise, a large one on a small one a heavy one)", [MATH, PROG], BRUISE,
        marker="K_COLLISION_BRUISE"),
    off("T_KERNEL_GAS_COVER_SHOVE", KERNEL,
        "a kernel case: a pawn on a covered superdeep cell under a gas burst is shoved one cell, as on any floor",
        [MATH, PROG], FOLD),
    off("T_KERNEL_NO_CONTACT", KERNEL,
        "a kernel case lane | sandbag | pawn: a throw stopped by the sandbag gives the pawn beyond it no hit and no "
        "bruise", [MATH, PROG], FOLD),
    off("T_BLAST_SHOW_OFFLINE", M + "/selftest_explosiveknockback_blast_show.py",
        "the blast show's structure, grown from proof/absorb_blast_show_check.py: our own flecks with our own art, the "
        "explosion hook, one saved on/off per part with its default on, the strength scaled by the blast's damage, and "
        "no donor mod named (%s)" % BLAST_SPEC, [M + "/proof/absorb_blast_show_check.py", MOD, BLAST_SPEC], ABSORB),
    off("T_SETTINGS_SWEEP_SHOW", M + "/selftest_explosiveknockback_settings_sweep.py",
        "the settings sweep gains the show's switches: each switch off changes only its own part, and every switch off "
        "gives the unmodded look of a blast with the throw unchanged", [MOD, SCENES], ABSORB),
    live("sc_pawn_arc_carried_thing", "pawn_arc",
         "a revised sc_pawn_arc lane: a colonist carrying a stack is thrown; two things fly on two paths, the stack "
         "lands where its own flight ends with no loss and no copy, the colonist lands empty-handed; a too-heavy "
         "stack drops where the colonist stood; a colonist carrying nothing flies as before",
         "two real flyers (the pawn's and the thing's) and the haul state of a real pawn", FLING, "sc_pawn_arc"),
    live("sc_pawn_arc_bruise_sizes", "pawn_arc",
         "a revised sc_pawn_arc lane with a small and a large second pawn: the landing bruises each by size",
         "a real landing on a real pawn and the injury the game records on it", BRUISE, "sc_pawn_arc"),
    live("sc_pawn_arc_sandbag_no_contact", "pawn_arc",
         "a revised sc_pawn_arc lane: a pawn behind a sandbag the throw cannot cross takes no impact and no bruise",
         "a real sandbag stopping a real flight, and the pawn beyond it read for injuries", FOLD, "sc_pawn_arc"),
    live("sc_gas_chain_pawn_on_cover", "gas_chain",
         "a lane of sc_gas_chain: a colonist on an intact pit cover is shoved one cell by a gas burst",
         "a real gas burst over a real FlowWorks pit cover", FOLD, "sc_gas_chain"),
    live("sc_storeroom_mortar_rebound_legs", "storeroom_mortar",
         "sc_storeroom_mortar's trace: each rebound leg of a thrown good is shorter than the leg before, until it rests",
         "the legs of real thing flights off real walls and doors", FOLD, "sc_storeroom_mortar"),
    dict(live(BS, "blast_show",
         "one grenade and one mortar shell on soil and on stone: fire and flash; camera shake after a small and a big "
         "blast at the same distance and with the slider at none; the air ring over a tiled floor; smoke at three times "
         "in still air and in wind with the thrown colonist visible in each; the scar after the blast, after a day and "
         "after cleaning; the paint of a wall, a door, a table and a floor cell inside and outside the blast and after "
         "the paint is removed; the soot of a colonist and an animal in the blast and of one outside it, then after "
         "rain; a grenade and an antigrain-class blast on two like pads, each part compared" + JUDGED,
         BS_WHY, ABSORB, reads=[BLAST_SPEC, ART]),
         # a scene on the scene library (CLAUDE.md: scenes and verdicts stay in Python), not a C# proof entry
         file=BS_SCENE, entry="scene_blast_show.py",
         command="python.exe src\\RimMandrake\\Utils\\scene.py accept src\\RimMandrake\\ExplosiveKnockback\\proof\\scene_blast_show.py"),
    live("sc_settings_sweep_show_switches", "settings_sweep",
         "sc_settings_sweep with each show switch off in turn, and a throw compared show-on against show-off",
         "the drawn look of a real blast with each switch off, and the throw beside it", ABSORB, "sc_settings_sweep"),
]
SHOW_PARTS = ["blast_show_fire_and_flash", "blast_show_screen_shake", "blast_show_air_ripple", "blast_show_smoke",
              "blast_show_crater_scar", "blast_show_soot_on_things", "blast_show_soot_on_pawns",
              "blast_show_scales_with_damage"]
DECIDES = {
    "carried_thing_own_arc": (["T_KERNEL_CARRY_OWN_PLAN", "T_CARRY_STATIC", "sc_pawn_arc_carried_thing"], []),
    "collision_bruise_by_size": (["T_KERNEL_COLLISION_BRUISE", "sc_pawn_arc_bruise_sizes"], []),
    "gas_shoves_pawn_on_pit_cover": (["T_KERNEL_GAS_COVER_SHOVE", "sc_gas_chain_pawn_on_cover"], []),
    "no_impact_without_contact": (["T_KERNEL_NO_CONTACT", "sc_pawn_arc_sandbag_no_contact"], []),
    "rebound_goes_shorter": (["T_KERNEL", "sc_storeroom_mortar_rebound_legs"], []),
    "blast_show_switches_off_clean": (["T_BLAST_SHOW_OFFLINE", "T_SETTINGS_SWEEP_SHOW",
                                       "sc_settings_sweep_show_switches"], ["T_SETTINGS_SWEEP_OFFLINE"]),
}
for p in SHOW_PARTS:
    DECIDES[p] = (["T_BLAST_SHOW_OFFLINE", BS], [])

def measure(t):
    """Fill a new test's runs_today from what is built (BUILT), measured now; an unbuilt one stays NOTRUN."""
    how = BUILT.get(t["id"])
    if not how:
        return
    kind, ev = how
    if t["kind"] == "offline":
        if not os.path.isfile(t["file"]):
            t["runs_today"] = dict(ran=False, why="named built, but %s does not exist" % t["file"])
            return
        t0 = time.time()
        # the table's own command, as the pipeline runs it (a file run bare missed a --half)
        r = subprocess.run(shlex.split(t["command"]), capture_output=True, text=True, stdin=subprocess.DEVNULL)
        out = (r.stdout or "") + (r.stderr or "")
        last = (out.strip().splitlines() or [""])[-1][:300]
        if ev not in out:
            t["runs_today"] = dict(ran=False, why="ran but printed no %r: not the built test (rc %d, last %r)" % (ev, r.returncode, last))
            return
        t.pop("new", None)
        t["runs_today"] = dict(ran=True, rc=r.returncode, seconds=round(time.time() - t0, 1), last=last,
                               at=datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
                               result="PASS" if r.returncode == 0 else "FAIL", command=t["command"])
    else:
        if not os.path.isfile(ev):
            t["runs_today"] = dict(ran=False, why="named built, but the scene %s does not exist" % ev)
            return
        t.pop("new", None)
        t["entry_exists"] = True
        t["runs_today"] = dict(ran=False, entry_exists=True, why="live: UNRUN until Stage 6; command: " + t["command"])
        # a builder's live run (maturation.py live-row, version/in_game/early_rows.jsonl) is this check's last run: Stage 6
        # reads it as a row of the next visit (build_match.early_rows); the table shows it, newest row of the check
        early = os.path.join(C, "version/in_game/early_rows.jsonl")
        rows = [json.loads(x) for x in open(early) if x.strip()] if os.path.isfile(early) else []
        mine = [r for r in rows if r.get("test") == t["id"]]
        if mine:
            r = mine[-1]
            t["runs_today"] = dict(ran=True, entry_exists=True, result=r.get("verdict"), outcome=r.get("outcome"),
                                   at=r.get("at"), game=r.get("game"), instance=r.get("instance"), mod_sha=r.get("mod_sha"),
                                   evidence=r.get("evidence"), command=t["command"], early_row=True)


def runnable(t):
    """The pipeline's own rule (maturation._bar_lines): ran today, or an in-game entry written and recorded UNRUN."""
    r = t.get("runs_today") or {}
    return bool(r.get("ran") or r.get("entry_exists") or (t["kind"] != "offline" and t.get("entry_exists") and t.get("command")))


tab = json.load(open(C + "/version/test_table.json"))
ver = json.load(open(C + "/version/VERSION.json"))
assert sorted(DECIDES) == sorted(ver["bars_new"]), "the placement does not cover bars_new exactly"
tests, bars = tab["tests"], tab["bars"]
for t in TESTS:
    if t["id"] == BS:
        t["cheaper_why"] = ("every part of the show is drawn by the same blast, at the same moment, on the same pads: one "
                            "staged grenade and one mortar shell show all eight parts in one set of frames, and a scene "
                            "per part would stage the same blasts eight times over for the same reading; the scene "
                            "holds one claim per part, each read and judged apart, so one part's fault names that part")
    if t["id"] == BS:
        t["reads"] = [BS_SCENE if r == PROOF else r for r in t["reads"]] + [M + "/Source/RM_KnockbackShow.cs"]
    if t["id"] in SCENES6:
        f = M + "/proof/" + SCENES6[t["id"]]
        t.update(file=f, entry=SCENES6[t["id"]], reads=[f if r == PROOF else r for r in t["reads"]],
                 command="python.exe src\\RimMandrake\\Utils\\scene.py accept " + f.replace("/", "\\"))
    if t["id"] in HALF:
        t["command"] = "python3 %s --half %s" % (t["file"], HALF[t["id"]])
    if t["id"] in ("T_KERNEL_CARRY_OWN_PLAN", "T_KERNEL_COLLISION_BRUISE", "T_KERNEL_GAS_COVER_SHOVE", "T_KERNEL_NO_CONTACT"):
        t["reads"] = t["reads"] + [M + "/Source/RM_KnockbackPlan.cs", M + "/Source/SelfTest/KnockbackMap.cs"]
    if t["id"] == "T_CARRY_STATIC":
        t["reads"] = t["reads"] + [M + "/Source/RM_ThingFlyer_Knockback.cs"]
    measure(t)
    tests[t["id"]] = t
# the 0.1.0 half of the settings sweep keeps its own command (its row is the 0.1.0 maker's; only the command moves)
if "T_SETTINGS_SWEEP_OFFLINE" in tests:
    tests["T_SETTINGS_SWEEP_OFFLINE"]["command"] = "python3 %s --half offline" % tests["T_SETTINGS_SWEEP_OFFLINE"]["file"]
have = {b["id"] for b in bars}
for bid in ver["bars_new"]:
    dec, sup = DECIDES[bid]
    for x in dec + sup:
        assert x in tests, x
    offd = [x for x in dec if tests[x]["kind"] == "offline"]
    row = dict(id=bid, source="record.json", kind="inventory",
               proves_at=max((tests[x]["stage"] for x in dec), key=lambda s: {"2": 2, "4-5": 4, "6": 6, "8": 8}[s]),
               decides=dec, supports=sup, held=[], offline_decides=offd,
               offline_green_today=bool(offd) and all(tests[x].get("runs_today", {}).get("result") == "PASS" for x in offd),
               every_decider_runnable_today=all(runnable(tests[x]) for x in dec),
               any_test_runnable_today=any(runnable(tests[x]) for x in dec + sup))
    if bid in have:
        bars[[b["id"] for b in bars].index(bid)] = row
    else:
        bars.append(row)
tab["version"] = ver["version"]
tab["made_0_2_0"] = dict(at=datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
                         by="steward run RIMMANDRAKE_STEWARD_EXPLOSIVEKNOCKBACK_PREFLIGHT_STAGE "
                            "(version/pilot_throwaway/extend_test_table_0_2_0.py)",
                         what="the 59 rows of 0.1.0 kept; the 14 bars of 0.2.0 added with the deciders their "
                              "record.json proof_note names, each new test specified (new: true) for Stage 3; a test a Stage 3 "
                              "batch built (BUILT) is measured now and leaves new: true",
                         built=sorted(BUILT))
json.dump(tab, open(C + "/version/test_table.json", "w"), indent=1)

# the read view: the 0.1.0 view stays below a 0.2.0 head and section
md = open(C + "/version/test_table.md").read()
cut = md.find("\n---\n# Explosive Knockback 0.1.0")
old = md[cut + 5:] if cut >= 0 else md
L = ["# Explosive Knockback 0.2.0: test-and-stage table", "",
     "Generated %s from `test_table.json` (the record; this is its read view) by "
     "`version/pilot_throwaway/extend_test_table_0_2_0.py`. 0.2.0 keeps the 59 bars of 0.1.0 (their rows are below, as "
     "0.1.0 left them) and adds 14. A bar passes when every deciding test passes." % tab["made_0_2_0"]["at"], "",
     "## Counts (measured)", "", "- bars: %d" % len(bars),
     "- with every deciding test runnable today: %d" % sum(1 for b in bars if b["every_decider_runnable_today"]),
     "- tests specified for Stage 3 (new: true): %d" % sum(1 for t in tests.values() if t.get("new")), "",
     "## The 14 bars new in 0.2.0", "", "| bar | proves at | decides | supports |", "|---|---|---|---|"]
L += ["| `%s` | %s | %s | %s |" % (b["id"], b["proves_at"], ", ".join(b["decides"]), ", ".join(b["supports"]) or "-")
      for b in bars if b["id"] in DECIDES]
L += ["", "## The tests new in 0.2.0 (specified; Stage 3 builds each, red first)", "",
      "| test | stage | kind | file or entry | item | observes |", "|---|---|---|---|---|---|"]
L += ["| `%s` | %s | %s | `%s` | %s | %s |" % (t["id"], t["stage"], t["kind"],
                                            t["file"] if t["kind"] == "offline" else "%s::%s" % (t["file"].split("/")[-1], t["entry"]),
                                            t["item"], t["observes"]) for t in TESTS]
open(C + "/version/test_table.md", "w").write("\n".join(L) + "\n\n---\n" + old)
print("table: %d bars, %d tests (%d new)" % (len(bars), len(tests), sum(1 for t in tests.values() if t.get("new"))))
