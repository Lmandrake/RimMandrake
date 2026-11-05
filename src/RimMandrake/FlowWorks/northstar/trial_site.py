#!/usr/bin/env python3
"""trial_site -- the FlowWorks dry golden trial site on the list the dry half runs on (TRIAL_SITE_REBUILD_FOR_FOURTEEN_MODS).

Three LIVE verbs, each one line of the item's live proofs (the supervisor holds the bridge, deploys and runs them):

  python.exe src/RimMandrake/FlowWorks/northstar/trial_site.py gate     # is the running game site_spec.TIER at all?
  python.exe src/RimMandrake/FlowWorks/northstar/trial_site.py ensure   # A1: golden save + sidecar exist, contract fresh
  python.exe src/RimMandrake/FlowWorks/northstar/trial_site.py prove    # A2: a Work copy loads and preflight reads CLEAN

gate   exit 0 fits; 2 wrong game (UNMEASURED: restage on the tier); 3 the instrument could not read. Never 1.
ensure no game call at all when site_spec.GOLDEN_NAME exists with a clean version contract (preflight
       contract_problems, which includes "built on another tier"). Otherwise: load the calm test site
       (test_site_saves.load_site, Route 1 of the item), dev mode on, then prep_site.prep(rebuild=True). The golden name
       is v2, so the only save --rebuild can move aside is a stale v2 of our own, never the owner's v1.
       exit 0 fresh or built; 1 not (refusal, calm load not verified, contract still dirty after the build).
prove  exit 1 unless the contract is clean; copies the golden to NS_FlowWorks_Work_<ts>.rws (the golden is never
       loaded: plan 3.4), checks the copy's mod header against the running list, loads it from the main menu, lets
       the modal broker close load dialogs, then runs preflight_flowworks live with --fix and exits 0 only on CLEAN
       (no FAIL, no UNMEASURED).
Each verb writes its receipt under Transient/trial_site/ and prints one line.
"""
import argparse
import glob
import json
import os
import shutil
import stat
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
_UTILS = os.path.join(os.path.dirname(os.path.dirname(HERE)), "Utils")
if HERE not in sys.path:
    sys.path.insert(0, HERE)
for _p in (_UTILS, os.path.join(_UTILS, "modcheck")):
    if _p not in sys.path:
        sys.path.append(_p)
import site_spec as S  # noqa: E402
import preflight_flowworks as PF  # noqa: E402

FITS, FAIL_EXIT, WRONG_GAME, BLIND = 0, 1, 2, 3
WORK_PREFIX = "NS_FlowWorks_Work_"


def _call(s):
    return lambda tool, **kw: s.call(tool, **kw)


def running_ids(s):
    from biome_site import running_retired
    running, _ = running_retired(_call(s))
    return [str(i).strip().lower() for i in running or () if str(i).strip()]


def gate(running, tier_list=None, want=None):
    """running packageIds -> problems against site_spec.TIER (empty = fits)."""
    import test_site_tier_gate as TG
    return TG.tier_gaps(running, None, tier_list=tier_list, want=want, tier=S.TIER)


def ensure(s, P, seat, load_calm=None, prep=None, log=print):
    """-> receipt; receipt['ok']. load_calm(call) -> load_site receipt; prep(s, P, seat) builds (defaults: the real ones)."""
    rec = {"verb": "ensure", "golden": S.GOLDEN_NAME, "tier": S.TIER, "problems": []}
    before = PF.contract_problems(P)
    rec["contract_before"] = before
    if not before:
        rec["action"] = "fresh"
        rec["ok"] = True
        return rec
    rec["action"] = "build"
    if load_calm is None:
        import test_site_saves as T
        load_calm = lambda call: T.load_site(call, "calm")   # noqa: E731
    calm = load_calm(_call(s))
    rec["calm"] = {k: calm.get(k) for k in ("save", "verified", "problems", "load_s")}
    if not calm.get("verified"):
        rec["problems"].append("calm site load not verified: %s" % (calm.get("problems") or [])[:3])
        rec["ok"] = False
        return rec
    from northstar_driver.preflight import check_dev_god
    dev = check_dev_god(s, need_dev=True, need_god=False, fix=True)
    if dev.status != PF.PASS:
        rec["problems"].append("dev mode: %s" % dev.evidence)
        rec["ok"] = False
        return rec
    if prep is None:
        import prep_site as PS

        def prep(s_, P_, seat_):
            try:
                PS.prep(s_, P_.saves, seat_, prefs=P_.prefs, player_log=P_.player_log, rebuild=True, bridge_paths=P_,
                        log=log)
            except PS.Refused as ex:
                return "PREP REFUSED at step %s" % ex
            return None
    why = prep(s, P, seat)
    if why:
        rec["problems"].append(why)
    after = PF.contract_problems(P)
    rec["contract_after"] = after
    rec["problems"].extend("contract after build: %s" % a for a in after)
    rec["ok"] = not rec["problems"]
    return rec


