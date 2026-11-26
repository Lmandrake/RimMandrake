#!/usr/bin/env python3
"""selftest_codebase_now.py — one test per promise on design/specs/2026-11-19-codebase-now/boundary.md.

Every test builds a throwaway git repo in a temp dir and points codebase_now at it; nothing here reads or writes
this repo's own review record or the real page on D:\\.

    python3 src/RimMandrake/Utils/selftest_codebase_now.py      exit 0 all pass, 1 a test failed
"""
import hashlib
from html import unescape as html_unescape
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import codebase_now as CN  # noqa: E402

NOW = 1795000000.0  # a pinned clock, so ages are exact


def _sh(root, *args):
    subprocess.run(["git", *args], cwd=root, check=True, capture_output=True)


def _write(root, rel, text):
    p = os.path.join(root, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(text)


def _mark(root, rel, verdict="clean", text=None):
    """One record line in the review shard, as code_review_status writes it."""
    with open(os.path.join(root, rel), "rb") as f:
        h = hashlib.sha256(f.read() if text is None else text.encode()).hexdigest()
    rec = {"path": rel, "ts": "2026-11-19T00:00:00Z", "seat": "BENCH", "sha": "abc", "date": "2026-11-19",
           "sha256": h, "cleanCount": 1, "verdict": verdict}
    d = os.path.join(root, "infrastructure", "state", "code_review")
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "BENCH.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")


def repo(fetch_age=60.0):
    """A small repo: a clean, an edited, a reopened, a never-read file, plus excluded trees and a non-code file."""
    root = tempfile.mkdtemp(prefix="cbnow_")
    _sh(root, "init", "-q", "-b", "main")
    _write(root, "src/a.py", "a = 1\nb = 2\n")
    _write(root, "src/b.py", "x = 1\n")
    _write(root, "src/c.py", "c = 1\n")
    _write(root, "src/d.py", "d = 1\ne = 2\nf = 3\n")
    _write(root, "whittle/w1.py", "w = 1\n")
    _write(root, "whittle/w2.py", "w = 2\n")
    _write(root, "infrastructure/whittle_claude/k.sh", "echo\n")
    _write(root, "vendor/v.js", "v\n")
    _write(root, "README.md", "not code\n")
    _mark(root, "src/a.py")
    _mark(root, "src/b.py")
    _write(root, "src/b.py", "x = 2\n")            # edited since its mark
    _mark(root, "src/c.py")
    _mark(root, "src/c.py", verdict="dirty")        # reopened
    _sh(root, "add", "-A")
    _sh(root, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "seed")
    fh = os.path.join(root, ".git", "FETCH_HEAD")
    open(fh, "w").close()
    if fetch_age is not None:
        os.utime(fh, (NOW - fetch_age, NOW - fetch_age))
    else:
        os.remove(fh)
    return root


def build(root, out=None, **kw):
    out = out or tempfile.mkdtemp(prefix="cbnow_out_")
    kw.setdefault("runner", lambda tests: (0, "ok"))
    rc, facts = CN.build(root=root, out=out, now=NOW, **kw)
    return rc, facts, out


def page(out):
    with open(os.path.join(out, CN.PAGE_NAME), encoding="utf-8") as f:
        return f.read()


def by_path(facts):
    return {f["path"]: f for f in facts["files"]}


# ---- the promises ---------------------------------------------------------------------------------------------------

def t_every_file_has_one_state():
    rc, facts, out = build(repo())
    assert rc == 0, rc
    files = by_path(facts)
    assert set(files) == {"src/a.py", "src/b.py", "src/c.py", "src/d.py"}, sorted(files)
    for f in files.values():
        assert f["state"] in CN.STATES, f
    tot = facts["totals"]
    assert sum(tot[s]["files"] for s in CN.STATES) == tot["all"]["files"] == 4, tot
    assert sum(tot[s]["lines"] for s in CN.STATES) == tot["all"]["lines"] == 2 + 1 + 1 + 3, tot
    html = page(out)
    assert "4 files" in html and "7 lines" in html, "totals not on the page"


def t_read_clean_is_hash_equal():
    rc, facts, _ = build(repo())
    files = by_path(facts)
    assert files["src/a.py"]["state"] == "read-clean", files["src/a.py"]
    assert files["src/b.py"]["state"] == "dirty", files["src/b.py"]
    assert files["src/c.py"]["state"] == "dirty", files["src/c.py"]
    assert files["src/d.py"]["state"] == "never-read", files["src/d.py"]


