#!/usr/bin/env python3
"""proof_restore_check.py — a live proof must undo every def / mod-setting poke on EVERY exit path.

Why (lesson 20261026T161651Z-BENCH-proof-scene-restore-leak): KineticArms and ExplosiveKnockback proof scenes set
kineticStrength=0, enabled=false or added an extension to vanilla Bullet_Revolver, and undid it only inside Verdict.
A Build throw or an INVALID return left the change in the running game, poisoning every later test of the session.
The same shape exists in Python drivers: `t.set_setting(T, {"x": False}) ... t.set_setting(T, {"x": True})` never
runs the second call once a component fails (TestContext._guard turns every later verb into a no-op), and it puts
back a FIXED value instead of what the player had.

What counts as a POKE
  C#   (proof/probe/smoke/playtest files and any file defining a static_call Stage/Verdict pair; offline SelfTest
       programs run in their own process and are skipped): an assignment to a static settings field
       (`XxxSettings.f =`, `Prefs.f =`, `DebugSettings.f =`, `DebugViewSettings.f =`, `settings.f =`),
       `.modExtensions.Add/Insert/Remove/Clear(`, `.comps.Add/Insert/Remove(`, or a field write through a def
       (`fooDef.f =`, `ThingDefOf.X.f =`).
  Py   (every tracked *.py under src/ except selftests): `jawa/mod_settings_field` with action "set" (the mailbox
       field `request` excluded), `rimworld/update_mod_settings`, a proof's static_call `Settings` (reset or
       field=value), and `.set_setting(...)`.
A poke is RESTORED when
  - it sits in a `try` whose `finally` writes the same target back (C#: same field; def lists: a Remove/restore
    runner; Py: any settings write in the finally), or it is followed directly by such a `try` with only plain
    statements between (C#: assignments that cannot throw; Py: nothing);
  - (C#) a restore delegate (`restore = () => ...`, `restore += ...`) naming the same target is registered before it
    in the same case, or right after it with nothing callable between, AND the file runs restore delegates both in a
    `catch` and in a `finally` (the Stage ERROR path and Verdict);
  - (Py) it is a `.set_setting` call and modcheck/suite.py restores every touched setting to its prior value in the
    chain's finally (marker `_restore_touched_settings`);
  - (Py) it is a `jawa/mod_settings_field` set reaching the game through a modcheck TestContext `t` in a suite file,
    and every chain's session records the prior of such writes (marker `_SettingsTrackingSession`); a Settings reset
    there is covered once `t.remember_settings(...)` names its fields first.
A restore that writes a LITERAL (true/false/a number/a default reset) is itself a hit: it must put back the PRIOR value.
A reviewed exception carries `restore-check: ok <why>` on the hit's line or the line above.

Usage:  proof_restore_check.py [--json OUT] [--all] [paths...]
Exit 1 when a hit is not covered by BASELINE (the filed, not-yet-fixed ones), 0 otherwise. `--all` prints filed hits too.
"""
from __future__ import annotations

import argparse
import ast
import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
SUITE = REPO / "src/RimMandrake/Utils/modcheck/suite.py"
SUITE_MARKER = "_restore_touched_settings"
TRACK_MARKER = "_SettingsTrackingSession"

# Filed hits not yet fixed (projects another batch builds). Key: "path::kind::target". Value: (rimflow item id, how many
# hits that key had when filed). A Python target is the write's kind, so one key covers every such write in the file:
# the count is what stops a NEW leak in an already-filed file from hiding behind the key (new_hits).
BASELINE: dict[str, tuple[str, int]] = {
    'src/RimMandrake/FlowWorks/Source/Hose/HoseProbe.cs::unrestored-on-throw::Prefs.DevMode': ('FLOWWORKS_PROOF_POKES_RESTORE_PRIOR', 2),
    'src/RimMandrake/FlowWorks/Source/Pits/Suspension/RM_SuspensionProofs.cs::unrestored-on-throw::DebugSettings.godMode': ('FLOWWORKS_PROOF_POKES_RESTORE_PRIOR', 3),
    'src/RimMandrake/FlowWorks/Source/RM_WaterLookProofs.cs::unrestored-on-throw::RM_WaterLookSettings.deepWaterTintEnabled': ('FLOWWORKS_PROOF_POKES_RESTORE_PRIOR', 1),
    'src/RimMandrake/FlowWorks/Source/RM_WaterLookProofs.cs::unrestored-on-throw::RM_WaterLookSettings.wetWallBandEnabled': ('FLOWWORKS_PROOF_POKES_RESTORE_PRIOR', 1),
    'src/RimMandrake/bridgetools/prove_sea_dive_floor.py::unrestored-on-throw::raw': ('SEA_DIVE_PROOF_RESTORE_PRIOR', 1),
}

