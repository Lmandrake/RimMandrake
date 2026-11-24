#!/usr/bin/env python3
"""launch_permissions.py - every way a Claude session is launched skips permissions: read each launch specification.

Owner, 2026-11-20: "Please ensure all Claude sessions everywhere have dangerously skip permissions in their launch
specifications from now on." Item RIMMANDRAKE_SKIP_PERMISSIONS_EVERYWHERE_AUTO_MODE_BLOCKED_HIM; page
design/specs/2026-11-23-launch-permissions/boundary.md.

    launch_permissions.py repo [--root DIR]     the specifications in this tree (the selftest's door)
    launch_permissions.py live [--reading FILE] the same, and this machine's and SteveDesktop's installed ones and running sessions

Verdicts: SKIPS (the flag) · WALLED (headless, a closed --tools list: a blind judge; it can show no prompt) ·
NOT A SESSION (auth, update, /usage) · EXCEPTION (named below with its reason) · LACKS · COULD NOT LOOK.
Exit: 0 every one looked at and none lacks it · 1 one lacks it · 3 one could not be looked at (and none lacks it).
"""
import argparse
import ast
import base64
import glob
import json
import os
import re
import subprocess
import sys
import time
import warnings

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
FLAG = "--dangerously-skip-permissions"
MODE = "bypassPermissions"
SKIPS, WALLED, NOSESSION, EXCEPTION, LACKS, BLIND = (
    "SKIPS", "WALLED", "NOT A SESSION", "EXCEPTION", "LACKS", "COULD NOT LOOK")
READING = "/mnt/d/ClaudeWork/rimmandrake/ops_watch/launch_permissions.json"
STEVE = "stevedesktop-wsl"

# A launch that keeps its own rule, with the reason. An entry that no longer matches a launch is itself a fault.
EXCEPTIONS = {
    "src/RimMandrake/Oracle/Source/Kernel/OracleKernel.cs":
        "the shipped game's own call on a player's machine: a player's CLI is never told to skip permissions",
    "src/RimMandrake/Utils/claude_bounded.sh":
        "passes its caller's arguments through and adds the flag itself when the caller gave none (skip_args)",
}
# A file that names the Claude program and launches no session, with the reason.
NO_LAUNCH = {
    "src/RimMandrake/Utils/launch_permissions.py": "this reader",
    "src/RimMandrake/Utils/agent_runner.py": "runs Codex, not Claude",
    "infrastructure/stevedesktop/bootstrap_wsl.sh": "installs and updates the program, and writes the settings default",
    "infrastructure/stevedesktop/claude_account.sh": "reads the login (auth status)",
}

SKIP_DIRS = ("design/", "conversations/", "Transient/", "infrastructure/state/", "infrastructure/output/", "observed/",
             "skills/", ".git/")
TESTY = re.compile(r"(^|/)(selftest_[^/]*|[^/]*_accept\.py|case_[^/]*|replay_[^/]*|[^/]*_mutants\.py)$|/(acceptance|tests)/")
CLAUDEISH = re.compile(r"^(CLAUDE(_?BIN|_EXE)?|BOUNDED|SHARED_BOUNDED|claude_?(bin|exe)?)$", re.I)
PROGRAM = re.compile(r"(^|/)(claude|claude\.exe|claude_bounded\.sh)$")
START = {"-p", "--print", "--bg", "--resume", "-r", "-c", "--continue", "remote-control", "--remote-control", FLAG,
         "--permission-mode", "--name"}
NOT_SESSION = {"auth", "update", "mcp", "doctor", "--version", "setup-token", "/usage", "install", "plugin"}
# a command, not a sentence about one: `claude -p timed out` is prose, `claude -p --model opus` and `claude -p "<brief>"` run
PROG_RX = (r"(?:(?:%s|\{(?:script|bounded|claude|exe)\}|(?:[~\w./${}\\-]*/)?claude_bounded\.sh)[\"']?\s+"
           r"(?=-p\s+(?:--[a-z]|[\"'$<\\{%])|--[a-z]|remote-control\s+--)"
           r"|(?:[~\w./${}\\-]*/)?claude(?:\.exe)?[\"']?\s+"
           r"(?=-p\s+(?:--[a-z]|[\"'$<\\{%])|--(?:dangerously|bg|resume|continue|name|permission|remote)|remote-control\s+--)"
           r"|^[ \t]*remote-control\s+(?=--))")
