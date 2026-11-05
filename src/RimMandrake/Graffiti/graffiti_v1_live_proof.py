"""Live proofs of GRAFFITI_V1_LIVE_PROOF_1, one clause per call:

    python.exe src/RimMandrake/Graffiti/graffiti_v1_live_proof.py A1|A2|A3|A4|A5|A6|A7|A8

Calls RimMandrake.Graffiti.RM_GraffitiProof through jawa/static_call on the current (quicktest) map; every set-up rebuilds
the same 20x12 walled site at the map centre (see the C# class), so the clauses run in any order.
Exit 0 = the clause holds, 1 = it answered and something is wrong, 2 = UNMEASURED (no bridge, REFUSED, no line).
  A1 spree     SpreeStart forces RM_GraffitiPaintingSpreeState on a colonist, the clock runs up to 3000 ticks, SpreeRead:
               marks >= 1 and every one has factionOk and ideoOk (maker/faction/ideo stamped)
  A2 raid      RaidStart closes and roofs the site's south half into a room, spawns 3 enemy pawns outside the wall and 1
               inside the room under LordJob_AssaultColony (marksIn 0), 120 ticks run, RaidExit moves the lord onto its own
               leaving toil: mid 0 (none on the way in), after >= 1, every tag raidExitEligible, on a wall and exterior
               (outside the room by geometry, unroofed, in the outdoors room); interiorClosed False, inside 0 or outsideOpen False is a SITE
               fault (UNMEASURED). "In its faction's mark": the driver then saves the game (RM_GraffitiA2Proof.rws, deleted after)
               and reads every mark placed since RaidStart's tick: factionOk (makerFaction = the RAID line's faction) must cover
               every exit tag; an unreadable save is UNMEASURED
  A3 sigil     Sigil paints RM_Graffiti_IdeoSigil by a colonist: ideo True, frame halo_0, iconIsIdeo True, tinted True
  A4 over      GoingOver: a colonist's Tag_A, then an enemy's ThrowUp_A on the same cell: firstGone True, marksAtCell 1,
               def RM_Graffiti_ThrowUp_A, rivalFaction True
  A5 thought   HostileThought: an enemy's tag 3 cells from a colonist: makerHostile True, worker True, mood True
  A6 scrub     CleanSetup (own Vandal, enemy Devotional sigil, enemy Vandal control), 700 ticks, CleanRead: unforced own False,
               unforced devotional False, unforced control True, forced own/devotional True, ordered True; then up to
               4000 ticks until CleanDone reads ownGone True and devotionalGone True
  A7 choose    DesignateSetup designates 3 cells with 3 named marks and orders the colonist onto them; up to 6000 ticks until
               DesignateRead reads painted 3, matched 3, pending 0
  A8 load      Player.log of this load (Graffiti reachable, all DLC) names no Graffiti config / cross-reference / XML error
verdict(), field() and log_verdict() are pure and are exercised offline by selftest_graffiti_v1_live.py.
"""
import json
import os
import re
import sys
import time
import xml.etree.ElementTree as ET