# ------------------------------------------------------------------------------------------------------------ C#

CS_NAME = re.compile(r"(Proof|Probe|Smoke|Playtest|SelfTest)", re.I)
CS_STAGE = re.compile(r"public\s+static\s+string\s+(Stage|Verdict)\s*\(")
SETTING_POKE = re.compile(
    r"(?<![\w.])((?:[A-Z]\w*Settings|Prefs|DebugSettings|DebugViewSettings|settings)\.(\w+))\s*(=(?!=)|\+=|-=|\*=|/=|\+\+|--)")
LIST_POKE = re.compile(r"\.(modExtensions|comps)\s*\.\s*(Add|AddRange|Insert|Remove|RemoveAll|Clear)\s*\(")
DEF_POKE = re.compile(r"(?<![\w.])((?:\w+\.)*\w*Def(?:Of\.\w+)?)\.(\w+)\s*=(?!=)")
LITERAL = re.compile(r"^\s*(true|false|null|-?[0-9][0-9_.]*[fFdDmM]?|\"[^\"]*\")\s*$")
RESTORE_REG = re.compile(r"(?:\w+\.)*\w*[Rr]estore\w*\s*(\+=|=)\s*(?:\(\s*\)|\w+)\s*=>")
RESTORE_RUN = re.compile(r"(RunRestore\w*\s*\(|[Rr]estore\w*\s*\?\s*\.\s*Invoke\s*\(|[Rr]estore\w*\s*\.\s*Invoke\s*\(|"
                         r"\b[Rr]estore\w*\s*\(\s*\))")


def strip_cs(src: str) -> str:
    """Comments and string/char literal BODIES blanked to spaces (length and newlines kept), quotes kept."""
    out = list(src)
    i, n = 0, len(src)
    while i < n:
        c = src[i]
        if src.startswith("//", i):
            j = src.find("\n", i)
            j = n if j < 0 else j
            for k in range(i, j):
                out[k] = " "
            i = j
        elif src.startswith("/*", i):
            j = src.find("*/", i + 2)
            j = n if j < 0 else j + 2
            for k in range(i, j):
                if out[k] != "\n":
                    out[k] = " "
            i = j
        elif c == '"' or (c == "@" and i + 1 < n and src[i + 1] == '"') or (c == "$" and i + 1 < n and src[i + 1] == '"'):
            verbatim = c == "@" or (c == "$" and i > 0 and src[i - 1] == "@")
            if c in "@$":
                i += 1
            j = i + 1
            while j < n:
                if verbatim and src[j] == '"' and j + 1 < n and src[j + 1] == '"':
                    j += 2
                    continue
                if not verbatim and src[j] == "\\":
                    j += 2
                    continue
                if src[j] == '"' or (not verbatim and src[j] == "\n"):
                    break
                j += 1
            for k in range(i + 1, min(j, n)):
                if out[k] != "\n":
                    out[k] = " "
            i = j + 1
        elif c == "'":
            j = i + 1
            while j < n and src[j] != "'" and src[j] != "\n":
                j += 2 if src[j] == "\\" else 1
            for k in range(i + 1, min(j, n)):
                out[k] = " "
            i = j + 1
        else:
            i += 1
    return "".join(out)