STRING_RX = re.compile(r"(?<![\w-])" + PROG_RX)


def text_verdict(t):
    """A command line as text -> its verdict."""
    if FLAG in t or re.search(r"--permission-mode[= ]+[\"']?" + MODE, t):
        return SKIPS
    if re.search(r"(?<!\w)--tools\b", t):
        return WALLED
    if re.search(r"claude[\"']?\s+(--version|--help|auth|update)\b|(?<!\S)/usage\b", t):
        return NOSESSION
    return LACKS


# ---------------------------------------------------------------- python
class Py:
    def __init__(self, src, path, loader=None):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self.tree, self.path, self.loader = ast.parse(src), path, loader
        self.parent, self.nodes, self.binds, self.docs, self.imports, self.defs = {}, [], {}, set(), {}, {}
        todo = [self.tree]      # one walk; everything below reads self.nodes
        while todo:
            n = todo.pop()
            self.nodes.append(n)
            for c in ast.iter_child_nodes(n):
                self.parent[c] = n
                todo.append(c)
        for n in self.nodes:
            if isinstance(n, ast.Assign):
                for t in n.targets:
                    if isinstance(t, ast.Name):
                        self.binds.setdefault((id(self.scope(n)), t.id), []).append(n)
            elif isinstance(n, ast.Expr):
                if isinstance(n.value, ast.Constant) and isinstance(n.value.value, str):
                    self.docs.add(n.value)
            elif isinstance(n, ast.Import):
                for x in n.names:
                    self.imports[x.asname or x.name] = x.name
            elif isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self.defs[n.name] = n
        for got in self.binds.values():
            got.sort(key=lambda g: g.lineno)

    def up(self, n, kinds):
        while n in self.parent:
            n = self.parent[n]
            if isinstance(n, kinds):
                return n
        return None

    def scope(self, n):
        return self.up(n, (ast.FunctionDef, ast.AsyncFunctionDef)) or self.tree

    def line(self, n):
        """The first line of the statement `n` is in: a name in it holds what an EARLIER statement bound."""
        st = n if isinstance(n, ast.stmt) else self.up(n, ast.stmt)
        return st.lineno if st is not None else None

    def assigned(self, name, scope, before=None):
        """The values bound to `name` in `scope` (its newest one before `before`), else at module level."""
        for sc in (scope, self.tree):
            got = self.binds.get((id(sc), name), [])
            if before is not None and sc is scope:
                got = [g for g in got if g.lineno < before] or got
            if got:
                return [got[-1].value]
        return []

    def is_claude(self, n, scope, depth=0):
        if isinstance(n, ast.Constant):
            return isinstance(n.value, str) and bool(PROGRAM.search(n.value))
        if isinstance(n, ast.Attribute):
            return bool(CLAUDEISH.match(n.attr))
        if isinstance(n, ast.Name):
            if CLAUDEISH.match(n.id):
                return True
            return depth < 3 and any(self.mentions(v) for v in self.assigned(n.id, scope))
        return isinstance(n, (ast.Call, ast.BoolOp)) and self.mentions(n)

    @staticmethod
    def mentions(v):
        """An expression that locates the program: a constant path to it, or one of its names."""
        if isinstance(v, (ast.List, ast.Tuple, ast.Dict)):
            return False
        return any((isinstance(c, ast.Constant) and isinstance(c.value, str) and PROGRAM.search(c.value))
                   or (isinstance(c, ast.Name) and CLAUDEISH.match(c.id)) for c in ast.walk(v))

    def verdict(self, e, scope, depth=0):
        """What an argv expression is sure to carry: SKIPS, WALLED, NOT A SESSION or None (nothing sure)."""
        if depth > 8 or e is None:
            return None
        if isinstance(e, (ast.List, ast.Tuple)):
            vals = [x.value if isinstance(x, ast.Constant) else None for x in e.elts]
            if FLAG in vals or any(a == "--permission-mode" and b == MODE for a, b in zip(vals, vals[1:])):
                return SKIPS
            if "--tools" in vals:
                return WALLED
            if any(v in NOT_SESSION for v in vals if isinstance(v, str)):
                return NOSESSION
            for x in e.elts:
                if isinstance(x, ast.Starred):
                    v = self.verdict(x.value, scope, depth + 1)
                    if v:
                        return v
            return None
        if isinstance(e, ast.BinOp) and isinstance(e.op, ast.Add):
            return self.best(self.verdict(e.left, scope, depth + 1), self.verdict(e.right, scope, depth + 1))
        if isinstance(e, ast.IfExp):
            a, b = self.verdict(e.body, scope, depth + 1), self.verdict(e.orelse, scope, depth + 1)
            return (a if a == b else WALLED) if a and b else None
        if isinstance(e, ast.Name):
            vs = self.assigned(e.id, scope, self.line(e))
            return self.verdict(vs[0], scope if scope is not self.tree else self.tree, depth + 1) if vs else None
        if isinstance(e, ast.Subscript) and isinstance(e.slice, ast.Slice) and isinstance(e.slice.lower, ast.Constant) \
                and e.slice.upper is None and isinstance(e.value, ast.Name):
            vs = self.assigned(e.value.id, scope, self.line(e))
            if vs and isinstance(vs[0], ast.List):
                return self.verdict(ast.List(elts=vs[0].elts[e.slice.lower.value:]), scope, depth + 1)
        if isinstance(e, ast.Call):
            f = e.func
            if isinstance(f, ast.Name) and f.id in ("list", "tuple") and e.args:
                return self.verdict(e.args[0], scope, depth + 1)
            mod, name = self, f.id if isinstance(f, ast.Name) else f.attr if isinstance(f, ast.Attribute) else None
            if isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name) and f.value.id in self.imports:
                mod = self.loader(self.imports[f.value.id], self.path) if self.loader else None
            d = mod and mod.defs.get(name)
            if not d:
                return None
            got = [mod.verdict(r.value, d, depth + 1) for r in ast.walk(d)
                   if isinstance(r, ast.Return) and mod.scope(r) is d]
            return None if not got or not all(got) else got[0] if len(set(got)) == 1 else WALLED
        return None

    @staticmethod
    def best(a, b):
        for v in (SKIPS, WALLED, NOSESSION):
            if v in (a, b):
                return v
        return None

    def consts(self, e, scope, depth=0):
        out = set()
        for c in ast.walk(e):
            if isinstance(c, ast.Constant) and isinstance(c.value, str):
                out.add(c.value)
            elif isinstance(c, ast.Name) and depth < 2 and isinstance(self.parent.get(c), (ast.BinOp, ast.Starred)):
                for v in self.assigned(c.id, scope):
                    if isinstance(v, (ast.List, ast.BinOp)):
                        out |= self.consts(v, scope, depth + 1)
        return out

    def sites(self):
        """-> [(line, verdict, what)]"""
        out = []
        for n in self.nodes:
            if not isinstance(n, ast.List) or not n.elts:
                continue
            sc = self.scope(n)
            if not any(self.is_claude(x, sc) for x in n.elts[:1]):
                continue
            whole = n
            while isinstance(self.parent.get(whole), ast.BinOp) and isinstance(self.parent[whole].op, ast.Add):
                whole = self.parent[whole]
            cs = self.consts(whole, sc)
            if not cs & (START | NOT_SESSION):
                continue
            v = self.verdict(whole, sc)
            tgt = self.parent.get(whole)
            if isinstance(tgt, ast.Assign) and isinstance(tgt.targets[0], ast.Name):
                for g in ast.walk(sc):      # an unconditional `cmd += ...` in the same block
                    if isinstance(g, ast.AugAssign) and isinstance(g.target, ast.Name) and g.lineno > tgt.lineno and \
                            g.target.id == tgt.targets[0].id and self.parent.get(g) is self.parent.get(tgt):
                        v = self.best(v, self.verdict(g.value, sc))
            out.append((n.lineno, v or LACKS, "argv"))
        for n in self.nodes:
            if not (isinstance(n, ast.Constant) and isinstance(n.value, str)) or n in self.docs:
                continue
            for m in STRING_RX.finditer(n.value):
                if m.group(0).lstrip().startswith("%s"):
                    p = self.parent.get(n)
                    if not (isinstance(p, ast.BinOp) and isinstance(p.op, ast.Mod) and any(
                            isinstance(c, ast.Name) and self.is_claude(c, self.scope(n)) for c in ast.walk(p.right))):
                        continue
                cmd = re.split(r"[`\n;]", n.value[m.start():])[0]
                out.append((n.lineno, text_verdict(cmd), "command text"))
        return out


