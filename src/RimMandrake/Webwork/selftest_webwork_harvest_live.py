"""Offline proof for CREEP_WEB_HARVEST_LIVE_1: the live proof's verdicts read the probe's real reply shapes right,
the committed Webwork DLL matches its .srchash, and the defs still promise the yields the live clauses expect."""
import json
import os
import subprocess
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import webwork_harvest_live_proof as P  # noqa: E402

FAILS = []


def check(cond, what):
    if not cond:
        FAILS.append(what)


def wrap(s):
    """jawa/static_call answers a dict; the proof json-dumps it, so test that shape too."""
    return json.dumps({"success": True, "result": s})


A1_OK = "HARVEST designatable True (after 2 ticks) | workgiver True | yield 3 | weaveNear 0->3 | spawned 1"
for text in (A1_OK, wrap(A1_OK)):
    check(P.verdict("A1", text)[0] == 0, "A1 pass shape not passed: %s" % (P.verdict("A1", text),))
check(P.verdict("A1", A1_OK.replace("spawned 1", "spawned 0"))[0] == 1, "A1 with no emergent spawn passed")
check(P.verdict("A1", A1_OK.replace("yield 3", "yield 0"))[0] == 1, "A1 yield 0 passed")
check(P.verdict("A1", A1_OK.replace("workgiver True", "workgiver False"))[0] == 1, "A1 workgiver False passed")
fog = "HARVEST designatable False (after 250 ticks) | workgiver False | yield 3 | weaveNear 0->3 | spawned 0"
check(P.verdict("A1", fog)[0] == 2, "a fog timeout scored as a mod result")
check(P.verdict("A1", "REFUSED: no current map")[0] == 2, "REFUSED not UNMEASURED")
check(P.verdict("A1", "")[0] == 2, "empty reply not UNMEASURED")

A2_OK = "HARVEST designatable True (after 0 ticks) | workgiver True | yield 2 | weaveNear 0->2 | spawned 0"
check(P.verdict("A2", wrap(A2_OK))[0] == 0, "A2 pass shape not passed")
check(P.verdict("A2", A2_OK.replace("0->2", "0->0"))[0] == 1, "A2 no silk on the ground passed")

A3_OK = "HARVEST designatable False (after 250 ticks) | workgiver False | yield 0 | weaveNear 0->0 | spawned 0"
check(P.verdict("A3", wrap(A3_OK))[0] == 0, "A3 (harvest off) pass shape not passed — a designator refusal is the PASS here")
check(P.verdict("A3", A3_OK.replace("designatable False", "designatable True"))[0] == 1, "A3 off but designatable passed")

A4_OK = "READ nodePresent False | weaveNear 3 | lastYield 3"
check(P.verdict("A4", wrap(A4_OK))[0] == 0, "A4 pass shape not passed")
check(P.verdict("A4", "READ nodePresent True | weaveNear 0 | lastYield 3")[0] == 1, "A4 uncut node passed")
check(P.verdict("A4", "READ nodePresent False | weaveNear 3 | lastYield 0")[0] == 1, "A4 lastYield 0 passed")

# every field each clause reads is pinned here, independent of the proof's want-dicts: breaking any one value in a
# pass line must FAIL (exit 1), so dropping a key from a want-dict turns this selftest red (blind check, gen 1)
PINS = {
    "A1": (A1_OK, [("designatable", "True", "False"), ("workgiver", "True", "False"), ("yield", "3", "0"),
                   ("weaveNear", "0->3", "0->0"), ("weaveNear", "0->3", "0->2"), ("spawned", "1", "0")]),
    "A2": (A2_OK, [("yield", "2", "3"), ("weaveNear", "0->2", "0->0"), ("spawned", "0", "1")]),
    "A3": (A3_OK, [("designatable", "False", "True"), ("yield", "0", "3")]),
    "A4": (A4_OK, [("nodePresent", "False", "True"), ("weaveNear", "3", "0"), ("weaveNear", "3", "2"),
                   ("lastYield", "3", "0")]),
}
for clause, (ok, muts) in PINS.items():
    for key, good, bad in muts:
        lead = "| " if not ok.startswith(("HARVEST %s " % key, "READ %s " % key)) else ok.split(" ")[0] + " "
        old, new = "%s%s %s" % (lead, key, good), "%s%s %s" % (lead, key, bad)
        check(ok.count(old) == 1, "pin %s %s: %r not once in the pass line" % (clause, key, old))
        got = P.verdict(clause, wrap(ok.replace(old, new)))
        check(got[0] == 1, "%s passed with %s %s (want %s): %s" % (clause, key, bad, good, got))

