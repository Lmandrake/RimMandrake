#!/usr/bin/env python3
"""selftest: a script that is run by its path keeps mode 100755 in git (design/specs/2026-11-26-exec-bits-kept/boundary.md).
A unit whose ExecStart script lost the bit fails with 203/EXEC and nothing else turns red (66512f784d dropped it on
findings_judge.sh; the 2026-11-26 daily findings judge never started)."""
import os
import re
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))

# Scripts that a caller outside a unit runs by path: path -> the caller.
DIRECT = {
    "infrastructure/stevedesktop/claude_session.sh": "SteveDesktop desktop shortcuts (kit/shortcuts.ps1) and verify_from_archmagi.sh test -x",
    "publish": "every seat and helper: ./publish",
    "pipe": "./pipe",
    "game": "./game",
    "bridge": "./bridge",
    "mirror": "./mirror",
}

EXEC_RE = re.compile(r"^\s*Exec[A-Za-z]*=\s*[-@:+!]*(\S+)")
CLONE_RE = re.compile(r"^(?:/home/[^/]+|%h)/rm/[^/]+/(.+)$")

BAD = []


def check(name, ok, got=""):
    print("%s %s%s" % ("PASS" if ok else "FAIL", name, "" if ok else "  got: %s" % (got,)))
    if not ok:
        BAD.append(name)


def run_targets(text):
    """The repo paths that this unit text runs directly (the first word of each Exec*= line)."""
    out = []
    for line in text.splitlines():
        m = EXEC_RE.match(line)
        if m:
            c = CLONE_RE.match(m.group(1))
            if c:
                out.append(c.group(1))
    return out


def git(*args):
    return subprocess.run(["git", "-C", ROOT] + list(args), capture_output=True, text=True, check=True).stdout


def tree_targets():
    units = [p for p in git("ls-files", "-z").split("\0")
             if p.endswith(".service") or (".service.d/" in p and p.endswith(".conf"))]
    found = {}
    for u in units:
        try:
            with open(os.path.join(ROOT, u), encoding="utf-8", errors="replace") as f:
                for t in run_targets(f.read()):
                    found.setdefault(t, u)
        except OSError:
            continue
    return found


REV = []       # --rev <commit>: read the modes of that commit's tree, not the index (replays a past instance)


def modes(paths):
    out = {}
    cmd = ("ls-tree", REV[0], "--") if REV else ("ls-files", "-s", "--")
    for line in git(*cmd, *paths).splitlines():
        meta, path = line.split("\t", 1)
        out[path] = meta.split()[0]
    return out


def t_units_name_their_scripts():
    unit = ("[Service]\nExecStart=/home/mandrake/rm/bench/src/x/a.sh --flag\nExecStartPre=-%h/rm/runner/b.sh\n"
            "ExecStart=/usr/bin/python3 /home/mandrake/rm/bench/c.py\n")
    got = run_targets(unit)
    check("units_name_their_scripts", got == ["src/x/a.sh", "b.sh"], got)


def t_tree_finds_the_judge():
    found = tree_targets()
    check("tree_finds_the_judge", "src/RimMandrake/Utils/findings_judge.sh" in found, sorted(found))


def t_run_scripts_keep_exec_bit():
    want = dict(tree_targets())
    want.update(DIRECT)
    m = modes(sorted(want))
    lost = ["%s (mode %s; run by %s)" % (p, m.get(p, "untracked"), want[p]) for p in sorted(want) if m.get(p) != "100755"]
    check("run_scripts_keep_exec_bit", not lost, "; ".join(lost))


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if argv[:1] == ["--rev"] and len(argv) == 2:
        REV.append(argv[1])
    elif argv:
        print("usage: selftest_exec_bits.py [--rev <commit>]")
        return 2
    t_units_name_their_scripts()
    t_tree_finds_the_judge()
    t_run_scripts_keep_exec_bit()
    print("%s selftest_exec_bits: %d checks, %d failed" % ("FAIL" if BAD else "PASS", 3, len(BAD)))
    return 1 if BAD else 0


if __name__ == "__main__":
    sys.exit(main())