# ---------------------------------------------------------------- shell, PowerShell, unit files, JSON, C#
def shell_sites(src, unit=False):
    src = re.sub(r"(?s)<#.*?#>", lambda m: "\n" * m.group(0).count("\n"), src)     # a PowerShell comment block
    joined = re.sub(r"[\\`]\n\s*", " ", src)
    names = set(re.findall(r"(?m)^\s*(?:export\s+)?\$?(\w+)\s*=\s*[^\n]*?(?:/claude|claude_bounded\.sh|-v claude\b|=claude)\b",
                           joined))
    names |= set(re.findall(r"\|\|\s*(\w+)=claude\b", joined))
    var = "|".join(r"\$\{?%s\}?" % re.escape(v) for v in sorted(names)) or r"(?!x)x"
    rx = re.compile(r"(?:(?<![\w/.-])[\"']?(?:%s)|(?<![\w.-])(?:[~\w./$\\-]*/)?claude(?:_bounded\.sh|\.exe)?)[\"']?\s+"
                    r"(?=-p\b|--(?!version|help)[a-z]|remote-control\b|\"\$@\")" % var)
    out = []
    for i, ln in enumerate(joined.splitlines(), 1):
        if ln.lstrip().startswith(("#", "echo ", "::", "rem ")) or (unit and not re.match(r"\s*Exec\w*=", ln)):
            continue
        for m in rx.finditer(ln):
            out.append((i, text_verdict(ln[m.start():]), "command line"))
    return out


