#!/usr/bin/env python3
"""relentless_bindjudge.py -- the launch the binding-repair judge never had (RELENTLESS_WIRE_BINDING_JUDGE_NOBODY_RUNS).

`relentless.py rebind` parks an item on an independent judge and `bind-judge` takes the ruling, but no program ever
started that judge: on 2026-11-07 53 proposals had met 3 hand rulings and 44 items sat blocked on kind judge. Each tick:
  - a repair that has been ruled (st["binding_ruled"], set by bind_judge under the lock) lifts its ledger block, so the
    item returns to a worker with the reason in its learned notes. A block of another kind (his park) is left standing;
  - a proposal on an item out of any worker's hands gets a fresh judge in its own detached unit, oldest first, at most
    IN_FLIGHT at a time, from the supervisor's released code, never from the item's clone. The unit rules through
    relentless.bind_judge, the same door as the CLI verb. AMBIGUOUS goes back to the worker here (give_back): nothing
    else would ever rule again on it;
  - a judge that ends with no ruling is tried again next tick, at most TRIES times per proposal, then the alarm carries it;
  - one alarm per episode when a proposal has waited over WAIT_ALARM_S (2 h).
A test's Fx has no bindjudge_kick, so it starts nothing. Limits are constants: the rules file does not grow (owner card
2026-11-06). The verb is `work <item> <pid>`, the unit's body.
"""
import calendar
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import relentless_exam  # noqa: E402

IN_FLIGHT = 4
TRIES = 3
JUDGE_MAX_S = 900
WAIT_ALARM_S = 2 * 3600
ENDED = ("done", "retired")
ELIGIBLE = ("blocked", "queued")    # running/stopping: the worker may still be on its way to the snag; closing cannot take it
RULING_RX = re.compile(r"^\s*RULING\s+(\{.*\})\s*$", re.M)
JUDGE_NAME = "rm-judge-"            # plus the proposal id: bind_judge refuses a name that reads as a worker of the item

PROMPT = """You are the independent Setter/Judge for a binding repair in the RimMandrake Relentless pipeline. You did not
build this item and you will never build it. A worker says the way its obligation is MEASURED is broken and proposes a new
measurement. The obligation itself may not move.

{packet}

Your working directory {repo} is the supervisor's released code. The item's own working clone is {clone} (its candidate commit: {cand}).
Read whatever you need there (the old and new proof scripts above all). Run nothing that writes; change nothing; run no
relentless.py verb.

Rule on one question: does the new binding measure the SAME obligation at least as independently as the old one?
  approve    it does, and the stated defect of the old binding is real.
  reject     it weakens the obligation, measures something else, or the old binding is not actually broken.
  ambiguous  you cannot tell from what you can read. Say exactly what evidence the worker must bring.

Your `why` goes to the next worker word for word: name the proof, the file and the fact you read.
End your answer with exactly one line, this form, on a line of its own:
RULING {{"verdict": "approve|reject|ambiguous", "why": "..."}}
"""


def pid_of(p):
    return hashlib.sha1(("%s|%s|%s" % (p.get("at"), p.get("by"), p.get("from_binding_hash"))).encode("utf-8")).hexdigest()[:10]


def unit_name(item, pid, tries):
    return "rm-relentless-bindjudge-" + hashlib.sha1(("%s/%s/%d" % (item, pid, tries)).encode("utf-8")).hexdigest()[:10]


def _dir(store):
    d = store.p("bindjudge")
    os.makedirs(d, exist_ok=True)
    return d


def _read(path):
    try:
        with open(path, encoding="utf-8") as f:
            got = json.load(f)
        return got if isinstance(got, dict) else {}
    except (OSError, ValueError):       # absent, or torn by a kill: one try more, never a dead tick
        return {}


def _write(path, obj):
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path), prefix=".bj-")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(obj, f, sort_keys=True)
    os.replace(tmp, path)


def _book(store, item):
    return os.path.join(_dir(store), item + ".json")


def _epoch(at):
    try:
        return calendar.timegm(time.strptime(str(at)[:19], "%Y-%m-%dT%H:%M:%S"))
    except ValueError:
        return None