class CsFile:
    def __init__(self, text: str):
        self.raw = text
        self.s = strip_cs(text)
        self.blocks = []            # (open, close, header)
        stack = []
        for i, ch in enumerate(self.s):
            if ch == "{":
                stack.append(i)
            elif ch == "}" and stack:
                o = stack.pop()
                self.blocks.append((o, i, self.header(o)))
        self.blocks.sort()

    def header(self, o: int) -> str:
        j = o - 1
        while j >= 0 and self.s[j] not in ";{}":
            j -= 1
        return " ".join(self.s[j + 1:o].split())

    def line(self, p: int) -> int:
        return self.s.count("\n", 0, p) + 1

    def enclosing(self, p: int):
        return [b for b in self.blocks if b[0] < p < b[1]]       # outermost first

    def stmt_start(self, p: int) -> int:
        j = p - 1
        while j >= 0 and self.s[j] not in ";{}":
            j -= 1
        return j + 1

    def stmt_end(self, p: int) -> int:
        depth, j = 0, p
        while j < len(self.s):
            ch = self.s[j]
            if ch in "({[":
                depth += 1
            elif ch in ")}]":
                if depth == 0:
                    return j
                depth -= 1
            elif ch == ";" and depth == 0:
                return j
            j += 1
        return j

    def block_at(self, o: int):
        for b in self.blocks:
            if b[0] == o:
                return b
        return None

    def after_try(self, close: int):
        """The catch blocks and the finally block that follow a try block ending at `close`."""
        catches, fin = [], None
        j = close + 1
        while True:
            m = re.compile(r"\s*(catch\b[^{]*|finally\s*)\{").match(self.s, j)
            if not m:
                break
            b = self.block_at(m.end() - 1)
            if b is None:
                break
            if m.group(1).startswith("catch"):
                catches.append(b)
            else:
                fin = b
                break
            j = b[1] + 1
        return catches, fin


def _cs_target(m, kind):
    if kind == "setting":
        return m.group(1).split(".")[-2] + "." + m.group(2)
    if kind == "deflist":
        return m.group(1)
    return "def." + m.group(2)


def _writes_target(text: str, kind: str, target: str) -> bool:
    if kind == "setting":
        cls, f = target.split(".")
        return re.search(r"(?<![\w])%s\.%s\s*=(?!=)" % (re.escape(cls), re.escape(f)), text) is not None
    if kind == "deflist":
        return re.search(r"\.%s\s*\.\s*(Remove|Clear|RemoveAll|Add|Insert)\s*\(" % target, text) is not None or \
            RESTORE_RUN.search(text) is not None
    return re.search(r"\.%s\s*=(?!=)" % re.escape(target.split(".", 1)[1]), text) is not None


def _rhs(f: CsFile, m) -> str:
    end = f.stmt_end(m.end())
    return f.s[m.end():end]


def cs_pokes(f: CsFile):
    seen = set()
    for kind, rx in (("setting", SETTING_POKE), ("deflist", LIST_POKE), ("def", DEF_POKE)):
        for m in rx.finditer(f.s):
            if m.start() in seen:
                continue
            if kind == "def":
                lhs = m.group(1)
                # `var def = ...` / `Def def = ...` is a local, not a write through a def; a settings hit wins
                if re.search(r"Settings$", lhs) or not re.search(r"(Def|def|DefOf\.\w+)$", lhs):
                    continue
                prev = f.s[max(0, m.start() - 40):m.start()]
                if re.search(r"(new|var|\bout|\bref)\s*$", prev):
                    continue
            seen.add(m.start())
            yield kind, m