def json_sites(src):
    out = []

    def walk(x):
        if isinstance(x, list):
            if x and all(isinstance(y, str) for y in x) and PROGRAM.search(x[0]) and set(x) & START:
                v = Py(repr(x), "json").verdict(ast.parse(repr(x), mode="eval").body, None)
                out.append((0, v or LACKS, "argv"))
            for y in x:
                walk(y)
        elif isinstance(x, dict):
            for y in x.values():
                walk(y)
        elif isinstance(x, str) and re.match(r"\S*claude(_bounded\.sh)?\s+(-p\b|--|remote-control)", x):
            out.append((0, text_verdict(x), "command text"))
    walk(json.loads(src))
    return out


def cs_sites(src):
    return [(src[:m.start()].count("\n") + 1, text_verdict(m.group(0)), "C# argument text")
            for m in re.finditer(r"\"-p --[^\"]*\"", src)]


NAMES_PROGRAM = re.compile(r"which\([\"']claude[\"']\)|\.local/bin/claude\b(?!-)|claude_bounded\.sh[\"']|[\"']claude[\"'], *[\"']-")


def code_lines(path, src):
    """The text without comments, for the does-this-file-name-the-program net."""
    if path.endswith(".py"):
        return re.sub(r"(?m)#.*$", "", re.sub(r'(?s)"""(?:.*?)"""', "", src))
    return re.sub(r"(?m)^\s*#.*$", "", src)


def files(root):
    r = subprocess.run(["git", "-C", root, "ls-files", "-z"], capture_output=True, timeout=120)     # hang guard
    if r.returncode != 0:
        raise OSError("git ls-files: " + r.stderr.decode(errors="replace")[:160])
    return [p for p in r.stdout.decode().split("\0") if p]


def wanted(p):
    if p.startswith(SKIP_DIRS) or TESTY.search(p):
        return None
    ext = os.path.splitext(p)[1]
    if ext in (".py", ".cs", ".json"):
        return ext
    if ext in (".sh", ".ps1", ".cmd", ".bat", ".zsh", ".service", ".vbs"):
        return ".sh"
    if not ext and "/" not in p:
        return "?"
    return None


# every form a launch can take names the program by one of these AND carries a starting token; a file with only one of
# the two is not parsed (speed). Read on the raw text: a comment stripper would also strip a brief in a long string.
TOKEN = re.compile(r"[\"' ]-p\b|--bg\b|--resume\b|--print\b|--continue\b|remote-control|--name\b|--dangerously|--permission|\"\$@\"")
MAYBE = re.compile(r"claude[\"']|claude_bounded|claude_bin|claude_exe|CLAUDE\b|claude\s+(?:-|remote)|BOUNDED|\{script\}|\{claude\}"
                   r"|\bclaude\s*[,=]")