def kick(store, item, pid, tries, runner=subprocess.run):
    """Start one judge, detached, from this release's code. -> None or why not."""
    tool = os.path.abspath(__file__)
    out = os.path.join(_dir(store), item + ".unit.out")
    argv = ["systemd-run", "--user", "--quiet", "--collect", "--unit", unit_name(item, pid, tries),
            "-p", "StandardOutput=append:" + out, "-p", "StandardError=append:" + out,
            "-p", "RuntimeMaxSec=%d" % JUDGE_MAX_S, "--working-directory", os.path.dirname(tool),
            "--setenv", "RELENTLESS_ROOT=" + store.root, "--setenv", "PATH=" + os.environ.get("PATH", "/usr/bin:/bin"),
            "--setenv", "PYTHONDONTWRITEBYTECODE=1", "--", sys.executable, tool, "work", item, pid]
    try:
        r = runner(argv, capture_output=True, text=True, timeout=60, stdin=subprocess.DEVNULL)
    except (OSError, subprocess.SubprocessError) as e:
        return "%s: %s" % (type(e).__name__, e)
    return ("systemd-run exit %d: %s" % (r.returncode, ((r.stdout or "") + (r.stderr or "")))) if r.returncode else None


def _in_flight(book, now):
    return bool(book.get("launched_at")) and not book.get("ended_at") and now - book["launched_at"] < JUDGE_MAX_S


def _lift(store, fx, st, now, acts, iso):
    """A ruled repair lets the item back. The ledger block goes only when it is the judge's; bind_judge wrote the flag."""
    item = st["item"]
    if st.get("status") in ("blocked", "queued") and not st.get("block_pending"):
        led = fx.item_state(item) or {}
        line = led.get("block")
        if line and line.rsplit("(kind ", 1)[-1].split(",")[0].rstrip(")") != "judge":
            return      # a block of another kind holds it: the flag waits, and is read again when that one ends
        if line:
            why = fx.ledger_unblock(item, "binding repair ruled %s: back to its builder" % st["binding_ruled"].get("verdict"))
            if why:
                acts.append({"do": "bindjudge_unblock_failed", "item": item, "why": why})
                return
        with store.lock():
            cur = store.load(item)
            cur.pop("binding_ruled", None)
            store.save(cur)
        acts.append({"do": "bindjudge_returned", "item": item})


