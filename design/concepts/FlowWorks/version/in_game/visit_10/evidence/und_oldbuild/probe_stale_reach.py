"""probe_stale_reach.py <clone> <seed> <loads>: many fresh under-deck lanes on a paused map; does a reach read stay False while the
clock stands? Last line: the verdict. Exit 0 none stale, 3 a stale lane (reach False for 5 s paused, True after some ticks), 4 a
lane that stays False (not this fault: read its cells), 2 could not look. Old build 78f51ace1d, 2026-11-24: 14 loads of
18 lanes read 8 stale lanes, all in one load (oldbuild_seed7_14loads.log, made before the VERDICT line was added); the same 14
loads again read 0 (oldbuild_seed7_repeat.log). The fault comes with the load, about 1 in 28, so 0 stale here shows no fix."""
import json, os, random, re, sys, time
R = sys.argv[1]
for p in ("src/RimMandrake/Utils", "src/RimMandrake/Utils/modcheck"):
    sys.path.insert(0, os.path.join(R, *p.split("/")))
import validation_core as V, test_site_saves as T
B = V.Bridge()
SRC = open(os.path.join(R, "src/RimMandrake/FlowWorks/northstar/suspension_bridge_proof.py"), encoding="utf-8").read()
PR = re.search(r'^PROOF\s*=\s*"([^"]+)"', SRC, re.M).group(1)


def pf(m, a): return str((B.call("jawa/static_call", type=PR, method=m, args=a) or {}).get("result"))
def ticks(n): B.call("rimworld/step_game_ticks", ticks=n, pauseFirst=True, timeoutMs=60000)
def dig(x, z, d): B.call("jawa/flowworks_excavation_drive", x=x, z=z, deepenLevels=d, setBodyWaterM=-1)


lanes, stale, stuck, settled = 0, 0, 0, 0
rng = random.Random(int(sys.argv[2]))
for load in range(int(sys.argv[3])):
    if not T.load_site(B.call, "calm").get("verified"):
        print("load", load, "site not verified", flush=True)
        continue
    V.site_calm(B)
    B.call("jawa/kill_hostiles")
    V.prepare_site(B, (138, 138, 40, 94), [], "und")
    ticks(70)
    for z in range(142, 230, 5):
        gap, age, split = rng.choice((0, 0, .02, .05, .1)), rng.choice((0, 0, 5, 20, 40, 61)), rng.randint(1, 8)
        for i in range(1, 9):
            dig(140 + i, z, 8)
            if gap:
                time.sleep(gap)
            if i == split and age:
                ticks(age)
        pf("ProofBuild", "144,%d;145,%d;steel;god" % (z - 1, z + 1))
        ps = (B.call("jawa/spawn_pawn", kindDef="Colonist", x=141, z=z, faction="player", count=1) or {}).get("pawns") or [{}]
        a = str(ps[0].get("id", "")).replace("Human", "")
        arg = "%s;148,%d" % (a, z)
        first, path = pf("ProofReach", arg), pf("ProofUnderPath", arg)
        rec = dict(load=load, z=z, gap=gap, age=age, split=split, first=first, path=path)
        if "reach=True" not in first:
            t0, polls = time.time(), 0
            while time.time() - t0 < 5 and "reach=True" not in pf("ProofReach", arg):
                polls += 1
                time.sleep(.05)
            rec["paused_s"], rec["polls"] = round(time.time() - t0, 2), polls
            n = 0
            while n < 600 and "reach=True" not in pf("ProofReach", arg):
                ticks(30)
                n += 30
            rec.update(ticks_to_reach=n, after=pf("ProofReach", arg), path_after=pf("ProofUnderPath", arg))
            rec["cells"] = [str(B.call("rimworld/get_cell_info", x=140 + i, z=z))[:300] for i in range(1, 9)]
        print(json.dumps(rec), flush=True)
        lanes += 1
        if "paused_s" in rec:
            if "reach=True" not in rec["after"]:
                stuck += 1
            elif rec["ticks_to_reach"]:
                stale += 1
            else:
                settled += 1
print("VERDICT lanes=%d stale=%d stuck=%d settled_while_paused=%d" % (lanes, stale, stuck, settled), flush=True)
sys.exit(2 if not lanes else 3 if stale else 4 if stuck else 0)
