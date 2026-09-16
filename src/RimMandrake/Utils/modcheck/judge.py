"""modcheck.judge -- grade a run's SCREENSHOTS against the must-show lines the
components claimed.

Why this module exists: before it, `runner.py` computed a mod's verdict from
state assertions alone, so a mod whose state was right and whose appearance was
absent went GREEN. The pit mod did exactly that -- `expect_pawn_despawned`
passes while the player watches a pawn stand in a 64px vanilla trap icon,
because `Building_OpenPit` draws its first occupant. See
`design/RimMandrake/north_star_validation_spec.md`.

Two rulings shape it:

  - **The LLM never drives** (owner, 2026-09-12). The run is deterministic
    Python; this module is one pass at the END over captured evidence.
  - **In-game / tooling LLM access is `claude -p`, a subprocess** (owner,
    2026-09-05) -- never an HTTP endpoint, no API key, no base URL.

The judge is asked a NARROW question. Never "does this look right" -- that is
unanswerable and its answer is worthless. Always "is `<this specific must-show
line>` true of this image, yes or no", with the line's own prose supplied.

MEASURED 2026-09-15: `claude` 2.1.116 at ~/.local/bin/claude supports
`--output-format json` and `--allowed-tools`. The subprocess reads the image
with its own Read tool from the path we give it, so no image-upload flag is
needed.
"""

import json
import os
import subprocess

YES = "YES"
NO = "NO"
UNJUDGEABLE = "UNJUDGEABLE"

MUST = "must"
CANNOT = "cannot"

CLAUDE_TIMEOUT_S = 180

_FRAMING = {
    MUST: "a requirement the mod must meet",
    # A `### cannot show` line describes a defect he would REJECT. The judge is
    # still asked the same narrow factual question -- is this true of the image
    # -- and the polarity is applied here, not by the model. Telling it the
    # answer we hope for is how a charitable verdict gets manufactured.
    CANNOT: "a defect the owner would reject the mod for",
}

_PROMPT = """\
You are grading one screenshot from an automated RimWorld mod validation run
against ONE specific visual statement. Answer only about what the image shows,
and only whether the statement is TRUE of it -- not whether that is good.

Read the image at this path: {image}

The statement, taken verbatim from the mod's owner-validated checklist, where it
is recorded as {framing}:

  id:   {req_id}
  says: {req_text}

Answer with a single JSON object and nothing else:

  {{"verdict": "YES" | "NO" | "UNJUDGEABLE", "why": "<one sentence>"}}

Rules for your verdict:
- YES  -- the image positively shows the statement to be true of it.
- NO   -- the image shows the statement to be false of it.
- UNJUDGEABLE -- the image cannot settle it (wrong zoom, subject occluded or
  off-frame, the relevant thing simply is not pictured). Use this freely. It is
  a real answer and it is far more useful than a guess.

Do NOT answer YES because the mechanics probably work, because the screenshot
looks broadly reasonable, or because you assume intent. You are the only check on
appearance in this system; a charitable verdict defeats its purpose.
"""


def _run_claude(prompt, cwd=None):
    """Returns (ok, text). Never raises on a failed judgement -- a broken judge
    must report itself broken, never fabricate a verdict (global rule: never
    hand-write the output a verifier would have produced)."""
    cmd = ["claude", "-p", prompt,
           "--output-format", "json",
           "--allowed-tools", "Read"]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True,
                           timeout=CLAUDE_TIMEOUT_S, cwd=cwd)
    except FileNotFoundError:
        return False, ("`claude` not found on PATH -- the judge needs Claude "
                       "Code installed and logged in (owner ruling 2026-09-05)")
    except subprocess.TimeoutExpired:
        return False, "claude -p timed out after %ds" % CLAUDE_TIMEOUT_S

    # Both streams matter: the CLI's auth failures print to stdout, not stderr
    # (LESSONS_INBOX, 2026-09-13 Oracle client).
    if r.returncode != 0:
        return False, (r.stderr.strip() or r.stdout.strip()
                       or "claude -p exited %d with no output" % r.returncode)
    return True, r.stdout