def _alarm(store, fx, waiting, now, acts, iso):
    path = os.path.join(_dir(store), "alarm.json")
    late = sorted((a, st["item"]) for a, st in waiting if a is not None and now - a > WAIT_ALARM_S)
    if not late:
        if os.path.exists(path):
            os.remove(path)
        return
    was = _read(path)
    if was.get("said"):
        return
    oldest = (now - late[0][0]) / 3600
    text = "%d binding repair(s) have waited over %d h for a judge, the oldest %.1f h: %s" % (
        len(late), WAIT_ALARM_S // 3600, oldest, ", ".join(i for _a, i in late[:6]))
    store.journal({"at": iso(now), "do": "alarm", "kind": "binding_judge_waiting", "why": text})
    acts.append({"do": "binding_judge_waiting", "n": len(late)})
    if not fx.conductor_alarm(text):
        _write(path, {"said": iso(now)})


def sweep(store, fx, now, acts, iso, paused=False):
    """Under the tick lock. Lift what was ruled, start judges for what waits, say so when one has waited too long."""
    states = store.states()
    waiting = []
    for st in states:
        if st.get("status") in ENDED:
            continue
        if st.get("binding_ruled") and not st.get("binding_proposal"):
            _lift(store, fx, st, now, acts, iso)
        if st.get("binding_proposal"):
            waiting.append((_epoch(st["binding_proposal"].get("at")), st))
    _alarm(store, fx, waiting, now, acts, iso)
    launch = getattr(fx, "bindjudge_kick", None)
    if launch is None or paused:
        return
    books = {st["item"]: _read(_book(store, st["item"])) for _a, st in waiting}
    live = sum(1 for b in books.values() if _in_flight(b, now))
    for _a, st in sorted(waiting, key=lambda w: (w[0] or 0, w[1]["item"])):
        if live >= IN_FLIGHT:
            break
        item, p = st["item"], st["binding_proposal"]
        if st.get("status") not in ELIGIBLE or st.get("block_pending"):
            continue
        pid = pid_of(p)
        b = books[item] if books[item].get("pid") == pid else {"pid": pid, "tries": 0}
        if _in_flight(b, now) or b["tries"] >= TRIES:
            continue
        b.update(tries=b["tries"] + 1, launched_at=now, ended_at=None)
        _write(_book(store, item), b)
        why = launch(store, item, pid, b["tries"])
        store.journal({"at": iso(now), "do": "bindjudge_launched", "item": item, "try": b["tries"], "why": why})
        acts.append({"do": "bindjudge_launched", "item": item, "why": why})
        if why:
            b["ended_at"] = now
            _write(_book(store, item), b)
        else:
            live += 1


def read_ruling(out_path):
    """-> (verdict, why) from the judge's output file, or None. The JSON envelope's `result` only: a prompt echoed in a log
    or a RULING inside a quoted file never rules."""
    try:
        with open(out_path, encoding="utf-8", errors="replace") as f:
            raw = f.read()
    except OSError:
        return None
    text = None
    for line in raw.splitlines():
        try:
            d = json.loads(line)
        except ValueError:
            continue
        for row in d if isinstance(d, list) else [d]:       # one envelope, or the array form of the same output format
            if isinstance(row, dict) and isinstance(row.get("result"), str):
                text = row["result"]
    found = RULING_RX.findall(text or "")
    if not found:
        return None
    try:
        d = json.loads(found[-1])
        verdict, why = d.get("verdict"), (d.get("why") or "").strip()
    except (ValueError, AttributeError):
        return None
    return (verdict, why) if verdict and why else None


def rule(R, store, item, judge, verdict, why, env=None):
    """Through relentless.bind_judge. An approve the machine refuses (a dead proof, a contract that moved under it) is a
    rejection with the machine's reason: the item must not wait on a ruling that can never apply."""
    cwd = _dir(store)
    try:
        return R.bind_judge(store, item, judge, verdict, why, env=env, cwd=cwd, give_back=True)
    except ValueError as e:
        if verdict != "approve":
            raise
        return R.bind_judge(store, item, judge, "reject", "The judge approved (%s), the machine refused: %s" % (why, e), env=env, cwd=cwd, give_back=True)


def work(store, item, pid, runner=subprocess.run, env=None):
    """The unit's body: judge one proposal. -> 0 ruled (or nothing left to rule), 1 no ruling (the tick tries again)."""
    import relentless as R
    st = store.load(item)
    p = (st or {}).get("binding_proposal")
    path = _book(store, item)
    code = 1
    try:
        if not p or pid_of(p) != pid:
            code = 0
            return code
        import relentless_binding
        repo = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
        prompt = PROMPT.format(packet=relentless_binding.packet(st), repo=repo, clone=st.get("clone") or "(reaped)",
                               cand=st.get("candidate") or "(none yet)")
        out = os.path.join(_dir(store), "%s.%s.out" % (item, pid))
        cfg = relentless_exam.config()      # cwd: `--agent rm-judge` is a project agent, found only from inside a repo tree
        relentless_exam.run_setter(repo, prompt, {"setter_agent": cfg.get("setter_agent", "rm-judge"),
                                                 "setter_model": cfg.get("setter_model", "opus"),
                                                 "setter_max_s": JUDGE_MAX_S - 30}, out, runner=runner)
        got = read_ruling(out)
        if not got:
            print("bindjudge %s: the judge ended with no RULING line (%s)" % (item, out))
            return code
        print(rule(R, store, item, JUDGE_NAME + pid, got[0], got[1], env=env))
        code = 0
        return code
    except ValueError as e:     # the item moved (ended, ruled by hand) while the judge read: nothing to retry unless it waits
        print("bindjudge %s: %s" % (item, e))
        return code
    finally:
        b = _read(path)
        if b.get("pid") == pid:
            b["ended_at"] = time.time()
            _write(path, b)


def main(argv):
    if len(argv) != 3 or argv[0] != "work":
        print("usage: relentless_bindjudge.py work <item> <pid>", file=sys.stderr)
        return 2
    import relentless as R
    return work(R.Store(os.environ.get("RELENTLESS_ROOT") or R.DEFAULT_ROOT), argv[1], argv[2])


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
