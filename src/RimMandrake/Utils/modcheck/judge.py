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

CLAUDE_TIMEOUT_S = 180

_PROMPT = """\
You are grading one screenshot from an automated RimWorld mod validation run
against ONE specific visual requirement. Answer only about what the image shows.

Read the image at this path: {image}

The requirement, taken verbatim from the mod's owner-validated checklist:

  id:   {req_id}
  says: {req_text}

Answer with a single JSON object and nothing else:

  {{"verdict": "YES" | "NO" | "UNJUDGEABLE", "why": "<one sentence>"}}

Rules for your verdict:
- YES  -- the image positively shows the requirement met.
- NO   -- the image shows the requirement NOT met.
- UNJUDGEABLE -- the image cannot settle it (wrong zoom, subject occluded or
  off-frame, the relevant thing simply is not pictured). Use this freely. It is
  a real answer and it is far more useful than a guess.

Do NOT pass a requirement because the mechanics probably work, because the
screenshot looks broadly reasonable, or because you assume intent. You are the
only check on appearance in this system; a charitable YES defeats its purpose.
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


def judge_component(component, must_show_text, cwd=None, runner=None):
    """Judge one component's screenshots against every must-show id it claims.

    `component`: a component dict from `Component.as_dict()`.
    `must_show_text`: {id: prose} from the mod's VALIDATED checklist.
    `runner`: injection point for tests -- callable(prompt) -> (ok, text).

    Returns a list of result dicts:
      {"id", "verdict", "why", "image"}

    A claimed id with no screenshot is UNJUDGEABLE, never a pass: a component
    that claims to demonstrate something visual and captured no image has not
    demonstrated it.
    """
    call = runner or (lambda p: _run_claude(p, cwd=cwd))
    shots = list(component.get("screenshots") or ())
    out = []

    for req_id in component.get("shows") or ():
        text = must_show_text.get(req_id)
        if text is None:
            out.append({"id": req_id, "verdict": UNJUDGEABLE, "image": "",
                        "why": ("claimed id is not in the validated checklist "
                                "-- orphaned `shows=` or a renamed id")})
            continue
        if not shots:
            out.append({"id": req_id, "verdict": UNJUDGEABLE, "image": "",
                        "why": "component claims this but captured no screenshot"})
            continue

        # Judge against the LAST screenshot of the component: the state at the
        # end of the component is the state the component asserts about.
        image = shots[-1]
        if not os.path.isfile(image):
            out.append({"id": req_id, "verdict": UNJUDGEABLE, "image": image,
                        "why": "screenshot path does not exist on disk"})
            continue

        ok, raw = call(_PROMPT.format(image=image, req_id=req_id, req_text=text))
        if not ok:
            out.append({"id": req_id, "verdict": UNJUDGEABLE, "image": image,
                        "why": "judge could not run: %s" % raw})
            continue
        verdict, why = _parse_verdict(raw)
        out.append({"id": req_id, "verdict": verdict, "image": image,
                    "why": why})

    return out


def judge_run(summary, must_show_text, cwd=None, runner=None):
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
            r = judge_component(c, must_show_text, cwd=cwd, runner=runner)
            c["visual"] = r
            results.extend(r)
    return results


def visual_all_green(results):
    """True only when every judged line came back YES. UNJUDGEABLE is NOT a
    pass -- an unanswerable screenshot is a gap in the evidence, and treating a
    gap as success is the exact failure this system was built to stop."""
    return all(r["verdict"] == YES for r in results)
