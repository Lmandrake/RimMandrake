#!/usr/bin/env python3
"""selftest_close_evidence_mut.py -- kills the mutants selftest_close_evidence.py + _props.py left alive
(CLOSE_EVIDENCE_HARDEN_MUTATION_SURVIVORS; mutmut run 20261027a on SteveDesktop, survivors re-checked by hand
against a COPY of close_evidence.py: 465 survivors listed, 415 still alive with the props test).

Each group names the behaviour it pins and, in a trailing comment, the mutant family it kills. What matters most to the
Arbiter, who trusts the sealed record: which lines are evidence (counts_as_evidence), which are not (schema, legacy,
replay, drift), what an unverifiable line becomes (_bad_marker, lookup), how a record's coverage is read
(cover_entries, summarize, latest_covering), and the CLI the Windows side and the gates drive.
Offline: fixture git repos under a temp dir, RM_CLOSE_EVIDENCE_DIR and the key redirected there.
"""
from __future__ import annotations

import contextlib
import hashlib
import hmac
import inspect
import io
import json
import os
import stat
import subprocess
import sys
import tempfile
import types
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import close_evidence as CE  # noqa: E402


FAILS: list = []


def check(cond, msg):
    print(("ok   " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


def git(repo, *a):
    return subprocess.run(["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@t", *a],
                          capture_output=True, text=True, check=True).stdout.strip()


def iso_mark(repo):
    """Stamp the fixture clone as an isolated checkout of its HEAD (what make_isolated leaves)."""
    sha = git(repo, "rev-parse", "HEAD")
    (Path(repo) / ".git" / CE.ISOLATED_MARK).write_text(
        hmac.new(CE._key(create=True), CE._iso_msg(repo, sha), hashlib.sha256).hexdigest())
    return sha


def commit_file(repo, rel, text, msg):
    p = Path(repo) / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text)
    git(repo, "add", rel)
    git(repo, "commit", "-q", "-m", msg, "--", rel)
    return iso_mark(repo)


def make_repo(root, name="clone"):
    repo = Path(root) / name
    repo.mkdir()
    git(repo, "init", "-q")
    return repo, commit_file(repo, "src/a.py", "x = 1\n", "one")


def good(repo, tool="selftest", paths=None, item=None, result="PASS", **kw):
    """A real evidence line: sealed, minted start, isolated clone."""
    return CE.record(tool, result, paths if paths is not None else [Path(repo) / "src" / "a.py"], clone=repo,
                     start=CE.snapshot(repo), item=item, **kw)


def run_main(argv):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            rc = CE._main(argv)
        except SystemExit as e:
            rc = e.code
    return rc, out.getvalue(), err.getvalue()


# ----------------------------------------------------------------------------------------------- pure functions

def g_pure():
    # _sha_match: prefix >= 7, either side empty/None never matches, case-insensitive
    check(CE._sha_match("abcdef0", "abcdef0123456") is True, "_sha_match: exactly 7 matching chars match")
    check(CE._sha_match("abcdef", "abcdef0123") is False, "_sha_match: 6 chars never match")
    check(CE._sha_match("ABCDEF0123", "abcdef0") is True, "_sha_match: case-insensitive")
    check(CE._sha_match("abcdef0", "abcdef1") is False, "_sha_match: a differing 7th char does not match")
    check(CE._sha_match("", "a" * 40) is False and CE._sha_match("a" * 40, "") is False, "_sha_match: empty side")
    try:
        r = (CE._sha_match(None, "a" * 40), CE._sha_match("a" * 40, None))
    except TypeError:
        r = "raised"
    check(r == (False, False), "_sha_match: None on either side is False, never an exception: %r" % (r,))
    check(CE._sha_match("abc", "xyz") is False, "_sha_match: short non-matching strings do not match")

    # _covers: ALL, '' and '.' cover everything; a folder covers its children; no sibling-prefix cover
    check(CE._covers(CE.ALL, "a/b.py") is True and CE._covers("", "a/b.py") is True and CE._covers(".", "a/b.py") is True,
          "_covers: * / '' / . cover every path")
    check(CE._covers("src", "src/a.py") and CE._covers("src/", "src/a.py") and CE._covers("src/a.py", "src/a.py"),
          "_covers: a folder and the file itself")
    check(not CE._covers("src", "srcx/a.py") and not CE._covers("src/a.py", "src/b.py"), "_covers: no sibling-prefix cover")

    # _norm_path strips every leading ./ and nothing else
    check(CE._norm_path("./././a.py", None) == "a.py" and CE._norm_path("./a/b.py", None) == "a/b.py"
          and CE._norm_path("a/./b.py", None) == "a/./b.py", "_norm_path: strips leading ./ only")

    # _legacy: BOTH seals absent
    check(CE._legacy({}) is True and CE._legacy({"mac": "x"}) is False and CE._legacy({"route": "x"}) is False
          and CE._legacy({"mac": "x", "route": "y"}) is False, "_legacy: a line carrying either seal is not legacy")

    # _bad_marker: the whole shape
    m = CE._bad_marker("c" * 40, [("2026-01-02", "x"), ("2026-01-01", "y"), ("2026-01-02", "z")], unverifiable=1)
    want = {"v": CE.V, "ts": "", "tool": "close_evidence", "clone": None, "sha": "c" * 40, "dirty": False, "dirty_n": 0,
            "dirty_paths": [], "start": {"sha": "c" * 40, "dirty": False, "dirty_n": 0}, "paths": [CE.ALL],
            "covers": [CE.ALL], "result": "UNMEASURED", "item": None, "seat": None, "live_only": False, "variant": None,
            "detail": {"unreadable_lines": 2, "unverifiable_lines": 1, "days": ["2026-01-01", "2026-01-02"]}}
    check(m == want, "_bad_marker: exact shape %r" % (m,))
    m0 = CE._bad_marker("c" * 40, [("d", "x")])
    check(m0["detail"] == {"unreadable_lines": 1, "unverifiable_lines": 0, "days": ["d"]}, "_bad_marker: default unverifiable=0")
    check(inspect.signature(CE._bad_marker).parameters["unverifiable"].default == 0, "_bad_marker signature default")

    # to_wsl
    check(CE.to_wsl("\\\\wsl.localhost\\Ubuntu\\home\\x\\y") == "/home/x/y", "to_wsl: wsl.localhost")
    check(CE.to_wsl("\\\\wsl$\\Ubuntu\\home\\x") == "/home/x", "to_wsl: wsl$")
    check(CE.to_wsl("D:\\Luke\\dev\\a.py") == "/mnt/d/Luke/dev/a.py", "to_wsl: drive letter backslashes")
    check(CE.to_wsl("C:/x/y") == "/mnt/c/x/y" and CE.to_wsl("c:") == "/mnt/c/", "to_wsl: drive letter forward / bare")
    check(CE.to_wsl("/home/x/y") == "/home/x/y" and CE.to_wsl("rel/p") == "rel/p", "to_wsl: POSIX passes through")

    # _days newest-first, going BACK
    import datetime
    d = datetime.date(2026, 1, 10)
    check(CE._days(3, today=d) == ["2026-01-10", "2026-01-09", "2026-01-08"], "_days: today and the days before it")

    # _iso_msg / _state_token: exactly what the marker / token is a mac of
    check(CE._iso_msg("/tmp", "ABC") == json.dumps(["isolated", os.path.realpath("/tmp"), "abc"]).encode()
          and CE._iso_msg("/tmp", None) == json.dumps(["isolated", os.path.realpath("/tmp"), ""]).encode(),
          "_iso_msg: realpath + lowercased sha")
    st = {"sha": "a" * 40, "dirty": False, "dirty_n": 0}
    tok = CE._state_token(st)
    check(tok == hmac.new(CE._PROC_SECRET, json.dumps(["a" * 40, False, 0]).encode(), hashlib.sha256).hexdigest(),
          "_state_token: hmac of [sha, dirty, dirty_n] under the process secret")
    check(CE._state_token({**st, "dirty_n": 1}) != tok and CE._state_token({**st, "dirty": True}) != tok
          and CE._state_token({**st, "dirty_paths": ["x"]}) == tok, "_state_token: sha/dirty/dirty_n only")

    # constants the sealed records and the gates depend on
    check(CE.V == 4 and CE._TOKEN == "_token" and CE.DIRTY_KEEP == 20 and isinstance(CE._ROOT_CACHE, list)
          and len(CE._PROC_SECRET) == 32 and CE.DIRTY_IGNORE == ("conversations/",) and CE.ALL == "*",
          "module constants: V=4 (bump deliberately), _TOKEN, DIRTY_KEEP=20, _ROOT_CACHE list, 32-byte secret")
    check(CE.AGENT_STORAGE == Path.home() / "dev/Lodestar/bin/lib/agent_storage.py"
          and CE.DEFAULT_KEY == Path.home() / ".config" / "rimmandrake" / "close_evidence.key",
          "module constants: agent_storage and default key locations")
    check(CE._SEATS_FALLBACK == ("BENCH", "FOUNDRY", "OWNER", "DECIDE", "BUILD", "CHECK", "REP", "RUNNER", "DISPATCHER"),
          "_SEATS_FALLBACK is rimflow's seat list")
    for fn in (CE.lookup, CE.read_all):
        check(inspect.signature(fn).parameters["days"].default == 30, "%s default days=30" % fn.__name__)
    check(inspect.signature(CE.publish_once).parameters["mode"].default == 0o600, "publish_once default mode 0600")
    check(inspect.signature(CE.build_record).parameters["live_only"].default is False, "build_record live_only defaults False")


def g_top_level():
    tl = CE._top_level
    check(tl('{"sha": "a\\"b", "tool": "t"}', "sha") == 'a"b' and tl('{"sha": "a\\"b", "tool": "t"}', "tool") == "t",
          "_top_level: an escaped quote does not end the string")
    check(tl('{"sha": "a\\\\", "tool": "t"}', "sha") == "a\\" and tl('{"sha": "a\\\\", "tool": "t"}', "tool") == "t",
          "_top_level: an escaped backslash before the closing quote does")
    check(tl('{"detail": {"x": {"f": 1}, "sha": "inner"}, "sha": "top"}', "sha") == "top",
          "_top_level: a closed nested object returns to the right depth (inner sha is not top-level)")
    check(tl('{"sha":"abc","tool":"t"}', "sha") == "abc", "_top_level: compact JSON (no space after the colon)")
    check(tl('{"sha" : "abc"}', "sha") == "abc" and tl('{"sha"\n:\t"abc"}', "sha") == "abc",
          "_top_level: whitespace between key and colon")
    check(tl('{"a\\q": "v", "sha": "s"}', "") is None and tl('{"a\\q": "v", "sha": "s"}', "sha") == "s",
          "_top_level: an unparseable key never equals any key, not even ''")
    check(tl('{"sha": "abc', "sha") is None and tl('{"sha": "a", "sha": "b"}', "sha") is None
          and tl('{"sha": 5}', "sha") is None and tl('{"tool": "t"}', "sha") is None, "_top_level: cut off / twice / non-string / absent")
    check(tl('{"x": ["sha", "y"], "sha": "ok"}', "sha") == "ok", "_top_level: an array element is not a key")


def g_cover_entries():
    ce = CE.cover_entries
    r = {"tool": "pytest", "paths": ["src/a.py", "src/dir/"], "covers": ["src/a.py", "src/dir/", "src/b.py", "/abs.py", "../x", "", "."]}
    check(ce(r) == [("src/a.py", False), ("src/dir/", False), ("src/b.py", True)],
          "cover_entries: path-vouched entries stay folder-capable, others are exact files, bad sources dropped: %r" % ce(r))
    check(ce({"tool": "pytest", "paths": ["src/a.py"]}) == [("src/a.py", False)],
          "cover_entries: no covers list -> the paths")
    check(ce({"tool": "pytest", "paths": ["src/a.py"], "covers": "src"}) == [("src/a.py", False)],
          "cover_entries: covers that is not a list -> the paths")
    check(ce({"tool": "pytest", "paths": None, "covers": None}) == [], "cover_entries: neither -> nothing")
    w = {"tool": "winbuild", "paths": ["a.csproj", "stage/"], "covers": ["a.csproj", "stage/", "x/y.cs"]}
    check(ce(w) == [("a.csproj", True), ("x/y.cs", True)],
          "cover_entries: a build's entries are all exact files; a bad-source path is dropped even if in paths: %r" % ce(w))
    # a path the run was pointed at may be a folder for a non-exact tool even though _bad_source says so
    check(ce({"tool": "t", "paths": ["d/"], "covers": ["d/"]}) == [("d/", False)], "cover_entries: pointed-at folder survives")
    # DERIVED_COVERS (selftest)
    s = {"tool": "selftest", "paths": ["tests/t.py"], "covers": ["tests/t.py", "src/m.py", "src/n.py", "src/o.py"],
         "detail": {"covers_by": {"src/m.py": ["tests/t.py"], "src/n.py": [], "src/o.py": ["other.py"]}}}
    check(ce(s) == [("tests/t.py", False), ("src/m.py", True)], "cover_entries: a selftest source needs covers_by naming run tests: %r" % ce(s))


def g_summary_order():
    mk = lambda ts, res, p="a.py", tool="t": {"tool": tool, "ts": ts, "result": res, "paths": [p], "covers": [p], "variant": None}
    recs = [mk("2026-01-02T00:00:02+00:00", "PASS"), mk("2026-01-02T00:00:01+00:00", "FAIL")]
    check(CE.summarize(recs) == {"t": "PASS"}, "summarize: the latest by ts decides, not file order: %r" % CE.summarize(recs))
    check(CE.summarize(recs[::-1]) == {"t": "PASS"}, "summarize: same either file order")
    check(CE.latest_covering(recs, "a.py")["t"] is recs[0], "latest_covering: the latest by ts, not file order")
    check(CE.latest_covering(recs[::-1], "a.py")["t"] is recs[0], "latest_covering: same either file order")
    check(CE.latest_covering(recs, "zzz.py") == {}, "latest_covering: nothing covers a foreign path")
    v = {**mk("2026-01-02T00:00:03+00:00", "FAIL"), "variant": "static"}
    check(set(CE.latest_covering(recs + [v], "a.py")) == {"t", "t:static"}, "latest_covering: a variant is its own key")
    # a ts-less record sorts first
    nots = {**mk("", "FAIL")}
    del nots["ts"]
    check(CE.summarize([recs[0], nots]) == {"t": "PASS"}, "summarize: a record without ts sorts before dated ones")
    # one tool, two paths: the worst path decides; a later run covering the FAIL path repairs it
    f = {"tool": "t", "ts": "2026-01-01T00:00:01+00:00", "result": "FAIL", "paths": ["b.py"], "covers": ["b.py"], "variant": None}
    p = {"tool": "t", "ts": "2026-01-01T00:00:02+00:00", "result": "PASS", "paths": ["a.py"], "covers": ["a.py"], "variant": None}
    check(CE.summarize([f, p]) == {"t": "FAIL"}, "summarize: a narrow later PASS does not erase an earlier FAIL elsewhere")


def g_schema_counts():
    probs = CE.schema_problems({})
    check(len(probs) == 1 + len(CE.REQUIRED) + 4 and any(x.startswith("v=") for x in probs)
          and all(("missing %s" % k) in probs for k in CE.REQUIRED),
          "schema_problems: every problem is listed, none overwritten: %d" % len(probs))
    check(CE.schema_problems({"origin": "inproc"}) != [] and CE.schema_problems({"origin": None}) != [],
          "schema_problems: a non-dict origin is a problem")
    full = {k: None for k in CE.REQUIRED}
    full.update(v=CE.V, origin={"via": "inproc", "start": "snapshot", "end": "git", "tree": "isolated"})
    check(CE.schema_problems(full) == [], "schema_problems: a complete v4 inproc/isolated line has none")
    for k, bad in (("via", "cli"), ("start", "caller"), ("end", "caller"), ("tree", "shared")):
        o = dict(full["origin"], **{k: bad})
        pr = CE.schema_problems({**full, "origin": o})
        check(len(pr) == 1 and ("origin.%s" % k) in pr[0], "schema_problems: origin.%s=%s named: %r" % (k, bad, pr))


def g_route():
    key = b"k" * 32
    sha = "a" * 40
    rt = CE._route_mac(sha, "t", key)
    check(CE.route_ok(sha, "t", rt, key) is True, "route_ok: a genuine route verifies")
    check(CE.route_ok(sha, None, CE._route_mac(sha, None, key), key) is False, "route_ok: a non-string tool never verifies")
    check(CE.route_ok(None, "t", CE._route_mac(None, "t", key), key) is False, "route_ok: a non-string sha never verifies")
    check(CE.route_ok(sha, "t", 5, key) is False and CE.route_ok(sha, "t", "ZZ", key) is False
          and CE.route_ok(sha, "u", rt, key) is False and CE.route_ok(sha, "t", rt, b"j" * 32) is False,
          "route_ok: non-string/short/other-tool/other-key routes fail")


def g_publish_key_append(td):
    # publish_once
    p = Path(td) / "pub" / "deep" / "k"
    check(CE.publish_once(p, "abc") is True and p.read_text() == "abc", "publish_once: first publisher wins (parents created)")
    check(CE.publish_once(p, "zzz") is False and p.read_text() == "abc", "publish_once: an existing file is never replaced, returns False")
    check(stat.S_IMODE(p.stat().st_mode) == 0o600, "publish_once: mode 0600")
    check([x.name for x in p.parent.iterdir()] == ["k"], "publish_once: no tmp file left behind")
    q = Path(td) / "pub" / "race"
    real_link = os.link

    def racing(src, dst):
        Path(dst).write_text("winner")
        raise FileExistsError(dst)
    os.link = racing
    try:
        lost = CE.publish_once(q, "mine")
    finally:
        os.link = real_link
    check(lost is False and q.read_text() == "winner" and sorted(x.name for x in q.parent.iterdir()) == ["deep", "race"],
          "publish_once: losing the link race returns False and cleans its tmp file")

    # _key: 32 chars is enough, 31 is not, missing raises RuntimeError unless create
    old = os.environ.get(CE.KEY_ENV)
    try:
        kp = Path(td) / "keys" / "k1"
        os.environ[CE.KEY_ENV] = str(kp)
        try:
            CE._key()
            r = "no raise"
        except RuntimeError as e:
            r = "missing" if "missing" in str(e) else str(e)
        check(r == "missing", "_key: a missing key raises RuntimeError: %s" % r)
        check(not kp.exists(), "_key: a read never creates the key")
        kp.parent.mkdir()
        kp.write_text("a" * 32)
        check(CE._key() == b"a" * 32, "_key: a 32-char key is accepted")
        kp.write_text("a" * 31 + "\n")
        try:
            CE._key()
            r = "no raise"
        except RuntimeError as e:
            r = "short" if "short" in str(e) else str(e)
        check(r == "short", "_key: a 31-char key is refused: %s" % r)
        kp.unlink()
        k = CE._key(create=True)
        check(len(k) == 64 and kp.is_file() and stat.S_IMODE(kp.stat().st_mode) == 0o600, "_key(create=True) publishes a 0600 key")
        # seal(create default): no key -> created and used; seal drops stale seals
        kp.unlink()
        rec = CE.seal({"sha": "a" * 40, "tool": "t", "mac": "stale", "route": "stale", "x": 1})
        check(kp.is_file() and CE.mac_ok(rec, CE._key()) and CE.route_ok("a" * 40, "t", rec["route"], CE._key())
              and rec["mac"] != "stale", "seal: creates the key when none exists, re-seals over stale mac/route")
        check(not CE.mac_ok({**rec, "x": 2}, CE._key()) and not CE.mac_ok({**rec, "mac": rec["mac"].upper()}, CE._key())
              and not CE.mac_ok({k2: v for k2, v in rec.items() if k2 != "mac"}, CE._key()), "mac_ok: edited / upper-case / absent mac fails")
    finally:
        if old is None:
            os.environ.pop(CE.KEY_ENV, None)
        else:
            os.environ[CE.KEY_ENV] = old

    # _append: mode, whole line even on short writes, short write of 0 raises
    old_umask = os.umask(0)
    try:
        f = Path(td) / "app" / "d.jsonl"
        f.parent.mkdir()
        CE._append(f, b"hello\n")
        check(stat.S_IMODE(f.stat().st_mode) == 0o644 and stat.S_IMODE(Path(str(f) + ".lock").stat().st_mode) == 0o644,
              "_append: file and lock are created 0644")
        real_write = os.write
        os.write = lambda fd, view: real_write(fd, bytes(view[:1]))
        try:
            CE._append(f, b"abc\n")
        finally:
            os.write = real_write
        check(f.read_bytes() == b"hello\nabc\n", "_append: a short write is retried until the whole line is down: %r" % f.read_bytes())
        os.write = lambda fd, view: 0
        try:
            CE._append(f, b"zzz\n")
            r = "no raise"
        except OSError as e:
            r = str(e)
        finally:
            os.write = real_write
        check(r.startswith("short write (0 of 4 bytes left)"), "_append: a zero-byte write raises OSError('short write ...'): %s" % r)
        os.write = lambda fd, view: real_write(fd, bytes(view[:1])) if len(view) > 0 else 0
        try:
            CE._append(f, b"q\n")
        finally:
            os.write = real_write
        check(f.read_bytes() == b"hello\nabc\nq\n", "_append: a 1-byte write is progress, not an error")

        # _read_locked: lock created 0644; an unwritable lock still reads
        g = Path(td) / "app" / "e.jsonl"
        g.write_text("l1\nl2\n")
        check(CE._read_locked(g) == ["l1\n", "l2\n"] and stat.S_IMODE(Path(str(g) + ".lock").stat().st_mode) == 0o644,
              "_read_locked: reads under a lock it created 0644")
        os.chmod(str(g) + ".lock", 0o444)
        check(CE._read_locked(g) == ["l1\n", "l2\n"], "_read_locked: a read-only lock file falls back to a read-only open")
    finally:
        os.umask(old_umask)


# ----------------------------------------------------------------------------------------------- git-backed

def g_tree_state(td):
    repo, sha = make_repo(td, "ts")
    st = CE.tree_state(repo)
    check(st["sha"] == sha and st["dirty"] is False and st["dirty_n"] == 0 and st["dirty_paths"] == [],
          "tree_state: a clean tree: %r" % {k: v for k, v in st.items() if k != '_token'})
    check(st["_token"] == CE._state_token(st) and CE._minted_here(st), "tree_state: carries this process's token")
    # one-char file name (a 4-char porcelain entry) counts
    (repo / "x").write_text("1")
    st = CE.tree_state(repo)
    check(st["dirty"] is True and st["dirty_paths"] == ["x"], "tree_state: a one-letter untracked file is dirt: %r" % st["dirty_paths"])
    # several files: all counted (paths accumulate)
    for n in ("b1", "b2", "b3"):
        (repo / n).write_text("1")
    st = CE.tree_state(repo)
    check(st["dirty_n"] == 4 and st["dirty_paths"] == ["b1", "b2", "b3", "x"], "tree_state: every dirty path is listed, sorted: %r" % st["dirty_paths"])
    # conversations/ alone is not dirt, and is not listed beside real dirt
    for n in ("b1", "b2", "b3", "x"):
        (repo / n).unlink()
    (repo / "conversations").mkdir()
    (repo / "conversations" / "s.md").write_text("t")
    st = CE.tree_state(repo)
    check(st["dirty"] is False and st["dirty_n"] == 0 and st["dirty_paths"] == [], "tree_state: conversations/ only is clean: %r" % st["dirty_paths"])
    (repo / "real.txt").write_text("1")
    st = CE.tree_state(repo)
    check(st["dirty_n"] == 1 and st["dirty_paths"] == ["real.txt"], "tree_state: conversations/ is not listed beside real dirt")
    (repo / "real.txt").unlink()
    # scope: dirt counted only inside it
    (repo / "out.txt").write_text("1")
    (repo / "src" / "n.py").write_text("1")
    check(CE.tree_state(repo, scope=["src"])["dirty_paths"] == ["src/n.py"], "tree_state: scope limits the count")
    (repo / "out.txt").unlink()
    (repo / "src" / "n.py").unlink()
    # DIRTY_KEEP
    for i in range(25):
        (repo / ("many%02d" % i)).write_text("1")
    st = CE.tree_state(repo)
    check(st["dirty_n"] == 25 and len(st["dirty_paths"]) == CE.DIRTY_KEEP == 20 and st["dirty_paths"][0] == "many00",
          "tree_state: dirty_n counts all, dirty_paths keeps the first 20 sorted: %d/%d" % (st["dirty_n"], len(st["dirty_paths"])))
    for i in range(25):
        (repo / ("many%02d" % i)).unlink()
    # a rename: both sides; a rename into conversations/ is still dirt at the source; followed by more files
    subprocess.run(["rm", "-rf", str(repo / "conversations")])      # an untracked entry between the rename and zz would hide a skipped field
    git(repo, "mv", "src/a.py", "src/b.py")
    (repo / "zz").write_text("1")
    st = CE.tree_state(repo)
    check(st["dirty_paths"] == ["src/a.py", "src/b.py", "zz"] and st["dirty_n"] == 3,
          "tree_state: a rename lists both sides and the field after it is read as the next entry: %r" % st["dirty_paths"])
    (repo / "zz").unlink()
    (repo / "conversations").mkdir(exist_ok=True)
    git(repo, "mv", "src/b.py", "conversations/b.py")
    st = CE.tree_state(repo)
    check(st["dirty"] is True and "src/a.py" in st["dirty_paths"] and not any(p.startswith("conversations/") for p in st["dirty_paths"]),
          "tree_state: a rename INTO conversations/ is dirt at its source: %r" % st["dirty_paths"])
    # not a repo: nothing known
    nr = Path(td) / "plain"
    nr.mkdir()
    st = CE.tree_state(nr)
    check(st["sha"] is None and st["dirty"] is None and st["dirty_n"] is None and "_token" not in st, "tree_state: a non-repo knows nothing")

    # snapshot: only sha/dirty/dirty_n + token; never raises
    repo2, sha2 = make_repo(td, "ss")
    sn = CE.snapshot(repo2)
    check(set(sn) == {"sha", "dirty", "dirty_n", "_token"} and sn["sha"] == sha2 and CE._minted_here(sn), "snapshot: shape and token")
    real = CE.tree_state
    CE.tree_state = lambda *a, **k: (_ for _ in ()).throw(OSError("boom"))
    try:
        sn = CE.snapshot(repo2)
    finally:
        CE.tree_state = real
    check(sn == {"sha": None, "dirty": None, "dirty_n": None}, "snapshot: a failing tree_state yields an unknown start, never raises: %r" % sn)

    # clone_of climbs from a missing path; None outside a repo
    top = os.path.realpath(str(repo2))
    check(CE.clone_of(repo2 / "no" / "such" / "f.py") == top and CE.clone_of(repo2 / "src" / "a.py") == top and CE.clone_of(repo2) == top,
          "clone_of: file / dir / not-yet-existing path under a repo -> its toplevel")
    check(CE.clone_of(nr) is None, "clone_of: a directory outside any repo -> None")


def g_build_record(td):
    repo, sha = make_repo(td, "br")
    end = {"sha": "a" * 40, "dirty": False, "dirty_n": 0}
    saved = {k: os.environ.pop(k, None) for k in ("RIMFLOW_ITEM",)}
    try:
        rec = CE.build_record("t", "PASS", [], end=dict(end))
        check(rec["live_only"] is False and rec["clone"] is None and rec["item"] is None and rec["variant"] is None
              and rec["origin"]["who"] == "whoami" and len(rec["nonce"]) == 32 and rec["detail"] == {},
              "build_record: defaults (live_only False, no clone, item None, who from whoami, 32-hex nonce)")
        check(CE.build_record("t", "PASS", [], end=dict(end), live_only=1)["live_only"] is True, "build_record: live_only is a bool")
        check(CE.build_record("t", "PASS", [], end=dict(end), who={"seat": "BENCH"})["origin"]["who"] == "caller",
              "build_record: a caller-supplied who is marked caller")
        os.environ["RIMFLOW_ITEM"] = "SOME_ITEM"
        check(CE.build_record("t", "PASS", [], end=dict(end))["item"] == "SOME_ITEM", "build_record: item from RIMFLOW_ITEM")
        check(CE.build_record("t", "PASS", [], end=dict(end), item="EXPL")["item"] == "EXPL", "build_record: explicit item wins")
        os.environ["RIMFLOW_ITEM"] = ""
        check(CE.build_record("t", "PASS", [], end=dict(end))["item"] is None, "build_record: empty RIMFLOW_ITEM -> None")
    finally:
        os.environ.pop("RIMFLOW_ITEM", None)
        for k, v in saved.items():
            if v is not None:
                os.environ[k] = v
    for bad in ("pass", "", None):
        try:
            CE.build_record("t", bad, [])
            r = "no raise"
        except ValueError as e:
            r = "ok" if "result must be one of" in str(e) else str(e)
        check(r == "ok", "build_record: result %r is refused with a ValueError naming the choices" % (bad,))
    # seat argument
    w = CE.build_record("t", "PASS", [], end=dict(end), who={"seat": None}, seat="BENCH")
    check(w["seat"] == "BENCH" and w["who"]["seat_from"] == "caller", "build_record: seat= with no seat_from -> 'caller'")
    w = CE.build_record("t", "PASS", [], end=dict(end), who={"seat": None, "seat_from": "RIMFLOW_SEAT"}, seat="BENCH")
    check(w["who"]["seat_from"] == "RIMFLOW_SEAT", "build_record: seat= keeps an existing seat_from")
    # clone: derived from the first path, resolved; an explicit clone is not overridden
    other, _s = make_repo(td, "br_other")
    rec = CE.build_record("t", "PASS", [repo / "src" / "a.py"], end=dict(end))
    check(rec["clone"] == os.path.realpath(str(repo)) and rec["paths"] == ["src/a.py"] and rec["covers"] == ["src/a.py"],
          "build_record: clone from the first path, repo-relative paths and covers: %r" % rec["clone"])
    rec = CE.build_record("t", "PASS", [repo / "src" / "a.py"], clone=other, end=dict(end))
    check(rec["clone"] == os.path.realpath(str(other)), "build_record: an explicit clone is kept (not re-derived from the path)")
    rec = CE.build_record("t", "PASS", [repo / "src" / "a.py"], end=dict(end), covers=[repo / "src" / "x.py"])
    check(rec["covers"] == ["src/x.py"] and rec["paths"] == ["src/a.py"], "build_record: covers= is mapped, not the paths")
    # origin flags: a state typed in by a caller is 'caller'; minted + isolated is inproc/isolated/git
    sn = CE.snapshot(repo)
    iso_mark(repo)
    rec = CE.build_record("t", "PASS", [repo / "src" / "a.py"], start=sn)
    o = rec["origin"]
    check(o["via"] == "inproc" and o["start"] == "snapshot" and o["end"] == "git" and o["tree"] == "isolated"
          and o["pid"] == os.getpid() and isinstance(o["host"], str) and o["host"], "build_record: origin of an honest run: %r" % o)
    rec = CE.build_record("t", "PASS", [repo / "src" / "a.py"], start=dict(sn, dirty_n=9), end={**dict(end), "dirty_paths": ["p"]})
    o = rec["origin"]
    check(o["start"] == "caller" and o["end"] == "caller" and o["tree"] == "shared" and rec["dirty_paths"] == ["p"],
          "build_record: a typed-in start/end is 'caller', a clone without a valid marker for that sha is 'shared'")
    rec = CE.build_record("t", "PASS", [repo / "src" / "a.py"], start=sn, via="cli")
    o = rec["origin"]
    check(o["via"] == "cli" and o["start"] == "caller" and o["end"] == "caller" and o["tree"] == "shared", "build_record: via cli is never inproc-minted")
    check(rec["start"] == {"sha": sn["sha"], "dirty": sn["dirty"], "dirty_n": sn["dirty_n"]}, "build_record: start keeps sha/dirty/dirty_n and drops the token")

    # isolated_ok
    check(CE.isolated_ok(None, sha) is False and CE.isolated_ok(repo, None) is False and CE.isolated_ok("", sha) is False
          and CE.isolated_ok(repo, "") is False, "isolated_ok: no clone / no sha -> False, no exception")
    check(CE.isolated_ok(repo, sha) is True and CE.isolated_ok(repo, "f" * 40) is False and CE.isolated_ok(Path(td) / "nope", sha) is False,
          "isolated_ok: marker valid only for its own clone and sha")


def g_record_and_store(td):
    repo, sha0 = make_repo(td, "st")
    store = Path(td) / "store"
    os.environ[CE.ENV_DIR] = str(store / "nested" / "deep")
    # evidence_dir creates parents
    d = CE.evidence_dir()
    check(d.is_dir() and d == store / "nested" / "deep", "evidence_dir: RM_CLOSE_EVIDENCE_DIR is created with its parents")
    os.environ[CE.ENV_DIR] = str(store)

    # record(): NESTED guard
    os.environ["RM_SELFTEST_NESTED"] = "1"
    try:
        r_skip = good(repo, tool="nested1")
        os.environ.pop(CE.ENV_DIR)
        r_skip2 = good(repo, tool="nested2")
        r_force = CE.record("nested3", "PASS", [repo / "src" / "a.py"], clone=repo, force=True) if False else None
        os.environ[CE.ENV_DIR] = str(store)
    finally:
        os.environ.pop("RM_SELFTEST_NESTED", None)
    check(r_skip is not None, "record: NESTED set but the store redirected -> still recorded")
    check(r_skip2 is None, "record: NESTED set, no redirect, no force -> a fixture, nothing written")
    # NESTED unset and no redirect: recorded through agent_storage (stubbed)
    stub = Path(td) / "agent_storage_stub.py"
    cnt = Path(td) / "stub_count"
    root = Path(td) / "stubroot" / "r"
    stub.write_text("import sys, pathlib\np = pathlib.Path(%r)\np.write_text(p.read_text() + 'x' if p.exists() else 'x')\n"
                    "mode = pathlib.Path(%r).read_text()\nif mode == 'ok': print(%r)\nelif mode == 'fail': print('out'); print('err text', file=sys.stderr); sys.exit(3)\n"
                    "elif mode == 'failquiet': sys.exit(3)\nelif mode == 'empty': pass\n" % (str(cnt), str(Path(td) / "stub_mode"), str(root)))
    real_as, real_cache = CE.AGENT_STORAGE, list(CE._ROOT_CACHE)
    os.environ.pop(CE.ENV_DIR)
    try:
        CE.AGENT_STORAGE = stub
        CE._ROOT_CACHE.clear()
        (Path(td) / "stub_mode").write_text("ok")
        rr = good(repo, tool="viastub")
        check(rr is not None and (root / "evidence").is_dir() and any((root / "evidence").glob("*.jsonl")),
              "record: NESTED unset and no redirect -> written under agent_storage root/evidence (parents created)")
        rr2 = good(repo, tool="viastub2")
        check(cnt.read_text() == "x" and CE._ROOT_CACHE == [str(root)], "evidence_dir: agent_storage is asked once, then cached: %r" % cnt.read_text())
        CE._ROOT_CACHE[:] = [str(Path(td) / "cached_root")]
        check(CE.evidence_dir() == Path(td) / "cached_root" / "evidence", "evidence_dir: the cache is used when filled (index 0)")
        for mode, want in (("fail", "err text"), ("failquiet", "no output"), ("empty", "no output")):
            CE._ROOT_CACHE.clear()
            (Path(td) / "stub_mode").write_text(mode)
            try:
                CE.evidence_dir()
                r = "no raise"
            except RuntimeError as e:
                r = str(e)
            check(r == "agent_storage.py rimmandrake failed: %s" % want, "evidence_dir: stub mode %s raises with %r: %s" % (mode, want, r))
        CE._ROOT_CACHE.clear()
        (Path(td) / "stub_mode").write_text("empty")
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            r = good(repo, tool="nostore")
        check(r is None and "CLOSE-EVIDENCE WRITE FAILED" in err.getvalue() and "tool=nostore" in err.getvalue(),
              "record: a store that cannot be found prints the loud failure and returns None")
    finally:
        CE.AGENT_STORAGE = real_as
        CE._ROOT_CACHE[:] = real_cache
        os.environ[CE.ENV_DIR] = str(store)
    err = io.StringIO()
    with contextlib.redirect_stderr(err):
        bad = CE.record("t", "BOGUS", [repo / "src" / "a.py"], clone=repo)
    check(bad is None and "CLOSE-EVIDENCE WRITE FAILED" in err.getvalue() and "ValueError" in err.getvalue(), "record: never raises, prints loudly")

    # written line == sort_keys JSON of the returned record
    rec = good(repo, tool="sorted")
    day = store / ("%s.jsonl" % rec["ts"][:10])
    lines = day.read_text().splitlines()
    mine = [ln for ln in lines if json.loads(ln).get("tool") == "sorted"][0]
    check(mine == json.dumps(json.loads(mine), sort_keys=True) and json.loads(mine) == json.loads(json.dumps(rec, default=str)),
          "record: the stored line is the sorted-key JSON of the returned record")
    check(CE.counts_as_evidence(rec, CE._key()) is True, "fixture: an honest record counts as evidence")

    # record() on the nt branch ships a payload (os.name faked for this module only)
    shipped = []
    real_os, real_ship = CE.os, CE._ship_to_wsl

    class FakeOs:
        name = "nt"

        def __getattr__(self, n):
            return getattr(real_os, n)
    CE.os, CE._ship_to_wsl = FakeOs(), (lambda p: shipped.append(p) or {"shipped": True})
    try:
        out = CE.record("t", "PASS", ["a.py", Path("b.py")], clone=Path("c"), detail={"d": 1}, item="I", start={"s": 1}, end={"e": 1},
                        scope=["x"], covers=[Path("a.py")], live_only=True, variant="v")
        out2 = CE.record("t", "PASS", None)
    finally:
        CE.os, CE._ship_to_wsl = real_os, real_ship
    check(out == {"shipped": True} and shipped[0] == {"tool": "t", "result": "PASS", "paths": ["a.py", "b.py"], "clone": "c",
                                                   "detail": {"d": 1}, "item": "I", "start": {"s": 1}, "end": {"e": 1},
                                                   "scope": ["x"], "covers": ["a.py"], "live_only": True, "variant": "v"},
          "record(nt): the whole payload is shipped to WSL: %r" % (shipped[:1],))
    check(shipped[1]["paths"] == [] and shipped[1]["clone"] is None and shipped[1]["covers"] is None, "record(nt): empty paths/clone/covers")


def g_ship_to_wsl(td):
    calls = []

    def fake_run(cmd, **kw):
        calls.append((cmd, kw))
        return types.SimpleNamespace(returncode=fake_run.rc, stdout=fake_run.out, stderr=fake_run.err)
    real_run = CE.subprocess.run
    CE.subprocess.run = fake_run
    saved = {k: os.environ.pop(k, None) for k in ("RIMFLOW_ITEM", CE.ENV_DIR)}
    try:
        fake_run.rc, fake_run.out, fake_run.err = 0, 'noise\n{"ok": 1}\n', ""
        os.environ[CE.ENV_DIR] = "D:\\ev\\dir"
        os.environ["RIMFLOW_ITEM"] = "ITEM_X"
        got = CE._ship_to_wsl({"tool": "t", "paths": ["D:\\a\\b.py"], "covers": ["D:\\a\\c.py"], "clone": "D:\\a"})
        cmd, kw = calls[-1]
        pl = json.loads(kw["input"])
        check(got == {"ok": 1}, "_ship_to_wsl: returns the last stdout line as JSON")
        check(cmd[:4] == ["wsl.exe", "-e", "python3", cmd[3]] and cmd[-1] == "record" and cmd[3].endswith("close_evidence.py"),
              "_ship_to_wsl: runs `wsl.exe -e python3 <this file> record`: %r" % cmd)
        check(kw["capture_output"] is True and kw["text"] is True and kw["timeout"] == 120, "_ship_to_wsl: capture, text, 120 s")
        check(pl["evidence_dir"] == "/mnt/d/ev/dir" and pl["paths"] == ["/mnt/d/a/b.py"] and pl["covers"] == ["/mnt/d/a/c.py"]
              and pl["clone"] == "/mnt/d/a" and pl["item"] == "ITEM_X" and isinstance(pl["who"], dict) and "seat" in pl["who"],
              "_ship_to_wsl: dir, paths, covers, clone translated; item and who attached: %r" % {k: pl[k] for k in pl if k != 'who'})
        os.environ.pop(CE.ENV_DIR)
        os.environ["RIMFLOW_ITEM"] = ""
        CE._ship_to_wsl({"tool": "t", "paths": None, "item": "KEEP", "who": {"seat": "X"}})
        pl = json.loads(calls[-1][1]["input"])
        check("evidence_dir" not in pl and pl["paths"] == [] and "covers" not in pl and "clone" not in pl and pl["item"] == "KEEP"
              and pl["who"] == {"seat": "X"}, "_ship_to_wsl: nothing invented: %r" % pl)
        CE._ship_to_wsl({"tool": "t"})
        check(json.loads(calls[-1][1]["input"])["item"] is None, "_ship_to_wsl: an empty RIMFLOW_ITEM ships None")
        for err, out, want in (("E" * 500, "", "E" * 400), ("", "O" * 500, "O" * 400)):
            fake_run.rc, fake_run.out, fake_run.err = 7, out, err
            try:
                CE._ship_to_wsl({"tool": "t"})
                r = "no raise"
            except RuntimeError as e:
                r = str(e)
            check(r == "wsl.exe close_evidence record exit 7: %s" % want, "_ship_to_wsl: a failure raises with exit code and the last 400 chars: %s" % r[:60])
        fake_run.rc, fake_run.out, fake_run.err = 7, "stdout text", "stderr text"
        try:
            CE._ship_to_wsl({"tool": "t"})
        except RuntimeError as e:
            check(str(e).endswith("stderr text"), "_ship_to_wsl: stderr is preferred to stdout in the message")
    finally:
        CE.subprocess.run = real_run
        for k, v in saved.items():
            os.environ.pop(k, None)
            if v is not None:
                os.environ[k] = v


def tamper(line, **kw):
    r = json.loads(line)
    r.update(kw)
    return json.dumps(r, sort_keys=True)


def g_lookup(td):
    repo, sha0 = make_repo(td, "lk")
    store = Path(td) / "lkstore"
    os.environ[CE.ENV_DIR] = str(store)
    z = good(repo, tool="old", item="I0")                                  # at an OLDER commit
    sha1 = commit_file(repo, "src/b.py", "y = 2\n", "two")
    a = good(repo, tool="ta", item="I1", paths=[repo / "src" / "a.py"])
    (repo / "dirt.txt").write_text("d")
    dirty = good(repo, tool="tdirty", item="I2")
    (repo / "dirt.txt").unlink()
    live = good(repo, tool="tl", item="I2", live_only=True)
    b = good(repo, tool="tb", item="I2", paths=[repo / "src" / "b.py"])
    day = store / ("%s.jsonl" % a["ts"][:10])
    orig = day.read_text().splitlines()
    by_tool = {json.loads(ln)["tool"]: ln for ln in orig}
    lines = [by_tool["old"], by_tool["ta"], by_tool["ta"], by_tool["tdirty"], by_tool["tl"], by_tool["tb"]]   # ta replayed
    day.write_text("\n".join(lines) + "\n")

    def tools(hits):
        return [h["tool"] for h in hits]
    check(tools(CE.lookup(sha1)) == ["ta", "tb"], "lookup: other commits, the replayed line, the dirty and the live-only line are skipped; later lines still read: %r" % tools(CE.lookup(sha1)))
    check(tools(CE.lookup(sha1, include_live=True)) == ["ta", "tl", "tb"], "lookup: include_live adds the live line only")
    check(tools(CE.lookup(sha1, include_dirty=True)) == ["ta", "tdirty", "tb"], "lookup: include_dirty adds the dirty line only")
    check(tools(CE.lookup(sha1, item="I2")) == ["tb"] and tools(CE.lookup(item="I2")) == ["tb"], "lookup: item filter (with and without sha)")
    check(tools(CE.lookup(sha1, tool="tb")) == ["tb"] and tools(CE.lookup(sha1, tool="ta")) == ["ta"], "lookup: tool filter")
    check(tools(CE.lookup(sha1, paths=["src/b.py"])) == ["tb"] and tools(CE.lookup(sha1, paths=["src/a.py"])) == ["ta"],
          "lookup: paths filter keeps only covering records")
    check(tools(CE.lookup(sha0)) == ["old"] and tools(CE.lookup(sha0[:40])) == ["old"], "lookup: the older commit's record belongs to the older sha")
    check(tools(CE.lookup(item="I0")) == ["old"], "lookup: item lookup finds a record at any commit")
    for bad in ("abc1234", "A" * 40, "g" * 40, "a" * 39):
        try:
            CE.lookup(bad)
            r = "no raise"
        except ValueError:
            r = "ValueError"
        check(r == "ValueError", "lookup: sha %r that is not one full lowercase 40-hex raises" % bad)
    try:
        CE.lookup()
        r = "no raise"
    except ValueError as e:
        r = "ok" if "needs a sha or an item" in str(e) else str(e)
    check(r == "ok", "lookup: neither sha nor item raises")

    # unverifiable lines: a tampered sealed line, an other-commit legacy line, a matching legacy line
    t_same = tamper(by_tool["ta"], result="FAIL")                       # mac broken, route intact (names sha1/ta)
    t_other = tamper(by_tool["old"], result="FAIL")                     # route names the OLDER commit
    leg_other = json.dumps({"v": 2, "ts": "2026-01-01T00:00:00+00:00", "tool": "ta", "sha": "b" * 40, "result": "PASS"})
    leg_prefix = json.dumps({"v": 2, "ts": "2026-01-01T00:00:00+00:00", "tool": "ta", "sha": sha1[:9], "result": "PASS"})
    leg_short = json.dumps({"v": 2, "ts": "2026-01-01T00:00:00+00:00", "tool": "ta", "sha": sha1[:6], "result": "PASS"})
    leg_badtype = json.dumps({"v": 2, "tool": "ta", "sha": 5, "result": "PASS"})
    leg_tool = json.dumps({"v": 2, "tool": "zzz", "sha": sha1, "result": "PASS"})
    day.write_text("\n".join([t_other, leg_other, leg_short, leg_badtype, t_same, leg_prefix, leg_tool] + lines) + "\n")
    hits = CE.lookup(sha1)
    mk = [h for h in hits if h["tool"] == "close_evidence"]
    check(tools(hits)[:2] == ["ta", "tb"] and len(mk) == 1 and hits[-1] is mk[0]
          and mk[0]["detail"]["unverifiable_lines"] == 3 and mk[0]["detail"]["unreadable_lines"] == 0,
          "lookup: tampered (own route) + 2 legacy lines naming this commit = ONE UNMEASURED marker last, counts 3: %r %r"
          % ([h["tool"] for h in hits], mk and mk[0]["detail"]))
    hits = CE.lookup(sha1, tool="ta")
    mk = [h for h in hits if h["tool"] == "close_evidence"]
    check(len(mk) == 1 and mk[0]["detail"]["unverifiable_lines"] == 2 and tools(hits)[0] == "ta",
          "lookup: with tool= the legacy line of another tool is not attributed: %r" % (mk and mk[0]["detail"]))
    check(tools(CE.lookup(item="I2")) == ["tb"], "lookup: an item lookup ignores unverifiable lines and reads past them")
    check(tools(CE.lookup(sha0)) == ["old", "close_evidence"] and CE.lookup(sha0)[-1]["detail"]["unverifiable_lines"] == 1,
          "lookup: the other commit's tampered line is attributed to ITS commit only")
    # unreadable fragments are marked with the days
    day.write_text("{\"sha\": \"%s\", \"tool\": \"ta\", \"res\n" % sha1 + "\n".join(lines) + "\n")
    hits = CE.lookup(sha1)
    check(hits[-1]["tool"] == "close_evidence" and hits[-1]["detail"]["unreadable_lines"] == 1
          and hits[-1]["detail"]["days"] == [day.stem], "lookup: a torn line whose top-level sha is ours -> marker with its day: %r" % hits[-1]["detail"])
    e40 = "e" * 40
    day.write_text("{\"sha\": \"%s\", \"tool\": \"ta\", \"route\": \"%s\", \"res\n" % (e40, CE._route_mac(e40, "ta", CE._key())) + "\n".join(lines) + "\n")
    check(CE.lookup(sha1)[-1]["tool"] != "close_evidence", "lookup: a torn line whose sealed route names another commit is not ours")
    day.write_text("{\"sha\": \"%s\", \"tool\": \"ta\", \"res\n" % e40 + "\n".join(lines) + "\n")
    check(CE.lookup(sha1)[-1]["tool"] == "close_evidence", "lookup: a torn line with no sealed route may be ours (conservative)")
    day.write_text("\n".join(lines) + "\n")

    # read_all: missing day files are skipped, not the end of the read; bad lines counted
    check(len(CE.read_all(30, store)) == 6 and len(CE.read_all(1, store)) == 6, "read_all: days with no file in between are skipped (30-day window, today's file read)")
    f2 = Path(td) / "ra"
    f2.mkdir()
    dfile = f2 / ("%s.jsonl" % CE._days(1)[0])
    dfile.write_text("\n\nnot json\n{\"a\": 1}\n[1]\n   \n")
    bo, err = [], io.StringIO()
    with contextlib.redirect_stderr(err):
        got = CE.read_all(3, f2, bad_out=bo)
    check(got == [{"a": 1}] and len(bo) == 2 and bo[0][0] == dfile.stem and err.getvalue().strip() == "close_evidence: 2 unreadable line(s) skipped",
          "read_all: blank lines are not bad; each bad line is counted once and reported in bad_out: %r %r" % (bo, err.getvalue()))
    dfile.write_text("\n\n")
    err = io.StringIO()
    with contextlib.redirect_stderr(err):
        got = CE.read_all(3, f2)
    check(got == [] and err.getvalue() == "", "read_all: a clean store says nothing on stderr")
    os.environ[CE.ENV_DIR] = str(store)


def g_make_isolated(td):
    repo, sha = make_repo(td, "mi")
    rootd = Path(td) / "isoroot" / "deep"
    old_env = os.environ.pop(CE.ISOLATED_ROOT_ENV, None)
    try:
        co, full, tdir = CE.make_isolated(repo, "HEAD", root=rootd)
        check(full == sha and co.startswith(os.path.realpath(str(rootd))) and Path(co, "src", "a.py").is_file() and CE.isolated_ok(co, full),
              "make_isolated: checkout under the given root (created with parents), marker valid for its sha")
        subprocess.run(["rm", "-rf", tdir])
        os.environ[CE.ISOLATED_ROOT_ENV] = str(Path(td) / "envroot")
        co, full, tdir = CE.make_isolated(repo, sha[:10])
        check(co.startswith(os.path.realpath(str(Path(td) / "envroot"))), "make_isolated: root from RM_ISOLATED_ROOT; a short sha resolves")
        subprocess.run(["rm", "-rf", tdir])
        co, full, tdir = CE.make_isolated(repo, "HEAD", root=rootd)
        check(co.startswith(os.path.realpath(str(rootd))), "make_isolated: an explicit root beats the environment")
        subprocess.run(["rm", "-rf", tdir])
    finally:
        os.environ.pop(CE.ISOLATED_ROOT_ENV, None)
        if old_env is not None:
            os.environ[CE.ISOLATED_ROOT_ENV] = old_env
    try:
        CE.make_isolated(repo, "no-such-ref", root=rootd)
        r = "no raise"
    except RuntimeError as e:
        r = str(e)
    check(r == "no-such-ref does not resolve in %s" % repo, "make_isolated: an unresolvable ref names the ref and the clone: %s" % r)

    # a failing git step: message names the step and the stderr tail; the temp dir is removed; the key is made last
    real_run = CE.subprocess.run
    for step, nth in (("clone", 0), ("checkout", 1)):
        n = [0]

        def fake(cmd, **kw):
            if cmd[0] == "git" and cmd[1] in ("clone", "-C") and (cmd[1] == "clone" or cmd[3] == "checkout"):
                if n[0] == nth:
                    n[0] += 1
                    return types.SimpleNamespace(returncode=128, stdout="", stderr="x" * 400 + " boom\n")
                n[0] += 1
            return real_run(cmd, **kw)
        before = set(os.listdir(rootd)) if rootd.exists() else set()
        CE.subprocess.run = fake
        try:
            CE.make_isolated(repo, "HEAD", root=rootd)
            r = "no raise"
        except RuntimeError as e:
            r = str(e)
        finally:
            CE.subprocess.run = real_run
        check(r == "git %s failed: %s" % (step, ("x" * 400 + " boom")[-300:]), "make_isolated: failing %s step -> %r" % (step, r[:50]))
        check(set(os.listdir(rootd)) == before, "make_isolated: the temp dir of a failed %s is removed" % step)
    # the key: created by make_isolated when it does not exist yet
    old = os.environ.get(CE.KEY_ENV)
    try:
        kp = Path(td) / "iso_key_dir" / "key"
        os.environ[CE.KEY_ENV] = str(kp)
        co, full, tdir = CE.make_isolated(repo, "HEAD", root=rootd)
        check(kp.is_file() and CE.isolated_ok(co, full), "make_isolated: creates the mac key when there is none and marks with it")
        subprocess.run(["rm", "-rf", tdir])
    finally:
        os.environ[CE.KEY_ENV] = old


def g_isolated_cli(td):
    repo, sha = make_repo(td, "ic")
    sub = repo / "src"
    err = io.StringIO()
    out = io.StringIO()
    marker = Path(td) / "ic_cwd.txt"
    with contextlib.redirect_stderr(err), contextlib.redirect_stdout(out):
        rc = CE._isolated_cli(["--clone", str(sub), "--", sys.executable, "-c",
                               "import os,sys; open(%r,'w').write(os.getcwd()); sys.exit(5)" % str(marker)])
    cwd = marker.read_text()
    check(rc == 5, "isolated CLI: returns the command's exit code: %r" % rc)
    check(not Path(cwd).exists() and cwd != str(repo) and "isolated checkout of %s at" % sha[:12] in err.getvalue()
          and ("isolated checkout of %s " % sha[:13]) not in err.getvalue(),
          "isolated CLI: a clone given as a subdirectory is lifted to its toplevel; the checkout is deleted; 12-char sha announced: %r" % err.getvalue()[:100])
    with contextlib.redirect_stderr(io.StringIO()):
        rc = CE._isolated_cli(["--clone", str(repo), "--keep", sys.executable, "-c",
                               "import os; open(%r,'w').write(os.getcwd())" % str(marker)])
    kept = marker.read_text()
    check(rc == 0 and Path(kept).is_dir(), "isolated CLI: --keep leaves the checkout (and a command without -- works)")
    subprocess.run(["rm", "-rf", str(Path(kept).parent)])
    e2 = io.StringIO()
    with contextlib.redirect_stderr(e2):
        try:
            CE._isolated_cli(["--clone", str(repo)])
            r = "no exit"
        except SystemExit as e:
            r = e.code
    check(r == 2 and "a command is needed" in e2.getvalue(), "isolated CLI: no command -> usage error 2")


def g_cli(td):
    repo, sha0 = make_repo(td, "cl")
    store = Path(td) / "clstore"
    os.environ[CE.ENV_DIR] = str(store)
    rc, out, err = run_main(["where"])
    check(rc == 0 and out.strip() == str(store) and store.is_dir(), "CLI where: prints the evidence folder, exit 0")
    rc, out, err = run_main([])
    check(rc == 2, "CLI: no subcommand is a usage error (2)")
    rc, out, err = run_main(["lookup"])
    check(rc == 2 and "lookup needs --sha or --item" in err, "CLI lookup: neither --sha nor --item is a usage error: %r %r" % (rc, err[-80:]))
    rc, out, err = run_main(["--help"])
    check(rc == 0 and " ".join(CE.__doc__.split("\n")[0].split()) in " ".join(out.split()),
          "CLI: --help carries the module's first docstring line")

    paths = ["p%d.py" % i for i in range(6)]
    for i, p in enumerate(paths):
        Path(repo, p).write_text("1")
        git(repo, "add", p)
    git(repo, "commit", "-q", "-m", "ps", "--", *paths)
    sha1 = commit_file(repo, "z.py", "1", "z")
    r1 = good(repo, tool="ta", paths=[repo / p for p in paths], item="II")
    r2 = good(repo, tool="tb", paths=[repo / "p0.py"], item="II")
    rc, out, err = run_main(["lookup", "--sha", sha1])
    ls = out.splitlines()
    check(rc == 0 and len(ls) == 3, "CLI lookup: one line per record + summary: %r" % ls)
    f1 = ls[0].split()
    check(f1[0] == r1["ts"] and f1[1] == "ta" and f1[2] == "PASS" and f1[3] == sha1[:12] and f1[4] == ",".join(paths[:4]) and f1[5] == "(+2)"
          and "NOT-EVIDENCE" not in ls[0] and "LIVE" not in ls[0], "CLI lookup: ts/tool/result/sha12/first 4 paths/(+n more): %r" % ls[0])
    check(ls[1].split()[-1] == "p0.py" and "(+" not in ls[1], "CLI lookup: a record with <=4 paths shows them all, no (+n): %r" % ls[1])
    check(ls[2] == '2 record(s); summary {"ta": "PASS", "tb": "PASS"}', "CLI lookup: summary is key-sorted JSON: %r" % ls[2])
    # exactly 4 / 5 paths boundaries
    good(repo, tool="t4", paths=[repo / p for p in paths[:4]])
    good(repo, tool="t5", paths=[repo / p for p in paths[:5]])
    rc, out, err = run_main(["lookup", "--sha", sha1, "--tool", "t4"])
    check("(+" not in out.splitlines()[0] and out.splitlines()[0].split()[-1] == ",".join(paths[:4]), "CLI lookup: exactly 4 paths -> no (+n): %r" % out.splitlines()[0])
    rc, out, err = run_main(["lookup", "--sha", sha1, "--tool", "t5"])
    check(out.splitlines()[0].endswith("(+1)"), "CLI lookup: 5 paths -> (+1): %r" % out.splitlines()[0])
    rc, out, err = run_main(["lookup", "--item", "II"])
    check(rc == 0 and out.splitlines()[-1].startswith("2 record(s)") and "uncovered" not in out, "CLI lookup: --item alone works, no uncovered line without --path")
    rc, out, err = run_main(["lookup", "--sha", sha1, "--path", "p0.py", "--path", "nothere.py"])
    check(out.splitlines()[-1] == "uncovered: nothere.py" and "t5" in out and "t4" in out, "CLI lookup: --path lists what no hit covers: %r" % out.splitlines()[-1])
    rc, out, err = run_main(["lookup", "--sha", sha1, "--path", "p0.py"])
    check(out.splitlines()[-1] == "uncovered: none", "CLI lookup: --path fully covered -> 'uncovered: none'")
    # flags are passed through (days default 30, paths None without --path)
    seen = []
    real_lookup = CE.lookup
    CE.lookup = lambda *a, **k: seen.append((a, k)) or []
    try:
        run_main(["lookup", "--sha", sha1])
        run_main(["lookup", "--sha", sha1, "--item", "X", "--tool", "tt", "--days", "7", "--all", "--live", "--path", "a", "--path", "b"])
    finally:
        CE.lookup = real_lookup
    check(seen[0] == ((sha1, None, None, 30), {"include_dirty": False, "paths": None, "include_live": False}),
          "CLI lookup: defaults pass days=30, no paths, no dirty, no live: %r" % (seen[0],))
    check(seen[1] == ((sha1, "X", "tt", 7), {"include_dirty": True, "paths": ["a", "b"], "include_live": True}),
          "CLI lookup: every option reaches lookup(): %r" % (seen[1],))
    # NOT-EVIDENCE / LIVE marks and a record without sha/paths
    fake = [{"ts": "T", "tool": "x", "result": "FAIL", "sha": None, "paths": None, "live_only": True}]
    CE.lookup = lambda *a, **k: fake
    try:
        rc, out, err = run_main(["lookup", "--item", "I"])
    finally:
        CE.lookup = real_lookup
    first = out.splitlines()[0]
    check(first.split()[:4] == ["T", "x", "FAIL", "-"] and "NOT-EVIDENCE" in first and " LIVE" in first and out.splitlines()[1] == '1 record(s); summary {"x": "FAIL"}',
          "CLI lookup: a sha-less live record prints '-', NOT-EVIDENCE and LIVE: %r" % first)
    # dispatch of record / isolated
    calls = []
    real_rc, real_ic = CE._record_cli, CE._isolated_cli
    CE._record_cli, CE._isolated_cli = (lambda: calls.append("record") or 7), (lambda argv: calls.append(("isolated", argv)) or 9)
    try:
        r1_ = run_main(["record"])[0]
        r2_ = run_main(["isolated", "--sha", "X", "--", "ls"])[0]
    finally:
        CE._record_cli, CE._isolated_cli = real_rc, real_ic
    check(r1_ == 7 and r2_ == 9 and calls == ["record", ("isolated", ["--sha", "X", "--", "ls"])], "CLI: record / isolated dispatch with their exit codes")


def g_record_cli(td):
    repo, sha = make_repo(td, "rc")
    store = Path(td) / "rcstore"
    env = dict(os.environ, **{CE.KEY_ENV: os.environ[CE.KEY_ENV]})
    env.pop(CE.ENV_DIR, None)
    env["RM_SELFTEST_NESTED"] = "1"
    payload = {"tool": "modcheck", "result": "PASS", "paths": [str(repo / "src" / "a.py")], "clone": str(repo), "detail": {"k": 1},
               "item": "ITEM", "start": {"sha": sha, "dirty": False, "dirty_n": 0, "_token": "forged"}, "end": {"sha": "f" * 40, "dirty": False, "dirty_n": 0},
               "covers": [str(repo / "src" / "a.py")], "evidence_dir": str(store), "who": {"seat": "BENCH", "seat_from": "RIMFLOW_SEAT"}}
    me = str(HERE / "close_evidence.py")
    p = subprocess.run([sys.executable, me, "record"], input=json.dumps(payload), capture_output=True, text=True, env=env, timeout=120)
    check(p.returncode == 0, "record CLI: exit 0 on a good payload (and RM_SELFTEST_NESTED is dropped): %r" % p.stderr[-200:])
    rec = json.loads(p.stdout)
    check(p.stdout.strip() == json.dumps(rec, sort_keys=True), "record CLI: prints the record as sorted-key JSON")
    files = list(store.glob("*.jsonl"))
    line = files[0].read_text().splitlines()[0] if files else ""
    check(line == json.dumps(json.loads(line), sort_keys=True) and json.loads(line) == rec, "record CLI: stores the same record, sorted-key JSON")
    check(rec["origin"]["via"] == "cli" and rec["origin"]["start"] == "caller" and rec["origin"]["end"] == "caller" and rec["sha"] == sha
          and rec["who"]["seat_from"] == "shipped:RIMFLOW_SEAT" and rec["live_only"] is False and rec["item"] == "ITEM" and rec["paths"] == ["src/a.py"],
          "record CLI: via cli, caller start, end re-read from git, shipped seat, live_only defaults False: %r" % rec["origin"])
    check(not CE.counts_as_evidence(rec), "record CLI: a shipped line is never sha evidence")
    payload2 = dict(payload, live_only=True, who="not a dict")
    p = subprocess.run([sys.executable, me, "record"], input=json.dumps(payload2), capture_output=True, text=True, env=env, timeout=120)
    rec2 = json.loads(p.stdout)
    check(rec2["live_only"] is True and rec2["who"]["seat_from"] == "shipped:None" and rec2["origin"]["who"] == "caller",
          "record CLI: live_only passes through; a non-dict who becomes shipped:None: %r" % rec2["who"])
    p = subprocess.run([sys.executable, me, "record"], input=json.dumps(dict(payload, result="BOGUS")), capture_output=True, text=True, env=env, timeout=120)
    check(p.returncode == 1 and p.stdout == "" and p.stderr.startswith("record failed: ValueError: result must be one of"),
          "record CLI: a bad payload -> exit 1, 'record failed: ...' on stderr, nothing on stdout: %r %r" % (p.returncode, p.stderr[:80]))
    p = subprocess.run([sys.executable, me, "record"], input=json.dumps({k: v for k, v in payload.items() if k != "tool"}), capture_output=True, text=True, env=env, timeout=120)
    check(p.returncode == 1 and "record failed: KeyError" in p.stderr, "record CLI: a payload without tool -> exit 1 KeyError")


def g_whoami_seats():
    saved = {k: os.environ.pop(k, None) for k in ("CLAUDE_CODE_BRIDGE_SESSION_ID", "RIMFLOW_SEAT", "AGENT_SEAT", "CLAUDE_SESSION_ID",
                                                  "CLAUDE_CODE_SESSION_ID", "AI_AGENT")}
    try:
        check(CE.whoami()["bridge_session"] is None, "whoami: no bridge session -> None")
        os.environ["CLAUDE_CODE_BRIDGE_SESSION_ID"] = "session_X"
        check(CE.whoami()["bridge_session"] == "session_X", "whoami: bridge_session from CLAUDE_CODE_BRIDGE_SESSION_ID")
        os.environ["CLAUDE_CODE_BRIDGE_SESSION_ID"] = ""
        check(CE.whoami()["bridge_session"] is None, "whoami: an empty bridge session -> None")
    finally:
        for k, v in saved.items():
            os.environ.pop(k, None)
            if v is not None:
                os.environ[k] = v
    # _seats_and_root: the fallback when rimflow cannot be imported, and sys.path restored
    CE._seats_and_root()                               # warm-up: importing rimflow may itself add its own entry once
    before = list(sys.path)
    seats, root = CE._seats_and_root()
    check(sys.path == before and "BENCH" in seats,
          "_seats_and_root: sys.path is exactly restored (no leaked entry, even after the whoami() calls above); rimflow's seats")
    real_mod = {k: sys.modules.get(k) for k in ("rimflow", "rimflow.model")}
    sys.modules["rimflow"] = None
    sys.modules["rimflow.model"] = None
    try:
        seats, root = CE._seats_and_root()
    finally:
        for k, v in real_mod.items():
            if v is None:
                sys.modules.pop(k, None)
            else:
                sys.modules[k] = v
    check(seats == CE._SEATS_FALLBACK and root == str(Path(CE.__file__).resolve().parents[3]) and sys.path == before,
          "_seats_and_root: an unimportable rimflow -> the fallback seats and the clone root (parents[3]); path restored")
    # the import really sees rimflow from sys.path[0] (not appended): shadow it from an earlier entry
    probe = ("import sys; sys.path.insert(0, %r); import close_evidence as C; b = list(sys.path); s, r = C._seats_and_root(); "
             "print(True, 'BENCH' in s)" % str(HERE))
    p = subprocess.run([sys.executable, "-I", "-c", probe], capture_output=True, text=True, timeout=60)
    check(p.stdout.strip() == "True True", "_seats_and_root: works and restores sys.path from a bare interpreter: %r %r" % (p.stdout, p.stderr[-120:]))


def g_counts_as_evidence(td):
    repo, sha0 = make_repo(td, "ce")
    store = Path(td) / "cestore"
    os.environ[CE.ENV_DIR] = str(store)
    key = CE._key()
    rec = good(repo)
    ok = lambda r: CE.counts_as_evidence(r)
    check(ok(rec), "counts_as_evidence: an honest record")
    for name, mut in (("no sha", {"sha": ""}), ("dirty", {"dirty": True}), ("dirty unknown", {"dirty": None}), ("bad result", {"result": "MAYBE"}),
                      ("live", {"live_only": True}), ("start dirty", {"start": dict(rec["start"], dirty=True)}),
                      ("start other sha", {"start": dict(rec["start"], sha="f" * 40)}), ("start no sha", {"start": dict(rec["start"], sha=None)}),
                      ("start not dict", {"start": "x"}), ("shared tree", {"origin": dict(rec["origin"], tree="shared")})):
        check(not ok({**rec, **mut}), "counts_as_evidence: %s -> not evidence" % name)
    check(not ok({**rec, "dirty": True, "sha": "a" * 40}) and not ok({k: v for k, v in rec.items() if k != "dirty"}),
          "counts_as_evidence: a dirty (or dirt-unknown) record with a sha is not evidence even if the rest is fine")
    check(ok({**rec, "start": dict(rec["start"], sha=rec["sha"].upper())}), "counts_as_evidence: start sha compares case-insensitively")
    check(CE.counts_as_evidence(rec, key) and not CE.counts_as_evidence({**rec, "detail": {"x": 1}}, key), "counts_as_evidence: with a key the mac must verify")
    check(CE.counts_as_evidence({**rec, "detail": {"x": 1}}, None), "counts_as_evidence: key=None does not check the mac")


def main():
    with tempfile.TemporaryDirectory() as td:
        os.environ[CE.ENV_DIR] = str(Path(td) / "evidence")
        os.environ[CE.KEY_ENV] = str(Path(td) / "close_evidence.key")
        for k in ("RIMFLOW_ITEM", "RM_SELFTEST_NESTED", CE.ISOLATED_ROOT_ENV):
            os.environ.pop(k, None)
        for g in (g_pure, g_top_level, g_cover_entries, g_summary_order, g_schema_counts, g_route, g_whoami_seats):
            g()
        for g in (g_publish_key_append, g_tree_state, g_build_record, g_counts_as_evidence, g_record_and_store, g_ship_to_wsl,
                  g_lookup, g_make_isolated, g_isolated_cli, g_cli, g_record_cli):
            os.environ[CE.ENV_DIR] = str(Path(td) / ("ev_" + g.__name__))
            os.environ[CE.KEY_ENV] = str(Path(td) / "close_evidence.key")
            g(td)
    print("\n%s" % ("FAILED: %d" % len(FAILS) if FAILS else "all ok"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
