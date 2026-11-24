"""designer_mend: the Designer mends the coverage judge's gaps in the session that already holds the design.

Page: design/specs/2026-11-24-designer-mends-in-its-session/boundary.md. `plan` names the session that the next Designer
run resumes after a stage 5 return, or says why that run starts fresh; `head` is the text that opens its message. The
judge that reads the mended design always starts fresh. Writes nothing; launches nothing.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

EXAM = 4        # the Cold Reader exam: a blind boundary, so no mend starts there and no exam run is resumed
JUDGE = 5       # the stage whose return owes a mend


def owed(st, verdict, tree=None):
    """Pure. -> the stage 5 return that owes a mend, or None: the newest result is an accepted return from stage 5, the
    concept stands at the stage it named, and the verdict on file is a not_covered one with gaps on this tree."""
    res = [r for r in st.get("results") or [] if isinstance(r, dict)] if isinstance(st, dict) else []
    last = res[-1] if res else {}
    if last.get("stage") != JUDGE or last.get("outcome") != "return" or st.get("stage") != last.get("to"):
        return None
    if not isinstance(verdict, dict) or verdict.get("verdict") != "not_covered" or not verdict.get("gaps"):
        return None
    if tree and verdict.get("tree") and verdict["tree"] != tree:
        return None
    return last


def transcript_model(path):
    """-> the model of the session's last main-thread turn, or None when no turn names one; OSError when it cannot be
    read. A role run's own model_id is None on a machine whose environment names no id for the tier (measured
    2026-11-24: all 6 role runs on record), so the transcript is read."""
    last = None
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            if '"model"' not in line:
                continue
            try:
                e = json.loads(line)
            except ValueError:
                continue        # a torn last line
            m = e.get("message") if isinstance(e, dict) and not e.get("isSidechain") else None
            if isinstance(m, dict) and isinstance(m.get("model"), str) and not m["model"].startswith("<"):
                last = m["model"]
    return last


def same_model(want, ran, env=None):
    """True when a launch on `want` (a tier or an id) is the model `ran`: the same tier and, where the environment or
    `want` names an id, the same price row. An id with no price row raises UnknownModel (mend_plan says it)."""
    import role_launch as RL
    if not want or not ran or RL.tier(want) not in RL.TIERS or RL.tier(want) != RL.tier(ran):
        return False
    wid = want if str(want).startswith("claude-") else RL.model_id(RL.tier(want), env)
    return wid is None or RL.resolve_model(wid) == RL.resolve_model(ran)


def _usable(run, unit, concept, now, want, projects, ceiling, warm_s):
    """-> (age in seconds, None), or (None, why this run is not resumed)."""
    import detached_helper as DH
    if run is None:
        return None, "no record of run %s in this role" % unit
    if run.get("concept") != concept:
        return None, "run %s worked on another concept" % unit
    if run.get("by"):
        return None, "run %s started no model (closed by %s)" % (unit, run["by"])
    if run.get("runner", "claude") != "claude":
        return None, "run %s is a %s run" % (unit, run["runner"])
    if run.get("state") == "running":
        return None, "run %s is still running" % unit
    if not run.get("session"):
        return None, "run %s recorded no session" % unit
    t = DH.find_transcript(run["session"], projects)
    if not t:
        return None, "run %s left no transcript" % unit
    ran = transcript_model(t)
    if not same_model(want, ran):
        return None, "run %s ran on model %s, the mend launches on %s" % (unit, ran, want)
    age = now - os.path.getmtime(t)
    if age >= warm_s:
        return None, "run %s ended %d min ago (its cache is cold)" % (unit, age // 60)
    ctx = DH.context_tokens(t)
    if not isinstance(ctx, int):
        return None, "the context of run %s cannot be read" % unit
    if ctx >= ceiling:
        return None, "the context of run %s is at or past the ceiling" % unit
    return age, None


def plan(runs, concept, st, verdict, now, want, projects=None, tree=None, warm_s=None, ceiling=None):
    """-> {"owed": False} when no mend is owed; else {"owed": True, "why", "session", "of", "gaps"}, session None when the
    run starts fresh. The stage 5 run that read the verdict is first, then the run that last finished the returned stage."""
    ret = owed(st, verdict, tree)
    if not ret:
        return {"owed": False}
    out = {"owed": True, "session": None, "of": None, "gaps": verdict["gaps"],
           "advisory": bool(verdict.get("advisory"))}
    if st["stage"] == EXAM:
        return dict(out, why="the return is to the exam, a blind boundary")
    if warm_s is None:
        import maturation_dispatch as MD
        warm_s = MD.RESUME_WARM_S
    if ceiling is None:
        import modledger
        ceiling = modledger.config()["holder_context_ceiling_tokens"]
    writer = next((r for r in reversed(st["results"]) if isinstance(r, dict) and r.get("stage") == st["stage"]
                   and r.get("outcome") == "done"), {})
    by_unit = {r.get("unit"): r for r in runs or [] if isinstance(r, dict)}
    whys = []
    for unit in [u for u in (ret.get("run"), writer.get("run")) if u]:
        age, why = _usable(by_unit.get(unit), unit, concept, now, want, projects, ceiling, warm_s)
        if why is None:
            return dict(out, session=by_unit[unit]["session"], of=unit, why="run %s ended %d min ago" % (unit, age // 60))
        whys.append(why)
    return dict(out, why="; ".join(whys) or "no run is named for the return")


def head(p, unit):
    """The text that opens a resumed mend's message. It states no spend and no limit."""
    import designer_stage as DS
    return "\n".join([
        "RESUMED TO MEND. This is your own session (run %s), resumed as run %s: everything above is your own earlier work. "
        "The coverage judge refused the design and the concept returned. The gaps:" % (p["of"], unit),
        *DS._gap_lines(p["gaps"], p["advisory"]),
        "Mend these gaps with the context that you hold. Read a file again only where you need its current text. Your "
        "earlier result.json is closed: end with a new result.json for run %s, for the stage that the packet below names. "
        "The exam and the judge that read the mended design start fresh: write nothing for them but the design." % unit])
