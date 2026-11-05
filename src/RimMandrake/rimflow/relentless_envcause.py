"""relentless_envcause.py -- why a live proof read UNMEASURED, when the reason is the ENVIRONMENT, not the build.

UNMEASURED_LANE_REWIRE_STOP_REBUILDING_SITES (owner 2026-11-05: "fix class not instance"; standing ruling "Fix it and
check it yourself"): a clause that measured nothing because its mod was not deployed or not in the running load, a reload
on another list was owed, the proof read a record no lane step writes, the proof's own call is broken or the harness
failed, went back through proof_weak / attribution / unhold cycles to new builder generations that could change none of
it (census 2026-11-05: 30 live items, ~105M tokens; MODCHECK_DONOR_ENVIRONMENTS_1 spent 12 generations because no lane
step ever ran `modcheck run Armoury`).

classify(row) -> None (not an environment cause: the old roads stand) or an Env:
  kind  deploy | load | produce   the game lane fixes it itself, ONCE (fix is set), then re-reads
        proof_call | harness | proof_or_site   nothing the lane can do: routed ONCE to one fixer, the item waits
  mods  mod folders or packageIds the next load must deploy / enable
  cmd   the producer to run on the up game before the re-read (kind produce)
  fp    the cause's key (relentless_live.cause: no paths, numbers or times), so the same cause is never tried twice
Never a builder and never a new generation for any of them (relentless_game._env)."""
import hashlib
import re

FIX_KINDS = ("deploy", "load", "produce")
ROUTE_KINDS = ("proof_call", "harness", "proof_or_site")
KINDS = FIX_KINDS + ROUTE_KINDS

# relentless_live's own words (deploy_gap, mod_gap, the round's defect head); every pattern is from a runs.jsonl row
PLAN_OMITS = re.compile(r"the deploy plan does not cover (?P<mods>[\w, ]+?): name it in --deploy")
PLAN_SAYS = re.compile(r"not deployed: the plan says (?P<plan>.+)")
PLAN_OFF = re.compile(r"(\w+): (?:not enabled in ModsConfig|NOT DEPLOYED)")
NO_PKG = re.compile(r"(?P<mod>\w+) has no readable packageId in its deployed About\.xml")
NOT_LOADED = re.compile(r"not in the running load: (?P<list>.+)")
RELOAD_HOLDS = re.compile(r"reload needed: restart on a list .*?that holds (?P<holds>[^;]+)")
LOAD_LACKS = re.compile(r"the running load lacks (?P<pkg>[\w.]+)")
TIER_LACKS = re.compile(r"not loaded on this tier")
# env_verify_check.py: no fresh `modcheck run <Mod>` verdict in infrastructure/state/modcheck_status.json
NO_VERDICT = re.compile(r"UNMEASURED (?P<mod>\w+): (?:no modcheck_status entry|entry hash \S+ is not the mod's current|"
                        r"entry \(ts [^)]*\) does not postdate)")
PROOF_CALL = ("the proof's own call is broken", "the proof crashed")
HARNESS = ("harness fault", "site not prepared", "the proof timed out", "bridge call failed",
           "the running load's mod list could not be read")
DEFECT = "proof or site defect"     # relentless_live.DEFECT
PKG = re.compile(r"\(([\w.]+)\)")
PRODUCER = "python.exe src/RimMandrake/Utils/modcheck/cli.py run %s --gate off --purpose fix --item %s"


class Env(dict):
    __getattr__ = dict.get


def _key(kind, why):
    import relentless_live
    return hashlib.sha1(("%s\x1f%s" % (kind, relentless_live.cause(why))).encode("utf-8", "replace")).hexdigest()[:16]


def _env(kind, row, mods=(), cmd=None):
    why = row.get("why") or ""
    return Env(kind=kind, fix=kind in FIX_KINDS, mods=sorted(set(m for m in mods if m)), cmd=cmd,
               criterion=row.get("criterion"), why=why, log=row.get("log"), fp=_key(kind, why))


def classify(row, item=None):
    """A runs.jsonl UNMEASURED row -> Env, or None when its cause is not the environment's (a stale build, a first dud,
    a final wait, no game yet: the lane's old roads)."""
    if not row or row.get("outcome") != "UNMEASURED":
        return None
    why = row.get("why") or ""
    m = NO_PKG.search(why)
    if m:       # the deployed tree lacks its About.xml: a redeploy of the tree writes it
        return _env("deploy", row, [m.group("mod")])
    m = PLAN_OMITS.search(why)
    if m:
        return _env("deploy", row, [x.strip() for x in m.group("mods").split(",")])
    m = PLAN_SAYS.search(why)
    if m:
        return _env("deploy", row, PLAN_OFF.findall(m.group("plan")))
    m = NO_VERDICT.search(why)
    if m:       # the proof reads a verdict only `modcheck run` writes, and no lane step ran it
        return _env("produce", row, cmd=PRODUCER % (m.group("mod"), item or row.get("item") or "?"))
    m = LOAD_LACKS.search(why)
    if m:
        return _env("load", row, [m.group("pkg")])
    m = RELOAD_HOLDS.search(why)
    if m:
        return _env("load", row, [x.strip() for x in m.group("holds").split(",")])
    m = NOT_LOADED.search(why)
    if m:
        return _env("load", row, PKG.findall(m.group("list")) or re.findall(r"\w+", m.group("list"))[:1])
    if TIER_LACKS.search(why):
        return _env("load", row)
    if any(w in why for w in PROOF_CALL):
        return _env("proof_call", row)
    if any(why.startswith(w) or (": %s" % w) in why for w in HARNESS):
        return _env("harness", row)
    if why.startswith(DEFECT) or row.get("defect"):
        return _env("proof_or_site", row)
    return None


def dud(row, item=None):
    """A row the lane's dud rules (relentless_game.not_measuring / blocked_here) already stopped on: a proof that ran
    and measured nothing, again. With no named cause of its own it is the proof's or its site's, never the build's."""
    return classify(row, item) or (_env("proof_or_site", row) if row and row.get("outcome") == "UNMEASURED" else None)


def line(e):
    return "%s %s (%s%s%s): %s" % (e.criterion or "?", e.kind, ", ".join(e.mods) or "no mod named",
                                   ("; " + e.cmd) if e.cmd else "", ("; log " + e.log) if e.log else "",
                                   (e.why or "")[-300:])