def make_work_copy(saves_dir, stamp=None):
    """Copy the golden to a fresh writable Work save (older Work copies are disposable and removed) -> its name."""
    for old in glob.glob(os.path.join(saves_dir, WORK_PREFIX + "*.rws")):
        os.chmod(old, stat.S_IREAD | stat.S_IWRITE)
        os.remove(old)
    name = WORK_PREFIX + (stamp or time.strftime("%Y%m%dT%H%M%S"))
    dst = os.path.join(saves_dir, name + ".rws")
    shutil.copyfile(os.path.join(saves_dir, S.GOLDEN_NAME + ".rws"), dst)
    os.chmod(dst, stat.S_IREAD | stat.S_IWRITE)
    return name


def load_work(s, name, budget_s=420, sleep=time.sleep):
    """Main menu -> load_game(name) -> Playing with a map; the journal scanned for a broken load; modal broker run.
    -> problems."""
    import test_site_saves as T
    call = _call(s)
    if T._state(call) == "Playing":
        call("rimworld/go_to_main_menu")
        if T._wait(lambda: T._state(call) == "Entry", 180, sleep) is None:
            return ["main menu not reached within 180 s"]
    seq0 = T._journal_seq(call)
    try:
        call("rimworld/load_game", saveName=name)
    except Exception:  # noqa: BLE001 - polled below, never resent
        pass
    got = T._wait(lambda: T._state(call) == "Playing" and (call("jawa/map_info") or {}).get("tile") is not None,
                  budget_s, sleep)
    if got is None:
        return ["no Playing map within %ds of load_game %s" % (budget_s, name)]
    out = []
    broken = T._load_errors(call, seq0)
    if broken:
        out.append("the load logged %s" % broken)
    import quiet_site as QS
    rc = QS.site_profile_receipt(T.call_session(call), "trial_site_prove", controls=("modal_broker",)) or {}
    if rc.get("error") or rc.get("problems"):
        out.append("modal broker: %s" % (rc.get("error") or rc.get("problems")))
    return out


def prove(s, P, seat, running=None, loader=None, live=None, tier_list=None):
    """-> receipt; receipt['ok'] only when the contract is clean, the copy's header fits, the load is clean and every
    preflight row PASSes."""
    import test_site_saves as T
    rec = {"verb": "prove", "golden": S.GOLDEN_NAME, "tier": S.TIER, "problems": []}
    con = PF.contract_problems(P)
    if con:
        rec["problems"].extend("contract: %s" % c for c in con)
        rec["ok"] = False
        return rec
    running = running if running is not None else running_ids(s)
    tier_list = tier_list if tier_list is not None else T.tier_ids(S.TIER)
    hp, ids = T.header_problems(os.path.join(P.saves, S.GOLDEN_NAME + ".rws"), running, tier=tier_list)
    rec["header"] = ids
    if hp:
        rec["problems"].extend(hp)
        rec["ok"] = False
        return rec
    name = make_work_copy(P.saves)
    rec["work"] = name
    rec["problems"].extend((loader or load_work)(s, name))
    if rec["problems"]:
        rec["ok"] = False
        return rec
    rows = (live or PF.run_live)(s, P, seat, fix=True)
    rec["rows"] = [r.as_dict() for r in rows]
    rec["problems"].extend("%s %s: %s" % (r.name, r.status, r.evidence) for r in rows if r.status != PF.PASS)
    rec["ok"] = not rec["problems"]
    return rec


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("verb", choices=("gate", "ensure", "prove"))
    ap.add_argument("--seat", default="RELENTLESS", choices=S.SEATS)
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    if a.verb == "gate":
        try:
            from northstar_driver.session import FastSession
            with FastSession() as s:
                running = running_ids(s)
            probs = gate(running)            # an unresolvable tier raises here: BLIND, never exit 1
        except Exception as ex:  # noqa: BLE001 - a blind read is UNMEASURED, never a verdict
            print("trial_site gate: BLIND %s: %s" % (type(ex).__name__, str(ex)[:300]))
            return BLIND
        if probs:
            print("trial_site gate: WRONG GAME (UNMEASURED; restage on tier %s) %s"
                  % (S.TIER, json.dumps({"problems": probs, "running": running})))
            return WRONG_GAME
        print("trial_site gate: FITS tier %s (%d mods)" % (S.TIER, len(running)))
        return FITS
    try:
        from northstar_driver.session import FastSession
        P = PF.Paths()
        with FastSession() as s:
            rec = ensure(s, P, a.seat) if a.verb == "ensure" else prove(s, P, a.seat)
    except Exception as ex:  # noqa: BLE001 - the bridge dropped: UNMEASURED, not the item's FAIL
        print("trial_site %s: BLIND %s: %s" % (a.verb, type(ex).__name__, str(ex)[:300]))
        return BLIND
    work = os.path.join(S.ROOT, "Transient", "trial_site")
    os.makedirs(work, exist_ok=True)
    out = a.out or os.path.join(work, "%s_%s.json" % (a.verb, time.strftime("%Y%m%dT%H%M%S")))
    with open(out, "w", encoding="utf-8") as f:
        json.dump(rec, f, indent=1, sort_keys=True, default=str)
    print("trial_site %s: %s -> %s %s" % (a.verb, "CLEAN" if rec["ok"] else "NOT CLEAN", out,
                                          "" if rec["ok"] else rec["problems"][:4]))
    return 0 if rec["ok"] else FAIL_EXIT


if __name__ == "__main__":
    sys.exit(main())
