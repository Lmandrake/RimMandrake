#!/usr/bin/env python3
"""Census of per-frame Update overrides in C# trees.

Usage: tickburst_guard_census.py <label>=<root> [<label>=<root> ...] --out <json>

Walks *.cs under each root and records every method definition named
WorldUpdate, MapComponentUpdate, GameComponentUpdate or WorldComponentUpdate.
Each hit: {root (label), file (relative to root), line, class (innermost
enclosing `class X` declaration), method}. String literals and comments are
skipped, so selftests that quote a method header are not counted. Used by TICKBURST guard G5.
"""
import argparse
import json
import os
import re
import sys

METHOD_RE = re.compile(
    r"\bvoid\s+(WorldUpdate|MapComponentUpdate|GameComponentUpdate|WorldComponentUpdate)\s*\(")
CLASS_RE = re.compile(r"\bclass\s+([A-Za-z_][A-Za-z0-9_]*)")


STRING_RE = re.compile(r'@"(?:[^"]|"")*"|\$?"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])\'')


def _code_only(text):
    """Drop string/char literals and // comments, so text quoted inside a
    selftest (e.g. "public override void MapComponentUpdate()") is no hit."""
    text = STRING_RE.sub('""', text)
    cut = text.find("//")
    return text if cut < 0 else text[:cut]


def scan_file(path):
    """Return (line, enclosing class, method) per hit. The class is the
    innermost class whose braces enclose the hit (nested classes pop when
    their body closes), falling back to the nearest preceding declaration."""
    hits = []
    stack = []          # [(class name, brace depth inside its body)]
    pending = None      # declared class whose '{' has not been seen yet
    depth = 0
    in_block = False
    try:
        with open(path, encoding="utf-8-sig", errors="replace") as fh:
            for no, raw in enumerate(fh, 1):
                text = raw
                if in_block:
                    end = text.find("*/")
                    if end < 0:
                        continue
                    text = text[end + 2:]
                    in_block = False
                text = _code_only(text)
                while "/*" in text:
                    a = text.index("/*")
                    b = text.find("*/", a + 2)
                    if b < 0:
                        text = text[:a]
                        in_block = True
                        break
                    text = text[:a] + text[b + 2:]
                for m in METHOD_RE.finditer(text):
                    cls = stack[-1][0] if stack else pending
                    hits.append((no, cls, m.group(1)))
                decls = [(m.start(), m.group(1)) for m in CLASS_RE.finditer(text)]
                for i, ch in enumerate(text):
                    while decls and decls[0][0] <= i:
                        pending = decls.pop(0)[1]
                    if ch == "{":
                        depth += 1
                        if pending is not None:
                            stack.append((pending, depth))
                            pending = None
                    elif ch == "}":
                        depth -= 1
                        while stack and stack[-1][1] > depth:
                            stack.pop()
    except OSError as exc:
        print(f"WARN cannot read {path}: {exc}", file=sys.stderr)
    return hits


def walk(label, root):
    out = []
    files = 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in (".git", "bin", "obj"))
        for name in sorted(filenames):
            if not name.endswith(".cs"):
                continue
            files += 1
            full = os.path.join(dirpath, name)
            rel = os.path.relpath(full, root).replace(os.sep, "/")
            for line, cls, method in scan_file(full):
                out.append({"root": label, "file": rel, "line": line,
                            "class": cls, "method": method})
    return out, files


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("roots", nargs="+", help="label=root pairs")
    ap.add_argument("--out", required=True, help="output JSON path")
    args = ap.parse_args(argv)
    roots, hits = [], []
    for spec in args.roots:
        if "=" not in spec:
            ap.error(f"root must be label=path: {spec}")
        label, root = spec.split("=", 1)
        if not os.path.isdir(root):
            ap.error(f"not a directory: {root}")
        found, nfiles = walk(label, root)
        roots.append({"label": label, "path": root, "cs_files": nfiles,
                      "hits": len(found)})
        hits.extend(found)
    doc = {"roots": roots, "count": len(hits), "hits": hits}
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=1)
        fh.write("\n")
    per = ", ".join(f"{r['label']}={r['hits']}/{r['cs_files']} files" for r in roots)
    print(f"tickburst_guard_census: {len(hits)} hits ({per}) -> {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
