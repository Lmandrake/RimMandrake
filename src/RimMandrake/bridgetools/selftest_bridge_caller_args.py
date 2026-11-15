#!/usr/bin/env python3
"""Every literal jawa/ tool call in our Python names only keys the C# tool declares.

RIMMANDRAKE_CLOSE_CAMPAIGN_GATE_BYPASSES: the companion's argument guard (JawaBenchArgGuard.cs) REFUSES an
undeclared key on our own tools, where it used to record it and let the call run on its defaults (a typo'd
`dryRun` for `dry_run` mutated). This census is the offline half: it parses each `[Tool("jawa/...")]` method's
parameters and every Python call whose first argument is a literal "jawa/..." string, and reports a key the
tool would now refuse. Matching is case-insensitive, as the guard's is; the reserved expect* keys pass.

Exit 0 = no mismatch, 1 = mismatches (one line each), 2 = the instrument could not see (no tools parsed).
Blind spots, by construction: tool names or keys built at run time (f-strings, **kwargs from a variable)
are not checked; the count of such calls is printed, never folded into "clean".
"""
import ast
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
CS_DIR = os.path.join(HERE, "JawaBench.BridgeTools")
PY_ROOTS = [os.path.join(REPO, "src", "RimMandrake"), os.path.join(REPO, "skills")]
PREFIXES = "jawa|deepfire"          # the tool namespaces this companion declares
RESERVED = {"expectgameepoch", "expectmapid", "expectcurrentmapid"}
SKIP_TYPES = ("IRimBridgeContext", "CancellationToken")
# transport keywords of the client wrappers, never sent as tool arguments
TRANSPORT_KW = {"check", "timeout", "timeout_s", "retries", "_answer"}   # _answer: validation_core.Guarded drops it
# wrappers defined in another module whose own keywords are not tool arguments (callee name -> keywords)
CROSS_MODULE_KW = {"step": {"expect"}, "_bridge": {"read_only_static"}}

_STR = re.compile(r'@?"(?:[^"\\]|\\.)*"')


def _strip_strings(src):
    return _STR.sub('""', src)


def tool_params(cs_dir=CS_DIR):
    """{tool: set(lower-case param names)} from every [Tool("jawa/...")] method."""
    tools = {}
    for fn in sorted(os.listdir(cs_dir)):
        if not fn.endswith(".cs"):
            continue
        raw = open(os.path.join(cs_dir, fn), encoding="utf-8-sig").read()
        for m in re.finditer(r'\[Tool\(\s*"((?:%s)/[A-Za-z0-9_]+)"' % PREFIXES, raw):
            name = m.group(1)
            rest = _strip_strings(raw[m.end():])
            # the method signature: first "(" after "public static ... Name" that follows the attribute
            sig = re.search(r'\b(?:public|internal|private)\s+(?:static\s+)?[^(;{=]*?\b\w+\s*\(', rest)
            if not sig:
                continue
            i, depth = sig.end(), 1
            while i < len(rest) and depth:
                depth += {"(": 1, ")": -1}.get(rest[i], 0)
                i += 1
            params_src = rest[sig.end():i - 1]
            params_src = re.sub(r'\[[^\[\]]*(?:\[[^\[\]]*\][^\[\]]*)*\]', ' ', params_src)   # attributes
            names, depth, cur = set(), 0, ""
            for ch in params_src + ",":
                if ch in "(<[{":
                    depth += 1
                elif ch in ")>]}":
                    depth -= 1
                if ch == "," and depth == 0:
                    part = cur.split("=")[0].strip()
                    cur = ""
                    if not part or any(t in part for t in SKIP_TYPES):
                        continue
                    names.add(part.split()[-1].lower())
                else:
                    cur += ch
            tools[name] = names
    return tools


def _keys_of(node):
    """(keys, dynamic) of a dict literal / dict(...) call; dynamic=True when not fully literal."""
    if isinstance(node, ast.Dict):
        keys, dyn = [], False
        for k in node.keys:
            if isinstance(k, ast.Constant) and isinstance(k.value, str):
                keys.append(k.value)
            else:
                dyn = True
        return keys, dyn
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "dict":
        return [k.arg for k in node.keywords if k.arg], any(k.arg is None for k in node.keywords) or bool(node.args)
    if isinstance(node, ast.Constant) and node.value is None:
        return [], False
    return [], True