def t_unreadable_file_is_unmeasured():
    root = repo()
    p = os.path.join(root, "src", "a.py")
    os.chmod(p, 0)
    try:
        if os.access(p, os.R_OK):
            raise AssertionError("UNMEASURED: running as a user who can read mode-000 files; this test cannot look")
        rc, facts, _ = build(root)
    finally:
        os.chmod(p, 0o644)
    f = by_path(facts)["src/a.py"]
    assert f["state"] == "unmeasured", f


def t_evidence_trees_excluded_and_said():
    rc, facts, out = build(repo())
    assert not any(p.startswith(("whittle/", "infrastructure/whittle_claude/", "vendor/")) for p in by_path(facts))
    ex = {e["tree"]: e["files"] for e in facts["excluded"]}
    assert ex.get("whittle/") == 2 and ex.get("infrastructure/whittle_claude/") == 1 and ex.get("vendor/") == 1, ex
    html = page(out)
    assert "whittle/" in html and "infrastructure/whittle_claude/" in html, "excluded trees not named on the page"


def t_flagged_unmeasured_without_source():
    rc, facts, out = build(repo())
    assert facts["flagged"]["state"] == "UNMEASURED" and facts["flagged"]["cause"], facts["flagged"]
    assert not any(f.get("flagged") for f in facts["files"])
    html = page(out)
    assert re.search(r"FLAGGED[^<]*</b>[^<]*UNMEASURED", html), "the FLAGGED legend does not read UNMEASURED"


def _with_page(root, test_exit=0):
    _write(root, "design/specs/x/boundary.md",
           "# BOUNDARY x\n\nCode: `src/a.py` and `src/d.py`.\n\n## PROMISES\n\n- **does-x.** It does x.\n")
    _write(root, "tests_x.py", "import sys\ndef t_does_x():\n    pass\ndef main():\n    t_does_x()\n"
                               "    sys.exit(%d)\nmain()\n" % test_exit)
    return {"design/specs/x/boundary.md": "tests_x.py"}


def t_page_state_where_a_page_names_it():
    root = repo()
    pages = _with_page(root)
    rc, facts, out = build(root, pages=pages)
    files = by_path(facts)
    assert files["src/a.py"]["page_state"] == "CLEAN", files["src/a.py"]
    assert files["src/d.py"]["page_state"] == "CLEAN", files["src/d.py"]
    assert files["src/b.py"]["page_state"] is None, files["src/b.py"]
    html = page(out)
    assert html.count('class="ring-clean"') >= 2 and "ring-dirty\"" not in html.split("<svg", 1)[1].split(
        "</svg>", 1)[0], "rings do not match the page states"
    rc, facts, _ = build(root, pages=pages, runner=lambda tests: (1, "a test failed"))
    assert by_path(facts)["src/a.py"]["page_state"] == "DIRTY", by_path(facts)["src/a.py"]


def t_tests_cache_reused_only_when_unchanged():
    root = repo()
    pages = _with_page(root)
    out = tempfile.mkdtemp(prefix="cbnow_out_")
    calls = []

    def runner(tests):
        calls.append(tests)
        return 0, "ok"
    build(root, out=out, pages=pages, runner=runner)
    build(root, out=out, pages=pages, runner=runner)
    assert len(calls) == 1, "unchanged inputs ran the tests again: %r" % calls
    _write(root, "src/d.py", "d = 9\n")             # a file the page names
    build(root, out=out, pages=pages, runner=runner)
    assert len(calls) == 2, "a changed named file reused the cache: %r" % calls
    cp = os.path.join(out, CN.CACHE_NAME)
    with open(cp) as f:
        cache = json.load(f)
    cache["tests_x.py"]["at"] = NOW - 25 * 3600       # the same inputs, verdict 25 h old
    with open(cp, "w") as f:
        json.dump(cache, f)
    build(root, out=out, pages=pages, runner=runner)
    assert len(calls) == 3, "a cached verdict older than 24 h was reused: %r" % calls
    build(root, out=out, pages=pages, runner=runner)
    assert len(calls) == 3, "a fresh verdict was not reused: %r" % calls
    html = page(out)
    assert "tests verdict" in html and "old" in html, "the page does not say how old the tests verdict is"


def t_could_not_look_says_unmeasured():
    notgit = tempfile.mkdtemp(prefix="cbnow_notgit_")
    rc, facts, out = build(notgit)
    assert rc == 3, rc
    assert facts["totals"] is None and facts["files"] == [] and facts["causes"], facts
    html = page(out)
    assert "UNMEASURED" in html and 'class="s-read-clean"' not in html.split("<svg", 1)[-1]
    assert not re.search(r">\s*0 files", html), "a could-not-look page shows 0"
    root = repo()
    with open(os.path.join(root, "infrastructure", "state", "code_review", "BENCH.jsonl"), "a") as f:
        f.write("{not json\n")
    rc, facts, out = build(root)
    assert rc == 3 and facts["totals"] is None and facts["causes"], (rc, facts["causes"])
    assert "UNMEASURED" in page(out)


