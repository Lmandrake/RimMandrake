"""set_down_judge.py: the LLM judge of a set-down. One bare model call reads the set-down and the filing run's transcript
and answers PASS or REFUSED.

Item RIMMANDRAKE_TIGHTEN_SET_DOWN_CLASSES_ANY_TWELVE_LETTERS_PASS; page design/specs/2026-11-24-filing-gate/boundary.md;
selftest selftest_filing_gate.py; brief roles/set_down_judge.md; calibration set_down_calibration.py. Why: on 2026-11-25
the Conductor read 25 set-downs and found about 16 with no sincere attempt, and the owner ordered "the filing program may
need to be an LLM actually, so it's intelligent enough to push back" with "a hook, block, refuse, and force present
inside". filing_gate.py checks the words first; this judge checks that the run did what the set-down claims.

The call is one `claude -p` with no tools, no settings, no MCP and no session, in an empty folder, so it reads only the
prompt (a full fresh session costs 113k to 236k weighted tokens before its first act: the sleep-and-resume report). The
model is RM_SET_DOWN_JUDGE_MODEL, or the alias `opus`, which the CLI resolves from the environment. A judge that cannot
answer passes the set-down, and says so. The verdict binds only when the row `set_down_judge` of the judge calibration
registry reads CALIBRATED (refusal_contract.status).
"""
import effort as EF  # the one effort table (RIMMANDRAKE_PASS_EFFORT_ON_EVERY_LAUNCH_STEVEDESKTOP_RAN_MEDIUM)
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import filing_gate as FG  # noqa: E402
import fulltext as FT  # noqa: E402

FAMILY = "set_down_judge"
BRIEF = os.path.join(HERE, "roles", "set_down_judge.md")
MODEL_ENV = "RM_SET_DOWN_JUDGE_MODEL"
DEFAULT_MODEL = "opus"      # an alias: the CLI resolves it from the environment (ANTHROPIC_DEFAULT_OPUS_MODEL)
SWITCH_ENV = "RM_SET_DOWN_JUDGE"
CLAUDE = shutil.which("claude") or os.path.expanduser("~/.local/bin/claude")   # systemd's PATH lacks ~/.local/bin
# A hang guard. Danger: a call that never returns holds the helper's `rimflow file` for good. Measured need: the
# longest of the 25 calibration calls (judge_agreement.md beside the page).
JUDGE_TIMEOUT_S = 900
# Danger: a prompt past the model's context window (about 200,000 tokens, about 800,000 characters) fails the call, and
# the set-down then passes unjudged. 80,000 is a tenth of that window.
DIGEST_MAX_CHARS = 80000
HEAD_SHARE = 0.3            # of the digest: the start of the run (its brief, its first reads); the rest is the end
CMD_CHARS, OUT_CHARS, SAY_CHARS = 400, 240, 300     # each entry's cut: a digest line is a pointer, not the output


def judge_argv(env=None):
    env = os.environ if env is None else env
    model = (env.get(MODEL_ENV) or DEFAULT_MODEL).strip()
    return [CLAUDE, "-p", "--model", model, "--tools", "", "--setting-sources", "", "--strict-mcp-config",
            "--no-session-persistence", "--output-format", "json"] + EF.effort_args(model) + ["--system-prompt",
            "You judge whether a helper run may set work down. You answer with one JSON object."]


def ask_model(prompt, timeout=JUDGE_TIMEOUT_S, env=None):
    """-> the model's answer text. One fresh call in an empty folder; raises OSError or TimeoutExpired."""
    with tempfile.TemporaryDirectory(prefix="rm-setdown-judge-") as d:
        r = subprocess.run(judge_argv(env), input=prompt, capture_output=True, text=True, cwd=d, timeout=timeout,
                           stdin=None)
    if r.returncode != 0:
        raise OSError("claude exit %s: %s" % (r.returncode, FT.fit((r.stderr or r.stdout).strip(), 300)))
    out = json.loads(r.stdout)
    if out.get("is_error"):
        raise OSError("claude: %s" % FT.fit(str(out.get("result")), 300))
    return str(out.get("result") or "")