def read_one(root, p, kind, loader=None):
    """-> [(line, verdict, what)] for one file; an unreadable file is one COULD NOT LOOK."""
    if not os.path.lexists(os.path.join(root, p)):
        return []       # deleted in this tree: no file, so no launch in it
    try:
        with open(os.path.join(root, p), encoding="utf-8", errors="strict") as f:
            src = f.read()
    except (OSError, UnicodeDecodeError) as e:
        return [(0, BLIND, type(e).__name__)] if kind != "?" else []
    if not MAYBE.search(src) or not (TOKEN.search(src) or NAMES_PROGRAM.search(src)):
        return []
    if kind == "?":
        kind = ".py" if "python" in src[:60] else ".sh" if src.startswith("#!") else None
        if not kind:
            return []
    try:
        got = {".py": lambda: Py(src, p, loader).sites(), ".sh": lambda: shell_sites(src, p.endswith(".service")), ".cs": lambda: cs_sites(src),
               ".json": lambda: json_sites(src)}[kind]()
    except (SyntaxError, ValueError) as e:
        return [(0, BLIND, "%s: %s" % (type(e).__name__, e))] if NAMES_PROGRAM.search(src) else []
    if not got and kind != ".json" and p not in NO_LAUNCH and NAMES_PROGRAM.search(code_lines(p, src)):
        got = [(0, BLIND, "the file names the Claude program and no launch could be read in it")]
    return got


def scan(root=ROOT, paths=None):
    """-> [(path, line, verdict, what)], every launch specification in the tree."""
    cache = {}

    def loader(mod, frm):
        for d in (os.path.dirname(frm), "src/RimMandrake/rimflow", "src/RimMandrake/Utils"):
            p = os.path.join(d, mod + ".py")
            if p in cache:
                return cache[p]
            f = os.path.join(root, p)
            if os.path.exists(f):
                with open(f, encoding="utf-8") as h:
                    cache[p] = Py(h.read(), p, loader)
                return cache[p]
        return None
    rows, used = [], set()
    for p in (files(root) if paths is None else paths):
        kind = wanted(p)
        if not kind:
            continue
        for line, v, what in read_one(root, p, kind, loader):
            if v in (LACKS, BLIND) and p in EXCEPTIONS:
                v, what = EXCEPTION, EXCEPTIONS[p]
                used.add(p)
            rows.append((p, line, v, what))
    if paths is None:
        for p in sorted(set(EXCEPTIONS) - used):
            rows.append((p, 0, LACKS, "a stale exception: no launch here needs it; take it off EXCEPTIONS"))
    return rows


# ---------------------------------------------------------------- what is installed and running
def settings_verdict(text):
    d = json.loads(text)
    if (d.get("permissions") or {}).get("defaultMode") != MODE:
        return LACKS, "permissions.defaultMode is %r" % (d.get("permissions") or {}).get("defaultMode")
    if not d.get("skipDangerousModePermissionPrompt"):
        return LACKS, "skipDangerousModePermissionPrompt is not set: the first start asks"
    return SKIPS, "defaultMode " + MODE
PROBE = r'''
import glob, json, os
out = {"settings": None, "procs": [], "fleet": None, "wt": []}
p = os.path.expanduser("~/.claude/settings.json")
out["settings"] = open(p).read() if os.path.exists(p) else "{}"
for d in glob.glob("/proc/[0-9]*/cmdline"):
    try:
        a = open(d, "rb").read().decode(errors="replace").split("\0")[:-1]
    except OSError:
        continue
    if a and (os.path.basename(a[0]) in ("claude", "claude.exe") or "/claude/versions/" in a[0]):
        out["procs"].append([x[:60] for x in a[:80]])
for f, k in (("/mnt/c/SteveDesktop/claude_fleet.ps1", "fleet"),):
    if os.path.exists(f):
        out[k] = open(f, encoding="utf-8", errors="replace").read()
for f in glob.glob("/mnt/c/Users/*/AppData/Local/Packages/Microsoft.WindowsTerminal_*/LocalState/settings.json"):
    try:
        out["wt"].append([f, open(f, encoding="utf-8-sig").read()])
    except OSError as e:
        out["wt"].append([f, None])
print(json.dumps(out))
'''


def proc_verdict(argv):
    if any(a in ("daemon", "bg-pty-host", "mcp", "auth", "update") for a in argv[1:2]):
        return NOSESSION
    for a, b in zip(argv, argv[1:] + [""]):
        if a == FLAG or (a == "--permission-mode" and b == MODE) or a == "--permission-mode=" + MODE:
            return SKIPS
        if a == "--tools":
            return WALLED
        if a == "/usage":
            return NOSESSION
    return LACKS


