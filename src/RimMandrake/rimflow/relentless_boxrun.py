"""Run the contract's proof as written in the Marker's box (RELENTLESS_BUILD_BOXRUN_AT_FINISH, redesign_final.md WP-07).

Owner 2026-11-06: "the checker should run the code to check it rather than philosophize". About 66 Marker returns all-time
were a proof that could not run as written; each one cost a Marker launch to learn what a mechanical run says in seconds.

Two callers:
- `finish()` (relentless.py) at the landed sha. It snapshots the contract under store.lock, RELEASES the lock, runs the
  proof here, then retakes the lock and re-fences (gen, status, contract hash) before it writes the receipt: a run of
  minutes never freezes the supervisor's tick (redesign_final.md G9).
- the `boxrun` verb: the builder runs the same box at its HEAD before it lands.

What runs: the shell commands at the head of the contract's proof (extract()), cut where prose starts. Only simple
python3/python/bash commands joined by `&&` (each may be negated with `!`) are run; anything else is `unrunnable` and
neither passes nor refuses. A contract that names offbox adapters or a reach_ok why measures outside the box: `skipped`.

Modes (relentless_boxrun.json `mode`): `off`; `shadow` runs and prints, refuses nothing; `enforce` refuses a red proof
with the box output on the builder's stdout. Every run (any verdict but off) is an immutable `run` receipt in the item's
evidence record at the sha (evidence.py, WP-09a: <store>/evidence/<ID>/<sha>.jsonl, hash-chained, anchored in
evidence/index.jsonl). That is the one receipt format: the SLI (Marker launches avoided = enforce reds per candidate; in
shadow, would-refuse reds) counts the evidence index, and finish's gen receipt carries the entry's hash.
"""
import hashlib
import json
import os
import re
import shlex
import subprocess
import sys
import time

import evidence
import relentless_wall

HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG = os.path.join(HERE, "relentless_boxrun.json")
MODES = ("off", "shadow", "enforce")
RUNNERS = ("python3", "python", "bash")


def config(path=None):
    """-> relentless_boxrun.json; a missing or unreadable file is mode off (nothing runs, nothing is refused)."""
    try:
        with open(path or CONFIG, encoding="utf-8") as f:
            got = json.load(f)
    except (OSError, ValueError):
        return {"mode": "off"}
    if not isinstance(got, dict) or got.get("mode") not in MODES:
        return {"mode": "off"}
    return got


# ---------------------------------------------------------------- what to run

# Where a proof's prose starts: a verb about the result, a colon, a parenthesis, a comma, a semicolon, an arrow.
_CUT = re.compile(r"\s+(?:exits?|exit code|prints?|printing|shows?|showing|reports?|returns?|outputs?|passes|is|are|"
                  r"must|should|gives?|says?|succeeds?|fails?|with|and then|then|both|all|green|GREEN|red|RED)\b"
                  r"|\s*:(?:\s|$)|\s+\(|,\s|;|\s+(?:->|=>|→|—|–|-)\s|\.\s+[A-Z]|\.$")
_WORD_OK = re.compile(r"^(?:-.*|.*[/._=0-9].*|[A-Z][A-Z0-9_]*|[a-z][a-z0-9]*_[a-z0-9_]*)$")
_PLAIN = re.compile(r"^[a-z]+$")
_SHELL_META = re.compile(r"[|<>`$*?{}\[\]~#]|\|\||\s&\s|&$")


def _quote_word(w):
    """shlex.quote, but a leading NAME=value stays an assignment (only the value is quoted)."""
    m = re.fullmatch(r"([A-Za-z_][A-Za-z0-9_]*)=(.*)", w, re.S)
    return "%s=%s" % (m.group(1), shlex.quote(m.group(2))) if m else shlex.quote(w)


