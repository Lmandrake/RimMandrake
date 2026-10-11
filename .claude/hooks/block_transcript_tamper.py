#!/usr/bin/env python3
"""PreToolUse hook -- nothing an agent runs may WRITE a Claude Code transcript.

WHY
===
`block_forged_owner_said.py` proves an `--owner-said` quote against the lines
of the session transcript the harness marks as typed by a human. That proof is
only as good as the file: an agent that appends a forged
`{"type":"user","promptSource":"typed","origin":{"kind":"human"},...}` line to
`~/.claude/projects/<project>/<session>.jsonl` makes any sentence "his"
(attack A37, `Transient/owner_said_guard_review_20261011.md`). The harness is
the only legitimate writer of those files, so every agent write is refused.

WHAT IS PROTECTED
=================
Anything under `<claude home>/projects/` that is a `.jsonl` file, a directory
or a glob (a directory target is how `mv forged.jsonl <dir>/` lands without a
`.jsonl` in the text), and every `.../subagents/*.jsonl` under the claude
home. `projects/*/memory/` is NOT protected -- agents keep their memory there.
The claude home is the account's real home (from the password database, not
`$HOME`, which a command can reassign) plus `$CLAUDE_CONFIG_DIR`.

WHAT IS REFUSED
===============
- Write / Edit / MultiEdit / NotebookEdit whose path (after symlinks) is
  protected.
- Bash: redirection (`>`, `>>`, `>|`, `&>`, `<>`) into a protected path;
  `tee`; `cp`/`install`/`rsync` targets; any `mv`/`ln` operand (moving the
  transcript away, or linking to it so a later write goes through the link);
  `dd of=`; `truncate`; `touch`; `sed -i` / `perl -i` operands; `tar -C` /
  `unzip -d`; inline `python -c` / `python - <<EOF` that opens a protected
  path for writing, writes, copies, moves or links it; `node -e`,
  `perl -e`, `ruby -e` by a conservative pattern. `sh -c`, `bash -c`, `eval`,
  `find -exec`, `xargs` and shell heredocs are analysed recursively.
- A write whose target cannot be resolved from the command text (`$(...)`,
  an unassigned `$VAR`, `{}` from find/xargs, a python variable) is refused
  when the command mentions the transcript area at all -- it might be one.

READING IS ALLOWED: `cat`, `grep`, `cp <transcript> /tmp/x`, a python census
that opens transcripts read-only and writes its report to a literal path.

LIMITS (a command-text hook cannot see them)
============================================
A script FILE (`python3 forge.py`) whose source does the write, or a path
assembled from fragments (`'.cl' + 'aude'`), is invisible here. That residual
is recorded in `Transient/pickAQ_20261011.md`.

Fails OPEN on any internal error (a broken hook must never wedge a session).
"""
import ast
import json
import os
import pwd
import re
import shlex
import sys
import warnings

# --------------------------------------------------------------------------
# protected paths
# --------------------------------------------------------------------------


def _real_home():
    try:
        return pwd.getpwuid(os.getuid()).pw_dir
    except Exception:
        return os.path.expanduser("~")


HOME = _real_home()


def claude_homes():
    homes = [os.path.join(HOME, ".claude")]
    cfg = os.environ.get("CLAUDE_CONFIG_DIR")
    if cfg:
        homes.append(os.path.normpath(os.path.expanduser(cfg)))
    return homes


_GLOB = re.compile(r"[*?\[{]")
_WSL_UNC = re.compile(r"^[\\/]{1,2}wsl(?:\.localhost|\$)[\\/][^\\/]+", re.I)


def _norm_path(p, cwd):
    """Literal path text -> absolute normalized path (no symlink resolution)."""
    p = _WSL_UNC.sub("", p).replace("\\", "/") if _WSL_UNC.match(p) else p
    if p == "~" or p.startswith("~/"):
        p = HOME + p[1:]
    for v in ("${HOME}", "$HOME"):
        if p.startswith(v):
            p = HOME + p[len(v):]
    if not p.startswith("/"):
        p = os.path.join(cwd or "/", p)
    return os.path.normpath(p)