PROBE = "RimMandrake.Graffiti.RM_GraffitiProof"
CLAUSES = ("A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8")
STEP = 250
HEADS = ("SPREE", "READ", "RAID", "EXIT", "SIGIL", "OVER", "THOUGHT", "CLEANSET", "CLEAN", "DONE", "DESIGNATED", "LOADED")
WANT = {
    "A3": {"ideo": "True", "frame": "halo_0", "iconIsIdeo": "True", "tinted": "True"},
    "A4": {"placed": "True", "firstGone": "True", "marksAtCell": "1", "def": "RM_Graffiti_ThrowUp_A", "rivalFaction": "True"},
    "A5": {"makerHostile": "True", "worker": "True", "mood": "True"},
    "A6": {"unforcedOwn": "False", "unforcedDevotional": "False", "unforcedControl": "True",
           "forcedOwn": "True", "forcedDevotional": "True", "ordered": "True"},
    "A6done": {"ownGone": "True", "devotionalGone": "True"},
    "A7": {"painted": "3", "matched": "3", "pending": "0"},
}
# a Graffiti-owned load error: an error-kind line that names anything Graffiti (namespace, def prefix, package, or one of
# its XML file names such as ThingDefs_Graffiti.xml) on itself or on its own continuation lines (indented, or a stack frame
# "at ..."), never on the next record. Deliberately wide: an error in a Graffiti family mod (SacredGraffiti, GraffitiImperial)
# loaded beside it fails A8 too.
OURS = re.compile(r"Graffiti|graffiti")
# continuation = indented, a .NET frame "at ...", Unity's "(Filename: ...)", or an unindented Unity frame
# "Namespace.Type:Method (args)" (UnityEngine StackTrace formatter)
CONTINUATION = re.compile(r"^(?:\s|at |\(Filename|\(wrapper |\[Ref |[\w.`<>+\[\],]+:[\w<>.`|$]+ ?\()")
# wide on purpose (a keyword list kept missing wordings: "XML format error", "is not a Def type"): any error, exception,
# failure, could-not, not-found, invalid or duplicate wording counts
ERROR_KIND = re.compile(r"error|exception|fail|could not|couldn't|cannot|not found|could not be found|not a Def type|invalid|"
                        r"duplicate|missing", re.I)


def _text(text):
    """A reply as plain probe text: a JSON-serialised bridge reply is decoded to its `result` string, so neither its
    escaping nor its closing quote reaches a field, and a faction name holding a quote or backslash stays whole."""
    s = str(text)
    if s.lstrip().startswith("{"):
        try:
            d = json.loads(s)
        except ValueError:
            return s
        if isinstance(d, dict) and isinstance(d.get("result"), str):
            return d["result"]
    return s


def field(text, key):
    """The token after `key ` in a probe line (' |' ends it), or None."""
    m = re.search(r"(?:^|\| |\b(?:%s) )%s ([^|\n]*)" % ("|".join(HEADS), re.escape(key)), _text(text))
    return m.group(1).strip() if m else None


def line(text, head):
    """The probe's own line starting with `head` out of a reply text, or None."""
    m = re.search(r"\b%s [^\n]*" % re.escape(head), _text(text))
    return m.group(0) if m else None


def _int(text, key):
    v = field(text, key)
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def _match(text, want):
    return ["%s %s (want %s)" % (k, field(text, k), v) for k, v in want.items() if field(text, k) != v]


SAVE_NAME = "RM_GraffitiA2Proof"


def exit_faction_marks(save_text, faction_name, since_tick):
    """-> (factionOk, sinceMarks, None) or (None, None, why) from a .rws text: of the Filth_Marks placed at or after
    since_tick, how many carry makerFaction = the faction named faction_name (Scribe ref 'Faction_<loadID>'; a loadID of 0
    is the Scribe default and is omitted from the save, so a missing loadID reads 0)."""
    try:
        root = ET.fromstring(save_text)
    except ET.ParseError as ex:
        return None, None, "save does not parse: %s" % ex
    facs = root.find(".//factionManager/allFactions")
    if facs is None:
        return None, None, "save has no factionManager/allFactions"
    ids = ["Faction_" + ((li.findtext("loadID") or "").strip() or "0") for li in facs.findall("li")
           if (li.findtext("name") or "").strip() == faction_name]
    if len(ids) != 1:
        return None, None, "faction %r is named by %d factions in the save" % (faction_name, len(ids))
    since = ok = 0
    for el in root.iter():
        tick = el.findtext("rmMarkPlacedTick")
        if tick is None:
            continue
        try:
            tick = int(tick)
        except ValueError:
            return None, None, "unreadable rmMarkPlacedTick %r" % tick
        if tick < since_tick:
            continue
        since += 1
        if (el.findtext("rmMarkMakerFaction") or "").strip() == ids[0]:
            ok += 1
    return ok, since, None