def extract(proof):
    """-> (shell command, None) or (None, why it is not run). The head of the proof up to where prose starts, split on
    `&&`; each part one python3/python/bash command whose words read as arguments. A plain lowercase word is an argument
    only right after the script (a sub-command) or after an option (its value); elsewhere it is prose and ends the part."""
    text = (proof or "").strip().replace("\n", " ")
    m = _CUT.search(text)
    head = (text[:m.start()] if m else text).strip()
    if not head:
        return None, "no command at the head of the proof"
    parts = [p.strip() for p in head.split("&&")]
    out = []
    for n, part in enumerate(parts):
        if not part:
            return None, "an empty part in %r" % head[:120]
        if _SHELL_META.search(part):
            if n == 0:
                return None, "shell syntax beyond `&&` and `!` (pipe, redirect, expansion, glob): %r" % part[:120]
            break
        try:
            words = shlex.split(part)
        except ValueError as e:
            return None, "unparseable: %s" % e
        neg = words[:1] == ["!"]
        words = words[1:] if neg else words
        envs = []
        while words and re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*=\S*", words[0]):
            envs.append(words.pop(0))
        if not words or words[0] not in RUNNERS:
            if n == 0:
                return None, "not a %s command: %r" % ("/".join(RUNNERS), part[:120])
            break
        keep = envs + words[:1]
        rest = words[1:]
        if words[0] != "bash" and rest[:1] == ["-c"]:
            return None, "inline code (-c) is not run: %r" % part[:120]
        if rest[:1] == ["-m"] and len(rest) > 1:
            keep += rest[:2]
            rest = rest[2:]
        elif rest:
            if not (rest[0].endswith((".py", ".sh")) or "/" in rest[0]):
                if n == 0:
                    return None, "no script after %s: %r" % (words[0], part[:120])
                break
            keep.append(rest[0])
            rest = rest[1:]
        else:
            return None, "%s with no script" % words[0]
        prev = None
        for i, w in enumerate(rest):
            if _PLAIN.match(w) and not (i == 0 or (prev or "").startswith("-")):
                break
            if not (_WORD_OK.match(w) or _PLAIN.match(w)) and not (w and " " in w):
                break
            keep.append(w)
            prev = w
        out.append(("! " if neg else "") + " ".join(_quote_word(w) for w in keep))
    return " && ".join(out), None


def contract_hash(contract):
    """relentless.contract_hash, the id finish() writes into the receipt, so the re-fence compares the same thing."""
    return hashlib.sha256(json.dumps(contract or {}, sort_keys=True).encode()).hexdigest()


def skip_reason(contract):
    """-> why the proof is not the box's to run (it measures outside the wall), or None."""
    c = contract or {}
    if c.get("offbox"):
        return "the contract reads offbox adapters (%s), run outside the box at check time" % ", ".join(c["offbox"])
    if c.get("reach_ok"):
        return "the contract's reach_ok says the box hides part of its proof"
    return None


# ---------------------------------------------------------------- running it

def toplevel(cwd):
    r = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=cwd, capture_output=True, text=True, timeout=30)
    if r.returncode:
        raise RuntimeError("not a git tree: %s" % cwd)
    return r.stdout.strip()


def run_in_box(cmd, sha, source, store_root, rules, timeout_s, nonce=None, base=None, item=None, texts=()):
    """-> {exit, out, secs, box_error}. The tree at sha exported as the Marker's box (relentless_wall.make_box, which
    since WP-02 carries git history and the toolchain), the command written to a script inside the box (systemd expands
    `$` in a unit's command line, lesson 1310Z-BENCH-systemd-run-expands-dollar-brace), run under the Marker's own systemd
    properties and environment from the box's tree, the box removed after. exit None: it did not run (box_error says why)
    or it timed out."""
    prof = relentless_wall.profile(rules)
    if not prof:
        return {"exit": None, "out": "", "secs": 0, "box_error": "no marker wall profile in the rules"}
    nonce = nonce or "boxrun-" + hashlib.sha256(os.urandom(16)).hexdigest()[:20]
    t0 = time.time()
    box = None
    try:
        os.makedirs(prof["box_root"], exist_ok=True)
        box = relentless_wall.make_box(prof, source, sha, nonce, base=base, item=item)
        script = os.path.join(box, "boxrun.sh")
        with open(script, "w", encoding="utf-8") as f:
            f.write("#!/bin/bash\nset -o pipefail\n%s\n" % cmd)
        thru = relentless_wall.through(prof, list(texts))
        unit = "rm-boxrun-%s" % nonce[-20:]
        argv = (["systemd-run", "--user", "--wait", "--pipe", "--collect", "--quiet", "--unit", unit,
                 "-p", "WorkingDirectory=" + os.path.join(box, "tree"), "-p", "RuntimeMaxSec=%d" % int(timeout_s)]
                + relentless_wall.props(prof, box, [store_root], thru)
                + sum((["--setenv", "%s=%s" % kv] for kv in relentless_wall.unit_env(prof, box).items()), [])
                + ["--", "/bin/bash", script])
        try:
            p = subprocess.run(argv, capture_output=True, encoding="utf-8", errors="replace", timeout=timeout_s + 30,
                           stdin=subprocess.DEVNULL)
        except subprocess.TimeoutExpired as e:
            subprocess.run(["systemctl", "--user", "stop", unit], capture_output=True, timeout=60)
            out = (e.stdout or b"") if isinstance(e.stdout, bytes) else (e.stdout or "").encode()
            return {"exit": None, "out": out.decode("utf-8", "replace"), "secs": round(time.time() - t0, 1),
                    "box_error": "timed out after %ds" % timeout_s}
        out = (p.stdout or "") + (p.stderr or "")
        secs = round(time.time() - t0, 1)
        if secs >= timeout_s:       # RuntimeMaxSec killed it: a timeout, not a red
            return {"exit": None, "out": out, "secs": secs, "box_error": "timed out after %ds" % timeout_s}
        if 200 <= p.returncode <= 243 and not out.strip():     # systemd's own spawn failures (226 NAMESPACE: a bind
            return {"exit": None, "out": out, "secs": secs,       # path missing): the box never started, no verdict
                    "box_error": "systemd could not start the box (exit %d, see journalctl --user)" % p.returncode}
        return {"exit": p.returncode, "out": out, "secs": secs, "box_error": None}
    except (OSError, RuntimeError, ValueError, subprocess.SubprocessError) as e:
        return {"exit": None, "out": "", "secs": round(time.time() - t0, 1), "box_error": "%s: %s" % (type(e).__name__, str(e)[-300:])}
    finally:
        if box:
            relentless_wall.remove_box(box)