def _is_protected_abs(p):
    for root in claude_homes():
        proj = os.path.join(root, "projects")
        if _GLOB.search(p):
            # a glob whose literal prefix is an ancestor of (or inside) projects
            prefix = p[:_GLOB.search(p).start()]
            if proj.startswith(prefix) or prefix.startswith(proj + "/"):
                if "/memory/" in prefix + "/" and prefix.startswith(proj + "/"):
                    continue
                return True
            continue
        if p.startswith(root + "/") and "/subagents/" in p and p.endswith(".jsonl"):
            return True
        if p == proj or p.startswith(proj + "/"):
            rest = p[len(proj):]
            if "/memory/" in rest + "/":
                continue
            if p.endswith(".jsonl"):
                return True
            last = os.path.basename(p)
            if "." not in last:          # a directory (or extension-less file)
                return True
    return False


def is_protected(p, cwd):
    """True if writing literal path text `p` could write a transcript."""
    a = _norm_path(p, cwd)
    if _is_protected_abs(a):
        return True
    try:
        r = os.path.realpath(a)          # a symlink pointing at a transcript
    except Exception:
        return False
    return r != a and _is_protected_abs(r)


def is_ancestor_of_projects(p, cwd):
    a = _norm_path(p, cwd)
    for root in claude_homes():
        proj = os.path.join(root, "projects")
        if proj == a or proj.startswith(a.rstrip("/") + "/"):
            return True
    return False


_MENTION = re.compile(
    r"\.claude[/\\]+projects|\.claude[^\s'\"]*subagents|\.claude[^\s'\"]*\.jsonl"
    r"|CLAUDE_CONFIG_DIR|transcript_path", re.I)
# `projects/<p>/memory/...` is agent memory, not a transcript: naming it is not
# touching the transcript area.
_MEMORY_PATH = re.compile(r"\.claude[/\\]+projects[/\\]+[^/\\\s'\"]+[/\\]+memory\b[^\s'\"]*")


def mentions(text):
    """True if the text names the transcript area: `.claude/projects` (outside
    a `memory/` path), a subagents file, a `.claude...jsonl` path, or the literal
    projects directory of any claude home (`$CLAUDE_CONFIG_DIR` included)."""
    flat = (text or "").replace("\\", "/")
    for h in claude_homes():
        flat = re.sub(re.escape(h) + r"/projects/[^/\s'\"]+/memory\b[^\s'\"]*", "", flat)
    flat = _MEMORY_PATH.sub("", flat)
    if _MENTION.search(flat):
        return True
    return any(h + "/projects" in flat for h in claude_homes())


# --------------------------------------------------------------------------
# shell analysis
# --------------------------------------------------------------------------
_HEREDOC = re.compile(r"<<-?\s*(['\"]?)([A-Za-z_][\w-]*)\1([^\n]*)\n(.*?)\n\s*\2\s*(?:\n|$)",
                      re.S)
_ASSIGN = re.compile(r"(?:^|[\s;&|(])(?:export\s+|local\s+)?([A-Za-z_]\w*)="
                     r"(\"(?:[^\"\\]|\\.)*\"|'[^']*'|[^\s;&|()]+)")
_REF = re.compile(r"\$(?:\{(\w+)\}|(\w+))")
_SEPS = {";", "&&", "||", "|", "&", "(", ")", "\n", "|&", ";;"}
_REDIR = {">", ">>", ">|", "&>", "&>>", "<>", ">>&"}
_PREFIX = {"sudo", "command", "builtin", "exec", "nohup", "time", "nice",
           "stdbuf", "doas", "noglob"}
_INTERP_PY = re.compile(r"^(?:.*/)?python(?:\d+(?:\.\d+)*)?(?:\.exe)?$")
_INTERP_OTHER = re.compile(r"^(?:.*/)?(?:node|nodejs|perl|ruby|php|deno|bun)(?:\.exe)?$")
_SHELLS = re.compile(r"^(?:.*/)?(?:sh|bash|zsh|dash|ksh)$")


class Refuse(Exception):
    pass


_FOR = re.compile(r"\bfor\s+([A-Za-z_]\w*)\s+in\s+([^;\n]*?)\s*(?:;|\n)\s*do\b")


def _vals(command):
    vals = {}
    for m in _ASSIGN.finditer(command):
        v = m.group(2)
        if v[:1] in "\"'":
            v = v[1:-1]
        vals.setdefault(m.group(1), []).append(v)
    for m in _FOR.finditer(command):
        try:
            words = shlex.split(m.group(2))
        except ValueError:
            words = [None]
        vals.setdefault(m.group(1), []).extend(words or [None])
    return vals


