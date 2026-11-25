#!/usr/bin/env python3
"""Selftest: the tap certificate of BRIDGE v2.0 (tap_certificate.py, the pure core; the witness counts of JawaBenchHookGuard.cs).
Item RIMMANDRAKE_BUILD_TAP_CERTIFICATE_CANARY_RUNS_OFF_STAGE. Page: design/specs/2026-11-23-bridge-v2/boundary.md §TAP CERTIFICATE;
one test per promise there, 11 checks:

  1 a certificate for another companion is refused      2 for another mod list      3 a changed patch inventory is refused
  4 a route not shown is listed as such, never as covered   5 a scene that needs an uncertified tap is COULD NOT ARM
  6 the arm check calls no op of the act list           7 a foreign prefix is named on the receipt
  8 a missing certificate is "could not look", never "covered"
  9 a changed setting of a mod with a foreign patch voids the certificate
 10 an entry with no record voids that tap's coverage for the run (and the guard counts what the witness reads)
 11 an absence on a method with a foreign prefix reads "not provable here"

Each plant breaks one rule of a COPY of the core and must turn its named check red. An offline test proves rules, never hooks:
the live proof is prove_tap_certificate.py. No game, no bridge, no dotnet.
Run: python3 src/RimMandrake/bridgetools/selftest_tap_certificate.py [--no-plants]"""
import copy
import importlib.util
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
CORE = os.path.join(HERE, "tap_certificate.py")
GUARD = os.path.join(HERE, "JawaBench.BridgeTools", "JawaBenchHookGuard.cs")
CAST = os.path.join(HERE, "JawaBench.BridgeTools", "JawaBenchCastCore.cs")
WORLD = os.path.join(HERE, "JawaBench.BridgeTools", "JawaBenchWorld.cs")


