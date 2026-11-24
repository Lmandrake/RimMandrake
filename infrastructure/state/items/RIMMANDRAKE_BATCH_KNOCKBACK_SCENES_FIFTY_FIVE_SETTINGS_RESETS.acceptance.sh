#!/bin/bash
# Acceptance test for RIMMANDRAKE_BATCH_KNOCKBACK_SCENES_FIFTY_FIVE_SETTINGS_RESETS. Exit 0 = pass, 1 = fail, 2 = could not look.
# Usage: bash <this file> [test_table.json]      |      bash <this file> --selftest
# Counts the DISTINCT knockback_runner.py commands among the stage-6 checks of the table: checks that share a command share one
# process (one settings snapshot and restore). Limit = sum over groups (same --ticks, --real-seconds and list note) of
# ceil(checks/10). The group of 10 is the study's "8 to 10 small scenes" (analysis.md section 8) = OUR OWN rule.
# Every one of the 80 scenes named by the table on 2026-11-24 must still be in some command (no verdict lost).
cd "$(dirname "$0")/../../.." || exit 2
BASELINE="all_fly_no_cap barrage_perf barrage_perf_off blast_kinds body_override calibration closed_containers closed_containers_control container_thrown corpse_into_pit cover_breaks door_stop emp_no_throw fire_half frame_probe_selfcheck frame_probe_selfcheck_paused gas_census gas_chain gas_clumps gas_into_pit gas_into_pit_off goods_fly_lands goods_fly_midair goods_fly_off goods_fly_rebound goods_fly_wall goods_fly_wild goods_obstacles goods_obstacles_control harmful_unpatched heavy_knock heavy_skip hose_carry_drop hose_carry_drop_off immunity_window impact_factor in_pit_skip items killed_by_blast land_no_bump land_no_bump_pit lookup_projectile lookup_zero_wins mass_and_power no_cross no_cross_ordered only_explosions open_storage over_sandbags pawn_arc pawn_hits_pawn pit_colonist pit_enemy pit_goods_fetch settings_off settings_sweep settings_sweep_after settings_sweep_closedGuard settings_sweep_debugDrawVectors settings_sweep_doorsTakeDamage settings_sweep_fireHalf settings_sweep_flyingGoods settings_sweep_gasChain settings_sweep_heavyGoodsKnock settings_sweep_heavyGoodsMinMass settings_sweep_landingStun settings_sweep_lightMassLimit20 settings_sweep_shoveClosedContainers settings_sweep_throwAnimals settings_sweep_throwCorpses settings_sweep_throwDowned settings_sweep_throwItems settings_sweep_throwMechanoids settings_sweep_vanillaCratesClosed shelf shield_counter spared_states storeroom_bomb_pit storeroom_bomb_pit_control wall_stop" exec python3 -I - "$@" <<'PY'
import json, sys, re, math, collections, os
CAP = 10
BASE = set(os.environ["BASELINE"].split())
def judge(tests, base):
    cmds = []
    for k, x in tests.items():
        if str(x.get("stage")) != "6": continue
        cmd = x.get("command", "")
        m = re.search(r"knockback_runner\.py(.*?)(?:\s{3}\((.*)\))?$", cmd)
        if not m: continue
        a = m.group(1)
        sc = re.search(r"--scenes\s+(\S+)", a)
        tk = re.search(r"--ticks\s+(\d+)", a)
        key = (tk.group(1) if tk else "300", "--real-seconds" in a, (m.group(2) or "").strip())
        cmds.append((k, cmd.strip(), sc.group(1).split(",") if sc else [], key))
    if not cmds:
        print("could not look: no stage-6 knockback_runner checks in the table"); return 2
    per_key = collections.Counter(key for _, _, _, key in cmds)
    limit = sum(math.ceil(n / CAP) for n in per_key.values())
    distinct = len({c for _, c, _, _ in cmds})
    have = {s for _, _, sc, _ in cmds for s in sc}
    lost = sorted(base - have)
    print("stage-6 runner checks read %d; distinct processes %d (limit %d, our own rule: groups of %d); baseline scenes %d, missing %d %s" % (len(cmds), distinct, limit, CAP, len(base), len(lost), lost[:3]))
    return 0 if distinct <= limit and not lost else 1
def mk(n, shared, drop=None):
    names = ["s%d" % j for j in range(n)]
    t = {}
    for i in range(n):
        sc = ",".join(x for x in names if x != drop) if shared else names[i]
        t["c%d" % i] = {"stage": "6", "command": "python.exe src\\RimMandrake\\ExplosiveKnockback\\knockback_runner.py --scenes %s --ticks 300   (proof build)" % sc}
    return t, set(names)
if sys.argv[1:2] == ["--selftest"]:
    ok = True
    def case(name, built, want):
        global ok
        got = judge(*built); g = got == want; ok &= g
        print("  case %-22s want rc %d got rc %d %s" % (name, want, got, "ok" if g else "WRONG"))
    case("planted_12_processes", mk(12, False), 1)
    case("batched_stays_green", mk(10, True), 0)
    case("scene_lost", mk(10, True, drop="s9"), 1)
    case("empty_table", ({}, set()), 2)
    print("SELFTEST OK" if ok else "SELFTEST BROKEN"); sys.exit(0 if ok else 1)
p = sys.argv[1] if len(sys.argv) > 1 else "design/concepts/ExplosiveKnockback/version/test_table.json"
try: tests = json.load(open(p, encoding="utf-8"))["tests"]
except Exception as e: print("could not look: %s: %s" % (p, e)); sys.exit(2)
sys.exit(judge(tests, BASE))
PY