def _resolve(tok, vals, depth=0):
    """-> list of literal candidates, or None if unresolvable."""
    if depth > 4 or "`" in tok or "$(" in tok or "{}" == tok or "<(" in tok:
        return None
    outs = [tok]
    for m in _REF.finditer(tok):
        name = m.group(1) or m.group(2)
        if name == "HOME":
            cands = [HOME]
        else:
            raw = vals.get(name)
            if not raw or None in raw:
                return None
            cands = []
            for c in raw:
                r = _resolve(c, vals, depth + 1) if "$" in c else [c]
                if r is None:
                    return None
                cands.extend(r)
        if len(outs) * len(cands) > 256:
            return None
        outs = [o.replace(m.group(0), c, 1) for o in outs for c in cands]
    if any("$" in o or "`" in o for o in outs):
        return None
    return outs


class Ctx:
    def __init__(self, cwd, text):
        self.cwd = cwd
        self.cwd_known = True
        self.mention = mentions(text)
        self.vals = _vals(text)


def _target(tok, ctx, why, ancestor_ok=False):
    cands = _resolve(tok, ctx.vals)
    if cands is None or (not ctx.cwd_known and not tok.startswith(("/", "~", "$HOME", "${HOME}"))):
        if ctx.mention:
            raise Refuse("%s: target %r cannot be resolved from the command text, and the "
                         "command touches the transcript area" % (why, tok))
        return
    for c in cands:
        if is_protected(c, ctx.cwd):
            raise Refuse("%s writes %r" % (why, c))
        if ancestor_ok and is_ancestor_of_projects(c, ctx.cwd):
            raise Refuse("%s copies a tree over %r, which holds the transcripts" % (why, c))


def _lex(command):
    lx = shlex.shlex(command, posix=True, punctuation_chars=";&|()<>\n")
    lx.whitespace = " \t\r"
    lx.whitespace_split = True
    lx.commenters = ""
    out = []
    try:
        for t in lx:
            out.append(t)
    except ValueError:
        # unbalanced quotes: fall back to a crude split; never crash
        out = re.findall(r"[;&|()<>\n]+|[^\s;&|()<>]+", command)
    return out


def _split_punct(tokens):
    """shlex glues runs like `;(` or `>>` -- split runs of punctuation into ops."""
    ops = sorted(_SEPS | _REDIR | {"<", "<<", "<<<", ">&", "<&"}, key=len, reverse=True)
    out = []
    for t in tokens:
        if t and all(c in ";&|()<>\n" for c in t):
            i = 0
            while i < len(t):
                for op in ops:
                    if t.startswith(op, i):
                        out.append(op)
                        i += len(op)
                        break
                else:
                    out.append(t[i])
                    i += 1
        else:
            out.append(t)
    return out


def analyse_shell(command, ctx=None, depth=0):
    if depth > 6:
        return
    if ctx is None:
        ctx = Ctx(os.getcwd(), command)
    # heredoc bodies: analyse as the consumer's language, then drop them
    bodies = []

    def _cut(m):
        bodies.append(m.group(4))
        return "<<HEREDOC_%d%s\n" % (len(bodies) - 1, m.group(3))
    stripped = _HEREDOC.sub(_cut, command)
    tokens = _split_punct(_lex(stripped))
    cmd = []
    i = 0
    while i < len(tokens):
        t = tokens[i]
        if t in _REDIR:
            if i + 1 < len(tokens):
                tgt = tokens[i + 1]
                if not (tgt.isdigit() or tgt == "-" or tgt in _SEPS):
                    _target(tgt, ctx, "a `%s` redirection" % t)
                i += 2
                continue
        if t in (">&",) and i + 1 < len(tokens):
            tgt = tokens[i + 1]
            if not (tgt.isdigit() or tgt == "-"):
                _target(tgt, ctx, "a `>&` redirection")
            i += 2
            continue
        if t in ("<", "<<<", "<&") and i + 1 < len(tokens):
            i += 2
            continue
        if t == "<<" and i + 1 < len(tokens):
            m = re.match(r"HEREDOC_(\d+)$", tokens[i + 1])
            if m:
                cmd.append(("HEREDOC", bodies[int(m.group(1))]))
            i += 2
            continue
        if t in _SEPS:
            _simple(cmd, ctx, depth)
            cmd = []
            i += 1
            continue
        # `2>file`, `1>>file`: shlex gives '2' then '>' -- the digit is harmless as a word
        cmd.append(t)
        i += 1
    _simple(cmd, ctx, depth)
    # any heredoc not attached to an interpreter (e.g. `cat <<EOF > f`) carries data only


