#!/usr/bin/env python3
"""Hose port step-1 gate (design FINAL §3.9, G2.6): every TOP-LEVEL type in _Shared/SlackGeometry and _Shared/StylePicker
is `internal`, so GimmeSomeSlack and FlowWorks each carry their own copy and neither exports a type the other could pick
up by name. Members (operators, fields) may stay `public`; only top-level type declarations are gated.
Sanity probe: a planted `public class` line must be caught."""
import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SHARED = os.path.dirname(HERE)
DECL = re.compile(r"^\s*(public|internal)\s+(sealed |static |readonly |abstract |partial )*(class|struct|enum|interface)\s+(\w+)")


def top_level_public(text):
    """(name) of each top-level type declared public. Top level = brace depth 1 (inside the namespace)."""
    bad, depth = [], 0
    for line in text.split("\n"):
        m = DECL.match(line)
        if m and depth <= 1 and m.group(1) == "public":
            bad.append(m.group(4))
        code = re.sub(r'"(\\.|[^"\\])*"', '""', line.split("//")[0])
        depth += code.count("{") - code.count("}")
    return bad


def main():
    probs, n = [], 0
    files = sorted(glob.glob(os.path.join(SHARED, "SlackGeometry", "*.cs")) + glob.glob(os.path.join(SHARED, "StylePicker", "*.cs")))
    for f in files:
        t = open(f, encoding="utf-8").read()
        n += sum(1 for line in t.split("\n") if DECL.match(line))
        probs += ["%s: public top-level type %s" % (os.path.basename(f), b) for b in top_level_public(t)]
    if top_level_public("namespace X\n{\n    public sealed class Planted\n    {\n    }\n}\n") != ["Planted"]:
        probs.append("sanity: a planted public class was not caught")
    if top_level_public("namespace X\n{\n    internal class A\n    {\n        public struct Nested { }\n    }\n}\n"):
        probs.append("sanity: a nested public type was flagged as top-level")
    print("slackgeometry internal gate: %s -- %d files, %d type declarations" % ("PASS" if not probs and files else "FAIL", len(files), n))
    for p in probs:
        print("  - " + p)
    return 0 if not probs and files else 1


if __name__ == "__main__":
    sys.exit(main())
