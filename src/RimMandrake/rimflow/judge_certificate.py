#!/usr/bin/env python3
"""The pre-judgement certificate (guard PRE_JUDGEMENT_CERTIFICATE, design/specs/2026-11-15-cheap-guards-at-every-door.md
section 4; item RIMMANDRAKE_CERTIFY_BARS_BEFORE_JUDGE_RED_TEST_WENT_IN). The owner, 2026-11-15: "how do we certify then
that it has all the tests needed to pass before we throw it to judgement? ... No reason to send it in knowing it will
fail, right?"

No blind judge and no in-game driver goes in on a mod while a program can already see one of its bars is red. For every
bar, every offline test that decides it (bar["offline_decides"]) is read on four clauses:
  decided            an offline bar (proves_at 2 or 4-5) names at least one offline decider, each also in its decides
  registered         the decider is in the table, with a file that exists and a command
  ran_on_this_build  its recorded run carries build_id of the test's `reads` and its own file, and that is the hash now;
                     a run that recorded its command must have run the table's command as it is now
  green              the run's rc is 0 and result PASS, and the test carries no `known_red`
  red_seen           the decider was seen to fail: PASS on a recorded red run (version/evidence/red_seen.json, written
                     only by red_seen(): a planted fault applied, the test run and seen non-zero, the fault reversed)
                     against the test file as it is now; WARN "grandfathered" for a test unchanged since its mod's
                     version/evidence/red_seen_grandfather.json was written (once, by grandfather()); REFUSED for a new
                     or edited deciding test with no proof (RIMMANDRAKE_RECORD_RED_SEEN_PER_TEST_OR_PASSED_GREEN)
Before an in-game visit (to="in_game") every in-game scene that decides a bar is also read on
  asks_on_empty_game the scene, run on an empty game (Utils/scene_empty_game.py: every bridge call a bare success), has no
                     row that reads PASS: a check that passes with nothing on the map tests nothing
                     (RIMMANDRAKE_DRYRUN_SCENES_ON_EMPTY_GAME_THREE_PASSED). Two harnesses have an adapter: FlowWorks'
                     concept_scenes.py STAGE3_SCENES and a file with a module-level modcheck suite whose chain the test
                     names as its entry (suite_vacuous); a scene in any other harness is did_not_run.
No model is called anywhere. `run_offline` is the path to pass for a stale table: it reruns the offline tests that are
stale, red or unstamped and stamps each with its build (`maturation.py certificate <Mod> --run`, zero tokens; a full
pass is `--all "<why>"`, a named act: owner, 2026-11-21, only the checks a change touches run again). A table that cannot be read is "did not run":
the guard lets the mod through and says so.

Contract: the docstring of acceptance/guard_judge_certificate_accept.py (the filing seat's; the builder does not edit it).
"""
import datetime
import hashlib
import json
import os
import re
import subprocess
import time

import check_margin as CM

TABLE = "version/test_table.json"
RUN_TIMEOUT_S = 6000      # the slowest measured offline decider is FlowWorks' C# suite, 531 s # budget: danger=a hung deciding test holds the certificate; longest=599s (the slowest offline PASS on a loaded machine, 2026-11-24)
# how long red_seen's no-fault probe waits before it reads the command as started. Danger: a probe as long as the test
# doubles every red proof (live commands run for minutes); evidence: a start-up death (import, shell syntax) ends in
# under 2 s, measured on the 46 Pyrelands live commands, 2026-11-20 (table_commands_start.py)
# budget: danger=a probe as long as the test doubles every red proof; longest=2s (start-up deaths of the 46 Pyrelands live
# budget: commands, 2026-11-20)
START_PROBE_S = 20
RED_SEEN = "version/evidence/red_seen.json"
# what a game loads only from a build and a deploy, never from the tree (red_seen refuses an in-game check planted there)
GAME_LOADED_EXT = (".cs", ".csproj", ".xml", ".dll")
GRANDFATHER = "version/evidence/red_seen_grandfather.json"
OFFLINE_STAGES = ("2", "4-5")   # a bar proving at one of these stages is decided offline
# budget: danger=a hung scene on an empty game holds the certificate; longest=0.15s (FlowWorks' 17 scenes, 2026-11-18)
EMPTY_GAME_TIMEOUT_S = 120      # FlowWorks' 17 scenes on an empty game: 0.15 s measured 2026-11-18


def tpath(root, mod):
    return os.path.join(root, "design", "concepts", mod, TABLE)