RUN = run_in_box    # the seam selftests replace: (cmd, sha, source, store_root, rules, timeout_s, **kw) -> result dict


def check(store, item, gen, sha, contract, source, rules, cfg=None, kind="finish", base=None, evidence="", say=None):
    """-> the run record (verdict green | red | unrunnable | skipped | box_error | off). Prints what the box printed on
    stdout (`say`). Every verdict but off is written as an evidence `run` receipt (_receipt). Raises nothing: refusing is refusal()'s, so the caller
    decides under which mode a red stops it."""
    cfg = config() if cfg is None else cfg
    say = say or (lambda s: print(s, flush=True))
    rec = {"at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "item": item, "gen": gen, "sha": sha, "kind": kind,
           "mode": cfg.get("mode", "off")}
    if rec["mode"] == "off":
        rec["verdict"] = "off"
        return rec
    why = skip_reason(contract)
    cmd, unrun = (None, None) if why else extract((contract or {}).get("proof"))
    if why or unrun:
        rec.update(verdict="skipped" if why else "unrunnable", why=why or unrun)
        say("relentless boxrun: %s: %s" % (rec["verdict"], rec["why"]))
        _receipt(store, rec, contract, None, source)
        return rec
    rec["cmd"] = cmd
    try:
        src = toplevel(source)
    except (OSError, RuntimeError, subprocess.SubprocessError) as e:
        rec.update(verdict="box_error", why=str(e)[-300:])
        _receipt(store, rec, contract, cmd, source)
        return rec
    got = RUN(cmd, sha, src, store.root, rules, int(cfg.get("timeout_s") or 420), base=base, item=item,
              texts=[json.dumps(contract or {}), evidence or ""])
    out = got.get("out") or ""
    rec.update(exit=got.get("exit"), secs=got.get("secs"), out_sha256=hashlib.sha256(out.encode()).hexdigest(),
               out_tail=out[-int(cfg.get("log_tail") or 600):])
    if got.get("box_error") or got.get("exit") is None:
        rec.update(verdict="box_error", why=got.get("box_error") or "no exit")
    else:
        rec["verdict"] = "green" if got["exit"] == 0 else "red"
    tail = out[-int(cfg.get("out_tail") or 6000):]
    say("relentless boxrun (%s, %s at %s): %s%s\n$ %s\n%s%s" % (
        rec["mode"], kind, sha[:10], rec["verdict"].upper(),
        " exit %s in %ss" % (rec.get("exit"), rec.get("secs")) if rec["verdict"] in ("green", "red") else ": " + rec.get("why", ""),
        cmd, "" if len(tail) == len(out) else "[... %d chars above cut]\n" % (len(out) - len(tail)), tail.rstrip()))
    _receipt(store, rec, contract, cmd, src)
    return rec


def refusal(rec, item, gen):
    """-> why finish refuses, or None: only a red proof under mode enforce."""
    if rec.get("verdict") != "red" or rec.get("mode") != "enforce":
        return None
    return ("the contract's proof is RED in the Marker's box at %s (exit %s; its output is on stdout above). A Marker "
            "would run the same and return the work. Fix the work (or, if the proof itself is broken, `rebind`), land, and "
            "finish again; `relentless.py boxrun --item %s --gen %s` reruns it at HEAD"
            % (rec["sha"][:10], rec.get("exit"), item, gen))