def load(path):
    spec = importlib.util.spec_from_file_location("tap_certificate_under_test", path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


# ------------------------------------------------------------------------------------------------ a fake loaded game
FOREIGN_PREFIX = {"owner": "other.mod.harmony", "priority": 400, "patchMethod": "Other.Patch.Prefix", "patchAssembly": "OtherMod"}


def game(K, companion="mvid-A", ids=("ludeon.rimworld", "mandrake.rm.bridge"), foreign=None, ours_off=()):
    """-> (identity-making reader, calls list). foreign {"Type.Method": [patch rows]} adds other owners' patches."""
    calls = []
    foreign = foreign or {}

    def read(tool, args):
        calls.append(tool)
        if tool == "jawa/running_mods":
            return {"success": True, "packageIds": list(ids),
                    "mods": [{"packageId": "mandrake.rm.bridge", "assembly": {"matches": [{"mvid": companion}]}}]}
        if tool == "jawa/harmony_patches":
            meth = "%s.%s" % (args["typeName"], args["methodName"])
            pre, post = [], []
            if meth not in ours_off:
                post.append({"owner": "jawabench.cast", "priority": 0, "patchMethod": "P", "patchAssembly": "JawaBench.BridgeTools"})
            for f in foreign.get(meth, []):
                (pre if f.get("kind", "prefix") == "prefix" else post).append({k: v for k, v in f.items() if k != "kind"})
            return {"success": True, "methods": [{"method": args["methodName"], "prefixes": pre, "postfixes": post}]}
        return {"success": False, "message": "unknown tool %s" % tool}
    return read, calls


def ident(K, settings=None, **kw):
    read, _ = game(K, **kw)
    return K.read_identity(read, settings)


def all_shown(K):
    return {t: list(v["routes"]) for t, v in K.TAPS.items()}


def cert(K, shown=None, settings=None, **kw):
    return K.make(ident(K, settings=settings, **kw), all_shown(K) if shown is None else shown, {"tap": "reserve", "reported": True})


def need(c, msg):
    if not c:
        raise AssertionError(msg)


# ------------------------------------------------------------------------------------------------ the checks
def t_a_certificate_for_another_companion_is_refused(K):
    c = cert(K)
    st, why = K.validate(c, ident(K, companion="mvid-B"))
    need(st == "refused" and any("companion" in w for w in why), "another companion: %s %s" % (st, why))
    need(K.validate(c, ident(K))[0] == "valid", "the same identity must be valid")


def t_a_certificate_for_another_mod_list_is_refused(K):
    c = cert(K)
    st, why = K.validate(c, ident(K, ids=("ludeon.rimworld", "mandrake.rm.bridge", "some.other")))
    need(st == "refused" and any("mod list" in w for w in why), "another mod list: %s %s" % (st, why))


def t_a_changed_patch_inventory_is_refused(K):
    c = cert(K)
    st, why = K.validate(c, ident(K, foreign={"Verse.AI.ReservationManager.Reserve": [FOREIGN_PREFIX]}))
    need(st == "refused" and any("inventory" in w for w in why), "a new foreign prefix: %s %s" % (st, why))


def t_a_route_not_shown_is_listed_never_covered(K):
    shown = all_shown(K)
    shown["reserve"] = ["made"]
    cov = K.coverage(cert(K, shown=shown))
    need(cov["reserve"]["not_shown"] == ["refused"] and "refused" not in cov["reserve"]["covered"], "reserve: %s" % cov["reserve"])
    read, _ = game(K)
    a = K.arm_check(cert(K, shown=shown), read, ["reserve.made"])
    need(a["verdict"] == K.ARMED and a["routes"]["reserve.made"] == "covered", "a shown route arms: %s" % a)


def t_a_scene_that_needs_an_uncertified_tap_could_not_arm(K):
    shown = all_shown(K)
    shown["reserve"] = ["made"]
    read, _ = game(K)
    a = K.arm_check(cert(K, shown=shown), read, ["reserve.refused", "fire"])
    need(a["verdict"] == K.COULD_NOT_ARM and a["routes"]["reserve.refused"] == "not shown", "route not shown: %s" % a)
    need(K.receipt_mode(a) == K.BOOTSTRAP, "an unarmed scene is BOOTSTRAP")
    read, _ = game(K, ours_off=("RimWorld.Fire.SpawnSetup",))
    a = K.arm_check(cert(K), read, ["fire.by_pawn"])
    need(a["verdict"] == K.COULD_NOT_ARM and a["routes"]["fire.by_pawn"] in ("blind", "uncertified"), "our hook off: %s" % a)
    read, _ = game(K)
    a = K.arm_check(cert(K), read, ["fire.by_pawn", "gate.quest.held"])
    need(a["verdict"] == K.ARMED and K.receipt_mode(a) == K.CERTIFIED, "a covered scene is CERTIFIED: %s" % a)


def t_the_arm_check_calls_no_act(K):
    read, calls = game(K)
    K.arm_check(cert(K), read, list(K.TAPS))
    need(calls, "the arm check read nothing")
    bad = [c for c in calls if c not in K.ARM_READS or c in K.ACT_TOOLS]
    need(not bad, "the arm check called %s" % sorted(set(bad)))
    need(not set(K.ARM_READS) & set(K.ACT_TOOLS), "an arm read is on the act list")


def t_a_foreign_prefix_is_named_on_the_receipt(K):
    fp = dict(FOREIGN_PREFIX, kind="prefix")
    f = {"Verse.AI.ReservationManager.Reserve": [fp]}
    c = cert(K, foreign=f)
    read, _ = game(K, foreign=f)
    a = K.arm_check(c, read, ["reserve.made"])
    need(a["verdict"] == K.ARMED, "armed with a certified foreign prefix: %s" % a)
    need(any("other.mod.harmony" in ln and "Reserve" in ln for ln in a["receipt"]), "receipt: %s" % a["receipt"])


def t_a_missing_certificate_is_could_not_look(K):
    read, _ = game(K)
    a = K.arm_check(None, read, ["reserve.made", "fire"])
    need(a["verdict"] == K.COULD_NOT_LOOK, "verdict %s" % a["verdict"])
    need(all(v == "could not look" for v in a["routes"].values()), "routes %s" % a["routes"])
    need(K.receipt_mode(a) == K.BOOTSTRAP, "no certificate is BOOTSTRAP")
    need(K.validate(None, ident(K))[0] == "could not look", "validate(None)")


def t_a_changed_setting_of_a_patching_mod_voids_the_certificate(K):
    f = {"Verse.AI.MentalStateHandler.TryStartMentalState": [dict(FOREIGN_PREFIX, kind="prefix")]}
    c = cert(K, foreign=f, settings={"other.mod.harmony": "sha256:aa"})
    st, why = K.validate(c, ident(K, foreign=f, settings={"other.mod.harmony": "sha256:bb"}))
    need(st == "refused" and any("settings" in w for w in why), "changed setting: %s %s" % (st, why))
    st, _ = K.validate(c, ident(K, foreign=f, settings={"other.mod.harmony": "sha256:aa", "a.mod.with.no.patch": "x"}))
    need(st == "valid", "a setting of a mod with no patch on a tapped method changes nothing: %s" % st)


def t_an_entry_with_no_record_voids_the_tap_for_the_run(K):
    def h(name, e, c):
        return {"hook": name, "runEntered": e, "runCommitted": c}
    close = {"cast": {"taps": {"hooks": [h("cast.reserve", 3, 2), h("cast.job_start", 4, 4)]}},
             "world": {"taps": {"hooks": [{"hook": "world.fire"}]}}}
    w = K.witness(close)
    need(w["cast.reserve"].startswith("void") and w["cast.job_start"] == "ok", "witness %s" % w)
    need(w["world.fire"] == "could not look", "a row with no counts must not read ok: %s" % w)
    cov = K.run_coverage(cert(K), close)
    need(cov["reserve"]["covered"] == [] and cov["job_start"]["covered"], "run coverage %s %s" % (cov["reserve"], cov["job_start"]))
    need(cov["fire"]["covered"] == [], "a hook the witness could not read covers nothing: %s" % cov["fire"])
    # the guard counts what the witness reads: a commit is counted, a run begins at Mark, the close row carries both
    g = open(GUARD, encoding="utf-8").read()
    for frag in ("Committed++;\n            return true;", "internal void Mark() { _markEntered = Entered; _markCommitted = Committed; }",
                 '",\\"runEntered\\":" + I(Entered - _markEntered) + ",\\"runCommitted\\":" + I(Committed - _markCommitted)'):
        need(frag in g, "JawaBenchHookGuard.cs lacks: %s" % frag)
    need("foreach (var g in Guards) g.Mark();" in open(CAST, encoding="utf-8").read(), "the cast taps do not Mark at a new run")
    need("foreach (var g in Tp.Guards) g.Mark();" in open(WORLD, encoding="utf-8").read(), "the world taps do not Mark at Join")


def t_an_absence_under_a_foreign_prefix_is_not_provable_here(K):
    f = {"RimWorld.Fire.SpawnSetup": [dict(FOREIGN_PREFIX, kind="prefix")]}
    c = cert(K, foreign=f)
    need(K.absence(c, "fire", "by_pawn") == K.NOT_PROVABLE, "fire with a foreign prefix: %s" % K.absence(c, "fire", "by_pawn"))
    need(K.absence(c, "explosion", "with_instigator") == "provable", "explosion, no foreign prefix")
    shown = all_shown(K)
    shown["letter"] = ["shown"]
    need(K.absence(cert(K, shown=shown), "letter", "queued") == "not covered", "a route not shown is not covered")


def t_every_owner_of_our_companion_is_ours(K):
    # The companion's Harmony ids are "jawabench.*" (cast, world, gates) AND "mandrake.jawabench.*": the kill tap's postfix is
    # "mandrake.jawabench.eventrecorder" (JawaBenchSituationalTools), the incident tap's prefix "mandrake.jawabench.awareness"
    # (JawaBenchAwareness). One read as foreign makes the arm say "our hook is not on" while it is on, puts our own patch in the
    # foreign inventory, and names it as a foreign prefix on the receipt.
    f = {"Verse.Pawn.Kill": [{"kind": "postfix", "owner": "mandrake.jawabench.eventrecorder", "priority": 400, "patchMethod": "KillPostfix",
                              "patchAssembly": "JawaBench.BridgeTools"}],
         "RimWorld.IncidentWorker.TryExecute": [{"kind": "prefix", "owner": "mandrake.jawabench.awareness", "priority": 800,
                                                 "patchMethod": "IncPre", "patchAssembly": "JawaBench.BridgeTools"}]}
    off = ("Verse.Pawn.Kill", "RimWorld.IncidentWorker.TryExecute")
    c = cert(K, foreign=f, ours_off=off)
    read, _ = game(K, foreign=f, ours_off=off)
    need(K.foreign_owners(ident(K, foreign=f, ours_off=off)["inventory"]) == [], "our own owners read as foreign")
    a = K.arm_check(c, read, ["kill.by_damage", "incident.held"])
    need(a["verdict"] == K.ARMED, "armed on our own kill and incident hooks: %s" % a)
    need(not a["receipt"], "our own prefix named as foreign: %s" % a["receipt"])


CHECKS = [t_a_certificate_for_another_companion_is_refused, t_a_certificate_for_another_mod_list_is_refused,
          t_a_changed_patch_inventory_is_refused, t_a_route_not_shown_is_listed_never_covered,
          t_a_scene_that_needs_an_uncertified_tap_could_not_arm, t_the_arm_check_calls_no_act, t_a_foreign_prefix_is_named_on_the_receipt,
          t_a_missing_certificate_is_could_not_look, t_a_changed_setting_of_a_patching_mod_voids_the_certificate,
          t_an_entry_with_no_record_voids_the_tap_for_the_run, t_an_absence_under_a_foreign_prefix_is_not_provable_here,
          t_every_owner_of_our_companion_is_ours]


def run_all(path):
    K = load(path)
    out = {}
    for t in CHECKS:
        try:
            t(K)
            out[t.__name__[2:]] = "ok"
        except Exception as e:            # a plant may break the core in any way: every exception is a red check
            out[t.__name__[2:]] = "FAIL %s: %s" % (type(e).__name__, e)
    return out


# ------------------------------------------------------------------------------------------------ plants
PLANTS = [
    ("a key with no companion compare", "a_certificate_for_another_companion_is_refused",
     [('    if want.get("companion") != have["companion"]:', '    if False:')]),
    ("a key with no mod list compare", "a_certificate_for_another_mod_list_is_refused",
     [('    if want.get("modlist") != have["modlist"]:', '    if False:')]),
    ("an inventory hash that ignores the patches", "a_changed_patch_inventory_is_refused",
     [("    return _sha(foreign_patches(inventory))", "    return _sha(sorted(foreign_patches(inventory)))")]),
    ("a coverage that folds a route not shown into covered", "a_route_not_shown_is_listed_never_covered",
     [('        shown = [r for r in t.get("shown") or [] if r not in (t.get("not_shown") or [])]',
       '        shown = list(t.get("shown") or []) + list(t.get("not_shown") or [])')]),
    ("an arm that lets a route not shown through", "a_scene_that_needs_an_uncertified_tap_could_not_arm",
     [('        out["routes"][n] = "covered" if not miss else "not shown"', '        out["routes"][n] = "covered"')]),
    ("an arm that never looks for our own hook (the blind tap)", "a_scene_that_needs_an_uncertified_tap_could_not_arm",
     [('        if not ours:\n', '        if False:\n')]),
    ("the canary rite: an arm that does an act", "the_arm_check_calls_no_act",
     [('    ident = read_identity(guarded, settings)', '    read("jawa/order_pawn", {})\n    ident = read_identity(guarded, settings)')]),
    ("a receipt that names no foreign prefix", "a_foreign_prefix_is_named_on_the_receipt",
     [('    return [f for f in t.get("foreign") or [] if f.get("kind") == "prefix"]', '    return []')]),
    ("a missing certificate read as covered", "a_missing_certificate_is_could_not_look",
     [('        out["routes"] = {n: "could not look" if state == "could not look" else "uncertified" for n in needs}\n        return out',
       '        out["routes"] = {n: "covered" for n in needs}\n        out["verdict"] = ARMED\n        return out')]),
    ("a key with no settings", "a_changed_setting_of_a_patching_mod_voids_the_certificate",
     [('    return _sha({o: (settings or {}).get(o, "unread") for o in foreign_owners(inventory)})', '    return _sha(foreign_owners(inventory))')]),
    ("a witness that trusts the entries", "an_entry_with_no_record_voids_the_tap_for_the_run",
     [("            elif e > c:", "            elif False:")]),
    ("a witness that reads a row with no counts as ok", "an_entry_with_no_record_voids_the_tap_for_the_run",
     [('                out[h.get("hook")] = "could not look"', '                out[h.get("hook")] = "ok"')]),
    ("an absence trusted under a foreign prefix", "an_absence_under_a_foreign_prefix_is_not_provable_here",
     [("    if _prefixes(cert, tap):\n        return NOT_PROVABLE", "    if False:\n        return NOT_PROVABLE")]),
    ("ours read as the cast's own prefix only", "every_owner_of_our_companion_is_ours",
     [('OUR_OWNERS = ("jawabench", "mandrake.jawabench")', 'OUR_OWNERS = ("jawabench",)')]),
]


def plants():
    good = True
    src = open(CORE, encoding="utf-8").read()
    d = tempfile.mkdtemp(prefix="tapcert_")
    for name, must, subs in PLANTS:
        text = src
        for old, new in subs:
            if text.count(old) != 1:
                print("FAIL plant %r: its text is in tap_certificate.py %d times, want 1: %r" % (name, text.count(old), old[:70]))
                good = False
            text = text.replace(old, new)
        p = os.path.join(d, "tap_certificate.py")
        with open(p, "w", encoding="utf-8") as f:
            f.write(text)
        red = sorted(u for u, v in run_all(p).items() if v != "ok")
        hit = must in red
        good = good and hit
        print("%s plant %r turns red: %s" % ("ok  " if hit else "FAIL", name, red), flush=True)
    return good


def main(argv):
    res = run_all(CORE)
    bad = 0
    for t in CHECKS:
        v = res[t.__name__[2:]]
        bad += v != "ok"
        print("%s %s%s" % ("ok  " if v == "ok" else "FAIL", t.__name__[2:], "" if v == "ok" else ": " + v), flush=True)
    good = True if "--no-plants" in argv else plants()
    print("tap certificate: %d of %d checks passed%s" % (len(CHECKS) - bad, len(CHECKS),
                                                       "" if "--no-plants" in argv else "; plants %s" % ("all red" if good else "NOT all red")))
    return 0 if bad == 0 and good else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
