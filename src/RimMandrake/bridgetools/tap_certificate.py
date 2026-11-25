#!/usr/bin/env python3
"""tap_certificate.py - the tap certificate of BRIDGE v2.0: is a tap blind, and on which routes? (stdlib only, pure core)

Item RIMMANDRAKE_BUILD_TAP_CERTIFICATE_CANARY_RUNS_OFF_STAGE. Design: design/specs/2026-11-23-bridge-v2/05_build_design.md
decision 4. Page: design/specs/2026-11-23-bridge-v2/boundary.md §TAP CERTIFICATE; each promise there has a check of its name in
selftest_tap_certificate.py.

An offline test proves the rules of a tap, never that Harmony put the hook on the method. The proof is a certification session
(prove_tap_certificate.py) in a disposable game: route fixtures do every tapped act by its real engine route, a positive and a
negative case each, and one hook is taken off by hand and must be reported blind. Its result is a CERTIFICATE:

  key    companion   the MVID of JawaBench.BridgeTools as LOADED (jawa/running_mods assembly=JawaBench.BridgeTools)
         modlist     loaded_build.fingerprint of the running packageIds, in load order
         inventory   sha256 over every OTHER owner's patch on a tapped method (owner, kind, priority, patch method, assembly)
         settings    sha256 over the settings of every mod that has such a patch ({owner: sha256 of its settings fields})
  taps   per tap: the routes shown, the routes not shown, the foreign patches on its methods

The four readers below are pure functions of data; the bridge reads live only in `read_identity` and the CLI.
  validate(cert, identity)          -> "valid" | "refused" (with every reason) | "could not look" (no certificate)
  coverage(cert)                    -> per tap: covered routes, and routes NOT SHOWN (never folded into covered)
  arm_check(cert, read, needs)      -> ARMED | COULD NOT ARM | COULD NOT LOOK, and the receipt lines; it calls `read` only
                                       with ARM_READS: no gameplay act, no op of the session's act list (ACT_TOOLS)
  witness(close)                    -> per hook of a run's close record: entries with no record void that tap for the run
  absence(cert, tap, route)         -> "provable" | "not provable here" (a foreign prefix) | "not covered"
  receipt_mode(arm)                 -> "CERTIFIED" with a valid certificate that covers the scene, else "BOOTSTRAP"

  python3 tap_certificate.py audit [RESULT]   exit 0: the committed live result shows a certificate made by the session, with
                                              every fixture's route shown and the planted blind tap reported blind; 1 not;
                                              2 could not look
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
SCHEMA = "tap_certificate_v1"
RESULT = os.path.join(REPO, "design", "specs", "2026-11-23-bridge-v2", "live", "tap_certificate_result.json")
COMPANION_ASM = "JawaBench.BridgeTools"
# Harmony ids of this companion. A patch whose owner starts with one of these is ours, never foreign. Both forms are live:
# "jawabench.cast/.world/.gates" and "mandrake.jawabench.*" (the kill tap's eventrecorder, the incident tap's awareness prefix).
OUR_OWNERS = ("jawabench", "mandrake.jawabench")

# Each tap: the methods it patches (type, method), the hooks of its run close record, and its routes. A route is one real engine
# way that the tapped fact comes about; the session shows each one by a fixture, positive and negative where the fact has two.
TAPS = {
    "job_start": {"methods": [("Verse.AI.Pawn_JobTracker", "StartJob")], "hooks": ["cast.job_start"], "routes": ["ordered", "think_tree"]},
    "job_end": {"methods": [("Verse.AI.Pawn_JobTracker", "CleanupCurrentJob")], "hooks": ["cast.job_end"], "routes": ["interrupted", "succeeded"]},
    "reserve": {"methods": [("Verse.AI.ReservationManager", "Reserve")], "hooks": ["cast.reserve"], "routes": ["made", "refused"]},
    "kill": {"methods": [("Verse.Pawn", "Kill")], "hooks": [], "routes": ["by_damage", "by_hediff"]},
    "mental": {"methods": [("Verse.AI.MentalStateHandler", "TryStartMentalState")], "hooks": ["world.mental"], "routes": ["started", "refused"]},
    "quest": {"methods": [("RimWorld.QuestManager", "Add")], "hooks": ["world.quest"], "routes": ["added", "already_there"]},
    "letter": {"methods": [("Verse.LetterStack", "ReceiveLetter")], "hooks": ["world.letter"], "routes": ["shown", "queued"]},
    "message": {"methods": [("Verse.Messages", "Message")], "hooks": ["world.message"], "routes": ["shown", "hidden_repeat"]},
    "fire": {"methods": [("RimWorld.Fire", "SpawnSetup")], "hooks": ["world.fire"], "routes": ["by_pawn", "by_thing"]},
    "explosion": {"methods": [("Verse.GenExplosion", "DoExplosion")], "hooks": ["world.explosion"], "routes": ["with_instigator", "no_instigator"]},
    "incident": {"methods": [("RimWorld.IncidentWorker", "TryExecute")], "hooks": [], "routes": ["fired", "held"]},
    "gate.quest": {"methods": [("RimWorld.QuestManager", "Add")], "hooks": [], "routes": ["allowed", "held"]},
    "gate.mental": {"methods": [("Verse.AI.MentalStateHandler", "TryStartMentalState")], "hooks": [], "routes": ["allowed", "held"]},
}
# The only bridge tools the arm check may call: reads. A scene arm does no gameplay act (decision 4).
ARM_READS = ("jawa/running_mods", "jawa/harmony_patches")
# The act list of the certification session: every tool that its fixtures use to change the game. None is an arm read.
ACT_TOOLS = ("jawa/ordered_job", "jawa/damage", "jawa/pawn_health", "jawa/pawn_mental", "jawa/scene_gate", "jawa/tap_fixture",
             "jawa/fire_quest", "jawa/letter_send_delayed", "jawa/static_call", "jawa/explosion_at", "jawa/fire_incident", "jawa/map_fire",
             "jawa/spawn_pawn", "jawa/spawn_batch")
CERTIFIED, BOOTSTRAP = "CERTIFIED", "BOOTSTRAP"
ARMED, COULD_NOT_ARM, COULD_NOT_LOOK = "ARMED", "COULD NOT ARM", "COULD NOT LOOK"
NOT_PROVABLE = "not provable here"


def _sha(obj):
    return "sha256:" + hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def tapped_methods():
    """Every (type, method) that a tap patches, once."""
    out = []
    for t in TAPS.values():
        for m in t["methods"]:
            if m not in out:
                out.append(m)
    return out


def is_ours(owner):
    o = (owner or "").lower()
    return any(o.startswith(p) for p in OUR_OWNERS)


def foreign_patches(inventory):
    """inventory {"Type.Method": [ {kind, owner, priority, patchMethod, patchAssembly} ]} -> the same, other owners only, sorted."""
    out = {}
    for meth, rows in sorted((inventory or {}).items()):
        f = sorted(({k: r.get(k) for k in ("kind", "owner", "priority", "patchMethod", "patchAssembly")} for r in rows or []
                    if not is_ours(r.get("owner"))), key=lambda r: json.dumps(r, sort_keys=True))
        out[meth] = f
    return out


def inventory_hash(inventory):
    return _sha(foreign_patches(inventory))


def foreign_owners(inventory):
    return sorted({r["owner"] for rows in foreign_patches(inventory).values() for r in rows if r.get("owner")})


def settings_hash(settings, inventory):
    """settings {owner: sha256 of that mod's settings} -> one hash over the owners with a foreign patch on a tapped method.
    An owner with a patch and no settings reading hashes as "unread", so a later reading changes the key."""
    return _sha({o: (settings or {}).get(o, "unread") for o in foreign_owners(inventory)})


def key_of(identity):
    """identity {companion, modlist, inventory, settings} -> the certificate key."""
    inv = identity.get("inventory") or {}
    return {"companion": identity.get("companion"), "modlist": identity.get("modlist"), "inventory": inventory_hash(inv),
            "settings": settings_hash(identity.get("settings"), inv)}


def make(identity, shown, blind, game=None, suite_ms=None, source_sha=None, by="prove_tap_certificate.py"):
    """The certificate. shown {tap: [routes a fixture showed]}; blind {tap, method, reported} (the planted blind tap)."""
    inv = foreign_patches(identity.get("inventory") or {})
    taps = {}
    for name, t in TAPS.items():
        got = [r for r in t["routes"] if r in (shown.get(name) or [])]
        meths = ["%s.%s" % m for m in t["methods"]]
        taps[name] = {"methods": meths, "shown": got, "not_shown": [r for r in t["routes"] if r not in got],
                      "foreign": [dict(r, method=m) for m in meths for r in inv.get(m, [])]}
    return {"schema": SCHEMA, "by": by, "game": game, "source_sha": source_sha, "suite_ms": suite_ms, "key": key_of(identity),
            "taps": taps, "blind": blind}


def validate(cert, identity):
    """-> (state, reasons). A certificate holds only for the identity it was made on; any difference refuses it."""
    if not isinstance(cert, dict) or cert.get("schema") != SCHEMA:
        return "could not look", ["no certificate" if cert is None else "the certificate is not %s" % SCHEMA]
    want, have = cert.get("key") or {}, key_of(identity)
    reasons = []
    if want.get("companion") != have["companion"]:
        reasons.append("companion differs: certified %s, loaded %s" % (want.get("companion"), have["companion"]))
    if want.get("modlist") != have["modlist"]:
        reasons.append("mod list differs: certified %s, loaded %s" % (want.get("modlist"), have["modlist"]))
    if want.get("inventory") != have["inventory"]:
        reasons.append("patch inventory on the tapped methods differs from the certified one")
    if want.get("settings") != have["settings"]:
        reasons.append("the settings of a mod with a patch on a tapped method differ from the certified ones")
    return ("refused", reasons) if reasons else ("valid", [])


def coverage(cert):
    """-> {tap: {"covered": [...], "not_shown": [...]}}. A route not shown is never read as covered."""
    out = {}
    for name, t in ((cert or {}).get("taps") or {}).items():
        shown = [r for r in t.get("shown") or [] if r not in (t.get("not_shown") or [])]
        out[name] = {"covered": shown, "not_shown": list(t.get("not_shown") or [])}
    return out


def _prefixes(cert, tap):
    t = ((cert or {}).get("taps") or {}).get(tap) or {}
    return [f for f in t.get("foreign") or [] if f.get("kind") == "prefix"]


def receipt_foreign(cert, taps):
    """Receipt lines that name each foreign prefix on a tapped method of these taps."""
    lines = []
    for tap in taps:
        for f in _prefixes(cert, tap):
            lines.append("foreign prefix on %s (tap %s): owner %s, %s, priority %s" % (f.get("method"), tap, f.get("owner"),
                                                                                    f.get("patchMethod"), f.get("priority")))
    return lines


def _patches_of(read, type_name, method):
    rep = read("jawa/harmony_patches", {"typeName": type_name, "methodName": method})
    if not isinstance(rep, dict) or rep.get("harmonyError") or not rep.get("success", True):
        return None
    rows = []
    for m in rep.get("methods") or []:
        for kind in ("prefix", "postfix", "transpiler", "finalizer"):
            for p in m.get(kind + "es") or m.get(kind + "s") or []:
                rows.append({"kind": kind, "owner": p.get("owner"), "priority": p.get("priority"), "patchMethod": p.get("patchMethod"),
                             "patchAssembly": p.get("patchAssembly")})
    return rows


def read_identity(read, settings=None):
    """The loaded identity, by reads only (ARM_READS). -> identity dict, or None when a read failed."""
    rm = read("jawa/running_mods", {"assembly": COMPANION_ASM, "details": True, "loadedOf": ""})
    if not isinstance(rm, dict) or not rm.get("success"):
        return None
    sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "rimflow"))
    import loaded_build
    mvid = None
    for m in rm.get("mods") or []:
        for x in ((m.get("assembly") or {}).get("matches") or []):
            mvid = mvid or x.get("mvid")
    inv = {}
    for t, m in tapped_methods():
        rows = _patches_of(read, t, m)
        if rows is None:
            return None
        inv["%s.%s" % (t, m)] = rows
    return {"companion": mvid, "modlist": loaded_build.fingerprint(rm.get("packageIds") or []), "inventory": inv,
            "settings": settings or {}}


def split_need(n):
    """"tap" or "tap.route" (a tap name may hold a dot: gate.quest.held) -> (tap, route or "")."""
    if n in TAPS:
        return n, ""
    head, _, tail = n.rpartition(".")
    return (head, tail) if head in TAPS else (n, "")


def arm_check(cert, read, needs, settings=None):
    """The check at arm. needs: ["tap.route" | "tap"] that the scene's conditions read. It calls read() with ARM_READS only.
    -> {"verdict", "mode", "routes": {need: covered | not shown | uncertified | blind}, "reasons", "receipt"}"""
    def guarded(tool, args):
        if tool not in ARM_READS:
            raise RuntimeError("the arm check may not call %s" % tool)
        return read(tool, args)
    out = {"verdict": ARMED, "mode": BOOTSTRAP, "routes": {}, "reasons": [], "receipt": []}
    ident = read_identity(guarded, settings)
    if ident is None:
        out.update(verdict=COULD_NOT_LOOK, reasons=["the loaded identity could not be read"])
        out["routes"] = {n: "could not look" for n in needs}
        return out
    state, why = validate(cert, ident)
    if state != "valid":
        out["verdict"] = COULD_NOT_LOOK if state == "could not look" else COULD_NOT_ARM
        out["reasons"] = why
        out["routes"] = {n: "could not look" if state == "could not look" else "uncertified" for n in needs}
        return out
    cov = coverage(cert)
    for n in needs:
        tap, route = split_need(n)
        t = TAPS.get(tap)
        if t is None:
            out["routes"][n] = "uncertified"
            out["reasons"].append("%s: no such tap" % n)
            continue
        ours = all(any(is_ours(r.get("owner")) for r in ident["inventory"].get("%s.%s" % m, [])) for m in t["methods"])
        if not ours:
            out["routes"][n] = "blind"
            out["reasons"].append("%s: our hook is not on %s" % (n, ", ".join("%s.%s" % m for m in t["methods"])))
            continue
        routes = [route] if route else t["routes"]
        miss = [r for r in routes if r not in cov.get(tap, {}).get("covered", [])]
        out["routes"][n] = "covered" if not miss else "not shown"
        if miss:
            out["reasons"].append("%s: route(s) not shown by the certificate: %s" % (n, ", ".join(miss)))
    out["receipt"] = receipt_foreign(cert, sorted({split_need(k)[0] for k in needs}))
    if any(v != "covered" for v in out["routes"].values()):
        out["verdict"] = COULD_NOT_ARM
    else:
        out["mode"] = CERTIFIED
    return out


def receipt_mode(arm):
    return CERTIFIED if isinstance(arm, dict) and arm.get("verdict") == ARMED and arm.get("mode") == CERTIFIED else BOOTSTRAP


def witness(close):
    """A run's close record -> {hook: "ok" | "void: N entries with no record"}. Reads close.cast.taps.hooks and
    close.world.taps.hooks; each row's runEntered and runCommitted count this run only (JawaBenchHookGuard.Mark at Join).
    An entry with no record (the original was skipped, or the postfix never ran) voids that tap's coverage for the run.
    A hook row without the two counts is "could not look", never "ok"."""
    out = {}
    for fam in ("cast", "world"):
        for h in (((close or {}).get(fam) or {}).get("taps") or {}).get("hooks") or []:
            e, c = h.get("runEntered"), h.get("runCommitted")
            if not isinstance(e, int) or not isinstance(c, int):
                out[h.get("hook")] = "could not look"
            elif e > c:
                out[h.get("hook")] = "void: %d entries with no record" % (e - c)
            else:
                out[h.get("hook")] = "ok"
    return out


def run_coverage(cert, close):
    """coverage(cert) for this run: a tap whose hook the witness voided covers nothing in this run."""
    cov = coverage(cert)
    w = witness(close)
    for tap, t in TAPS.items():
        if any(w.get(h, "ok") != "ok" for h in t["hooks"]) and tap in cov:
            cov[tap] = {"covered": [], "not_shown": cov[tap]["covered"] + cov[tap]["not_shown"], "void": [w[h] for h in t["hooks"] if w.get(h, "ok") != "ok"]}
    return cov


def absence(cert, tap, route):
    """May a judge read "this did not happen" on this tap and route? A foreign prefix on the method can skip the original in
    this run as it did not in the session: such an absence is not provable here."""
    cov = coverage(cert).get(tap)
    if not cov or route not in cov["covered"]:
        return "not covered"
    if _prefixes(cert, tap):
        return NOT_PROVABLE
    return "provable"


# ------------------------------------------------------------------------------------------------ the committed live result
def audit(path=RESULT):
    """-> (rc, line). The live result of prove_tap_certificate.py: rows of the session and the certificate it made."""
    try:
        with open(path, encoding="utf-8") as f:
            res = json.load(f)
    except FileNotFoundError:
        return 1, "FAIL no live result at %s: prove_tap_certificate.py has not run" % os.path.relpath(path, REPO)
    except (OSError, ValueError) as e:
        return 2, "COULD NOT LOOK %s: %s" % (path, e)
    cert = res.get("certificate") or {}
    bad = []
    if cert.get("schema") != SCHEMA or cert.get("by") != "prove_tap_certificate.py":
        bad.append("the result holds no certificate made by prove_tap_certificate.py")
    for name in TAPS:
        t = (cert.get("taps") or {}).get(name)
        if t is None:
            bad.append("tap %s is not on the certificate" % name)
        elif t.get("not_shown"):
            bad.append("tap %s: route(s) not shown: %s" % (name, ", ".join(t["not_shown"])))
    if not (cert.get("blind") or {}).get("reported"):
        bad.append("the planted blind tap was not reported blind")
    if not (cert.get("key") or {}).get("companion"):
        bad.append("the certificate names no loaded companion")
    if bad:
        return 1, "FAIL tap certificate: " + "; ".join(bad)
    return 0, "PASS tap certificate made %s on %s: %d taps, every route shown, blind tap %s reported" % (
        res.get("made"), cert.get("game"), len(TAPS), (cert.get("blind") or {}).get("tap"))


def main(argv):
    if argv[:1] == ["audit"]:
        rc, line = audit(argv[1] if len(argv) > 1 else RESULT)
        print(line)
        return rc
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