def t_stale_clone_says_unmeasured():
    for age in (2 * 3600.0, None):
        rc, facts, out = build(repo(fetch_age=age))
        assert rc == 3, (age, rc)
        assert facts["totals"] is None and any("fetch" in c for c in facts["causes"]), facts["causes"]
        assert "UNMEASURED" in page(out)


def _node():
    for c in (shutil.which("node"), os.path.expanduser("~/.local/bin/node")):
        if c and os.path.exists(c):
            return c
    raise AssertionError("UNMEASURED: no node binary, so the page's stale script cannot be run")


def t_stale_page_says_so():
    rc, facts, out = build(repo())
    html = page(out)
    m = re.search(r"<script>(.*?)</script>", html, re.S)
    assert m, "the page has no stale script"
    stub = """
const els = {stale: {hidden: true, textContent: ''}};
const totals = [{textContent: '4 files'}, {textContent: '7 lines'}];
global.document = {body: {dataset: {built: '%s'}}, getElementById: id => els[id],
  querySelectorAll: q => q === '.total' ? totals : []};
""" % facts["built"]
    for now_s, want_stale in ((facts["built"] + 1800, False), (facts["built"] + 3 * 3600, True)):
        js = stub + "Date.now = () => %d;\n" % (now_s * 1000) + m.group(1) + \
            "\nconsole.log(JSON.stringify({hidden: els.stale.hidden, t: totals.map(x => x.textContent)}));"
        r = subprocess.run([_node(), "-e", js], capture_output=True, text=True, timeout=30)
        assert r.returncode == 0, r.stderr
        got = json.loads(r.stdout.strip().splitlines()[-1])
        if want_stale:
            assert got["hidden"] is False and all(t == "UNMEASURED" for t in got["t"]), got
        else:
            assert got["hidden"] is True and got["t"] == ["4 files", "7 lines"], got


def t_whole_page_or_none():
    out = tempfile.mkdtemp(prefix="cbnow_out_")
    target = os.path.join(out, CN.PAGE_NAME)
    seen = []
    real = os.replace

    def spy(src, dst):
        if os.path.abspath(dst) == target:
            seen.append(os.path.exists(dst))
            with open(src, encoding="utf-8") as f:
                assert f.read().rstrip().endswith("</html>"), "renamed a partial page"
        return real(src, dst)
    os.replace = spy
    try:
        build(repo(), out=out)
    finally:
        os.replace = real
    assert seen == [False], "the page was not written through one rename: %r" % seen
    assert not [n for n in os.listdir(out) if n.endswith(".tmp")], os.listdir(out)


def t_no_network_no_model():
    rc, facts, out = build(repo())
    html = page(out)
    assert not re.search(r"""(src|href)\s*=\s*["']?(https?:)?//""", html), "the page loads from the network"
    with open(os.path.join(HERE, "codebase_now.py"), encoding="utf-8") as f:
        src = f.read()
    for bad in ("anthropic", "openai", "urllib.request", "requests", "http.client", "claude -p", "gpt_consult"):
        assert bad not in src, "codebase_now.py names %s" % bad


def _chrome():
    for c in (os.environ.get("CHROME_EXE"), "/mnt/c/Program Files/Google/Chrome/Application/chrome.exe",
              "/mnt/c/Program Files (x86)/Google/Chrome/Application/chrome.exe"):
        if c and os.path.exists(c):
            return c
    raise AssertionError("UNMEASURED: no Chrome binary, so a click on the treemap cannot be run")