def verdict(clause, text, extra=None):
    """-> (exit code, reason) for one clause's decisive reply text (A2: the EXIT line with `extra` = the RAID line;
    A6: the CLEAN line with `extra` = the DONE line)."""
    s = str(text)
    if "REFUSED" in s:
        return 2, "probe refused: " + s[s.find("REFUSED"):][:300]
    head = {"A1": "READ", "A2": "EXIT", "A3": "SIGIL", "A4": "OVER", "A5": "THOUGHT", "A6": "CLEAN", "A7": "READ"}[clause]
    ln = line(s, head)
    if not ln:
        return 2, "no %s line: %s" % (head, s[:300])
    if clause == "A1":
        n, f, i = _int(ln, "marks"), _int(ln, "factionOk"), _int(ln, "ideoOk")
        if n is None or f is None or i is None:
            return 2, "unreadable spree read: " + ln
        if n < 1:
            return 1, "the spree left no mark: " + ln
        return (0, ln) if f == n and i == n else (1, "marks without maker faction/ideo: " + ln)
    if clause == "A2":
        raid = line(str(extra), "RAID")
        if not raid or _int(raid, "marksIn") is None:
            return 2, "no RAID line: " + str(extra)[:300]
        fails = []
        if _int(raid, "marksIn") != 0:
            fails.append("marks of the raid faction before it arrived: %s" % field(raid, "marksIn"))
        if _int(ln, "mid") != 0:
            fails.append("tagged on the way in (mid %s)" % field(ln, "mid"))
        after = _int(ln, "after")
        if not after:
            fails.append("no tag when the raid turned to leave (after %s)" % field(ln, "after"))
        elif _int(ln, "eligible") != after or _int(ln, "onWall") != after:
            fails.append("a tag not raidExitEligible or not on a wall")
        elif _int(ln, "exterior") != after:
            fails.append("a tag on an interior wall (exterior %s of %s)" % (field(ln, "exterior"), after))
        if after and _int(ln, "factionOk") is None:
            return 2, "the exit tags' maker faction was not read (no factionOk): " + ln
        if after and _int(ln, "factionOk") < after:
            fails.append("a tag not in the raid faction's mark (factionOk %s of %s)" % (field(ln, "factionOk"), after))
        if _int(ln, "standing") == 0:
            return 2, "SITE: no raider was standing when the exit fired: " + ln
        if field(ln, "interiorClosed") != "True" or not _int(ln, "inside"):
            return 2, "SITE: the roofed interior was not closed or held no raider, so exterior is not tested: " + ln
        if field(ln, "outsideOpen") != "True":
            return 2, "SITE: the raiders' side of the wall is not open outdoors (enclosed terrain), so no exterior face exists: " + ln
        return (1, "; ".join(fails) + " | " + ln) if fails else (0, ln)
    if clause == "A6":
        fails = _match(ln, WANT["A6"])
        if fails:
            return 1, "; ".join(fails) + " | " + ln
        done = line(str(extra), "DONE")
        if not done:
            return 2, "no DONE line: " + str(extra)[:300]
        fails = _match(done, WANT["A6done"])
        return (1, "forced clean left a mark: " + "; ".join(fails) + " | " + done) if fails else (0, ln + " || " + done)
    fails = _match(ln, WANT[clause])
    return (1, "; ".join(fails) + " | " + ln) if fails else (0, ln)