def refence(st, snap_hash):
    """After the unlocked run: the contract the run measured must still be the item's contract."""
    if contract_hash(st.get("contract")) != snap_hash:
        raise ValueError("the contract changed while its proof ran in the box: finish again so the run measures the "
                         "contract the receipt will name")


def argv_of(cmd):
    """The argv the box ran: run_in_box writes `set -o pipefail` + cmd to a script and runs it with /bin/bash; this is
    the same program as one argv a Marker rerun can execute."""
    return ["/bin/bash", "-o", "pipefail", "-c", cmd] if cmd else None


def full_sha(source, sha):
    """-> the full commit id for sha (a short id is resolved in source), or sha unchanged when it cannot be resolved."""
    if isinstance(sha, str) and re.fullmatch(r"[0-9a-f]{40}", sha):
        return sha
    try:
        r = subprocess.run(["git", "rev-parse", "--verify", "--quiet", "%s^{commit}" % sha], cwd=source,
                           capture_output=True, text=True, timeout=30)
        return r.stdout.strip() if r.returncode == 0 and r.stdout.strip() else sha
    except (OSError, subprocess.SubprocessError, TypeError):
        return sha


def _receipt(store, rec, contract, cmd, source):
    """The run's immutable receipt (evidence.run_receipt). rec gains `evidence` {n, hash, path} or `evidence_error`: a
    receipt that cannot be written is said loudly and never stops the finish (09a writes; nothing reads it to gate yet)."""
    try:
        sha = full_sha(source, rec.get("sha"))
        e = evidence.run_receipt(store.dir, rec.get("item"), sha, rec, contract_hash(contract), argv_of(cmd))
        rec["evidence"] = {"n": e["n"], "hash": e["hash"], "path": evidence.record_path(store.dir, rec["item"], sha)}
    except (OSError, ValueError) as ex:      # TamperError is a ValueError
        rec["evidence_error"] = "%s: %s" % (type(ex).__name__, str(ex)[:300])
        print("relentless boxrun: the evidence receipt was NOT written: %s" % rec["evidence_error"], file=sys.stderr)


def at_finish(store, item, gen, sha, contract, source, rules, st=None, evidence="", cfg=None):
    """finish()'s call, made OUTSIDE store.lock. -> the record for the receipt (None when nothing ran). Raises ValueError
    (finish's refusal) on a red proof under enforce. Runs only for the stores relentless_boxrun.json names (`stores`):
    the selftests' temporary stores finish without a box."""
    cfg = config() if cfg is None else cfg
    roots = [os.path.realpath(x) for x in cfg.get("stores") or []]
    if cfg.get("mode", "off") == "off" or os.path.realpath(store.root) not in roots:
        return None
    rec = check(store, item, gen, sha, contract, source, rules, cfg, "finish", base=(st or {}).get("base"), evidence=evidence)
    why = refusal(rec, item, gen)
    if why:
        raise ValueError(why)
    return {k: rec[k] for k in ("verdict", "mode", "exit", "secs", "cmd", "out_sha256", "why", "evidence", "evidence_error")
            if k in rec}


def verb(store, item, gen, sha, source, rules, cfg=None):
    """`relentless.py boxrun`: the builder's own run before it lands. -> process exit: 0 green, 1 red, 3 anything else.
    Runs in any mode but off; reads the contract, writes nothing but its evidence receipt (kind_of_run verb)."""
    cfg = dict(config() if cfg is None else cfg)
    if cfg.get("mode", "off") == "off":
        cfg["mode"] = "shadow"      # the builder asked: run it, refuse nothing
    with store.lock():
        st = store.load(item)
    if not st or not st.get("contract"):
        raise ValueError("%s has no contract: set it with `contract` first" % item)
    if gen is not None and st.get("gen") != gen:
        print("relentless boxrun: note: your gen %s is not the item's (%s)" % (gen, st.get("gen")), file=sys.stderr)
    rec = check(store, item, gen, sha, st["contract"], source, rules, cfg, "verb", base=st.get("base"))
    return {"green": 0, "red": 1}.get(rec["verdict"], 3)


def sli(store, since=None):
    """-> {kind/mode: {verdict: n}} over the evidence index's `run` rows, at or after `since` (ISO)."""
    out = {}
    for r in evidence.index_rows(store.dir, since):
        if r.get("kind") != "run":
            continue
        k = out.setdefault("%s/%s" % (r.get("kind_of_run"), r.get("mode")), {})
        k[r.get("verdict")] = k.get(r.get("verdict"), 0) + 1
    return out