def check_cs(rel: str, text: str):
    f = CsFile(text)
    hits = []
    regs = []   # (start, end, bodytext)
    for m in RESTORE_REG.finditer(f.s):
        st = m.start()
        rest = f.s[m.end():]
        k = len(rest) - len(rest.lstrip())
        if rest[k:k + 1] == "{":
            b = f.block_at(m.end() + k)
            end = b[1] if b else f.stmt_end(m.end())
        else:
            end = f.stmt_end(m.end())
        regs.append((st, end, f.s[st:end]))
    finally_blocks = []
    catch_blocks = []
    for b in f.blocks:
        if b[2] == "finally":
            finally_blocks.append(b)
        elif b[2].startswith("catch"):
            catch_blocks.append(b)
    runs_in_finally = any(RESTORE_RUN.search(f.s[b[0]:b[1]]) for b in finally_blocks)
    runs_in_catch = any(RESTORE_RUN.search(f.s[b[0]:b[1]]) for b in catch_blocks)

    def add(kind, m, why, target):
        hits.append({"path": rel, "line": f.line(m.start()), "kind": why, "target": target,
                     "text": " ".join(f.raw[f.stmt_start(m.start()):f.stmt_end(m.end()) + 1].split())[:160]})

    for kind, m in cs_pokes(f):
        p = m.start()
        target = _cs_target(m, kind)
        encl = f.enclosing(p)
        in_finally = any(b[2] == "finally" for b in encl)
        in_reg = any(r[0] < p < r[1] for r in regs)
        rhs = _rhs(f, m) if kind != "deflist" else ""
        if in_finally or in_reg:
            if kind != "deflist" and LITERAL.match(rhs):
                add(kind, m, "restores-fixed-value", target)
            continue
        guarded = False
        # (a) inside a try whose finally writes the target back
        for b in reversed(encl):
            if b[2] == "try":
                _, fin = f.after_try(b[1])
                if fin and _writes_target(f.s[fin[0]:fin[1]], kind, target):
                    guarded = True
                    break
        # (b) followed directly (same block) by such a try, only non-throwing statements between
        if not guarded:
            j = f.stmt_end(m.end()) + 1
            while True:
                nxt = re.compile(r"\s*try\s*\{").match(f.s, j)
                if nxt:
                    b = f.block_at(nxt.end() - 1)
                    _, fin = f.after_try(b[1]) if b else (None, None)
                    if fin and _writes_target(f.s[fin[0]:fin[1]], kind, target):
                        guarded = True
                    break
                k = j
                while k < len(f.s) and f.s[k].isspace():
                    k += 1
                if k >= len(f.s) or f.s[k] in "{}":
                    break
                e = f.stmt_end(k)
                st = f.s[k:e]
                plain = "(" not in st or SETTING_POKE.match(st.strip()) is not None
                if not plain:
                    break
                j = e + 1
        # (c) a restore delegate for the same target registered before it in the same case, or right after it
        if not guarded:
            for (rs, re_, body) in regs:
                if not _writes_target(body, kind, target) and not (kind == "deflist" and target in body):
                    continue
                if re_ < p:
                    between = f.s[re_:p]
                    if re.search(r"\bcase\s+\"|\bstatic\b", between):
                        continue
                    guarded = True
                elif rs > p:
                    between = f.s[f.stmt_end(m.end()) + 1:rs]
                    stmts = [x for x in between.split(";") if x.strip()]
                    if all("(" not in x for x in stmts[:-1]) and "(" not in (stmts[-1] if stmts else ""):
                        guarded = True
                if guarded:
                    if not (runs_in_finally and runs_in_catch):
                        add(kind, m, "restore-delegate-not-run-on-throw", target)
                    break
        if not guarded:
            add(kind, m, "unrestored-on-throw", target)
    return hits


# ------------------------------------------------------------------------------------------------------------ Py

PY_MAILBOX_FIELDS = {"request", "serial", "result"}


def _const(n):
    return n.value if isinstance(n, ast.Constant) else None


def _kw(call: ast.Call, name: str):
    for k in call.keywords:
        if k.arg == name:
            return k.value
    for a in call.args:
        if isinstance(a, ast.Dict):
            for kk, vv in zip(a.keys, a.values):
                if _const(kk) == name:
                    return vv
    return None


def py_poke_kind(call: ast.Call):
    """'harness' for .set_setting, 'raw' for a jawa/mod_settings_field set (modcheck's chain session sees and restores
    it), 'raw-other' for any other settings write (update_mod_settings, a proof's Settings("f=v") static call),
    'reset' for a Settings reset, None else."""
    fn = call.func
    if isinstance(fn, ast.Attribute) and fn.attr == "set_setting":
        return "harness"
    strs = [_const(a) for a in call.args if isinstance(_const(a), str)]
    if "jawa/mod_settings_field" in strs:
        act = _const(_kw(call, "action"))
        fld = _const(_kw(call, "field"))
        if act == "set" and fld not in PY_MAILBOX_FIELDS:
            return "raw"
        return None
    if "rimworld/update_mod_settings" in strs:
        return "raw-other"   # not a mod_settings_field write: the suite cannot see it
    meth = _const(_kw(call, "method"))
    if meth is None and len(call.args) >= 2 and isinstance(_const(call.args[-2]), str):
        meth = _const(call.args[-2])          # _call(t, "Settings", "reset") / call(b, "Settings", "x=1")
    if meth == "Settings" or (isinstance(meth, str) and meth.endswith(".Settings")):
        arg = _const(_kw(call, "args"))
        if arg is None and call.args:
            arg = _const(call.args[-1])
        if arg == "reset":
            return "reset"
        if isinstance(arg, str) and "=" in arg:
            return "raw-other"
        if arg is None:
            return "raw-other"
    return None