# A4 walk against a fake bridge (gen 8; the gen 5/6 attribution): the no-cut FAIL must need a vetted colonist AND
# >= 4000 MEASURED game ticks. A proof that counts requested ticks, or ignores unforcedJob/awake, goes red here.
D_OK = ("DESIGNATED 150,159 | designatable True (after 0 ticks) | colonist Ava | unforcedJob True | awake True"
        " | curJob Wait_Wander")
D_OLD = "DESIGNATED 150,159 | designatable True (after 0 ticks) | colonist Ava"  # the 097710e DLL's reply


class FakeRB:
    """A game: step_game_ticks advances TicksGame by min(asked, deliver) + extra; a colonist cuts the anchor at cut_at."""

    def __init__(self, designate=D_OK, deliver=500, cut_at=None, clock=True, read_ok=True, extra=0):
        self.t, self.t0, self.deliver, self.cut_at, self.clock, self.extra = 1000, 1000, deliver, cut_at, clock, extra
        self.designate, self.read_ok, self.asked = designate, read_ok, []

    def call(self, name, args):
        if name == "rimworld/step_game_ticks":
            self.asked.append(args["ticks"])
            self.t += min(args["ticks"], self.deliver) + self.extra
            return {"success": True}
        if name == "jawa/time_clock":
            return {"success": True, "ticksGame": self.t} if self.clock else {"success": False, "error": "no game"}
        if args["method"] == "ProofHarvestDesignate":
            return {"success": True, "result": self.designate}
        cut = self.cut_at is not None and self.t - self.t0 >= self.cut_at
        y = "3" if self.read_ok else "0"
        return {"success": True, "result": "READ nodePresent %s | weaveNear %s | lastYield %s"
                % (not cut, y if cut else "0", y if cut else "0")}


def a4(**kw):
    rb = FakeRB(**kw)
    return P.run("A4", rb, None), rb


WALK = [  # (fake game, want exit code, what it shows)
    (dict(cut_at=1500), 0, "a vetted colonist cuts it at 1500 measured ticks: PASS"),
    (dict(cut_at=None), 1, "4000 measured ticks, vetted colonist, no cut: FAIL (the mod route)"),
    (dict(cut_at=1500, read_ok=False), 1, "cut but no Hyperweave on the ground: FAIL"),
    (dict(cut_at=None, deliver=50), 2, "step_game_ticks under-delivers (50/500): a no-cut is UNMEASURED, not FAIL"),
    (dict(cut_at=None, deliver=0), 2, "the clock never moves: UNMEASURED"),
    (dict(cut_at=None, clock=False), 2, "no ticksGame: UNMEASURED"),
    (dict(cut_at=4500, extra=4500), 2, "cut seen only after an over-delivered 5000 ticks: within-4000 unproven"),
    (dict(designate=D_OLD, cut_at=None), 2, "a DLL that does not vet the colonist: UNMEASURED"),
    (dict(designate=D_OK.replace("awake True", "awake False"), cut_at=None), 2, "asleep colonist: UNMEASURED (SITE)"),
    (dict(designate=D_OK.replace("unforcedJob True", "unforcedJob False"), cut_at=1500), 1,
     "WorkGiver_Deconstruct refuses an unforced job to a vetted colonist: FAIL even if something else cut it"),
    (dict(designate=D_OK.replace("designatable True", "designatable False")), 1, "designator refused: FAIL"),
]
for kw, want, what in WALK:
    (code, why), rb = a4(**kw)
    check(code == want, "A4 walk %s: got %d want %d: %s" % (what, code, want, why[:200]))