def calls_in(path):
    """[(line, tool, [keys], dynamic)] for each Call whose first positional arg is a literal jawa/ string."""
    src = open(path, encoding="utf-8", errors="replace").read()
    if "jawa/" not in src and "deepfire/" not in src:
        return []
    tree = ast.parse(src, filename=path)
    # a local wrapper `def call(tool, allow=False, **kw)` consumes its named keywords; only **kw reaches the tool
    wrapper_kw = {}
    for f in ast.walk(tree):
        if isinstance(f, (ast.FunctionDef, ast.AsyncFunctionDef)) and f.args.kwarg is not None:
            named = [a.arg for a in f.args.args + f.args.kwonlyargs if a.arg != "self"][1:]
            wrapper_kw.setdefault(f.name, set()).update(named)
    out = []
    for n in ast.walk(tree):
        if not isinstance(n, ast.Call) or not n.args:
            continue
        a0 = n.args[0]
        if not (isinstance(a0, ast.Constant) and isinstance(a0.value, str) and re.fullmatch(r"(?:%s)/[a-z0-9_]+" % PREFIXES, a0.value)):
            continue
        callee = n.func.id if isinstance(n.func, ast.Name) else n.func.attr if isinstance(n.func, ast.Attribute) else ""
        consumed = TRANSPORT_KW | wrapper_kw.get(callee, set()) | CROSS_MODULE_KW.get(callee, set())
        keys, dyn = [], False
        dict_args = len(n.args) > 1
        if dict_args:
            k, d = _keys_of(n.args[1])
            keys += k
            dyn |= d
        for kw in n.keywords:
            if dict_args and kw.arg not in ("params", "args", "arguments"):
                continue        # the dict carries the tool's arguments; keywords belong to the wrapper
            if kw.arg is None:
                k, d = _keys_of(kw.value)
                keys += k
                dyn |= d
            elif kw.arg in ("params", "args", "arguments"):
                k, d = _keys_of(kw.value)
                keys += k
                dyn |= d
            elif kw.arg not in consumed:
                keys.append(kw.arg)
        out.append((n.lineno, a0.value, keys, dyn))
    return out


def census(roots=PY_ROOTS, cs_dir=CS_DIR):
    tools = tool_params(cs_dir)
    bad, unparsable, dynamic, checked, unknown_tool = [], [], 0, 0, []
    exempt = [0]
    for root in roots:
        for d, dirs, files in os.walk(root):
            dirs[:] = [x for x in dirs if x not in ("__pycache__", ".git", "node_modules")]
            for fn in files:
                if not fn.endswith(".py"):
                    continue
                p = os.path.join(d, fn)
                if fn.startswith("selftest") and os.path.abspath(p) != os.path.abspath(__file__):
                    exempt[0] += 1      # selftests drive stub clients, never the companion
                    continue
                try:
                    found = calls_in(p)
                except (SyntaxError, ValueError):
                    unparsable.append(p)
                    continue
                for line, tool, keys, dyn in found:
                    rel = os.path.relpath(p, REPO)
                    if tool not in tools:
                        unknown_tool.append("%s:%d %s" % (rel, line, tool))
                        continue
                    checked += 1
                    dynamic += dyn
                    for k in keys:
                        if k.lower() not in tools[tool] and k.lower() not in RESERVED:
                            bad.append("%s:%d %s %s (declared: %s)" % (rel, line, tool, k, ", ".join(sorted(tools[tool])) or "none"))
    census.exempt = exempt[0]
    return tools, bad, unparsable, dynamic, checked, unknown_tool


def main():
    tools, bad, unparsable, dynamic, checked, unknown_tool = census()
    if not tools:
        print("UNMEASURED: no [Tool(\"jawa/...\")] methods parsed under %s" % CS_DIR)
        return 2
    for b in bad:
        print("MISMATCH " + b)
    for u in unknown_tool:
        print("NOTE tool not in source (retired or a prose name): " + u)
    print("%d tools parsed; %d literal calls checked (%d with run-time keys not checked); %d unparsable file(s)%s; "
          "%d selftest file(s) skipped (stub clients); %d mismatch(es)" % (len(tools), checked, dynamic, len(unparsable),
                               (": " + ", ".join(os.path.relpath(u, REPO) for u in unparsable[:5])) if unparsable else "",
                               census.exempt, len(bad)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