def _fixed(v) -> bool:
    """A literal, or anything read from a DEFAULTS table: not the value the field held before the poke."""
    if isinstance(v, ast.Constant):
        return True
    if isinstance(v, ast.IfExp):
        return _fixed(v.body) and _fixed(v.orelse)     # `prior if prior is not None else DEFAULT` restores the prior
    for n in ast.walk(v):
        if isinstance(n, ast.Name) and re.search(r"default", n.id, re.I):
            return True
        if isinstance(n, ast.Attribute) and re.search(r"default", n.attr, re.I):
            return True
    if isinstance(v, ast.Call) and isinstance(v.func, ast.Name) and v.func.id in ("str", "int", "float", "bool") \
            and len(v.args) == 1 and not v.keywords:
        return isinstance(v.args[0], ast.Constant)        # str(True); str(x) is judged through x by the caller
    return False


def _resolved_fixed(v, env) -> bool:
    """One level through a local: `want = P.DEFAULTS[f]` then `value=str(want)` is a fixed value too -- when EVERY
    assignment to that local is fixed (`old = None` ... `old = read()` is a captured prior)."""
    for n in ast.walk(v):
        if isinstance(n, ast.Name) and env and n.id in env:
            return all(_fixed(x) for x in env[n.id])
    return False


def _value_is_literal(call: ast.Call, env=None) -> bool:
    v = _kw(call, "value")
    if v is not None:
        return _fixed(v) or _resolved_fixed(v, env)
    for a in call.args:
        if isinstance(a, ast.Dict):
            return all(_fixed(x) for x in a.values) and bool(a.values)
    return False


def _has_settings_write(nodes, setters=()) -> bool:
    for n in nodes:
        for c in ast.walk(n):
            if isinstance(c, ast.Call) and py_poke_kind(c) is not None:
                return True
            if isinstance(c, ast.Call) and isinstance(c.func, (ast.Name, ast.Attribute)):
                nm = c.func.id if isinstance(c.func, ast.Name) else c.func.attr
                if re.search(r"restore", nm, re.I) or nm in setters:
                    return True       # a call to a setter wrapper (sset/fset) in a finally is a settings write
    return False


def _locals(fn):
    """name -> every value assigned to it by a single-name assignment in a function."""
    env = {}
    if fn is None:
        return env
    for n in ast.walk(fn):
        if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name):
            env.setdefault(n.targets[0].id, []).append(n.value)
        elif isinstance(n, ast.For) and isinstance(n.target, ast.Tuple):
            for e in n.target.elts:                     # `for f, before in changed.items()`: a loop-bound prior
                if isinstance(e, ast.Name):
                    env.setdefault(e.id, []).append(n.iter)
    return env


def _t_scoped(call: ast.Call, chain) -> bool:
    """The write reaches the game through a modcheck TestContext: the receiver is rooted at `t` (t.session.call,
    t.bridge_call) or it sits in a function that takes the context as its `t` parameter."""
    n = call.func
    while isinstance(n, ast.Attribute):
        n = n.value
    if isinstance(n, ast.Name) and n.id == "t":
        return True
    if any(isinstance(a, ast.Name) and a.id == "t" for a in call.args[:1]):
        return True
    return any(isinstance(p, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)) and
               any(a.arg == "t" for a in p.args.args) for p, _ in chain)


def _remembered_before(call: ast.Call, chain) -> bool:
    """A t.remember_settings(...) earlier in the same function: the chain's finally restores what a reset rewrites."""
    fn = next((p for p, _ in chain if isinstance(p, (ast.FunctionDef, ast.AsyncFunctionDef))), None)
    if fn is None:
        return False
    return any(isinstance(c, ast.Call) and isinstance(c.func, ast.Attribute) and c.func.attr == "remember_settings"
               and c.lineno <= call.lineno for c in ast.walk(fn))