def _opts_and_operands(args, takes_value=()):
    opts, ops = [], []
    j = 0
    end = False
    while j < len(args):
        a = args[j]
        if not end and a == "--":
            end = True
        elif not end and a.startswith("-") and a != "-":
            opts.append(a)
            if a in takes_value and j + 1 < len(args):
                opts.append(args[j + 1])
                j += 1
        else:
            ops.append(a)
        j += 1
    return opts, ops


def _simple(words, ctx, depth):
    heredocs = [w[1] for w in words if isinstance(w, tuple)]
    words = [w for w in words if not isinstance(w, tuple)]
    # strip leading assignments and wrappers
    while words:
        w = words[0]
        if re.match(r"^[A-Za-z_]\w*=", w):
            words = words[1:]
        elif w in _PREFIX:
            words = words[1:]
        elif w == "env":
            words = words[1:]
            while words and (words[0].startswith("-") or re.match(r"^[A-Za-z_]\w*=", words[0])):
                if words[0] in ("-u", "-C", "-S") and len(words) > 1:
                    words = words[1:]
                words = words[1:]
        elif w == "timeout":
            words = words[1:]
            while words and words[0].startswith("-"):
                words = words[1:]
            words = words[1:]           # the duration
        elif w == "xargs":
            words = words[1:]
            while words and words[0].startswith("-"):
                if words[0] in ("-I", "-n", "-P", "-d", "-L", "-s", "-E", "-a") and len(words) > 1:
                    words = words[1:]
                words = words[1:]
            words = words + ["{}"]      # xargs appends operands nobody can see
        else:
            break
    if not words:
        for b in heredocs:
            pass
        return
    name = os.path.basename(words[0])
    args = words[1:]

    if name in ("cd", "pushd"):
        tgt = args[0] if args else "~"
        cands = _resolve(tgt, ctx.vals)
        if cands is None or tgt == "-" or len(cands) != 1:
            ctx.cwd_known = False
        else:
            ctx.cwd = _norm_path(cands[0], ctx.cwd)
            ctx.cwd_known = True
            if is_ancestor_of_projects(ctx.cwd, "/") or is_protected(ctx.cwd, "/"):
                ctx.mention = True
        return

    if name == "find":
        for k, a in enumerate(args):
            if a in ("-exec", "-execdir", "-ok", "-okdir"):
                sub = []
                for b in args[k + 1:]:
                    if b in (";", "\\;", "+"):
                        break
                    sub.append(b)
                _simple(sub, ctx, depth + 1)
            if a in ("-fprint", "-fprintf", "-fls", "-fprint0") and k + 1 < len(args):
                _target(args[k + 1], ctx, "find %s" % a)
        return

    if _SHELLS.match(words[0]) or name == "eval":
        if name == "eval":
            analyse_shell(" ".join(args), ctx, depth + 1)
            return
        if "-c" in args:
            k = args.index("-c")
            if k + 1 < len(args):
                analyse_shell(args[k + 1], ctx, depth + 1)
        for b in heredocs:
            analyse_shell(b, ctx, depth + 1)
        return

    if _INTERP_PY.match(words[0]):
        code = None
        if "-c" in args:
            k = args.index("-c")
            code = args[k + 1] if k + 1 < len(args) else ""
        for c in ([code] if code is not None else []) + heredocs:
            analyse_python(c, ctx, depth)
        return

    if _INTERP_OTHER.match(words[0]):
        if name.startswith("perl"):
            if any(re.match(r"^-[a-zA-Z]*i", a) for a in args):
                # perl -i: every non-option operand that is not the -e script
                skip = set()
                for k, a in enumerate(args):
                    if re.match(r"^-[a-zA-Z]*[eE]$", a) and k + 1 < len(args):
                        skip.add(k + 1)
                ops = [a for k, a in enumerate(args) if k not in skip and not a.startswith("-")]
                if not any(re.match(r"^-[a-zA-Z]*[eE]$", a) for a in args) and ops:
                    ops = ops[1:]       # first operand is the script
                for o in ops:
                    _target(o, ctx, "perl -i")
        codes = []
        for k, a in enumerate(args):
            if re.match(r"^-[a-zA-Z]*[eEr]$|^--eval$|^-p$", a) and k + 1 < len(args):
                codes.append(args[k + 1])
        codes += heredocs
        for c in codes:
            if mentions(c) and _OTHER_WRITE.search(c):
                raise Refuse("an inline %s script both names the transcript area and writes "
                             "files" % name)
        return

    if name == "tee":
        _, ops = _opts_and_operands(args)
        for o in ops:
            _target(o, ctx, "tee")
    elif name in ("cp", "install", "rsync", "scp", "gcp"):
        opts, ops = _opts_and_operands(args, takes_value=("-t", "-S", "-m", "-o", "-g",
                                                          "-e", "--target-directory"))
        tgt = None
        for k, o in enumerate(opts):
            if o in ("-t", "--target-directory") and k + 1 < len(opts):
                tgt = opts[k + 1]
            elif o.startswith("--target-directory="):
                tgt = o.split("=", 1)[1]
        srcs = ops
        if tgt is None and ops:
            tgt, srcs = ops[-1], ops[:-1]
        if tgt is not None:
            recursive = name == "rsync" or any(
                o in ("-r", "-R", "-a", "--recursive", "--archive") or
                (re.match(r"^-[a-zA-Z]+$", o) and set(o[1:]) & set("rRa")) for o in opts)
            tree = recursive and any(
                os.path.basename(s.rstrip("/")) in (".claude", "projects") or s.endswith("/")
                for s in srcs)
            _target(tgt, ctx, name, ancestor_ok=tree)
    elif name in ("mv", "ln", "link", "rename"):
        opts, ops = _opts_and_operands(args, takes_value=("-t", "-S", "--target-directory"))
        allops = ops + [o.split("=", 1)[1] for o in opts if o.startswith("--target-directory=")]
        for k, o in enumerate(opts):
            if o in ("-t", "--target-directory") and k + 1 < len(opts):
                allops.append(opts[k + 1])
        srcs = ops[:-1]
        tree = any(os.path.basename(s.rstrip("/")) in (".claude", "projects") for s in srcs)
        for o in allops:
            _target(o, ctx, name, ancestor_ok=tree and o == (ops[-1] if ops else None))
    elif name == "dd":
        for a in args:
            if a.startswith("of="):
                _target(a[3:], ctx, "dd of=")
    elif name in ("truncate", "touch", "shred"):
        _, ops = _opts_and_operands(args, takes_value=("-s", "-r", "--size", "--reference",
                                                       "-d", "-t", "-n"))
        for o in ops:
            _target(o, ctx, name)
    elif name == "sed" or name == "gsed":
        if any(a.startswith("--in-place") or re.match(r"^-[a-zA-Z]*i", a) for a in args):
            opts, ops = _opts_and_operands(args, takes_value=("-e", "-f", "--expression", "--file"))
            if not any(o in ("-e", "-f", "--expression", "--file") or o.startswith(("--expression=", "--file="))
                       for o in opts) and ops:
                ops = ops[1:]
            for o in ops:
                _target(o, ctx, "sed -i")
    elif name in ("tar", "bsdtar"):
        for k, a in enumerate(args):
            if a in ("-C", "--directory") and k + 1 < len(args):
                _target(args[k + 1], ctx, "tar -C", ancestor_ok=True)
            elif a.startswith("--directory="):
                _target(a.split("=", 1)[1], ctx, "tar --directory", ancestor_ok=True)
    elif name == "unzip":
        for k, a in enumerate(args):
            if a == "-d" and k + 1 < len(args):
                _target(args[k + 1], ctx, "unzip -d", ancestor_ok=True)
    elif name in ("chattr", "chmod", "chown"):
        pass
    for b in heredocs:
        pass