def _parse_verdict(raw):
    """Pull {"verdict","why"} out of claude's JSON envelope. Anything we cannot
    read becomes UNJUDGEABLE with the reason -- never a pass."""
    text = raw
    try:
        env = json.loads(raw)
        if isinstance(env, dict) and "result" in env:
            text = env["result"]
    except (ValueError, TypeError):
        pass
    if not isinstance(text, str):
        text = str(text)

    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end <= start:
        return UNJUDGEABLE, "no JSON object in the judge's reply"
    try:
        obj = json.loads(text[start:end + 1])
    except ValueError as e:
        return UNJUDGEABLE, "unparseable judge reply: %s" % e

    v = str(obj.get("verdict", "")).strip().upper()
    why = str(obj.get("why", "")).strip()
    if v not in (YES, NO, UNJUDGEABLE):
        return UNJUDGEABLE, "judge returned an unknown verdict %r" % v
    return v, why


def passes(verdict, polarity):
    """Whether one verdict clears its line. A must-show line needs YES; a
    cannot-show line needs NO, because it states a defect. UNJUDGEABLE clears
    neither -- a gap in the evidence is not a result."""
    return verdict == (YES if polarity == MUST else NO)


def judge_component(component, must_show_text, cannot_show_text=None,
                    cwd=None, runner=None):
    """Judge one component's screenshots against every checklist id it claims.

    `component`: a component dict from `Component.as_dict()`.
    `must_show_text`: {id: prose} from the mod's VALIDATED `### must show`.
    `cannot_show_text`: {id: prose} from its `### cannot show` -- judged with
      the opposite polarity, so a YES there fails the mod.
    `runner`: injection point for tests -- callable(prompt) -> (ok, text).

    Returns a list of result dicts:
      {"id", "polarity", "verdict", "pass", "why", "image"}

    A claimed id with no screenshot is UNJUDGEABLE, never a pass: a component
    that claims to demonstrate something visual and captured no image has not
    demonstrated it.
    """
    call = runner or (lambda p: _run_claude(p, cwd=cwd))
    cannot_show_text = cannot_show_text or {}
    shots = list(component.get("screenshots") or ())
    out = []

    def result(req_id, polarity, verdict, why, image=""):
        return {"id": req_id, "polarity": polarity, "verdict": verdict,
                "pass": passes(verdict, polarity), "why": why, "image": image}

    for req_id in component.get("shows") or ():
        polarity = CANNOT if req_id in cannot_show_text else MUST
        text = cannot_show_text.get(req_id, must_show_text.get(req_id))
        if text is None:
            out.append(result(req_id, polarity, UNJUDGEABLE,
                              "claimed id is not in the validated checklist "
                              "-- orphaned `shows=` or a renamed id"))
            continue
        if not shots:
            out.append(result(req_id, polarity, UNJUDGEABLE,
                              "component claims this but captured no screenshot"))
            continue

        # Judge against the LAST screenshot of the component: the state at the
        # end of the component is the state the component asserts about.
        image = shots[-1]
        if not os.path.isfile(image):
            out.append(result(req_id, polarity, UNJUDGEABLE,
                              "screenshot path does not exist on disk", image))
            continue

        ok, raw = call(_PROMPT.format(image=image, req_id=req_id, req_text=text,
                                      framing=_FRAMING[polarity]))
        if not ok:
            out.append(result(req_id, polarity, UNJUDGEABLE,
                              "judge could not run: %s" % raw, image))
            continue
        verdict, why = _parse_verdict(raw)
        out.append(result(req_id, polarity, verdict, why, image))

    return out


def judge_run(summary, must_show_text, cannot_show_text=None, cwd=None,
              runner=None):
    """Judge every component in a run summary. Mutates each component dict by
    attaching `visual` (its list of results) and returns the flat list.

    Leaves components with no `shows` untouched -- that is a mod without a
    validated checklist, which behaves exactly as it did before this module
    existed (owner ruling 2026-09-15: enforcement is per mod, as he validates).
    """
    results = []
    for chain in summary.get("chains") or ():
        for c in chain.get("components") or ():
            if not (c.get("shows")):
                continue
            r = judge_component(c, must_show_text, cannot_show_text,
                                cwd=cwd, runner=runner)
            c["visual"] = r
            results.extend(r)
    return results


def visual_all_green(results):
    """True only when every judged line cleared its own polarity. UNJUDGEABLE
    is NOT a pass -- an unanswerable screenshot is a gap in the evidence, and
    treating a gap as success is the exact failure this system was built to
    stop."""
    return all(r["pass"] for r in results)