def log_verdict(log_text, loaded_reply):
    """-> (exit code, reason). loaded_reply is the Loaded() answer proving Graffiti is in this game."""
    r = str(loaded_reply)
    ln = line(r, "LOADED")
    if not ln:
        return 2, "RimMandrake.Graffiti not reachable in this game (a clean log would prove nothing): " + r[:200]
    if field(ln, "graffiti") != "True":
        return 2, "the probe answered but does not report Graffiti loaded: " + ln
    if field(ln, "ideology") != "True":
        return 2, "Ideology is not active: every DLC is assumed, restage with all five: " + ln
    if not log_text or "RimWorld" not in log_text:
        return 2, "Player.log empty or unreadable"
    # a record counts when its head is error-worded and any line names Graffiti, or when any of its lines is a Graffiti
    # stack frame (a frame of ours is only printed under an error or exception, whatever its heading looked like)
    # and, whatever the grouping, an error-worded line with Graffiti on it or on any of the next WINDOW lines (RimWorld's
    # own continuations - "Full node:", "Context:", "[Ref ...]" - keep coming in new shapes; a false FAIL here costs a
    # look at the named line, a false PASS certifies a broken load)
    hits = [rec[0].strip()[:200] for rec in _records(log_text)
            if (ERROR_KIND.search(rec[0]) and any(OURS.search(x) for x in rec)) or any(OUR_FRAME.search(x) for x in rec)]
    lines = log_text.splitlines()
    hits += [l.strip()[:200] for i, l in enumerate(lines)
             if ERROR_KIND.search(l) and any(OURS.search(x) for x in lines[i:i + 1 + WINDOW]) and l.strip()[:200] not in hits]
    if hits:
        return 1, "Player.log names %d Graffiti load error line(s): %s" % (len(hits), " || ".join(hits[:5]))
    if field(ln, "thought") != "True" or field(ln, "raidHook") != "True":
        return 1, "the load lacks the hostile-maker thought or the raid-exit hook: " + ln
    return 0, "Player.log clean of Graffiti load errors | " + ln


WINDOW = 3
OUR_FRAME = re.compile(r"(?:^\s*at |^)RimMandrake\.Graffiti\.[\w.`<>+]+[:.][\w<>`]+ ?\(")


def _records(log_text):
    """Player.log split into records: a line plus the continuation lines (indented / stack frames) that follow it."""
    recs = []
    for l in log_text.splitlines():
        if recs and CONTINUATION.match(l):
            recs[-1].append(l)
        else:
            recs.append([l])
    return recs


def _reply(out):
    """The probe's own string out of a jawa/static_call reply: the dict's `result` when it is one (so a non-ASCII faction
    name is never JSON-escaped into a backslash that ends a field), else the whole reply as unescaped JSON text."""
    if isinstance(out, str):
        return out
    if isinstance(out, dict) and isinstance(out.get("result"), str):
        return out["result"]
    return json.dumps(out, ensure_ascii=False)


def _exit_factions(rb, R, faction_name, since):
    """' | factionOk N | sinceMarks M' read from a fresh save of this game, or ' | factionUnread <why>' (verdict A2 then
    says UNMEASURED)."""
    if not faction_name or not isinstance(since, int):
        return " | factionUnread no RAID faction or RaidStart tick"
    dirs = [os.path.join(os.path.dirname(p), "Saves") for p in R._player_log_candidates() if p]
    t0 = time.time() - 2
    r = rb.call("rimworld/save_game", {"saveName": SAVE_NAME})
    paths = ([r["path"]] if isinstance(r, dict) and isinstance(r.get("path"), str) else []) + \
        [os.path.join(d, SAVE_NAME + ".rws") for d in dirs]
    for _ in range(20):  # the write is not instant
        fresh = [p for p in paths if os.path.isfile(p) and os.path.getmtime(p) >= t0 and os.path.getsize(p) > 1000]
        if fresh:
            time.sleep(1.0)
            with open(fresh[0], encoding="utf-8", errors="replace") as fh:
                text = fh.read()
            try:
                os.remove(fresh[0])
            except OSError:
                pass
            ok, n, why = exit_faction_marks(text, faction_name, since)
            if ok is None:
                return " | factionUnread " + why.replace("|", "/")
            return " | factionOk %d | sinceMarks %d" % (ok, n)
        time.sleep(0.5)
    return " | factionUnread no fresh %s.rws in %s" % (SAVE_NAME, "; ".join(paths).replace("|", "/"))


def _read_log(R):
    for p in R._player_log_candidates():
        if p and os.path.isfile(p):
            with open(p, encoding="utf-8", errors="replace") as fh:
                return fh.read()
    return ""