_OTHER_WRITE = re.compile(
    r"writeFile|appendFile|createWriteStream|copyFile|rename|symlink|truncate|"
    r"open\s*\(|>>|print\s*\{|syswrite|File\.(?:write|open)|IO\.write|FileUtils|"
    r"file_put_contents|fopen", re.I)

# --------------------------------------------------------------------------
# python analysis
# --------------------------------------------------------------------------
_PY_WRITE_FALLBACK = re.compile(
    r"open\s*\([^)]*['\"][rwax+bt]*[wax+]|write_text|write_bytes|shutil\.|os\.(?:rename|"
    r"replace|link|symlink|truncate|open)|\.touch\(|\.rename\(|\.replace\(|symlink_to|"
    r"hardlink_to|subprocess|os\.system|O_WRONLY|O_APPEND|O_RDWR")


def _dotted(node):
    parts = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if isinstance(node, ast.Name):
        parts.append(node.id)
        return ".".join(reversed(parts))
    return None


class _PyEval:
    """Evaluate a path expression to a literal string, or None."""

    def __init__(self, tree):
        self.names = {}
        counts = {}
        for n in ast.walk(tree):
            if isinstance(n, ast.Assign):
                for t in n.targets:
                    if isinstance(t, ast.Name):
                        counts[t.id] = counts.get(t.id, 0) + 1
                        self.names[t.id] = n.value
            elif isinstance(n, (ast.For, ast.AugAssign, ast.AnnAssign, ast.With,
                                ast.comprehension, ast.NamedExpr)):
                for t in ast.walk(n.target if hasattr(n, "target") and n.target is not None
                                  else n):
                    if isinstance(t, ast.Name) and isinstance(t.ctx, ast.Store):
                        counts[t.id] = counts.get(t.id, 0) + 2
        for k, c in counts.items():
            if c != 1:
                self.names.pop(k, None)
        self._depth = 0

    def ev(self, node):
        self._depth += 1
        try:
            if self._depth > 30:
                return None
            return self._ev(node)
        finally:
            self._depth -= 1

    def _ev(self, node):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return node.value
        if isinstance(node, ast.JoinedStr):
            out = ""
            for v in node.values:
                if isinstance(v, ast.Constant):
                    out += str(v.value)
                elif isinstance(v, ast.FormattedValue):
                    s = self.ev(v.value)
                    if s is None:
                        return None
                    out += s
            return out
        if isinstance(node, ast.Name):
            v = self.names.get(node.id)
            return self.ev(v) if v is not None else None
        if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Div, ast.Add)):
            a, b = self.ev(node.left), self.ev(node.right)
            if a is None or b is None:
                return None
            return os.path.join(a, b) if isinstance(node.op, ast.Div) else a + b
        if isinstance(node, ast.Call):
            fn = _dotted(node.func) or ""
            short = fn.split(".")[-1]
            if short in ("Path", "PurePath", "PosixPath", "expanduser", "abspath",
                         "normpath", "realpath", "fspath", "str", "resolve", "expandvars"):
                if not node.args:
                    if isinstance(node.func, ast.Attribute) and short in ("resolve", "expanduser"):
                        return self.ev(node.func.value)
                    return None
                s = self.ev(node.args[0])
                return s
            if fn.endswith("path.join") or fn == "join":
                parts = [self.ev(a) for a in node.args]
                return None if any(p is None for p in parts) else os.path.join(*parts)
            if short == "home":
                return HOME
            if short in ("getcwd", "cwd"):
                return None
        return None


