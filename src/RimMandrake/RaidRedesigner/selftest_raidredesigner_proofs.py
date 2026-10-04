#!/usr/bin/env python3
"""selftest_raidredesigner_proofs.py -- offline proof for RaidRedesigner's roster/hook chains (RAIDREDESIGNER_COVERAGE_GAPS_1).

Run bare: python3 src/RimMandrake/RaidRedesigner/selftest_raidredesigner_proofs.py   (exit 0 = clean)

A mock jawa/static_call answers RaidRedesignerProof by running a Python MIRROR of the shipped rules (RecordEncounter's
cap/idempotence/multiplier/clamp/switch/pin and the five postfix bodies) with planted breaks. Clean must PASS (the two
engine/scribe stubs UNMEASURED, a stale DLL UNMEASURED, never PASS); each break must redden its component. Statically,
planted source breaks (a hook retargeted/role changed/pin flipped, a setting gate removed, a field dropped from
ExposeData, the proof left out of the csproj) must redden static_findings; the shipped source must be clean.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
UTILS = os.path.join(ROOT, "src", "RimMandrake", "Utils")
for p in (HERE, UTILS, os.path.join(UTILS, "modcheck")):
    if p not in sys.path:
        sys.path.insert(0, p)

import runner                                                  # noqa: E402
import validation as V                                         # noqa: E402
from modcheck import Suite                                     # noqa: E402
from northstar_driver.session import FastSession               # noqa: E402
from northstar_driver.transport import MockGame, MockTransport  # noqa: E402

FAILS = []
CHAINS = ("roster_rules_on_a_scratch_roster", "hook_bodies_record_the_right_role")


def check(name, cond, detail=""):
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, ("" if cond else detail)))
    if not cond:
        FAILS.append(name)


class Roster(object):
    """Python mirror of GameComponent_OldFriends.RecordEncounter with planted breaks."""
    def __init__(self, brk, cap=3, mult=1.0, on=True, pin=True):
        self.brk, self.cap, self.mult, self.on, self.pin = set(brk), cap, mult, on, pin
        self.entries, self.pinned = [], set()

    def find(self, p):
        return next((e for e in self.entries if e["pawn"] == p and not e["dead"]), None)

    def record(self, p, role, tick, g=0, n=0, pin=False):
        if self.on or "off_ignored" in self.brk:
            pass
        if not self.on and "off_ignored" not in self.brk:
            return None
        e = self.find(p)
        new = e is None
        if new:
            e = dict(pawn=p, role=role, enc=0, g=0, n=0, seen=tick, dead=False, summary=None)
            self.entries.append(e)
        elif role == "Captain" or ("downgrade" in self.brk):
            e["role"] = role
        if "dup" in self.brk and not new:
            self.entries.append(dict(e))
        e["enc"] += 1
        e["seen"] = tick
        m = self.mult if "mult_ignored" not in self.brk else 1.0
        clamp = (lambda v, lo, hi: v) if "no_clamp" in self.brk else (lambda v, lo, hi: max(lo, min(hi, v)))
        e["g"] = clamp(e["g"] + int(g * m), -100, 100)
        e["n"] = clamp(e["n"] + int(n * m), 0, 100)
        if new:
            living = [x for x in self.entries if not x["dead"] or "dead_counts" in self.brk]
            over = len(living) - self.cap
            if over > 0 and "no_cap" not in self.brk:
                key = (lambda x: (-x["n"], x["seen"])) if "evict_highest" in self.brk else (lambda x: (x["n"], x["seen"]))
                for v in sorted(living, key=key)[:over]:
                    self.entries.remove(v)
        if pin and (self.pin or "pin_setting_ignored" in self.brk):
            self.pinned.add(p)
        if "pin_arg_ignored" in self.brk and self.pin:
            self.pinned.add(p)
        return e


def roster_text(brk):
    R = Roster(brk)
    e1 = R.record("p1", "FledRaider", 100, 10, 5)
    s = {"a_count": len(R.entries), "a_grudge": e1["g"], "a_notab": e1["n"], "a_enc": e1["enc"]}
    R.record("p1", "Captain", 200)
    s.update(b_count=len(R.entries), b_role=e1["role"], b_enc=e1["enc"], b_seen=e1["seen"])
    R.record("p1", "FledRaider", 300)
    s["c_role"] = e1["role"]
    R.record("p2", "FledRaider", 400, 0, 20)
    R.record("p3", "FledRaider", 500, 0, 30)
    R.record("p4", "FledRaider", 600, 0, 40)
    s.update(cap_count=len(R.entries), cap_p1=R.find("p1") is not None, cap_p4=R.find("p4") is not None)
    R.mult = 2.0
    e2 = R.record("p2", "FledRaider", 700, 10, 10)
    s.update(mult_grudge=e2["g"], mult_notab=e2["n"])
    R.record("p2", "FledRaider", 710, 200, 200)
    s.update(clamp_grudge_hi=e2["g"], clamp_notab_hi=e2["n"])
    R.record("p2", "FledRaider", 720, -200, -200)
    s.update(clamp_grudge_lo=e2["g"], clamp_notab_lo=e2["n"])
    R.mult = 1.0
    n0 = len(R.entries)
    R.on = False
    off = R.record("p5", "FledRaider", 800, 5, 5, True)
    s.update(off_null=off is None, off_count=len(R.entries) - n0, off_pinned="p5" in R.pinned)
    R.on = True
    e3 = R.find("p3")
    e3["dead"], e3["summary"] = True, "p3 (FledRaider) - died"
    R.record("p5", "FledRaider", 900, 0, 50)
    s.update(dead_flag=e3["dead"], dead_summary_has_cause="died" in e3["summary"], dead_kept=e3 in R.entries, dead_total=len(R.entries),
             dead_idempotent=True)
    R.cap = 30
    R.record("p6", "FledRaider", 1000, 0, 1, True)
    s["pin_on"] = "p6" in R.pinned
    R.record("p8", "FledRaider", 1000, 0, 1, False)
    s["pin_arg_false"] = "p8" in R.pinned
    R.pin = False
    R.record("p7", "FledRaider", 1000, 0, 1, True)
    s["pin_setting_off"] = "p7" in R.pinned
    return s


def hooks_text(brk, pirate=True, home=True):
    s = {"pirate": pirate, "other": True, "map_home": home}
    if not pirate:
        return s
    s.update(flee_role="FledRaider" if home else "-", flee_grudge=5 if home else "-", flee_pinned=home if home else "-",
             flee_friend_recorded=("True" if "friend_recorded" in brk else False) if home else "-")
    if "flee_wrong_role" in brk and home:
        s["flee_role"] = "Captain"
    s.update(esc_role="EscapedPrisoner", esc_grudge=20, esc_pinned=True, rel_blackstar_role="Released" if "blackstar_unsplit" in brk else "NamedHunter",
             rel_blackstar_grudge=-5, rel_other_role="Released", cap_role="NamedHunter", cap_notab=15, cap_pinned=("pin_flip" in brk),
             cap_not_by_player_recorded=("cap_any_captor" in brk), kid_role="Kidnapper", kid_grudge=25, kid_names_victim=True,
             hook_off_recorded=("hook_ignores_switch" in brk), hook_off_count_delta=1 if "hook_ignores_switch" in brk else 0)
    if "esc_no_pin" in brk:
        s["esc_pinned"] = False
    return s


def fmt(d):
    return " ".join("%s=%s" % (k, v) for k, v in d.items())


def make_ext(brk, stale=False, **hk):
    def ext(game, tool, p):
        if tool != "jawa/static_call" or p.get("type") != V._PROOF:
            return None
        if stale:
            return {"success": False, "message": "no public static method %s" % p.get("method")}
        txt = fmt(roster_text(brk)) if p.get("method") == "ProofRoster" else fmt(hooks_text(brk, **hk))
        return {"success": True, "result": txt}
    return ext


def run(brk=(), stale=False, **hk):
    suite = Suite("RaidRedesignerProofs")      # only the two proof chains: the legacy chains screenshot the real desktop
    for name in CHAINS:
        suite.chain(name)(getattr(V, name))
    game = MockGame()
    game.ext = make_ext(set(brk), stale=stale, **hk)
    s = FastSession(transport=MockTransport(game), strict=False)
    with s:
        res = runner.run_suite(suite, s, anchor=None, mod=None)
    out = {}
    for ch in res["chains"]:
        if ch["name"] in CHAINS:
            for c in ch["components"]:
                out[c["name"]] = c["verdict"]
    return out


def main():
    srcs = V._src_with_proj()
    check("static_findings clean on the shipped source", V.static_findings(srcs) == [], V.static_findings(srcs))

    clean = run()
    stubs = [k for k in clean if k.endswith("state_read")]
    check("clean: every non-stub bar PASSes", all(v == "PASS" for k, v in clean.items() if k not in stubs), clean)
    check("clean: the 2 engine/scribe stubs are UNMEASURED, never PASS", len(stubs) == 2 and all(clean[k] == "UNMEASURED" for k in stubs), clean)
    got = run(stale=True)
    check("stale DLL: proof bars UNMEASURED, never PASS", got["cap_evicts_the_lowest_notability_living_entry"] == "UNMEASURED", got)
    got = run(pirate=False)
    check("no Pirate faction: hook bars UNMEASURED/skipped, flee not PASS", got["flee_hook_records_hostile_raiders_pins_them_and_ignores_friends"] == "UNMEASURED", got)
    got = run(home=False)
    check("not a player home: flee bar UNMEASURED", got["flee_hook_records_hostile_raiders_pins_them_and_ignores_friends"] == "UNMEASURED", got)

    for brk, comp in (("dup", "one_entry_per_pawn_and_role_only_upgrades"), ("downgrade", "one_entry_per_pawn_and_role_only_upgrades"),
                      ("no_cap", "cap_evicts_the_lowest_notability_living_entry"), ("evict_highest", "cap_evicts_the_lowest_notability_living_entry"),
                      ("mult_ignored", "multiplier_scales_deltas_and_both_clamp"), ("no_clamp", "multiplier_scales_deltas_and_both_clamp"),
                      ("off_ignored", "rosterTrackingEnabled_off_records_nothing_and_pins_nothing"),
                      ("dead_counts", "dead_entry_collapses_once_stays_and_does_not_count_against_the_cap"),
                      ("pin_arg_ignored", "pinEncounteredPawns_pins_only_when_both_the_hook_and_the_setting_say_so"),
                      ("pin_setting_ignored", "pinEncounteredPawns_pins_only_when_both_the_hook_and_the_setting_say_so"),
                      ("flee_wrong_role", "flee_hook_records_hostile_raiders_pins_them_and_ignores_friends"),
                      ("friend_recorded", "flee_hook_records_hostile_raiders_pins_them_and_ignores_friends"),
                      ("esc_no_pin", "escaped_and_kidnapper_hooks_write_their_role_and_deltas"),
                      ("blackstar_unsplit", "release_and_capture_hooks_split_blackstar_from_everyone_else"),
                      ("pin_flip", "release_and_capture_hooks_split_blackstar_from_everyone_else"),
                      ("cap_any_captor", "release_and_capture_hooks_split_blackstar_from_everyone_else"),
                      ("hook_ignores_switch", "a_real_hook_records_nothing_with_rosterTrackingEnabled_off")):
        got = run((brk,))
        check("break %-20s reddens %s" % (brk, comp), got.get(comp) == "FAIL", got.get(comp))

    def mutate(fn, old, new, tag, must=None):
        mut = dict(srcs)
        check("source break (%s) is findable in the shipped text" % tag, old in mut[fn], old)
        mut[fn] = mut[fn].replace(old, new)
        got = V.static_findings(mut)
        check("source break %-26s reddens static_findings" % tag, bool(got) and (must is None or any(must in g for g in got)), got)

    mutate("Patch_PrisonerEscaped.cs", "nameof(GuestUtility.Notify_PrisonerEscaped)", "nameof(GuestUtility.Notify_PrisonerReleased)", "escape hook retargeted", "no longer patches")
    mutate("Patch_PrisonerEscaped.cs", "RoleTag.EscapedPrisoner", "RoleTag.Released", "escape role changed", "RoleTag.EscapedPrisoner")
    mutate("Patch_ColonistKidnapped.cs", "pin: false", "pin: true", "kidnapper pin flipped", "pin argument")
    mutate("Patch_PrisonerReleasedOrNamedHunter.cs", "if (by != Faction.OfPlayer) return;", "", "capture-by-player guard (no static bar: body check only)") if False else None
    mutate("GameComponent_OldFriends.cs", "if (!RaidRedesignerSettings.rosterTrackingEnabled) return null;", "", "master switch removed", "rosterTrackingEnabled")
    mutate("GameComponent_OldFriends.cs", "RaidRedesignerSettings.grudgeNotabilityMultiplier", "1f", "multiplier ignored", "grudgeNotabilityMultiplier")
    mutate("GameComponent_OldFriends.cs", "RaidRedesignerSettings.maxLivingEntries", "24", "cap setting ignored", "maxLivingEntries")
    mutate("GameComponent_OldFriends.cs", "pin && RaidRedesignerSettings.pinEncounteredPawns", "pin", "pin setting ignored", "pinEncounteredPawns")
    mutate("OldFriendEntry.cs", 'Scribe_Values.Look(ref Grudge, "grudge", 0);', "", "Grudge dropped from ExposeData", "Grudge")
    mutate("Encounter.cs", 'Scribe_Values.Look(ref Summary, "summary");', "", "Summary dropped from ExposeData", "Summary")
    mutate("RM_RaidRedesigner.csproj", '<Compile Include="RaidRedesignerProof.cs" />', "", "proof left out of csproj", "csproj")

    if FAILS:
        print("\n%d RaidRedesigner proof selftest(s) FAILED" % len(FAILS))
        return 1
    print("\nall RaidRedesigner proof selftests passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
