"""Live proofs of CREEP_WEB_HARVEST_LIVE_1 (SHOKKWEAVE_SOLE_SOURCE_1 route 4), one clause per call:

    python.exe src/RimMandrake/Webwork/webwork_harvest_live_proof.py A1|A2|A3|A4|A5

Calls RimMandrake.Webwork.RM_WebworkProof through jawa/static_call on the current (quicktest) map.
jawa/static_call splits its args on '|' into parameters, so every one-string proof argument is sent with ';'.
Exit 0 = the clause holds, 1 = it answered and something is wrong, 2 = UNMEASURED (no bridge, REFUSED, no line).
  A1 anchor   ProofHarvest "true;RM_Webwork_Anchor;34": designatable True, workgiver True, yield 3,
              weaveNear 0->3, spawned 1 (a sure emergent ollathrix)
  A2 web      ProofHarvest "true;RM_Webwork_Web;0": yield 2, weaveNear 0->2, spawned 0
  A3 off      ProofHarvest "false;RM_Webwork_Anchor;0": designatable False, yield 0
  A4 walk     ProofHarvestDesignate "RM_Webwork_Anchor" beside an awake colonist able to construct (the DESIGNATED
              line must read unforcedJob True | awake True), step in 500-tick steps until the node is gone or
              jawa/time_clock shows 4000 game ticks MEASURED, then ProofHarvestRead "x,z": nodePresent False,
              weaveNear 3, lastYield 3 (a real colonist cut it with vanilla Deconstruct). A no-cut under 4000
              measured ticks is UNMEASURED, never FAIL.
  A5 log      Player.log (this load, with RimMandrake.Webwork loaded) names none of the three load errors
verdict(), designate_verdict() and log_verdict() are pure, walk() takes any rb and are exercised offline by selftest_webwork_harvest_live.py.
"""
import json
import os
import re
import sys

PROBE = "RimMandrake.Webwork.RM_WebworkProof"
CLAUSES = ("A1", "A2", "A3", "A4", "A5")
ARGS = {"A1": "true;RM_Webwork_Anchor;34", "A2": "true;RM_Webwork_Web;0", "A3": "false;RM_Webwork_Anchor;0"}
WALK_STEP, WALK_MAX, WALK_CALLS = 500, 4000, 40  # 40 calls: room for 4x under-delivery
LOG_FORBIDDEN = (
    "RM_CompProperties_HarvestYield has no yield",
    "Could not find type named RimMandrake.Webwork.RM_CompProperties_HarvestYield",
)
DECON_CLASH = re.compile(r"RM_Webwork_\S*.{0,200}?alwaysDeconstructible=true but deconstructible=false"
                         r"|alwaysDeconstructible=true but deconstructible=false.{0,200}?RM_Webwork_")


def field(text, key):
    """The token after `key ` in a proof line (the next ' |' ends it), or None."""
    m = re.search(r"(?:^|\| |HARVEST |READ |DESIGNATED )%s ([^|\"\\]*)" % re.escape(key), str(text))
    return m.group(1).strip().split(" (")[0].strip() if m else None


def verdict(clause, text):
    """-> (exit code, reason) for a ProofHarvest (A1-A3) or ProofHarvestRead (A4) reply text."""
    s = str(text)
    if "REFUSED" in s:
        return 2, "probe refused: " + s[s.find("REFUSED"):][:300]
    want = {
        "A1": {"designatable": "True", "workgiver": "True", "yield": "3", "weaveNear": "0->3", "spawned": "1"},
        "A2": {"yield": "2", "weaveNear": "0->2", "spawned": "0"},
        "A3": {"designatable": "False", "yield": "0"},
        "A4": {"nodePresent": "False", "weaveNear": "3", "lastYield": "3"},
    }[clause]
    head = "READ" if clause == "A4" else "HARVEST"
    m = re.search(r"%s [^\"\\]*" % head, s)
    if not m:
        return 2, "no %s line: %s" % (head, s[:300])
    line = m.group(0)
    if clause in ("A1", "A2"):
        after = re.search(r"designatable False \(after (\d+) ticks\)", line)
        if after and int(after.group(1)) >= 250:
            return 2, "HARNESS/SITE: fog of war hid the node from the designator for the whole wait: " + line
    fails = ["%s %s (want %s)" % (k, field(line, k), v) for k, v in want.items() if field(line, k) != v]
    return (1, "; ".join(fails) + " | " + line) if fails else (0, line)


def log_verdict(log_text, type_reply):
    """-> (exit code, reason). type_reply is the static_call answer that proves RimMandrake.Webwork loaded."""
    r = str(type_reply)
    if not ("READ " in r or "no current map" in r):
        return 2, "RimMandrake.Webwork not reachable in this game (a clean log would prove nothing): " + r[:200]
    if not log_text or "RimWorld" not in log_text:
        return 2, "Player.log empty or unreadable"
    hits = [s for s in LOG_FORBIDDEN if s in log_text]
    m = DECON_CLASH.search(log_text)
    if m:
        hits.append(m.group(0)[:200])
    return (1, "Player.log names: " + " || ".join(hits)) if hits else (0, "Player.log clean of the three harvest load errors")


