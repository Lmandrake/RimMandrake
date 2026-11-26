#!/usr/bin/env python3
"""list_effect.py: an outcome check on a list item, and the timed beat that closes an item whose check passes.

Item RIMMANDRAKE_BUILD_LIST_OUTCOME_CHECKS_SEVEN_DONE_NEVER_CLOSED, step 1 of
design/specs/2026-11-22-coordination-every-agent-must-use/plan.md. Page: design/specs/2026-11-22-list-outcome-checks/
boundary.md; selftest: selftest_list_effect.py. Why: 7 of the 48 Conductor debts in the census of 2026-11-22 were done
and never closed. No model, no tokens. It LAUNCHES NOTHING and files nothing (step 2 adds the launch).

A check is one string on the item (`rimflow file --effect`, `rimflow effect <ID> --check`):
    path-has:<repo path>::<text>     the file holds the text            (a missing file: fails)
    path-lacks:<repo path>::<text>   the file exists without the text   (a missing file: unmeasured)
    cmd:<shell command>              bash -c from the clone root: exit 0 holds, 1 fails, anything else unmeasured
A check is accepted only when it is seen failing: now, or (a path check) at the commit where the item was filed, or the
filer states why it cannot be (`--holds-why`). A vacuous command is refused always.

    python3 src/RimMandrake/rimflow/list_effect.py tick [--apply]    one beat; closes only with --apply
    python3 src/RimMandrake/rimflow/list_effect.py status            the last reading
    python3 src/RimMandrake/rimflow/list_effect.py check "<check>"   run one check here: holds|fails|unmeasured, output
    python3 src/RimMandrake/rimflow/list_effect.py closed [--started] ID...   a check's helper: exit 0 every ID is
            done, dropped or superseded (--started: or taken up: doing, built, validated); 1 one is not (named, never
            filed included); 2 the ledger could not be read
            (a check reads `cmd:python3 src/RimMandrake/rimflow/list_effect.py closed A B`)

Per open item that carries a check, one decision:
    pipeline_paused | off | blind   the pause, a `pipe off` (all, family:list_effect, item:<ID>), or an unreadable store
    work            the check fails (step 2 launches one helper; this step does nothing)
    blind           the check could not be run: nothing
    closed_by_check the check holds: `rimflow close --no-code` with the check, head sha and output (seat BENCH,
                    role_unit rm-list-effect.service: the pipeline's act, never his or the Conductor's)
    close_refused   `rimflow close` refused: said once on the Needs Conductor line; no second close until the item or
                    its check changes (a program never sends the same refused input again unchanged)
    would_close     a dry beat
Runs on rm-list-effect.timer from the dispatch clone. Reading: <RM_DISPATCHER_STATE>/list_effect/reading.json
(RM_LIST_EFFECT_DIR overrides); evidence/<ID>-<epoch>.txt beside it holds each close's whole output.
"""
import argparse
import datetime as dt
import fcntl
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for _p in (HERE, os.path.join(REPO, "src", "RimMandrake", "Utils")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

ITEM = "RIMMANDRAKE_BUILD_LIST_OUTCOME_CHECKS_SEVEN_DONE_NEVER_CLOSED"
UNIT = "rm-list-effect.service"
FAMILY = "list_effect"
CLOSED = ("done", "dropped", "superseded")
FORMS = "path-has:<repo path>::<text>, path-lacks:<repo path>::<text>, cmd:<shell command>"
PAC = dt.timezone(dt.timedelta(hours=-8), "PST")
# Hang guard (the class of call_deadline_lint.py): a check command that never ends would hold this beat's lock and stop
# every later check. Set far above a real check (a grep or one selftest: seconds), never a speed bar.
# budget: danger=a check command that never ends holds this beat's lock and stops every later check; never reached in the 14
# budget: days to 2026-11-24; no record of its run
CMD_TIMEOUT_S = 600
# Text cut: the close event is one ledger line that every replay of every seat reads; the whole output is kept in the
# evidence file, so the line carries only its head.
OUT_IN_EVENT = 400
# Hang guard for the `rimflow close` subprocess (a publish retries a push; minutes at worst).
CLOSE_TIMEOUT_S = 21600  # budget: class=publish
VACUOUS = re.compile(r"^\s*(?:true|/bin/true|/usr/bin/true|:|exit(?:\s+0)?|echo\b.*|printf\b.*|test\s+1|\[\s+1\s+\])"
                     r"\s*;?\s*$")


# ---- the check ------------------------------------------------------------------------------------------------------

def parse(text):
    """-> {"kind": "path-has"|"path-lacks", "path", "text"} | {"kind": "cmd", "cmd"} | {"kind": "unreadable", "why"}."""
    if not isinstance(text, str) or not text.strip():
        return {"kind": "unreadable", "why": "no check text; the forms are: " + FORMS}
    s = text.strip()
    kind, sep, rest = s.partition(":")
    if not sep or kind not in ("path-has", "path-lacks", "cmd"):
        return {"kind": "unreadable", "why": "%r is not a check; the forms are: %s" % (s[:80], FORMS)}
    if kind == "cmd":
        if not rest.strip():
            return {"kind": "unreadable", "why": "cmd: names no command"}
        return {"kind": "cmd", "cmd": rest.strip()}
    path, sep, want = rest.partition("::")
    path = path.strip()
    if not sep or not want.strip():
        return {"kind": "unreadable", "why": "%s needs <repo path>::<text>, and the text may not be empty" % kind}
    if not path or os.path.isabs(path) or re.match(r"^[A-Za-z]:[\\/]", path) or ".." in path.replace("\\", "/").split("/"):
        return {"kind": "unreadable", "why": "%s reads a relative repo path without `..` (got %r); a file outside the "
                                             "repo is checked with cmd:" % (kind, path)}
    return {"kind": kind, "path": path, "text": want}


def _path_verdict(kind, want, body, exists):
    """-> (verdict, output) for a path check over a file's bytes (body None: could not be read)."""
    if not exists:
        return ("fails", "the file does not exist, so it does not hold the text") if kind == "path-has" else \
            ("unmeasured", "the file does not exist, so it cannot be read for the text")
    if body is None:
        return "unmeasured", "the file could not be read"
    hit = [ln for ln in body.splitlines() if want in ln]
    if kind == "path-has":
        return ("holds", "\n".join(hit[:20])) if want in body else ("fails", "the text is not in the file")
    return ("fails", "\n".join(hit[:20]) or "the text is in the file") if want in body else \
        ("holds", "the file no longer holds the text")


def run(text, root, timeout=None):
    """-> (verdict, output): verdict holds | fails | unmeasured. Never raises."""
    p = parse(text)
    if p["kind"] == "unreadable":
        return "unmeasured", p["why"]
    if p["kind"] == "cmd":
        try:
            r = subprocess.run(["bash", "-c", p["cmd"]], cwd=root, capture_output=True, text=True, errors="replace",
                               timeout=CMD_TIMEOUT_S if timeout is None else timeout, stdin=subprocess.DEVNULL)
        except subprocess.TimeoutExpired:
            return "unmeasured", "the command ran past its %gs deadline" % (CMD_TIMEOUT_S if timeout is None else timeout)
        except OSError as e:
            return "unmeasured", "the command could not start: %s" % e
        out = ((r.stdout or "") + (r.stderr or "")).strip()
        if r.returncode == 0:
            return "holds", out
        if r.returncode == 1:
            return "fails", out
        return "unmeasured", ("exit %d (only 0 holds and 1 fails)" % r.returncode) + ("\n" + out if out else "")
    full = os.path.join(root, p["path"])
    if not os.path.exists(full):
        return _path_verdict(p["kind"], p["text"], None, False)
    try:
        with open(full, encoding="utf-8", errors="replace") as f:
            body = f.read()
    except OSError:
        body = None
    return _path_verdict(p["kind"], p["text"], body, True)


def holds(text, root):
    """-> "holds" | "fails" | "unmeasured"."""
    return run(text, root)[0]


def decide(item, verdict):
    """-> close | work | blind | no_effect | closed. item = {"state", "effect"}."""
    if (item or {}).get("state") in CLOSED:
        return "closed"
    if not (item or {}).get("effect"):
        return "no_effect"
    return {"holds": "close", "fails": "work"}.get(verdict, "blind")


def _git(root, *args):
    """-> probe_result: value(stdout), or could_not_look(cause) when git cannot answer (no repo, no such object)."""
    import probe_result as PR
    try:
        r = subprocess.run(["git", "-C", root] + list(args), capture_output=True, text=True, timeout=60,
                           stdin=subprocess.DEVNULL, errors="replace")
    except (OSError, subprocess.TimeoutExpired) as e:
        return PR.could_not_look("git %s: %s" % (args[0], e))
    if r.returncode:
        return PR.could_not_look("git %s exit %d: %s" % (args[0], r.returncode, (r.stderr or "").strip()))
    return PR.value(r.stdout)


def live_changes(iid, root):
    """One log for the item being closed. Return the published changes that oblige a live line, newest first."""
    import live_line
    import probe_result as PR
    got = _git(root, "log", "origin/main", "--format=%x1e%H%x00%ct%x00%s", "--name-status", "-z",
               "--no-renames", "--diff-merges=first-parent", "-F", "--grep=" + iid)
    if not got.ok:
        return got
    named = re.compile(r"(?<![A-Za-z0-9_])%s(?![A-Za-z0-9_])" % re.escape(iid))
    changes = []
    for chunk in got.value.split("\x1e")[1:]:
        sha, at, subject, *files = chunk.rstrip("\0").split("\0")
        if named.search(subject):
            changes.extend((path, sha, int(at), status.strip()) for status, path in zip(files[::2], files[1::2])
                           if live_line.needs_line([path]))
    return PR.value(changes) if changes else PR.empty()


def at_commit(text, root, filed_ts):
    """-> (verdict, rev) of a path check over the repo as it stood when the item was filed; (None, why) when that cannot
    be read (a cmd check, no git, no commit before the filing)."""
    p = parse(text)
    if p["kind"] not in ("path-has", "path-lacks"):
        return None, "a cmd: check cannot be run on a past commit"
    when = dt.datetime.fromtimestamp(filed_ts, dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    got = _git(root, "rev-list", "-1", "--before=" + when, "HEAD")
    if not got.ok:
        return None, got.cause
    rev = got.value.strip()
    if not rev:
        return None, "no commit before %s here" % when
    listed = _git(root, "ls-tree", "--name-only", rev, "--", p["path"])
    if not listed.ok:
        return None, listed.cause
    exists = bool(listed.value.strip())
    body = _git(root, "show", "%s:%s" % (rev, p["path"])) if exists else None
    body = body.value if body is not None and body.ok else None     # unreadable at rev: _path_verdict says unmeasured
    return _path_verdict(p["kind"], p["text"], body, exists)[0], rev


def attach_gate(text, root, filed_ts=None, holds_why=None, now=None):
    """-> (seen, None) to accept the check, or (None, refusal with its path to pass).
    seen = {"verdict": "fails"|"holds", "at", "rev"?, "why"?, "out"}: the reading that shows the check can fail."""
    now = time.time() if now is None else now
    p = parse(text)
    if p["kind"] == "unreadable":
        return None, "outcome check refused: %s" % p["why"]
    if p["kind"] == "cmd" and VACUOUS.match(p["cmd"]):
        return None, ("outcome check refused: %r passes whatever the work did, so it can close an item that is not done. "
                      "Path to pass: a command that exits 1 until the work is done (grep -q, test -f, a selftest)." % p["cmd"])
    verdict, out = run(text, root)
    head = (out or "")[:OUT_IN_EVENT]
    if verdict == "unmeasured":
        return None, ("outcome check refused: it is unmeasured here (%s). Path to pass: repair the check so it reads "
                      "holds or fails from the clone root." % head)
    if verdict == "fails":
        return {"verdict": "fails", "at": int(now), "out": head}, None
    if filed_ts is not None:
        then, rev = at_commit(text, root, filed_ts)
        if then == "fails":
            return {"verdict": "fails", "at": int(now), "rev": rev[:12], "out": "holds now; failed at %s, where the "
                    "item was filed" % rev[:12]}, None
        if then == "holds":
            gone = "it held already at %s, where the item was filed" % rev[:12]
        else:
            gone = rev
    else:
        gone = "the item is new"
    if holds_why and str(holds_why).strip():
        return {"verdict": "holds", "at": int(now), "why": str(holds_why).strip(), "out": head}, None
    return None, ("outcome check refused: it holds now and cannot be seen failing (%s), so it cannot tell done from not "
                  "done. Path to pass: a check that fails until the work is done, or --holds-why \"<why it cannot be "
                  "seen failing>\" when the work is done already." % gone)


# ---- the beat -------------------------------------------------------------------------------------------------------

def check_root():
    return os.environ.get("RM_LIST_EFFECT_ROOT") or REPO


def sdir(create=True):
    d = os.environ.get("RM_LIST_EFFECT_DIR")
    if not d:
        import doorbell
        d = os.path.join(doorbell.state_dir(), "list_effect")
    if create:
        os.makedirs(d, exist_ok=True)
    return d


def _read(p, default):
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


def _write(p, obj):
    with open(p + ".tmp", "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=1, ensure_ascii=False)
    os.replace(p + ".tmp", p)


def pac(t):
    return dt.datetime.fromtimestamp(t, PAC).strftime("%Y-%m-%d %I:%M %p %Z").replace(" 0", " ")


def _world(observe=None):
    import model as LM
    if os.environ.get("RIMFLOW_LEDGER"):        # a throwaway ledger, as cli._bind_paths reads it
        LM.EVENTS = os.environ["RIMFLOW_LEDGER"]
    if os.environ.get("RIMFLOW_ITEMS"):
        LM.ITEMS = os.environ["RIMFLOW_ITEMS"]
        LM.CLOSED = os.path.join(LM.ITEMS, "closed")
    return LM.replay(observe=observe)


def _pause(now):
    import pipeline_pause as PP     # an unreadable pause store reads paused (its own rule)
    return PP.blocks(None, now)


def _blocked(iid):
    import control as C
    return C.blocked({"family": FAMILY, "item": iid})


LIVE_WAIT, LIVE_BLIND = 5, 6          # shared close results for both ticks, separate from a refused close
LIVE_WAIT_PREFIX = "close: live promise pending: "


def close_item(iid, text, why, publish):
    """`rimflow close <iid> --no-code <text>` as the pipeline's act. -> (rc, output). An item that is already done is
    closed (rc 0): its own run closed it between the tick's read and this close."""
    argv = [sys.executable, os.path.join(HERE, "cli.py"), "close", iid, "--no-code", text, "--seat", "BENCH",
            "--why", why] + (["--publish"] if publish else [])
    env = dict(os.environ)
    env["RM_ROLE_UNIT"] = os.environ.get("RM_ROLE_UNIT") or UNIT
    env["RIMFLOW_SEAT"] = "BENCH"
    for k in ("CLAUDE_SESSION_ID", "CLAUDE_CODE_SESSION_ID"):     # never a window's session
        env.pop(k, None)
    try:
        r = subprocess.run(argv, cwd=REPO, env=env, capture_output=True, text=True, timeout=CLOSE_TIMEOUT_S,
                           stdin=subprocess.DEVNULL, errors="replace")
    except (OSError, subprocess.TimeoutExpired) as e:
        return 99, "%s: %s" % (type(e).__name__, e)
    said = ((r.stdout or "") + (r.stderr or "")).strip()
    pending = next((line for line in (r.stdout or "").splitlines() if line.startswith(LIVE_WAIT_PREFIX)), None)
    if pending and r.returncode in (0, 4):   # the note can be published through the normal success path
        return LIVE_WAIT, said
    if r.returncode and ("%s is already `done`" % iid) in said:     # model's SECOND-close refusal: its run closed it first
        return 0, said
    return r.returncode, said


def conductor_need(text, now, path=None):
    """One Needs Conductor line in the Conductor log (the guards red_dispatch.conductor_need uses)."""
    import detached_helper as DH
    import doorbell
    import conductor_log_guard
    path = path or DH.conductor_log_path()
    if (os.path.abspath(path) == os.path.abspath(DH.REAL_LOG)
            and os.environ.get("RM_DISPATCHER_STATE", doorbell.DEFAULT_STATE) != doorbell.DEFAULT_STATE):
        raise RuntimeError("refusing to write the REAL conductor log from a test process: " + path)
    conductor_log_guard.refuse_if_test(path)
    with open(path, "a", encoding="utf-8") as f:
        f.write("\n%s — NEEDS CONDUCTOR (list_effect): %s\n" % (DH.iso(now), text))
    return path


def _one(s, n):
    s = " ".join(str(s or "").split())
    return s if len(s) <= n else s[: n - 1] + "…"


def tick(apply=False, publish=True, root=None, fx=None, now=None):
    """One beat. -> the reading. fx (tests): pause(now), blocked(iid), close(iid, text, why, publish), need(text, now)."""
    fx = fx or {}
    root = root or check_root()
    now = time.time() if now is None else now
    d = sdir(create=apply)
    lock = None
    if apply:
        lock = open(os.path.join(d, "tick.lock"), "w")
        fcntl.flock(lock, fcntl.LOCK_EX)
    try:
        return _tick(apply, publish, root, fx, now, d)
    finally:
        if lock:
            lock.close()


def _tick(apply, publish, root, fx, now, d):
    st = _read(os.path.join(d, "state.json"), {}) if apply else {}
    items_st = st.setdefault("items", {})
    w = _world()
    pause = fx.get("pause", _pause)
    blocked = fx.get("blocked", _blocked)
    do_close = fx.get("close", close_item)
    do_need = fx.get("need", conductor_need)
    try:
        paused = pause(now)
    except Exception as e:  # noqa: BLE001 - a pause that cannot be read is a pause
        paused = "the pause store could not be read (%s: %s)" % (type(e).__name__, e)
    got = _git(root, "rev-parse", "--short=12", "HEAD")
    head = got.value.strip() if got.ok else "UNMEASURED (%s)" % got.cause
    rows = {}
    for iid in sorted(w.items):
        it = w.items[iid]
        eff = getattr(it, "effect", None)
        if not eff or it.state in CLOSED:
            continue
        row = rows[iid] = {"effect": eff, "state": it.state}

        def put(decision, why, row=row):
            row["decision"], row["why"] = decision, why
        if paused:
            put("pipeline_paused", paused)
            continue
        try:
            off = blocked(iid)
        except Exception as e:  # noqa: BLE001 - a store that cannot be read is never "nothing is off"
            put("blind", "the control store could not be read (%s: %s)" % (type(e).__name__, e))
            continue
        if off:
            put("off", off)
            continue
        verdict, out = run(eff, root)
        row["verdict"] = verdict
        dec = decide({"state": it.state, "effect": eff}, verdict)
        if dec == "work":
            put("work", "the check fails: %s" % _one(out, 200))
            continue
        if dec != "close":
            put("blind", "the check is unmeasured: %s" % _one(out, 200))
            continue
        fp = [eff, len(it.history)]
        s = items_st.setdefault(iid, {})
        ref = s.get("refused") or {}
        if ref.get("fp") == fp:
            put("close_refused", ref.get("why") or "refused")
            continue
        if not apply:
            put("would_close", "the check holds: %s" % _one(out, 200))
            continue
        evid = os.path.join(d, "evidence")
        os.makedirs(evid, exist_ok=True)
        epath = os.path.join(evid, "%s-%d.txt" % (iid, int(now)))
        with open(epath, "w", encoding="utf-8") as f:
            f.write("check: %s\nroot: %s\nhead: %s\nat: %s\nverdict: holds\n\n%s\n" % (eff, root, head, pac(now), out))
        text = "outcome check holds at %s: %s | output: %s | evidence %s" % (
            head, eff, _one(out, OUT_IN_EVENT) or "(none)", epath)
        rc, said = do_close(iid, text, "pipeline act (list_effect tick, %s): the item's outcome check holds" % UNIT,
                            publish)
        row["evidence"] = epath
        if rc == 0:
            put("closed_by_check", "closed: %s" % _one(out, 200))
            s.pop("refused", None)
            continue
        if rc in (LIVE_WAIT, LIVE_BLIND):
            put("blind" if rc == LIVE_BLIND else "close_refused", _one(said, 600))
            continue
        why = _one(said, 600) or "rc %s" % rc
        s["refused"] = {"fp": fp, "why": why, "at": now}
        put("close_refused", why)
        try:
            do_need("%s: its outcome check holds (%s) but `rimflow close` refused: %s. The list_effect tick sends no "
                    "second close until the item or its check changes." % (iid, eff, _one(why, 300)), now)
        except Exception as e:  # noqa: BLE001 - said on the row; the reading carries it
            row["need_failed"] = "%s: %s" % (type(e).__name__, e)
    counts = {}
    for r in rows.values():
        counts[r["decision"]] = counts.get(r["decision"], 0) + 1
    rd = {"schema": 1, "at": now, "at_pac": pac(now), "root": root, "head": head, "apply": apply, "counts": counts,
          "items": rows}
    if apply:
        _write(os.path.join(d, "state.json"), st)
        _write(os.path.join(d, "reading.json"), rd)
        with open(os.path.join(d, "ticks.jsonl"), "a", encoding="utf-8") as f:
            f.write(json.dumps({"at": now, "counts": counts,
                                "closed": [i for i, r in rows.items() if r["decision"] == "closed_by_check"]}) + "\n")
    return rd


STARTED = ("doing", "built", "validated")


def closed_main(ids, started=False):
    """-> exit code: 0 every id is terminal (started: or doing, built, validated), 1 one is not or was never filed, 2 the
    ledger could not be read or no id was given."""
    if not ids:
        print("closed: name at least one item")
        return 2
    try:
        w = _world()
    except Exception as e:  # noqa: BLE001 - could not look is its own exit
        print("UNMEASURED: the ledger could not be read (%s: %s)" % (type(e).__name__, e))
        return 2
    open_ = []
    for i in ids:
        it = w.items.get(i)
        st = "never filed" if it is None else it.state
        print("%-12s %s" % (st, i))
        if it is None or it.state not in CLOSED + (STARTED if started else ()):
            open_.append(i)
    print("%d of %d %s" % (len(ids) - len(open_), len(ids), "started or closed" if started else "closed"))
    return 1 if open_ else 0


def _print(rd):
    for iid, r in sorted(rd["items"].items()):
        print("%-64s %-16s %s" % (iid, r["decision"], _one(r.get("why"), 160)))
    print("list_effect %s at %s: %d item(s) with a check; %s" % (
        "beat" if rd.get("apply") else "dry beat", rd["at_pac"], len(rd["items"]),
        ", ".join("%s %d" % kv for kv in sorted(rd["counts"].items())) or "nothing to do"))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("tick")
    t.add_argument("--apply", action="store_true", help="close and write state; without it, a dry beat")
    sub.add_parser("status")
    c = sub.add_parser("check")
    c.add_argument("text")
    k = sub.add_parser("closed")
    k.add_argument("ids", nargs="*")
    k.add_argument("--started", action="store_true", help="an item taken up (doing, built, validated) also passes")
    o = ap.parse_args(argv)
    if o.cmd == "closed":
        return closed_main(o.ids, o.started)
    if o.cmd == "tick":
        _print(tick(apply=o.apply))
        return 0
    if o.cmd == "status":
        rd = _read(os.path.join(sdir(create=False), "reading.json"), None)
        if not rd:
            print("UNMEASURED: no reading yet at %s" % os.path.join(sdir(create=False), "reading.json"))
            return 2
        _print(rd)
        return 0
    v, out = run(o.text, check_root())
    print(v)
    if out:
        print(out)
    return {"holds": 0, "fails": 1}.get(v, 2)


if __name__ == "__main__":
    sys.exit(main())