def _until(rb, call, method, done, limit):
    """Step the clock in STEP-tick slices up to `limit`, reading `method` after each; -> (last reply, ticks stepped)."""
    read, stepped = call(method), 0
    while not done(read) and stepped < limit:
        rb.call("rimworld/step_game_ticks", {"ticks": STEP})
        stepped += STEP
        read = call(method)
    return read, stepped


def run(clause, rb, R):
    last = {}

    def call(m, a="x"):  # static_call reads "" as ZERO params; every probe method takes one string
        last["out"] = rb.call("jawa/static_call", {"type": PROBE, "method": m, "args": a})
        return _reply(last["out"])

    if clause == "A1":
        s = call("SpreeStart")
        sp = line(s, "SPREE")
        if not sp or "REFUSED" in s:
            return verdict("A1", s) if "REFUSED" in s else (2, "no SPREE line: " + s[:300])
        if field(sp, "started") != "True":
            return 1, "the spree did not start: " + sp
        read, ticks = _until(rb, call, "SpreeRead", lambda r: (_int(line(r, "READ") or "", "marks") or 0) >= 1, 3000)
        code, why = verdict("A1", read)
        return code, "%s (after %d ticks)" % (why, ticks)
    if clause == "A2":
        raid = call("RaidStart")
        if "REFUSED" in raid:
            return verdict("A2", raid)
        since = last["out"].get("ticksGame") if isinstance(last["out"], dict) else None
        rb.call("rimworld/step_game_ticks", {"ticks": 120})
        ex = call("RaidExit")
        ln = line(ex, "EXIT")
        if ln and "REFUSED" not in ex:
            ex = ln + _exit_factions(rb, R, field(line(raid, "RAID") or "", "faction"), since)
        return verdict("A2", ex, extra=raid)
    if clause in ("A3", "A4", "A5"):
        return verdict(clause, call({"A3": "Sigil", "A4": "GoingOver", "A5": "HostileThought"}[clause]))
    if clause == "A6":
        s = call("CleanSetup")
        if "REFUSED" in s:
            return verdict("A6", s)
        rb.call("rimworld/step_game_ticks", {"ticks": 700})
        clean = call("CleanRead")
        cl = line(clean, "CLEAN")
        if not cl or _match(cl, WANT["A6"]):
            return verdict("A6", clean, extra="")
        done, ticks = _until(rb, call, "CleanDone",
                             lambda r: field(r, "ownGone") == "True" and field(r, "devotionalGone") == "True", 4000)
        code, why = verdict("A6", clean, extra=done)
        return code, "%s (after %d ticks)" % (why, ticks)
    if clause == "A7":
        s = call("DesignateSetup")
        d = line(s, "DESIGNATED")
        if not d:
            return verdict("A7", s)
        if _int(d, "ordered") != 3:
            return 1, "3 designated cells did not each become a colonist's job: " + d
        read, ticks = _until(rb, call, "DesignateRead", lambda r: _int(line(r, "READ") or "", "pending") == 0, 6000)
        code, why = verdict("A7", read)
        return code, "%s (after %d ticks; %s)" % (why, ticks, d[:160])
    return log_verdict(_read_log(R), call("Loaded"))


def main(argv):
    if len(argv) != 2 or argv[1] not in CLAUSES:
        print(__doc__)
        return 2
    clause = argv[1]
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Utils"))
    try:
        import rimbridge_client as R
        host, port, token = R.resolve_endpoint()
        if not token:
            print("UNMEASURED: no bridge token")
            return 2
        with R.RimBridge(host, port, token, timeout=180) as rb:
            code, why = run(clause, rb, R)
    except Exception as ex:  # any transport failure means the proof could not see
        print("UNMEASURED: bridge call failed: %s" % str(ex)[:300])
        return 2
    print("%s %s: %s" % (clause, {0: "PASS", 1: "FAIL", 2: "UNMEASURED"}[code], why))
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv))