def t_click_a_cell_drills_in():
    """A click on a treemap cell descends one folder; the breadcrumb comes back. Run in real headless Chrome."""
    root = repo()
    _write(root, "src/sub/z1.py", "z = 1\nz = 2\n")
    _write(root, "src/sub/z2.py", "z = 3\n")
    _sh(root, "add", "-A")
    _sh(root, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "deeper")
    rc, facts, out = build(root)
    html = page(out)
    probe = """<script>
var R = [];
function st() { var s = document.querySelector('svg.map');
  return {path: s.getAttribute('data-path'), n: s.querySelectorAll('rect').length}; }
function cell(p) { var r = document.querySelectorAll('svg.map rect[data-p]');
  for (var i = 0; i < r.length; i++) { if (r[i].getAttribute('data-p') === p) { return r[i]; } } return null; }
function click(e) { e.dispatchEvent(new MouseEvent('click', {bubbles: true, cancelable: true})); }
try {
  R.push(st());
  click(cell('src/sub/z1.py')); R.push(st());
  click(cell('src/sub/z1.py')); R.push(st());
  var c = document.querySelector('#crumb a'); click(c); R.push(st());
} catch (e) { R.push({err: String(e)}); }
document.body.insertAdjacentHTML('beforeend', '<pre id="probe">' + JSON.stringify(R) + '</pre>');
</script>"""
    scratch = "/mnt/d/ClaudeWork/rimmandrake/scratch/codebase_now_click"
    os.makedirs(scratch, exist_ok=True)
    target = os.path.join(scratch, "probe.html")
    with open(target, "w", encoding="utf-8") as f:
        f.write(html.replace("</body>", probe + "</body>"))
    win = subprocess.run(["wslpath", "-w", target], capture_output=True, text=True).stdout.strip()
    prof = subprocess.run(["wslpath", "-w", os.path.join(scratch, "profile")], capture_output=True,
                          text=True).stdout.strip()
    r = subprocess.run([_chrome(), "--headless=new", "--disable-gpu", "--no-first-run", "--user-data-dir=" + prof,
                        "--virtual-time-budget=4000", "--dump-dom", "file:///" + win.replace("\\", "/")],
                       capture_output=True, timeout=120)
    dom = r.stdout.decode("utf-8", "replace")
    m = re.search(r'<pre id="probe">(\[.*?)</pre>', dom, re.S)
    assert m, "the probe script did not run in Chrome: %s" % r.stderr.decode("utf-8", "replace")[-300:]
    got = json.loads(html_unescape(m.group(1)))
    assert not any("err" in g for g in got), got
    start, one, two, back = got
    assert start["path"] == "", got
    assert one["path"] == "src" and one["n"] != start["n"], "first click did not drill in: %s" % got
    assert two["path"] == "src/sub" and two["n"] != one["n"], "second click did not drill in: %s" % got
    assert back["path"] == "" and back["n"] == start["n"], "breadcrumb did not come back: %s" % got
    print("  click read %d states: %s" % (len(got), got))


def t_a_mod_file_takes_its_mod_bar_state():
    """A file inside a mod (code_review_status.mod_of) is asked whether or not a boundary page names it, and its ring is
    its mod's bar state. The mod's answer is planted (CRS.mod_page_state has its own tests)."""
    root = repo(fetch_age=None)
    _write(root, "src/RimMandrake/Mod/Source/m.py", "m = 1\n")
    _write(root, "design/concepts/Mod/version/VERSION.json", "{}\n")
    _write(root, "src/RimMandrake/NoConcept/n.py", "n = 1\n")
    _sh(root, "add", "-A")
    _sh(root, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "mod")
    fh = os.path.join(root, ".git", "FETCH_HEAD")
    open(fh, "w").close()
    os.utime(fh, (NOW - 60, NOW - 60))
    asked = []
    real = CN.CRS.mod_page_state
    CN.CRS.mod_page_state = lambda mod, builds=None: (asked.append(mod), (
        "UNREADABLE", "mod %s 0.1.0 locked bars: bars green 1 of 2, UNRUN 1" % mod))[1]
    try:
        rc, facts, out = build(root, pages=_with_page(root))
    finally:
        CN.CRS.mod_page_state = real
    files = by_path(facts)
    m = files["src/RimMandrake/Mod/Source/m.py"]
    assert m["page_state"] == "UNREADABLE" and "bars green 1 of 2" in (m["page_detail"] or ""), m
    assert asked == ["Mod"], asked
    assert files["src/RimMandrake/NoConcept/n.py"]["page_state"] is None, files["src/RimMandrake/NoConcept/n.py"]
    assert files["src/a.py"]["page_state"] == "CLEAN", files["src/a.py"]
    assert 'class="ring-unreadable"' in page(out).split("<svg", 1)[1].split("</svg>", 1)[0], "no ring on the mod file"


def main():
    tests = [t_every_file_has_one_state, t_read_clean_is_hash_equal, t_unreadable_file_is_unmeasured,
             t_evidence_trees_excluded_and_said, t_flagged_unmeasured_without_source,
             t_page_state_where_a_page_names_it, t_tests_cache_reused_only_when_unchanged,
             t_could_not_look_says_unmeasured, t_stale_clone_says_unmeasured, t_stale_page_says_so,
             t_whole_page_or_none, t_no_network_no_model, t_click_a_cell_drills_in, t_a_mod_file_takes_its_mod_bar_state]
    failed = 0
    for t in tests:
        try:
            t()
            print("PASS", t.__name__)
        except Exception as e:  # noqa: BLE001  a test that raised is a failed test, named
            failed += 1
            print("FAIL", t.__name__, "%s: %s" % (type(e).__name__, e))
    print("%d of %d pass" % (len(tests) - failed, len(tests)))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