# ---- the transcript ------------------------------------------------------------------------------------------------

def _text_of(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return " ".join(str(c.get("text") or "") for c in content if isinstance(c, dict))
    return ""


def _one_line(text, n):
    t = re.sub(r"\s+", " ", text or "").strip()
    return t if len(t) <= n else t[:n] + "…"


def _entry(c):
    name, inp = c.get("name") or "?", c.get("input") or {}
    if name == "Bash":
        return "$ " + _one_line(str(inp.get("command") or ""), CMD_CHARS)
    for k in ("file_path", "path", "pattern", "description", "query", "url"):
        if inp.get(k):
            return "%s %s" % (name, _one_line(str(inp[k]), CMD_CHARS))
    return "%s %s" % (name, _one_line(json.dumps(inp)[:CMD_CHARS], CMD_CHARS))


def digest(path, until=None, max_chars=DIGEST_MAX_CHARS):
    """-> (the digest text, "") or (None, why). One line per act of the main thread up to `until` (an ISO time): each
    tool call, the first of its output (indented), and the run's own words (»). A sidechain is not the run's thread."""
    if not path:
        return None, "the transcript of the filing run could not be found"
    entries = []
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            for line in f:
                try:
                    ev = json.loads(line)
                except ValueError:
                    continue
                if not isinstance(ev, dict) or ev.get("isSidechain") or ev.get("type") not in ("assistant", "user"):
                    continue
                if until and str(ev.get("timestamp") or "") > until:
                    break
                content = (ev.get("message") or {}).get("content")
                if not isinstance(content, list):
                    continue
                for c in content:
                    if not isinstance(c, dict):
                        continue
                    if c.get("type") == "tool_use":
                        entries.append(_entry(c))
                    elif c.get("type") == "tool_result":
                        out = _one_line(_text_of(c.get("content")), OUT_CHARS)
                        if out:
                            entries.append("  " + out)
                    elif c.get("type") == "text" and ev.get("type") == "assistant":
                        entries.append("» " + _one_line(c.get("text"), SAY_CHARS))
    except OSError as e:
        return None, "the transcript could not be read: %s: %s" % (type(e).__name__, e)
    if not entries:
        return None, "the transcript holds no act of the run before the filing"
    text = "\n".join(entries)
    if len(text) <= max_chars:
        return text, ""
    head, tail, size = [], [], 0
    for e in entries:
        if size + len(e) + 1 > max_chars * HEAD_SHARE:
            break
        head.append(e)
        size += len(e) + 1
    size = 0
    for e in reversed(entries[len(head):]):
        if size + len(e) + 1 > max_chars * (1 - HEAD_SHARE) - 100:
            break
        tail.append(e)
        size += len(e) + 1
    tail.reverse()
    gone = len(entries) - len(head) - len(tail)
    return "\n".join(head + ["… %d entries elided (the middle of the run) …" % gone] + tail), ""


def transcript_of_this_run(env=None):
    """-> (the transcript path of the process that files, or None, why). CLAUDE_CODE_SESSION_ID of the filing process."""
    env = os.environ if env is None else env
    sid = (env.get("CLAUDE_CODE_SESSION_ID") or env.get("CLAUDE_SESSION_ID") or "").strip()
    if not sid:
        return None, "the filing process names no session (no CLAUDE_CODE_SESSION_ID)"
    try:
        import detached_helper as DH
        p = DH.find_transcript(sid)
    except Exception as e:  # noqa: BLE001 - could not look: the judge cannot read the run, and says so
        return None, "the transcript of session %s could not be looked for: %s" % (sid, e)
    return (p, "") if p else (None, "no transcript of session %s was found" % sid)


def earlier_refusals(unit, state_dir, iid):
    return FG.refusals_of(unit, state_dir, iid)


# ---- the prompt and the answer -------------------------------------------------------------------------------------

def build_prompt(sd, digest_text, digest_why, earlier):
    with open(BRIEF, encoding="utf-8") as f:
        brief = f.read()
    lines = [brief, "", "## THE SET-DOWN", "door: %s" % sd.get("door"), "item: %s" % sd.get("id"),
             "title: %s" % (sd.get("title") or ""), "kind: %s" % sd.get("kind"),
             "class (the requirement it tried to meet): %s" % sd.get("class"), "evidence: %s" % sd.get("evidence"), "",
             "## EARLIER REFUSALS OF THIS SET-DOWN IN THIS RUN"]
    lines += ["- %s: %s" % (r.get("at", "?"), _one_line(str(r.get("why") or ""), 600)) for r in earlier] or ["none"]
    lines += ["", "## TRANSCRIPT DIGEST (the filing run, up to the filing)"]
    lines.append(digest_text if digest_text else "could not be read: %s" % digest_why)
    return "\n".join(lines)


def parse(answer):
    """-> (the verdict dict, "") or (None, why)."""
    m = re.search(r"(?s)\{.*\}", answer or "")
    if not m:
        return None, "the answer holds no JSON (%r)" % (answer or "")[:80]
    try:
        v = json.loads(m.group(0))
    except ValueError as e:
        return None, "the answer's JSON does not parse: %s" % e
    if not isinstance(v, dict) or v.get("verdict") not in ("PASS", "REFUSED"):
        return None, "the answer's verdict is not PASS or REFUSED (%r)" % (v.get("verdict") if isinstance(v, dict) else v)
    if v["verdict"] == "REFUSED" and not (str(v.get("missing") or "").strip() and str(v.get("next_act") or "").strip()):
        return None, "a REFUSED answer names no missing part or no next act"
    return {k: v.get(k) for k in ("verdict", "requirement", "claims", "missing", "next_act")}, ""


def judge(sd, transcript, earlier, ask=ask_model, until=None):
    """-> {"verdict": PASS | REFUSED | "could not judge", ...}. A transcript that cannot be read, a failed or timed-out
    call, or a malformed answer is "could not judge" with its cause in `why`: the set-down then passes."""
    dg, why = digest(transcript, until=until) if transcript else (None, "the transcript of the filing run could not be "
                                                                         "found")
    if not dg:      # nothing to check the claims against: no call, and the set-down passes (page)
        return {"verdict": "could not judge", "why": why, "transcript": why}
    prompt = build_prompt(sd, dg, why, earlier)
    try:
        ans = ask(prompt)
    except subprocess.TimeoutExpired:
        return {"verdict": "could not judge", "why": "no answer in %d s" % JUDGE_TIMEOUT_S, "transcript": why or "read"}
    except (OSError, ValueError) as e:
        return {"verdict": "could not judge", "why": "%s: %s" % (type(e).__name__, FT.fit(str(e), 300)),
                "transcript": why or "read"}
    v, bad = parse(ans)
    if v is None:
        return {"verdict": "could not judge", "why": bad, "transcript": why or "read"}
    v["transcript"] = "read"
    return v


def wanted(env=None):
    """-> (on, why off). Off: RM_SET_DOWN_JUDGE=0, a test process (test_process.under_test), or no Claude Code."""
    env = os.environ if env is None else env
    if env.get(SWITCH_ENV, "1") == "0":
        return False, "off: %s=0" % SWITCH_ENV
    try:
        import test_process
        if test_process.under_test():
            return False, "off: a test process spends no model call"
    except Exception:  # noqa: BLE001 - when it cannot be read, the judge stays off: a test must never spend
        return False, "off: test_process could not be read"
    if not env.get("CLAUDECODE"):
        return False, "off: not inside Claude Code (no CLAUDECODE)"
    return True, ""


def door_judge(sd, earlier, env=None):
    """The judge as the door calls it: this process's transcript, a fresh call. Never raises."""
    on, why = wanted(env)
    if not on:
        return {"verdict": "could not judge", "why": why}
    path, twhy = transcript_of_this_run(env)
    v = judge(sd, path, earlier)
    if twhy:
        v.setdefault("why", twhy)
    return v


def binding():
    """-> True when the calibration row of this judge reads CALIBRATED at its brief's hash (refusal_contract.status)."""
    import refusal_contract as RC
    return RC.status(FAMILY) == "CALIBRATED"
