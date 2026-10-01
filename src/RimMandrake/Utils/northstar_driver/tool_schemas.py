#!/usr/bin/env python3
"""Committed snapshot of the bridge's declared tool schemas (LINT_CALLS_1).

    tool_schemas.json   {"_source": ..., "tools": {name: {"parameters": [...], "required": [...]}}}

The lint (lint_calls.py) checks every literal bridge call against it, offline.

REFRESH (only the bridge holder may run --live; --from-census is offline):
    python3 tool_schemas.py --from-census <file> [--supplement-csharp <dir>]
    python.exe tool_schemas.py --live [--supplement-csharp <dir>]
`--list-tools` prints {"count": N, "tools": [{name, parameters:[{name,required}], inputSchema}]}.
Required = parameters flagged required, plus inputSchema.required.
--supplement-csharp adds [Tool] methods a census lacks (a census can predate a DLL build);
those entries carry "source": "csharp" and take required = parameters with no `= default`.
A fresh --live refresh makes the supplement unnecessary; run it without the flag.
"""
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SNAPSHOT = os.path.join(HERE, "tool_schemas.json")
CLIENT = os.path.join(os.path.dirname(HERE), "rimbridge_client.py")
_SKIP_TYPES = ("IRimBridgeContext", "CancellationToken")


def build(census, source):
    tools = {}
    for t in census["tools"]:
        schema = t.get("inputSchema") or {}
        params = set((schema.get("properties") or {}).keys())
        req = set(schema.get("required") or [])
        plist = t.get("parameters")
        if isinstance(plist, list):
            for p in plist:
                params.add(p["name"])
                if p.get("required"):
                    req.add(p["name"])
        tools[t["name"]] = {"parameters": sorted(params), "required": sorted(req)}
    return {"_source": source, "tools": dict(sorted(tools.items()))}


def _skip_string(src, i):
    """src[i] == '"'. Return index just past the literal (handles @"..." verbatim and \\ escapes)."""
    n = len(src)
    if i > 0 and src[i - 1] == "@":
        i += 1
        while i < n:
            if src[i] == '"':
                if src[i + 1:i + 2] == '"':
                    i += 2
                    continue
                return i + 1
            i += 1
        return n
    i += 1
    while i < n and src[i] != '"':
        i += 2 if src[i] == "\\" else 1
    return i + 1


def _balanced(src, i, open_c="(", close_c=")"):
    """Index just past the group opened at src[i]."""
    depth = 0
    n = len(src)
    while i < n:
        c = src[i]
        if c == '"':
            i = _skip_string(src, i)
            continue
        if c == "'":
            i += 1
            while i < n and src[i] != "'":
                i += 2 if src[i] == "\\" else 1
        elif c == open_c:
            depth += 1
        elif c == close_c:
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    return n


def _split_top(text):
    parts, depth, cur, i, n = [], 0, [], 0, len(text)
    while i < n:
        c = text[i]
        if c == '"':
            j = _skip_string(text, i)
            cur.append(text[i:j])
            i = j
            continue
        if c in "([{<":
            depth += 1
        elif c in ")]}>":
            depth -= 1
        if c == "," and depth == 0:
            parts.append("".join(cur))
            cur = []
        else:
            cur.append(c)
        i += 1
    parts.append("".join(cur))
    return [p.strip() for p in parts if p.strip()]


_SIG = re.compile(r"\b(?:public|internal)\s+(?:static\s+)?(?:async\s+)?[\w<>\[\],.? ]+?\s+\w+\s*\(")


def parse_csharp(src):
    """[Tool("ns/name")] methods -> {name: {parameters, required}}. Required = no `= default`."""
    tools = {}
    for m in re.finditer(r'\[Tool\(\s*"([A-Za-z_]+/[A-Za-z0-9_]+)"', src):
        sig = _SIG.search(src, _balanced(src, src.index("(", m.start())))
        if not sig:
            continue
        end = _balanced(src, sig.end() - 1)
        plist = re.sub(r"\s+", " ", src[sig.end():end - 1])
        params, required = [], []
        for part in _split_top(plist):
            while part.startswith("["):
                part = part[_balanced(part, 0, "[", "]"):].strip()
            decl = part.split("=", 1)[0].strip()
            if not decl or any(t in decl for t in _SKIP_TYPES):
                continue
            name = decl.split()[-1]
            params.append(name)
            if "=" not in part:
                required.append(name)
        tools[m.group(1)] = {"parameters": sorted(params), "required": sorted(required), "source": "csharp"}
    return tools


def supplement_csharp(snap, directory):
    added = []
    for fn in sorted(os.listdir(directory)):
        if not fn.endswith(".cs"):
            continue
        with open(os.path.join(directory, fn), encoding="utf-8", errors="replace") as f:
            for name, spec in parse_csharp(f.read()).items():
                if name not in snap["tools"]:
                    snap["tools"][name] = spec
                    added.append(name)
                else:
                    # The census flags `required` false for our [Tool]s whose C# parameter has
                    # no default (MEASURED: bill_list thingId), so merge: params = union
                    # (source may be newer than the deployed DLL), required = C# no-default.
                    cur = snap["tools"][name]
                    cur["parameters"] = sorted(set(cur["parameters"]) | set(spec["parameters"]))
                    cur["required"] = sorted(set(cur["required"]) | set(spec["required"]))
    snap["tools"] = dict(sorted(snap["tools"].items()))
    return added


def save(snap):
    with open(SNAPSHOT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(snap, f, indent=1)
        f.write("\n")


def load(path=None):
    with open(path or SNAPSHOT, encoding="utf-8") as f:
        return json.load(f)


def main(argv):
    import datetime
    today = datetime.date.today().isoformat()
    if len(argv) >= 3 and argv[1] == "--from-census":
        with open(argv[2], encoding="utf-8") as f:
            census = json.load(f)
        snap = build(census, "census file %s (a live --list-tools capture), snapshot written %s"
                     % (argv[2].replace("\\", "/"), today))
    elif len(argv) >= 2 and argv[1] == "--live":
        out = subprocess.run([sys.executable, CLIENT, "--list-tools"], capture_output=True, text=True, check=True).stdout
        snap = build(json.loads(out), "live bridge --list-tools, %s" % today)
    else:
        print(__doc__)
        return 2
    if "--supplement-csharp" in argv:
        d = argv[argv.index("--supplement-csharp") + 1]
        added = supplement_csharp(snap, d)
        snap["_source"] += ("; +%d tools from C# [Tool] attributes in %s "
                            "(source=csharp: not yet seen in a live census); for tools in both, "
                            "params are the union and required adds every C# parameter with no default"
                            % (len(added), d.replace("\\", "/")))
    save(snap)
    print("wrote %s: %d tools (%s)" % (SNAPSHOT, len(snap["tools"]), snap["_source"]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