def check_py(rel: str, text: str, harness_restores: bool, harness_tracks: bool = False):
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return []
    hits = []
    suite_file = "modcheck" in text and ".chain(" in text
    parents = {}
    for p in ast.walk(tree):
        for c in ast.iter_child_nodes(p):
            parents[c] = p
    # one level of wrappers: a function whose body pokes and takes the value as a parameter is a setter; its call
    # sites are the pokes (the write inside it is judged where it is called from)
    setters = {}
    for fn in ast.walk(tree):
        if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            pk = [c for c in ast.walk(fn) if isinstance(c, ast.Call) and (py_poke_kind(c) or "").startswith("raw")]
            params = {a.arg for a in fn.args.args}

            def uses_param(c):
                v = _kw(c, "value")
                return v is not None and any(isinstance(n, ast.Name) and n.id in params for n in ast.walk(v))
            if pk and (fn.name == "set_setting" or re.search(r"set|poke|flip|toggle", fn.name, re.I)
                       and not re.search(r"restore|teardown|cleanup", fn.name, re.I)) and \
                    (fn.name == "set_setting" or any(uses_param(c) for c in pk)):
                setters[fn.name] = "raw" if all(py_poke_kind(c) == "raw" for c in pk) else "raw-other"
    for c in ast.walk(tree):
        if not isinstance(c, ast.Call):
            continue
        kind = py_poke_kind(c)
        if kind is None and isinstance(c.func, ast.Name) and c.func.id in setters:
            kind = setters[c.func.id]
        if kind is None:
            continue
        chain, n = [], c
        while n in parents:
            chain.append((parents[n], n))
            n = parents[n]
        fn = next((p for p, _ in chain if isinstance(p, (ast.FunctionDef, ast.AsyncFunctionDef))), None)
        if fn is not None and fn.name in setters and kind.startswith("raw") and py_poke_kind(c) is not None:
            continue                       # the write inside a setter wrapper: judged at its call sites
        in_finally = any(isinstance(p, ast.Try) and ch in p.finalbody for p, ch in chain)
        in_handler = any(isinstance(p, ast.ExceptHandler) for p, _ in chain)
        in_restore_fn = fn is not None and re.search(r"restore|teardown|cleanup", fn.name, re.I)
        line = c.lineno
        src = " ".join(ast.get_source_segment(text, c).split())[:160] if ast.get_source_segment(text, c) else ""
        if kind == "harness" and harness_restores:
            continue                       # modcheck/suite.py puts the prior value back in the chain's finally
        if harness_tracks and suite_file and _t_scoped(c, chain):
            if kind == "raw":
                continue                   # every settings write through t records its prior; the chain's finally restores
            if kind == "reset" and _remembered_before(c, chain):
                continue
        if in_finally or in_handler or in_restore_fn:
            if kind == "reset" or (kind.startswith("raw") and _value_is_literal(c, _locals(fn))) or (kind == "harness" and _value_is_literal(c)):
                hits.append({"path": rel, "line": line, "kind": "restores-fixed-value", "target": kind, "text": src})
            continue
        guarded = any(isinstance(p, ast.Try) and ch in p.body and p.finalbody and _has_settings_write(p.finalbody, setters)
                      for p, ch in chain)
        if not guarded:
            # the statement right after the poke's statement is a try whose finally writes settings back
            stmt = next(((p, ch) for p, ch in chain if isinstance(ch, ast.stmt)), None)
            if stmt is not None:
                parent, st = stmt
                for field in ("body", "orelse", "finalbody", "handlers"):
                    seq = getattr(parent, field, None)
                    if isinstance(seq, list) and st in seq:
                        i = seq.index(st)
                        if i + 1 < len(seq) and isinstance(seq[i + 1], ast.Try) and seq[i + 1].finalbody and \
                                _has_settings_write(seq[i + 1].finalbody, setters):
                            guarded = True
        if kind == "reset" and not guarded:
            hits.append({"path": rel, "line": line, "kind": "reset-loses-player-values", "target": kind, "text": src})
        elif not guarded:
            hits.append({"path": rel, "line": line, "kind": "unrestored-on-throw", "target": kind, "text": src})
    return hits


def _suite_text(text):
    if text is None:
        try:
            text = SUITE.read_text(encoding="utf-8")
        except OSError:
            return ""
    return text