# an UNMEASURED must name its own cause, so one guard cannot stand in silently for another
REASON = [(dict(designate=D_OLD), "predates the colonist vetting"), (dict(clock=False), "gave no ticksGame"),
          (dict(designate=D_OK.replace("awake True", "awake False")), "not awake"),
          (dict(deliver=50), "ran only"), (dict(cut_at=4500, extra=4500), "within-limit unproven")]
for kw, want in REASON:
    (code, why), rb = a4(**kw)
    check(code == 2 and want in why, "A4 UNMEASURED %s does not say %r: %s" % (kw, want, why[:200]))
(code, why), rb = a4(cut_at=None, deliver=50)
check(rb.t - rb.t0 < P.WALK_MAX and "measured" in why, "under-delivery walk did not report its measured ticks: " + why)
(code, why), rb = a4(cut_at=None)
check(sum(rb.asked) == P.WALK_MAX and rb.t - rb.t0 == P.WALK_MAX, "full walk asked %s ticks, ran %d"
      % (sum(rb.asked), rb.t - rb.t0))
check("4000 measured ticks" in why and "curJob" in why, "A4 FAIL does not carry the ticks and colonist state: " + why)

loaded = wrap("REFUSED: no current map")
log = "RimWorld 1.6.4633 rev1261\nLoading mandrake.rm.webwork\n"
check(P.log_verdict(log, loaded)[0] == 0, "clean log not passed")
for bad in P.LOG_FORBIDDEN:
    check(P.log_verdict(log + "Config error in RM_Webwork_Anchor: " + bad + "\n", loaded)[0] == 1, "missed: " + bad)
clash = "Config error in RM_Webwork_Web: alwaysDeconstructible=true but deconstructible=false\n"
check(P.log_verdict(log + clash, loaded)[0] == 1, "missed the deconstructible clash on a Webwork def")
check(P.log_verdict(log + clash.replace("RM_Webwork_Web", "SomeoneElse_Def"), loaded)[0] == 0,
      "a clash on another mod's def failed the Webwork clause")
check(P.log_verdict(log, wrap("REFUSED: Could not find type RimMandrake.Webwork.RM_WebworkProof"))[0] == 2,
      "a clean log with Webwork not loaded passed")
check(P.log_verdict("", loaded)[0] == 2, "an empty log passed")

# the committed DLL is the one its sources stamp
r = subprocess.run([sys.executable, os.path.join(REPO, "src/RimMandrake/Utils/dll_source_stamp.py"), "check"],
                   cwd=REPO, capture_output=True, text=True, timeout=300)
check("MATCH src/RimMandrake/Webwork/Assemblies/RimMandrake.Webwork.dll" in r.stdout.splitlines(),
      "Webwork DLL is not MATCH in dll_source_stamp: " + (r.stdout + r.stderr)[-400:])

# the defs promise what A1/A2 expect: Anchor 3, Web 2 Hyperweave, both deconstructible-harvestable
root = ET.parse(os.path.join(REPO, "src/RimMandrake/Webwork/Defs/ThingDefs_Buildings/RM_WebworkStructures.xml")).getroot()
yields = {}
for d in root.findall("ThingDef"):
    for li in d.findall("comps/li"):
        if li.get("Class") == "RimMandrake.Webwork.RM_CompProperties_HarvestYield":
            yields[d.findtext("defName")] = (li.findtext("yield"), li.findtext("count"))
check(yields.get("RM_Webwork_Anchor") == ("Hyperweave", "3"), "Anchor yield %s" % (yields.get("RM_Webwork_Anchor"),))
check(yields.get("RM_Webwork_Web") == ("Hyperweave", "2"), "Web yield %s" % (yields.get("RM_Webwork_Web"),))

if FAILS:
    print("FAIL selftest_webwork_harvest_live:\n  " + "\n  ".join(FAILS))
    sys.exit(1)
print("PASS selftest_webwork_harvest_live")