def _file_hash(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def build_id(root, paths):
    """-> a hash of the CONTENT of these repo-relative files, in a fixed order; a directory hashes every file under it
    (by its path inside the directory), a missing path hashes as missing. Content, never a time: the same bytes give
    the same id."""
    h = hashlib.sha256()
    for p in sorted(dict.fromkeys(str(x).rstrip("/") for x in paths or [] if x)):
        full = os.path.join(root, p)
        if os.path.isfile(full):
            h.update(("F %s %s\n" % (p, _file_hash(full))).encode())
        elif os.path.isdir(full):
            h.update(("D %s\n" % p).encode())
            for d, dirs, files in os.walk(full):
                dirs[:] = sorted(x for x in dirs if x not in ("bin", "obj", "__pycache__", ".git"))
                for f in sorted(files):
                    fp = os.path.join(d, f)
                    h.update(("  %s %s\n" % (os.path.relpath(fp, full), _file_hash(fp))).encode())
        else:
            h.update(("M %s\n" % p).encode())
    return h.hexdigest()[:20]


APPEND_ONLY = ("infrastructure/state/ledger/",)


def test_build(root, t):
    """-> build_id of the test's reads and its own file. A read of the ledger is left out: it is append-only (an event
    once written stays), and every seat's ledger write would otherwise stale a record test the moment it was stamped
    (Pyrelands' RECORD_ART_SHEET names infrastructure/state/ledger/events/ as its file and a read)."""
    paths = list(t.get("reads") or []) + ([t["file"]] if t.get("file") else [])
    return build_id(root, [p for p in paths if not str(p).startswith(APPEND_ONLY)])


def read_table(root, mod):
    """-> (table, None) or (None, why)."""
    p = tpath(root, mod)
    try:
        with open(p, encoding="utf-8") as f:
            tt = json.load(f)
    except FileNotFoundError:
        return None, "no file at %s" % os.path.relpath(p, root)
    except (OSError, ValueError) as e:
        return None, "%s cannot be read: %s" % (os.path.relpath(p, root), e)
    if not isinstance(tt, dict) or not isinstance(tt.get("tests"), dict) or not isinstance(tt.get("bars"), list):
        return None, "%s holds no tests object and bars list" % os.path.relpath(p, root)
    return tt, None


def _write_table(root, mod, tt):
    p = tpath(root, mod)
    with open(p, "rb") as f:
        old = f.read()
    nl, ascii_only = old.endswith(b"\n"), all(c < 128 for c in old)     # keep the file's own spelling: a diff of stamps
    tmp = p + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(json.dumps(tt, indent=1, ensure_ascii=ascii_only) + ("\n" if nl else ""))
    os.replace(tmp, p)


def _run_env():
    """A test's environment: ours, writing no bytecode, so a certificate run leaves the tree it read byte-for-byte as it
    found it (a red proof checks exactly that)."""
    return dict(os.environ, PYTHONDONTWRITEBYTECODE="1")


def _last_line(*texts):
    for t in texts:
        lines = [x.strip() for x in str(t or "").splitlines() if x.strip()]
        if lines:
            return lines[-1]
    return ""


def run_offline(root, mod, runner=subprocess.run, now=None, resume=False):
    """Run every offline test of the mod's table (its `command`, cwd root), and any other test a bar names among its
    offline deciders (a `record` read), and write back its runs_today with the build it ran on.
    resume (RIMMANDRAKE_RESUME_CERTIFICATE_RERUN_KILLED_AFTER_THIRTY_EIGHT): keep, unrun, a test whose stamp is green on
    the build and command it has now (the evidence a rerun would write); a red, stale or unstamped test still runs.
    -> {"ran": n, "failed": [ids], "seconds": total, "skipped": kept}; {"ran": 0, "failed": [], "error": why} when the
    table cannot be read. In-game tests are left alone."""
    tt, err = read_table(root, mod)
    if tt is None:
        return {"ran": 0, "failed": [], "error": err}
    dec = {d for b in tt["bars"] if isinstance(b, dict) and isinstance(b.get("offline_decides"), list)
           for d in b["offline_decides"]}
    ran, failed, total, skipped = 0, [], 0.0, 0
    for tid, t in tt["tests"].items():
        if not isinstance(t, dict) or not t.get("command") or not (t.get("kind") == "offline" or tid in dec):
            continue
        build = test_build(root, t)      # the content the run reads, taken before it runs
        old = t.get("runs_today") if isinstance(t.get("runs_today"), dict) else {}
        if resume and old.get("ran") and old.get("rc") == 0 and old.get("result", "PASS") == "PASS" \
                and old.get("build") == build \
                and old.get("command") == t["command"]:     # green as certify reads it: a stamp it refuses reruns
            skipped += 1
            continue
        t0 = time.time()
        try:
            r = runner(t["command"], shell=True, cwd=root, capture_output=True, text=True, timeout=RUN_TIMEOUT_S,
                       env=_run_env())
            rc, last, cut = r.returncode, _last_line(r.stdout, r.stderr), False
            margins = CM.parse(r.stdout)      # T2: [] when it printed none
        except subprocess.TimeoutExpired:
            rc, last, margins, cut = -1, "timed out after %d s" % RUN_TIMEOUT_S, None, True    # no verdict: never FAIL
        except OSError as e:
            rc, last, margins, cut = -1, "could not start: %s" % e, None, True
        secs = round(time.time() - t0, 2)
        at = now if now is not None else datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        t["runs_today"] = {"ran": True, "rc": rc, "seconds": secs, "last": last, "at": at,
                           "result": "PASS" if rc == 0 else "UNMEASURED" if cut else "FAIL", "build": build,
                           "command": t["command"]}
        if margins is not None:         # a run that never finished read no margin: no key, never []
            t["runs_today"]["margins"] = margins
        ran += 1
        total += secs
        if rc != 0:
            failed.append(tid)
        _write_table(root, mod, tt)     # after each test: a run killed part way keeps the stamps it earned
    return {"ran": ran, "failed": failed, "seconds": round(total, 2), "skipped": skipped}


def margin_rows(tt):
    """T2 (RIMMANDRAKE_LIST_THINNEST_MARGINS_IN_CERTIFICATE_RUN): -> (rows, none, unread) over the tests run_offline
    runs. rows: [{"test", "worst", "limit", "cases", "name"?, "thinness"}], each test's thinnest margin, thinnest first;
    none: ids that ran and printed no margin; unread: ids whose stamp holds no margins key (not run since margins were
    read, or a run that never finished). Reads only: the verdict is certify's alone."""
    rows, none, unread = [], [], []
    dec = {d for b in tt.get("bars") or [] if isinstance(b, dict) and isinstance(b.get("offline_decides"), list)
           for d in b["offline_decides"]}
    for tid, t in sorted((tt.get("tests") or {}).items()):
        if not isinstance(t, dict) or not t.get("command") or not (t.get("kind") == "offline" or tid in dec):
            continue
        ms = (t.get("runs_today") or {}).get("margins") if isinstance(t.get("runs_today"), dict) else None
        if not isinstance(ms, list):
            unread.append(tid)
        elif not ms:
            none.append(tid)
        else:
            m = min(ms, key=CM.thinness)
            rows.append(dict(m, test=tid, thinness=CM.thinness(m)))
    return sorted(rows, key=lambda r: (r["thinness"], r["test"])), none, unread


def _ended_items(root, ids):
    """-> the known_red items closed, dropped or superseded on the ledger (maturation.ledger_ended, 0.06 s measured);
    an empty set when it cannot be read: the mark then refuses as written."""
    if not ids:
        return set()
    try:
        import maturation
        return set(maturation.ledger_ended(root, ids))
    except Exception:  # noqa: BLE001
        return set()


def _evidence_path(root, mod, name):
    return os.path.join(os.path.dirname(os.path.dirname(tpath(root, mod))), name)


def _read_evidence(root, mod, name):
    """-> the evidence file's object; {} when it is absent (looked, none); None when it is there but cannot be read
    (could not look: never read as "no proof", never overwritten)."""
    p = _evidence_path(root, mod, name)
    if not os.path.exists(p):
        return {}
    try:
        with open(p, encoding="utf-8") as f:
            v = json.load(f)
    except (OSError, ValueError):
        return None
    return v if isinstance(v, dict) else None


def _write_evidence(root, mod, name, obj, exclusive=False):
    """Write the evidence file atomically; exclusive: only when no such file exists (-> False when one does)."""
    p = _evidence_path(root, mod, name)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    tmp = "%s.%d.tmp" % (p, os.getpid())
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(json.dumps(obj, indent=1, sort_keys=True) + "\n")
    if not exclusive:
        os.replace(tmp, p)
        return True
    try:
        os.link(tmp, p)         # fails when the file exists: two writers cannot both create it
        return True
    except FileExistsError:
        return False
    finally:
        os.remove(tmp)


def test_blob(root, t):
    """-> the git blob hash of the test's own file as it is now (computed, no git needed); for a record test that names
    a folder, "dir:" + its build_id (an append-only ledger folder: a constant, as test_build leaves it out); "missing"."""
    f = t.get("file") if isinstance(t, dict) else None
    p = os.path.join(root, f) if f else None
    if p and os.path.isdir(p):
        return "append-only" if str(f).startswith(APPEND_ONLY) else "dir:" + build_id(root, [f])
    if not p or not os.path.isfile(p):
        return "missing"
    with open(p, "rb") as fh:
        data = fh.read()
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def grandfather(root, mod):
    """Write version/evidence/red_seen_grandfather.json ONCE: {test id: blob of its file now} for every test of the table
    with a file, so a test that existed when the clause arrived owes no red proof until it is edited. A list already
    there is never rewritten or widened. -> {"written": bool, "tests": n, "why"}."""
    if os.path.exists(_evidence_path(root, mod, GRANDFATHER)):
        return {"written": False, "tests": len(_read_evidence(root, mod, GRANDFATHER) or {}),
                "why": "%s is already written; it is never widened" % GRANDFATHER}
    tt, err = read_table(root, mod)
    if tt is None:
        return {"written": False, "tests": 0, "why": "the table cannot be read: %s" % err}
    gf = {tid: test_blob(root, t) for tid, t in sorted(tt["tests"].items()) if isinstance(t, dict) and t.get("file")}
    gf = {k: v for k, v in gf.items() if v != "missing"}
    if not _write_evidence(root, mod, GRANDFATHER, gf, exclusive=True):
        return {"written": False, "tests": len(_read_evidence(root, mod, GRANDFATHER) or {}),
                "why": "%s was written by another call meanwhile; it is never widened" % GRANDFATHER}
    return {"written": True, "tests": len(gf), "why": "grandfathered %d tests" % len(gf)}


def _patch_paths(root, patch):
    """-> (the repo-relative paths the patch touches, None) or (None, why); NUL-delimited, so no path is quoted."""
    r = subprocess.run(["git", "apply", "--numstat", "-z", patch], cwd=root, capture_output=True, timeout=60)
    if r.returncode != 0:
        return None, "the patch does not parse: %s" % (r.stderr.decode("utf-8", "replace").strip()
                                                       or "rc %s" % r.returncode)
    paths, recs = [], r.stdout.decode("utf-8", "surrogateescape").split("\0")
    i = 0
    while i < len(recs):
        rec = recs[i]
        if rec.count("\t") >= 2:
            name = rec.split("\t", 2)[2]
            if name:
                paths.append(name)
            else:                       # a rename: "added\tdeleted\t" then the old and new paths
                paths += [x for x in recs[i + 1:i + 3] if x]
                i += 2
        i += 1
    return (sorted(set(paths)), None) if paths else (None, "the patch touches no file")


def _snapshot(root, paths):
    out = {}
    for p in paths:
        fp = os.path.join(root, p)
        if os.path.isfile(fp):
            with open(fp, "rb") as fh:
                out[p] = fh.read()
        else:
            out[p] = None
    return out


NO_VERDICT_RC = (126, 127)      # the shell could not run the command: not a test that failed


def _no_verdict(rc):
    """True for an exit that is no test's verdict: none, a signal (negative, or the shell's 128 + n), 126/127."""
    return rc is None or rc < 0 or rc > 128 or rc in NO_VERDICT_RC


def _watch_paths(root, t, paths):
    """-> every regular file a red proof must leave as it found it: the patch's, the test's own, its reads (a folder
    read: every file under it, build artefacts left out)."""
    out = set(paths)
    for p in [t.get("file")] + list(t.get("reads") or []):
        fp = os.path.join(root, p) if p else None
        if not fp or str(p).startswith(APPEND_ONLY):
            continue
        if os.path.isfile(fp):
            out.add(os.path.normpath(p))
        elif os.path.isdir(fp):
            for d, dirs, files in os.walk(fp):
                dirs[:] = [x for x in dirs if x not in ("bin", "obj", "__pycache__", ".git")]
                out.update(os.path.relpath(os.path.join(d, f), root) for f in files)
    return sorted(out)


def _git_dirty(root):
    """-> the set of `git status` entries under root, or None outside a git work tree (nothing to compare)."""
    r = subprocess.run(["git", "status", "--porcelain", "-z", "--untracked-files=all"], cwd=root, capture_output=True,
                       timeout=120)
    return set(r.stdout.decode("utf-8", "surrogateescape").split("\0")) - {""} if r.returncode == 0 else None


def _snapshot_changes(root, before):
    """-> [(path, its bytes before)] for every snapshotted path whose bytes differ now."""
    now = _snapshot(root, list(before))
    return [(p, old) for p, old in before.items() if now[p] != old]


def red_seen(root, mod, test_id, patch=None, runner=subprocess.run, now=None):
    """Prove a deciding test can fail: apply the planted fault (git apply, in root), run the test's command, want a
    non-zero exit, reverse the fault and prove every file it touched is byte-identical to before. Only a red run is
    recorded (version/evidence/red_seen.json[test]: rc, last line, the test file's blob, the patch, when); a test that
    stays green under the fault is the test that could not fail, and nothing is recorded. -> {"ok", "why"}."""
    tt, err = read_table(root, mod)
    if tt is None:
        return {"ok": False, "why": "did not run: the table cannot be read: %s" % err}
    t = tt["tests"].get(test_id)
    if not isinstance(t, dict) or not t.get("command"):
        return {"ok": False, "why": "did not run: %s is not a test with a command in the table" % test_id}
    if not patch or not os.path.isfile(patch):
        return {"ok": False, "why": "did not run: a red proof needs a planted fault (--patch FILE); %r is no file" % patch}
    with open(patch, encoding="utf-8", errors="replace") as fh:
        patch_text = fh.read()
    paths, perr = _patch_paths(root, os.path.abspath(patch))
    if paths is None:
        return {"ok": False, "why": "did not run: %s" % perr}
    own = os.path.normpath(str(t.get("file") or "")) if t.get("file") else ""
    if own and any(os.path.normpath(p) == own or p.startswith(own + os.sep) for p in paths):
        return {"ok": False, "why": "did not run: the fault edits %s itself; a red proof plants a fault in what the test "
                "reads, never in the test" % own}
    # RIMMANDRAKE_REFUSE_LIVE_RED_SEEN_ON_A_FAULT_THE_GAME_NEVER_LOADS: an in-game check drives the DEPLOYED build; a fault
    # in what the game loads from a build or a deploy (C#, a csproj, Defs or Patches XML) planted in this tree never reaches
    # it, so a red there is the check's own chance and proves nothing (FlowWorks visit 6: sc_hung_bridge reads FAIL about
    # one run in two on the real build)
    unloaded = [p for p in paths if os.path.splitext(p)[1].lower() in GAME_LOADED_EXT]
    if str(t.get("kind") or "").startswith("live") and unloaded:
        return {"ok": False, "why": "did not run: %s is an in-game check and the fault edits %s, which the game loads only "
                "from a build and a deploy, never from this tree; plant the fault in code the check runs from the tree, or "
                "build and deploy the faulted mod first and prove the red by hand; nothing recorded"
                % (test_id, ", ".join(unloaded[:4]))}
    # a scene library check (`scene.py accept`) refuses a tree that differs from its commit (REFUSED TREE_NOT_CLEAN, exit 3),
    # so any fault planted here reads non-zero without the scene running, and accept exits 0 on a scene that prints FAIL:
    # neither exit says anything about the fault (ExplosiveKnockback visit 3, 2026-11-26)
    if re.search(r"scene\.py['\"]?\s+accept\b", str(t.get("command") or "")):
        return {"ok": False, "why": "did not run: %s runs `scene.py accept`, which refuses a tree a planted fault has changed "
                "(TREE_NOT_CLEAN, exit 3) and exits 0 on a scene that prints FAIL; prove the scene red with its own "
                "`accept --plant <name>` and write the planted reading on the visit row's repair field; nothing recorded"
                % test_id}
    reds = _read_evidence(root, mod, RED_SEEN)
    if reds is None:
        return {"ok": False, "why": "did not run: %s is there but cannot be read; nothing is overwritten" % RED_SEEN}
    watched = _watch_paths(root, t, paths)
    before = _snapshot(root, watched)
    dirty0 = _git_dirty(root)
    a = subprocess.run(["git", "apply", os.path.abspath(patch)], cwd=root, capture_output=True, text=True, timeout=60)
    if a.returncode != 0:
        return {"ok": False, "why": "did not run: the fault does not apply: %s" % a.stderr.strip()}
    try:
        try:
            r = runner(t["command"], shell=True, cwd=root, capture_output=True, text=True, timeout=RUN_TIMEOUT_S,
                       env=_run_env())
            rc, last = r.returncode, _last_line(r.stdout, r.stderr)
        except subprocess.TimeoutExpired:
            rc, last = None, "timed out after %d s" % RUN_TIMEOUT_S
        except OSError as e:
            rc, last = None, "could not start: %s" % e
    finally:
        rev = subprocess.run(["git", "apply", "-R", os.path.abspath(patch)], cwd=root, capture_output=True, text=True,
                             timeout=60)
        bad = []
        for p, old in _snapshot_changes(root, before):  # not restored (the reverse, or the test's own writes): by hand
            fp = os.path.join(root, p)
            if old is None:
                os.remove(fp)
            else:
                with open(fp, "wb") as fh:
                    fh.write(old)
            bad.append(p)
    dirty1 = _git_dirty(root) if dirty0 is not None else None
    new = sorted(dirty1 - dirty0) if dirty1 is not None else []
    if new:     # the run changed the tree outside what was watched: no bytes to restore it from, so name it
        return {"ok": False, "why": "the run left the work tree changed outside the files it reads: %s; nothing recorded"
                % ", ".join(x[3:] for x in new[:6])}
    if bad:
        return {"ok": False, "why": "after the run and the fault's reverse (rc %s) %s still differed from before (the "
                "reverse failed or the test wrote them); restored from the bytes read before; nothing recorded"
                % (rev.returncode, ", ".join(bad))}
    if _no_verdict(rc):
        return {"ok": False, "why": "did not run to a verdict under the fault (rc %s: %s); nothing recorded" % (rc, last)}
    if rc == 0:
        return {"ok": False, "why": "%s stayed green under the fault (rc 0: %s): a test that could not fail; nothing "
                "recorded" % (test_id, last or "no output")}
    # the same command with no fault: one that ends at once the same way (an import error, a shell syntax error) never
    # reached its test, so its red proves nothing about the fault (RIMMANDRAKE_REPAIR_PYRE_TABLE_LIVE_COMMANDS_THAT_NEVER_
    # START: all 46 Pyrelands live commands died at start, 2026-11-20). Still running at START_PROBE_S: it started.
    try:
        r0 = runner(t["command"], shell=True, cwd=root, capture_output=True, text=True, timeout=START_PROBE_S,
                    env=_run_env())
        same = r0.returncode == rc and _last_line(r0.stdout, r0.stderr) == last
    except (subprocess.TimeoutExpired, OSError):
        same = False
    if same:
        return {"ok": False, "why": "%s fails the same way without the fault (rc %s: %s): the command never reached its "
                "test, so the red proves nothing; repair the table's command; nothing recorded" % (test_id, rc, last)}
    at = now if now is not None else datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    reds[test_id] = {"rc": rc, "last": last, "at": at, "file": t.get("file"), "test_blob": test_blob(root, t),
                     "command": t["command"], "patch_files": paths, "patch": patch_text,
                     "patch_sha": hashlib.sha256(patch_text.encode("utf-8", "replace")).hexdigest()[:16]}
    _write_evidence(root, mod, RED_SEEN, reds)
    return {"ok": True, "why": "%s went red under the fault (rc %s: %s); recorded in %s" % (test_id, rc, last, RED_SEEN)}


def certify(root, mod, to="blind_challenge"):
    """-> {"ok", "rows", "did_not_run", "to"}: one row per (bar, offline decider, clause), status PASS / REFUSED / WARN,
    each with observed, would_pass and smallest_fix. ok is False when any row is REFUSED. Reads only; under a second."""
    tt, err = read_table(root, mod)
    out = {"ok": True, "rows": [], "did_not_run": [], "to": to, "mod": mod}
    if tt is None:
        out["did_not_run"].append("the certificate did not run: %s; the mod goes through on this guard" % err)
        return out
    tests, rows = tt["tests"], out["rows"]
    run_fix = "python3 src/RimMandrake/rimflow/maturation.py certificate %s --run (reruns only the offline deciders " \
              "that are stale, red or unstamped, and stamps each with its build; no tokens)" % mod
    builds = {}
    reds, gf = _read_evidence(root, mod, RED_SEEN), _read_evidence(root, mod, GRANDFATHER)
    blind = [n for n, v in ((RED_SEEN, reds), (GRANDFATHER, gf)) if v is None]
    if blind:       # could not look: red_seen only warns until the evidence reads again
        out["did_not_run"].append("red_seen did not run: %s cannot be read" % " and ".join(blind))
    ended = _ended_items(root, {t.get("known_red") for t in tests.values() if isinstance(t, dict)
                                and isinstance(t.get("known_red"), str)})

    def row(bar, test, clause, status, observed, would_pass, fix):
        rows.append({"bar": bar, "test": test, "clause": clause, "status": status, "observed": observed,
                     "would_pass": would_pass, "smallest_fix": fix})

    for b in tt["bars"]:
        if not isinstance(b, dict) or not b.get("id"):
            continue
        ds = b.get("offline_decides")
        if str(b.get("proves_at")) in OFFLINE_STAGES and not (isinstance(ds, list) and ds):
            # an offline bar no test decides would certify on no run at all (RIMMANDRAKE_BIND_CERTIFICATE_TO_OFFLINE_DECIDERS_NO_OP_PASSED)
            row(b["id"], None, "decided", "REFUSED", "bar %s proves at stage %s and names no offline decider (offline_decides %s)"
                % (b["id"], b.get("proves_at"), json.dumps(ds)), "bar %s's offline_decides names at least one offline test" % b["id"],
                "name the bar's offline deciders in offline_decides (and decides), or build the check")
        for d in ds if isinstance(ds, list) else []:
            bid, t = b["id"], tests.get(d)
            if d not in (b.get("decides") or []):
                row(bid, d, "decided", "REFUSED", "bar %s names %s in offline_decides but not in decides, and the table passes a "
                    "bar on decides" % (bid, d), "every offline decider of bar %s is also in its decides" % bid,
                    "add %s to bar %s's decides (or drop it from offline_decides)" % (d, bid))
            if not isinstance(t, dict):
                row(bid, d, "registered", "REFUSED", "bar %s names offline decider %s; the test table holds no such "
                    "test" % (bid, d), "a tests.%s entry with a file that exists and a command" % d,
                    "build the check and register it in the test table, or remake the table so the bar names the "
                    "checks it has")
                continue
            f, cmd = t.get("file"), t.get("command")
            fok = bool(f) and os.path.exists(os.path.join(root, f))      # a record test names a folder
            row(bid, d, "registered", "PASS" if fok and cmd else "REFUSED",
                "file %s %s; command %s" % (f or "(none)", "exists" if fok else "is not there", "written" if cmd
                                            else "missing"),
                "tests.%s with a file that exists and a command" % d,
                "point tests.%s.file at the test's real path and write its command (or build the check)" % d)
            r = t.get("runs_today") if isinstance(t.get("runs_today"), dict) else {}
            if d not in builds:
                builds[d] = test_build(root, t)
            now = builds[d]
            if not r.get("ran"):
                obs = "no recorded run (runs_today %s)" % json.dumps(t.get("runs_today"))[:80]
            elif not r.get("build"):
                obs = "the recorded run (%s) carries no build: a stored flag is not a run on this build" % (
                    r.get("at") or "no time")
            elif r["build"] != now:
                obs = "the recorded run (%s) was on build %s; the test and what it reads hash to %s now" % (
                    r.get("at") or "no time", r["build"], now)
            elif r.get("command") is not None and r["command"] != cmd:
                # the build hashes files, not the command: a command swapped after a green run kept the stamp
                # (RIMMANDRAKE_BIND_CERTIFICATE_TO_OFFLINE_DECIDERS_NO_OP_PASSED; a stamp from before run_offline recorded
                # its command carries none and is read as before until its next --run)
                obs = "the recorded run (%s) ran `%s`; the table's command is now `%s`" % (
                    r.get("at") or "no time", str(r["command"])[:80], str(cmd)[:80])
            else:
                obs = None
            row(bid, d, "ran_on_this_build", "PASS" if obs is None else "REFUSED",
                obs or "ran on build %s at %s" % (now, r.get("at")),
                "runs_today.build == %s (the content of %s's reads and file now)" % (now, d), run_fix)
            kr = t.get("known_red")
            if kr and kr in ended:
                # a mark whose item has closed: the test's own run says whether clearing it is the whole fix
                fresh = r.get("ran") and r.get("build") == now and r.get("rc") == 0
                obs = "tests.%s carries known_red %s, and that item is closed on the ledger; %s" % (
                    d, json.dumps(kr), "the test ran green on this build (%s)" % r.get("last") if fresh else
                    "its run on this build is not green (%s)" % (r.get("last") or "no run"))
                fix = ("the mark is stale: delete tests.%s.known_red" % d) if fresh else (
                    "delete the stale tests.%s.known_red, then fix the mod or the test and rerun (%s)" % (d, run_fix))
            elif kr:
                obs = "tests.%s carries known_red %s" % (d, json.dumps(kr))
                fix = "work and close %s, then clear known_red and rerun (%s)" % (
                    kr if isinstance(kr, str) else json.dumps(kr), run_fix)
            elif not r.get("ran"):
                obs, fix = "no recorded run, so no rc", run_fix
            elif r.get("rc") == 0 and r.get("result", "PASS") == "PASS":
                obs = None
            else:
                obs = "rc %s, result %s; last line: %s" % (r.get("rc"), r.get("result"), r.get("last") or "(none)")
                fix = "fix the mod or the test so `%s` exits 0, then rerun (%s)" % (cmd, run_fix)
            row(bid, d, "green", "PASS" if obs is None else "REFUSED",
                obs or "rc 0, PASS: %s" % (r.get("last") or ""), "rc 0, result PASS, no known_red",
                None if obs is None else fix)
            blob = test_blob(root, t)
            seen = (reds or {}).get(d) if isinstance((reds or {}).get(d), dict) else {}
            if blind:
                row(bid, d, "red_seen", "WARN", "did not run: %s cannot be read" % " and ".join(blind),
                    "a readable %s" % " and ".join(blind), "repair or restore %s from git" % " and ".join(blind))
            elif seen.get("rc") not in (0, None) and seen.get("test_blob") == blob \
                    and seen.get("command") == t.get("command"):
                row(bid, d, "red_seen", "PASS", "seen red (rc %s) under a planted fault at %s, against %s as it is now"
                    % (seen.get("rc"), seen.get("at") or "no time", f), "a recorded red run of %s's file as it is now" % d,
                    None)
            elif (gf or {}).get(d) is not None and gf.get(d) == blob:
                row(bid, d, "red_seen", "WARN", "grandfathered: %s is unchanged since %s was written (no red proof "
                    "owed for a test that existed then)" % (f, GRANDFATHER),
                    "a recorded red run of %s's file as it is now" % d, None)
            else:
                why = ("its red proof (%s) was of another version of %s" % (seen.get("at") or "no time", f)
                       if seen and seen.get("test_blob") != blob else
                       "its red proof (%s) ran `%s`; the table's command is now `%s`" % (
                           seen.get("at") or "no time", str(seen.get("command"))[:60], str(t.get("command"))[:60])
                       if seen else "no recorded red run") + (
                    "; it was grandfathered, then edited" if d in gf else "")
                row(bid, d, "red_seen", "REFUSED", "%s: a deciding test nobody has seen fail (%s)" % (d, why),
                    "a planted fault recorded turning %s red against its file as it is now" % d,
                    "plant a fault the test must catch and prove it: python3 src/RimMandrake/rimflow/maturation.py "
                    "red-seen %s %s --patch <fault.patch> (applied, run, reversed; recorded only when the test goes red)"
                    % (mod, d))
                # when its newest red proof was made: cert_red_decide reads whether the last try paid its debt
                rows[-1]["proof_at"] = seen.get("at") if seen.get("rc") not in (0, None) else None
    if to == "in_game":
        try:
            _asks_on_empty_game(root, tt, row, out["did_not_run"])
        except Exception as e:  # noqa: BLE001  this clause could not look: it says so and refuses nothing
            out["did_not_run"].append("asks_on_empty_game did not run: %s: %s" % (type(e).__name__, str(e)))
    out["ok"] = not any(x["status"] == "REFUSED" for x in rows)
    return out


def _asks_on_empty_game(root, tt, row, did_not_run):
    """The asks_on_empty_game clause: a REFUSED row per (bar, in-game decider) whose scene passes a row on an empty game;
    a did_not_run line for the scenes no adapter can run, or when the scene file cannot be loaded."""
    import sys
    utils = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Utils")
    if utils not in sys.path:
        sys.path.insert(0, utils)
    import scene_empty_game as SE
    tests, fw, other, suites = tt["tests"], {}, {}, {}
    if not isinstance(tests, dict) or not isinstance(tt.get("bars"), list):
        did_not_run.append("asks_on_empty_game did not run: the table has no tests map or bars list")
        return
    for b in tt["bars"]:
        for d in (b.get("decides") or []) if isinstance(b, dict) and b.get("id") else []:
            t = tests.get(d)
            if not isinstance(t, dict) or not str(t.get("kind") or "").startswith("live"):
                continue
            if t.get("file") == SE.FLOWWORKS_SCENES and t.get("entry"):
                fw.setdefault(t["entry"], []).append((b["id"], d))
            elif t.get("file") and t.get("entry"):     # maybe a modcheck Suite chain: the Suite adapter decides
                suites.setdefault(str(t["file"]), {}).setdefault(str(t["entry"]), []).append((b["id"], d))
            else:
                other.setdefault(str(t.get("file")), set()).add(d)
    if fw:
        # its own process, bounded: a scene that loops on an empty answer cannot hang the certificate, and the scene
        # module's imports stay out of this one
        try:
            r = subprocess.run([sys.executable, SE.__file__, "--root", root, "--json"], capture_output=True, text=True,
                               timeout=EMPTY_GAME_TIMEOUT_S)
            got = json.loads(r.stdout.strip().splitlines()[-1]) if r.stdout.strip() else {}
        except (subprocess.TimeoutExpired, OSError, ValueError) as e:
            got = {"did_not_run": "%s: %s" % (type(e).__name__, str(e))}
        pairs, why = (got["vacuous"], None) if isinstance(got.get("vacuous"), list) else (
            None, got.get("did_not_run") or "scene_empty_game.py printed no verdict (rc %s): %s" % (
                r.returncode, (r.stderr or "").strip()))
        ran = set(got.get("scenes") or []) if pairs is not None else set()
        unseen = sorted(e for e in fw if e not in ran)
        if pairs is not None and unseen:    # never run, so its absence from the vacuous list establishes nothing
            did_not_run.append("asks_on_empty_game did not run on %d in-game scene(s) %s: not in %s's STAGE3_SCENES"
                               % (len(unseen), ", ".join(unseen[:6]), SE.FLOWWORKS_SCENES))
        if pairs is None:
            did_not_run.append("asks_on_empty_game did not run on %d in-game scene(s): %s" % (len(fw), why))
        else:
            vac = {}
            for scene, rid in pairs:
                vac.setdefault(scene, []).append(str(rid))
            for entry, users in sorted(fw.items()):
                if entry not in vac:
                    continue
                for bid, d in users:
                    row(bid, d, "asks_on_empty_game", "REFUSED",
                        "on an empty game (every bridge call a bare success, nothing on the map) %s's row(s) %s read PASS"
                        % (entry, ", ".join(vac[entry])),
                        "every row of %s reads FAIL, UNMEASURED or ERROR when nothing is on the map" % entry,
                        "make each listed row read UNMEASURED when the event it judges was never seen (nothing spawned, "
                        "no draw, a vacuous read), then check: python3 src/RimMandrake/Utils/scene_empty_game.py")
    for path, entries in sorted(suites.items()):
        # RIMMANDRAKE_ADAPT_SUITE_SCENES_TO_EMPTY_GAME_FLOWWORKS_ONLY: a modcheck Suite file, its named chains run on an
        # empty game in their own bounded process (scene_empty_game.suite_vacuous); a file with no suite falls back to
        # "no empty-game adapter"
        try:
            r = subprocess.run([sys.executable, SE.__file__, "--root", root, "--suite", path, "--chains",
                                ",".join(sorted(entries)), "--json"], capture_output=True, text=True,
                               timeout=EMPTY_GAME_TIMEOUT_S)
            got = json.loads(r.stdout.strip().splitlines()[-1]) if r.stdout.strip() else {
                "did_not_run": "scene_empty_game.py --suite printed no verdict (rc %s): %s"
                               % (r.returncode, (r.stderr or "").strip())}
        except (subprocess.TimeoutExpired, OSError, ValueError) as e:
            got = {"did_not_run": "%s: %s" % (type(e).__name__, str(e))}
        if not isinstance(got.get("vacuous"), list):
            why = str(got.get("did_not_run") or "no verdict")
            if "has no module-level modcheck suite" in why:
                other.setdefault(path, set()).update(d for users in entries.values() for _b, d in users)
            else:
                did_not_run.append("asks_on_empty_game did not run on %d in-game test(s) in %s: %s"
                                   % (sum(len(u) for u in entries.values()), path, why))
            continue
        if got.get("refused"):
            did_not_run.append("asks_on_empty_game: the sandbox refused %d act(s) of %s's chains on an empty game (a "
                               "chain that needed one may list too little): %s" % (len(got["refused"]), path,
                                                                                    "; ".join(got["refused"][:3])))
        missing = [e for e in sorted(entries) if e in (got.get("missing") or [])]
        if missing:     # never run, so absence from the vacuous list establishes nothing
            did_not_run.append("asks_on_empty_game did not run on %d in-game scene(s) %s: not a live chain of %s's suite"
                               % (len(missing), ", ".join(missing[:6]), path))
        vac = {}
        for chain, comp in got["vacuous"]:
            vac.setdefault(str(chain), []).append(str(comp))
        for entry, users in sorted(entries.items()):
            if entry not in vac:
                continue
            for bid, d in users:
                row(bid, d, "asks_on_empty_game", "REFUSED",
                    "on an empty game (every bridge call a bare success, nothing on the map) %s's chain %s reads PASS "
                    "on row(s) %s" % (path, entry, ", ".join(vac[entry])),
                    "every row of chain %s reads FAIL, UNMEASURED or ERROR when nothing is on the map" % entry,
                    "make each listed row read UNMEASURED when the event it judges was never seen (nothing spawned, "
                    "no draw, a vacuous read), then check: python3 src/RimMandrake/Utils/scene_empty_game.py --suite %s "
                    "--chains %s" % (path, entry))
    if other:
        did_not_run.append("asks_on_empty_game did not run on %d in-game test(s) in %s: no empty-game adapter for that "
                           "harness (FlowWorks' concept_scenes.py STAGE3_SCENES and a file with a module-level modcheck "
                           "suite have one; a test naming no entry chain has none)" % (sum(len(v) for v in other.values()),
                                                  ", ".join(sorted(other)[:4]) + (" ..." if len(other) > 4 else "")))


def summary(v):
    """-> one line: the certificate's reading."""
    if v.get("did_not_run") and not v.get("rows"):
        return v["did_not_run"][0]
    ref = [r for r in v.get("rows") or [] if r["status"] == "REFUSED"]
    bars = sorted({r["bar"] for r in v.get("rows") or []})
    dnr = "".join("; DID NOT RUN: %s" % d for d in v.get("did_not_run") or [])   # a clause that could not look
    if not ref:
        gfn = len({r["test"] for r in v.get("rows") or [] if r["clause"] == "red_seen" and r["status"] == "WARN"})
        return "certified: %d bars' offline deciders registered, run on this build, green and seen red%s%s" % (
            len(bars), " (%d grandfathered)" % gfn if gfn else "", dnr)
    rb = sorted({r["bar"] for r in ref})
    by = {}
    for r in ref:
        by.setdefault(r["clause"], set()).add(str(r["test"] if r["test"] is not None else "(bar %s)" % r["bar"]))
    return "refused: %d of %d bars (%s); %s%s" % (len(rb), len(bars), ", ".join(rb[:6]) + (" ..." if len(rb) > 6 else ""),
                                                  "; ".join("%s %s" % (c, ", ".join(sorted(t)[:5])) for c, t in
                                                            sorted(by.items())), dnr)


def first_fix(v):
    """-> the smallest fix of the certificate's first refusal (a stale build first: one command passes it), and when
    deciders are also recorded red, those named after it: a rerun alone does not pass a red test (FlowWorks,
    2026-11-16: three red records, one still red when rerun)."""
    ref = [r for r in v.get("rows") or [] if r["status"] == "REFUSED"]
    ref.sort(key=lambda r: {"ran_on_this_build": 0, "registered": 1, "green": 2}.get(r["clause"], 3))
    if not ref:
        return None
    red = sorted({r["test"] for r in ref if r["clause"] == "green"})
    if ref[0]["clause"] == "green" or not red:
        return ref[0]["smallest_fix"]
    return "%s; then the deciders recorded red (%s): fix the mod or the test, or work the item that owes it" % (
        ref[0]["smallest_fix"], ", ".join(red[:6]) + (" ..." if len(red) > 6 else ""))


def print_certificate(v, out=print):
    out("CERTIFICATE %s (to %s): %s" % (v.get("mod"), v.get("to"), "OK" if v.get("ok") else "REFUSED"))
    for d in v.get("did_not_run") or []:
        out("  DID NOT RUN: %s" % d)
    seen = set()
    for r in v.get("rows") or []:
        if r["status"] != "REFUSED":
            continue
        out("  REFUSED %s / %s / %s" % (r["bar"], r["test"], r["clause"]))
        out("    observed:     %s" % r["observed"])
        out("    would_pass:   %s" % r["would_pass"])
        out("    smallest_fix: %s" % r["smallest_fix"])
        seen.add(r["bar"])
    warn = [r for r in v.get("rows") or [] if r["status"] == "WARN"]
    if warn:
        out("  WARN red_seen grandfathered on %d decider rows (unchanged since %s)" % (len(warn), GRANDFATHER))
    out("  %s" % summary(v))