def analyse_python(code, ctx, depth=0):
    if not code:
        return
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            tree = ast.parse(code)
    except SyntaxError:
        if mentions(code) and _PY_WRITE_FALLBACK.search(code):
            raise Refuse("an inline python script both names the transcript area and writes "
                         "files (and could not be parsed to tell which)")
        return
    pe = _PyEval(tree)
    mention = ctx.mention or mentions(code)

    def target(node, why):
        if node is None:
            return
        s = pe.ev(node)
        if s is None:
            if mention:
                raise Refuse("inline python %s a path it builds at run time, and the script "
                             "touches the transcript area" % why)
            return
        s = os.path.expanduser(s) if s.startswith("~") else s
        if is_protected(s, ctx.cwd):
            raise Refuse("inline python %s %r" % (why, s))

    def mode_writes(node):
        if node is None:
            return False
        s = pe.ev(node)
        if s is None:
            return True                       # unknown mode: assume it writes
        return any(c in s for c in "wax+")

    for n in ast.walk(tree):
        if not isinstance(n, ast.Call):
            continue
        fn = _dotted(n.func) or ""
        short = fn.split(".")[-1] if fn else (n.func.attr if isinstance(n.func, ast.Attribute) else "")
        kw = {k.arg: k.value for k in n.keywords if k.arg}
        if fn in ("open", "io.open", "codecs.open", "builtins.open"):
            mode = n.args[1] if len(n.args) > 1 else kw.get("mode")
            if mode_writes(mode) if mode is not None else False:
                target(n.args[0] if n.args else kw.get("file"), "opens for writing")
        elif fn == "os.open":
            flags = ast.unparse(n.args[1]) if len(n.args) > 1 else ""
            if re.search(r"O_(?:WRONLY|RDWR|APPEND|TRUNC|CREAT)", flags) or not flags:
                target(n.args[0] if n.args else None, "os.open()s for writing")
        elif fn in ("os.rename", "os.replace", "os.link", "os.symlink", "os.renames",
                    "shutil.move"):
            for a in n.args[:2]:
                target(a, "moves or links")
        elif fn in ("shutil.copy", "shutil.copy2", "shutil.copyfile", "shutil.copytree",
                    "shutil.copyfileobj"):
            if len(n.args) > 1:
                target(n.args[1], "copies onto")
            elif "dst" in kw:
                target(kw["dst"], "copies onto")
        elif fn in ("os.truncate", "os.utime", "os.chmod"):
            if fn == "os.truncate":
                target(n.args[0] if n.args else None, "truncates")
        elif fn in ("os.system", "os.popen") or fn.startswith("subprocess."):
            arg = n.args[0] if n.args else kw.get("args")
            if isinstance(arg, (ast.List, ast.Tuple)):
                parts = [pe.ev(e) for e in arg.elts]
                if any(p is None for p in parts):
                    if mention:
                        raise Refuse("inline python runs a command it builds at run time, and "
                                     "the script touches the transcript area")
                else:
                    analyse_shell(shlex.join(parts), ctx, depth + 1)
            elif arg is not None:
                s = pe.ev(arg)
                if s is None:
                    if mention:
                        raise Refuse("inline python runs a command it builds at run time, and "
                                     "the script touches the transcript area")
                else:
                    analyse_shell(s, ctx, depth + 1)
        elif isinstance(n.func, ast.Attribute):
            recv = n.func.value
            if short in ("write_text", "write_bytes", "touch", "symlink_to", "hardlink_to",
                         "link_to", "unlink_missing"):
                target(recv, "." + short + "()s")
            elif short in ("rename", "replace") and len(n.args) == 1 and _looks_like_path(recv):
                target(recv, "." + short + "()s")
                if n.args:
                    target(n.args[0], "." + short + "()s onto")
            elif short == "open" and _looks_like_path(recv):
                mode = n.args[0] if n.args else kw.get("mode")
                if mode is not None and mode_writes(mode):
                    target(recv, "opens for writing")