def suite_restores(text: str | None = None) -> bool:
    """modcheck/suite.py records each set_setting field's prior value and restores it in the chain's finally."""
    text = _suite_text(text)
    if SUITE_MARKER not in text:
        return False
    chain = text.split("def chain(", 1)[-1].split("def components_declared", 1)[0]
    fin = chain.split("finally:", 1)
    return len(fin) == 2 and SUITE_MARKER in fin[-1]


def suite_tracks(text: str | None = None) -> bool:
    """... and every chain's session records the prior of ANY jawa/mod_settings_field set (not only set_setting)."""
    text = _suite_text(text)
    chain = text.split("def chain(", 1)[-1].split("def components_declared", 1)[0]
    return suite_restores(text) and TRACK_MARKER + "(" in chain and "class " + TRACK_MARKER in text


# ------------------------------------------------------------------------------------------------------------ scan

def tracked(root: Path):
    out = subprocess.run(["git", "-C", str(root), "ls-files", "-z", "--", "src"], capture_output=True, check=True)
    return [p for p in out.stdout.decode("utf-8", "replace").split("\0") if p]


def is_cs_target(rel: str, text: str) -> bool:
    if not rel.endswith(".cs") or "/SelfTest/" in rel or "/obj/" in rel:
        return False
    return bool(CS_NAME.search(Path(rel).name)) or bool(CS_STAGE.search(text))


def is_py_target(rel: str) -> bool:
    name = Path(rel).name
    return rel.endswith(".py") and not name.startswith("selftest") and "/selftest_fixtures/" not in rel \
        and name != "proof_restore_check.py"


def scan(root: Path = REPO, paths=None):
    sp = root / "src/RimMandrake/Utils/modcheck/suite.py"
    st = sp.read_text(encoding="utf-8") if sp.exists() else ""
    harness, tracks = suite_restores(st), suite_tracks(st)
    files = paths if paths else tracked(root)
    hits, seen = [], {"cs": 0, "py": 0}
    for rel in files:
        p = root / rel
        if not (rel.endswith(".cs") or rel.endswith(".py")) or not p.is_file():
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        if rel.endswith(".cs") and is_cs_target(rel, text):
            seen["cs"] += 1
            found = check_cs(rel, text)
        elif is_py_target(rel):
            if "settings" not in text.lower():
                continue
            seen["py"] += 1
            found = check_py(rel, text, harness, tracks)
        else:
            continue
        hits += [h for h in found if not waived(text, h["line"])]
    return hits, seen, harness


WAIVER = "restore-check: ok"


def waived(text: str, line: int) -> bool:
    """`restore-check: ok <why>` on the hit's line or the line above: a reviewed write whose restore lives where a
    lexical scan cannot follow (a caller's finally) or whose fixed value IS the prior (a gate refused anything else)."""
    lines = text.split("\n")
    return any(WAIVER in lines[i] for i in (line - 1, line - 2) if 0 <= i < len(lines))


def key(h) -> str:
    return "%s::%s::%s" % (h["path"], h["kind"], h["target"])


def new_hits(hits, baseline=None):
    """Hits not covered by the baseline: an unfiled key, or every hit past the count a filed key had when filed."""
    baseline = BASELINE if baseline is None else baseline
    by = {}
    for h in hits:
        by.setdefault(key(h), []).append(h)
    out = []
    for k, hs in by.items():
        out += hs[baseline[k][1]:] if k in baseline else hs
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("paths", nargs="*")
    ap.add_argument("--json")
    ap.add_argument("--all", action="store_true", help="print baseline (filed) hits too")
    a = ap.parse_args(argv)
    hits, seen, harness = scan(REPO, a.paths or None)
    new = new_hits(hits)
    for h in (hits if a.all else new):
        tag = "" if any(h is x for x in new) else "  [filed %s]" % BASELINE[key(h)][0]
        print("%s:%d %s %s :: %s%s" % (h["path"], h["line"], h["kind"], h["target"], h["text"], tag))
    print("scanned cs=%d py=%d harness_restores=%s hits=%d new=%d baseline=%d"
          % (seen["cs"], seen["py"], harness, len(hits), len(new), len(hits) - len(new)))
    if a.json:
        Path(a.json).write_text(json.dumps({"hits": hits, "seen": seen, "harness": harness}, indent=1), encoding="utf-8")
    return 1 if new else 0


if __name__ == "__main__":
    sys.exit(main())