def _reply(out):
    """The probe's string out of a jawa/static_call reply (dict or text)."""
    return json.dumps(out) if not isinstance(out, str) else out


def _read_log(R):
    for p in R._player_log_candidates():
        if p and os.path.isfile(p):
            with open(p, encoding="utf-8", errors="replace") as fh:
                return fh.read()
    return ""


def designate_verdict(d):
    """-> (code, reason, cell). The DESIGNATED reply must show a vetted colonist who would take the job unforced:
    without `unforcedJob`/`awake` the deployed DLL predates the colonist vetting (b2f8c3c1) and a no-cut would say
    nothing about the mod (gen 5/6 attribution: an unvetted, asleep or Construction-off colonist)."""
    m = re.search(r"DESIGNATED (\d+),(\d+) \| designatable (\w+)", d)
    if not m:
        return 2, "designate gave no cell: " + d[:300], None
    if m.group(3) != "True":
        return 1, "the Deconstruct designator refused the anchor beside a colonist: " + d[:300], None
    job, awake = field(d, "unforcedJob"), field(d, "awake")
    if job is None or awake is None:
        return 2, "HARNESS: DESIGNATED names no unforcedJob/awake: the deployed Webwork DLL predates the colonist " \
                  "vetting, so a no-cut could not be told from an unwilling colonist: " + d[:300], None
    if awake != "True":
        return 2, "SITE: the chosen colonist is not awake after WakeUp, he cannot walk to it: " + d[:300], None
    if job != "True":
        return 1, "WorkGiver_Deconstruct.HasJobOnThing(forced: false) is False for an awake colonist who can " \
                  "construct, Construction on: no colonist would ever cut it: " + d[:300], None
    return 0, d, "%s,%s" % (m.group(1), m.group(2))


def ticks_now(rb):
    """TicksGame from jawa/time_clock, or None when the clock cannot be read."""
    out = rb.call("jawa/time_clock", {})
    if isinstance(out, str):
        try:
            out = json.loads(out)
        except ValueError:
            return None
    if isinstance(out, dict) and isinstance(out.get("result"), dict):
        out = out["result"]
    v = out.get("ticksGame") if isinstance(out, dict) else None
    return v if isinstance(v, int) and not isinstance(v, bool) else None


def walk(rb, call):
    """A4: designate, then step until the node is gone or the game has MEASURABLY run WALK_MAX ticks
    (TicksGame read before and after every step; step_game_ticks may under-deliver, lesson 20261021T032330Z).
    A no-cut counts as FAIL only after a vetted colonist and >= WALK_MAX measured ticks; otherwise UNMEASURED."""
    d = call("ProofHarvestDesignate", "RM_Webwork_Anchor")
    code, why, cell = designate_verdict(d)
    if code:
        return code, why
    t0 = ticks_now(rb)
    if t0 is None:
        return 2, "HARNESS: jawa/time_clock gave no ticksGame, the walk cannot measure the ticks it ran"
    read, ran = "", 0
    for _ in range(WALK_CALLS):
        rb.call("rimworld/step_game_ticks", {"ticks": min(WALK_STEP, WALK_MAX - ran)})
        t = ticks_now(rb)
        if t is None:
            return 2, "HARNESS: jawa/time_clock stopped answering mid-walk after %d measured ticks" % ran
        ran = t - t0
        read = call("ProofHarvestRead", cell)
        if field(read, "nodePresent") == "False" or ran >= WALK_MAX:
            break
    tail = " (after %d measured ticks, TicksGame %d->%d; %s)" % (ran, t0, t0 + ran, d[:200])
    if field(read, "nodePresent") == "False" and ran > WALK_MAX:
        return 2, "cut, but only seen after %d measured ticks > %d: within-limit unproven%s" % (ran, WALK_MAX, tail)
    if field(read, "nodePresent") != "False" and ran < WALK_MAX:
        return 2, "the game ran only %d of %d ticks in %d steps, a no-cut proves nothing%s" % (
            ran, WALK_MAX, WALK_CALLS, tail)
    code, why = verdict("A4", read)
    return code, why + tail


def run(clause, rb, R):
    call = lambda m, a: _reply(rb.call("jawa/static_call", {"type": PROBE, "method": m, "args": a}))
    if clause in ARGS:
        return verdict(clause, call("ProofHarvest", ARGS[clause]))
    if clause == "A4":
        return walk(rb, call)
    return log_verdict(_read_log(R), call("ProofHarvestRead", "0,0"))


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