def _looks_like_path(node):
    """A `.rename()`/`.replace()`/`.open()` receiver that is a Path, not a str."""
    if isinstance(node, ast.Constant):
        return False                         # "abc".replace(...) is string work
    if isinstance(node, ast.Call):
        fn = _dotted(node.func) or ""
        return fn.split(".")[-1] in ("Path", "PurePath", "PosixPath", "home", "resolve",
                                     "expanduser", "with_suffix", "with_name")
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
        return True
    return isinstance(node, (ast.Name, ast.Attribute, ast.Subscript))


# --------------------------------------------------------------------------
# entry
# --------------------------------------------------------------------------
WRITE_TOOLS = ("Write", "Edit", "MultiEdit", "NotebookEdit")


def offence(payload):
    """-> reason string if the call would write a transcript, else None."""
    tool = payload.get("tool_name")
    ti = payload.get("tool_input") or {}
    cwd = payload.get("cwd") or os.getcwd()
    try:
        if tool in WRITE_TOOLS:
            p = ti.get("file_path") or ti.get("notebook_path") or ""
            if p and is_protected(p, cwd):
                return "%s targets %r" % (tool, p)
            return None
        if tool == "Bash":
            cmd = ti.get("command") or ""
            analyse_shell(cmd, Ctx(cwd, cmd))
            return None
    except Refuse as e:
        return str(e)
    return None


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0
    try:
        why = offence(payload)
    except Exception:
        return 0                          # fail open
    if not why:
        return 0
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": (
                "Blocked: this would write a Claude Code transcript (%s).\n\n"
                "Session transcripts under ~/.claude/projects/**.jsonl (and "
                "subagents/*.jsonl) are written by the harness and nobody else: "
                "they are the evidence `--owner-said` is proven against, so an agent "
                "write to one could forge the owner's words. Reading them is fine.\n\n"
                "If this was a census or report, write the OUTPUT somewhere else, to a "
                "literal path (python: open('/abs/out.md', 'w')), and open transcripts "
                "read-only. See block_transcript_tamper.py." % why
            ),
        }
    }))
    return 0


if __name__ == "__main__":
    sys.exit(main())