def judge_host(host, probe):
    """-> rows for one machine from its probe dict."""
    rows = []
    v, why = settings_verdict(probe["settings"])
    rows.append((host, "~/.claude/settings.json", v, why))
    covered = v == SKIPS
    for a in probe["procs"]:
        pv = proc_verdict(a)
        if pv == LACKS and covered:
            pv, note = SKIPS, "no flag; the settings default covers it"
        else:
            note = "argv"
        rows.append((host, "running: " + " ".join(a)[:110], pv, note))
    if probe.get("fleet") is not None:
        got = [x for x in shell_sites(probe["fleet"]) if x[1] != NOSESSION]
        rows += [(host, "claude_fleet.ps1:%d" % ln, v, w) for ln, v, w in got] or \
            [(host, "claude_fleet.ps1", BLIND, "no launch line could be read in it")]
    for f, text in probe.get("wt") or []:
        if text is None:
            rows.append((host, f, BLIND, "unreadable"))
            continue
        try:
            prof = (json.loads(re.sub(r"(?m)^\s*//.*$", "", text)).get("profiles") or {})
        except ValueError as e:
            rows.append((host, f, BLIND, "not JSON: %s" % e))
            continue
        for p in prof.get("list", []) if isinstance(prof, dict) else prof:
            c = p.get("commandline") or ""
            if STRING_RX.search(c):
                rows.append((host, "Terminal profile %s" % p.get("name"), text_verdict(c), "commandline"))
    return rows


# budget: danger=a hung probe (ssh to another machine) holds the permission check; never reached in the 14 days to 2026-11-24;
# budget: no record of its run
def run_probe(host, ssh=None, timeout=60):
    argv = ["python3", "-c", PROBE] if not ssh else [
        "ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=15", ssh,
        "echo %s | base64 -d | python3 -" % base64.b64encode(PROBE.encode()).decode()]
    r = subprocess.run(argv, capture_output=True, text=True, timeout=timeout)       # hang guard
    if r.returncode != 0:
        raise OSError("exit %d: %s" % (r.returncode, (r.stderr or r.stdout).strip()[-160:]))
    return json.loads(r.stdout.strip().splitlines()[-1])


def live(hosts=(("Archmagi", None), ("SteveDesktop", STEVE)), probe=run_probe):
    rows = []
    for host, ssh in hosts:
        try:
            rows += judge_host(host, probe(host, ssh))
        except (OSError, ValueError, KeyError, IndexError, subprocess.SubprocessError) as e:
            rows.append((host, "the whole machine", BLIND, "%s: %s" % (type(e).__name__, str(e)[:160])))
    rows.append(("Archmagi, SteveDesktop", "claude.exe on the Windows side", "NOT CHECKED", "the probe reads WSL processes only"))
    for mac in ("Mac Desktop (mt-515497)", "Mac Laptop (mt-400028)"):
        rows.append((mac, "the whole machine", "NOT CHECKED", "no route from Archmagi; Lodestar's shell/claude.zsh adds the flag there"))
    return rows


def code(verdicts):
    return 1 if LACKS in verdicts else 3 if BLIND in verdicts else 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("cmd", choices=("repo", "live"))
    ap.add_argument("--root", default=ROOT)
    ap.add_argument("--reading", default=None, help="live: write the reading here, only when every machine was looked at")
    ap.add_argument("--all", action="store_true", help="print the good rows too")
    a = ap.parse_args(argv)
    rows = [("%s:%s" % (p, ln), "", v, w) for p, ln, v, w in scan(a.root)]
    if a.cmd == "live":     # the tree this runs from is a launch specification too: one not caught at ./publish is, here
        rows += live()
    vs = [r[2] for r in rows]
    for r in rows:
        if a.all or r[2] in (LACKS, BLIND, "NOT CHECKED"):
            print("%-14s %s %s  (%s)" % (r[2], r[0], r[1], r[3]))
    rc = code(vs)
    print("%s: %s" % ({0: "OK", 1: "LACKS", 3: "COULD NOT LOOK"}[rc],
                      ", ".join("%d %s" % (vs.count(v), v) for v in sorted(set(vs)))))
    if a.cmd == "live":
        path = a.reading or READING
        if rc:      # the promised reading moves only on a whole clean look; a failed one is kept beside it
            path = path[:-5] + "_failed.json"
        with open(path + ".tmp", "w", encoding="utf-8") as f:
            json.dump({"at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "rc": rc, "rows": rows}, f, indent=1)
        os.replace(path + ".tmp", path)
    return rc


if __name__ == "__main__":
    sys.exit(main())
