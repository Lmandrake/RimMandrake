#!/usr/bin/env python3
"""Narrow C# source reading for the Graffiti offline selftests (selftest_graffiti_weather.py, selftest_graffiti_raid_tag_wall.py,
selftest_graffiti_message_counters.py): find one method's declaration and body, the methods a body calls, a class's base type.

Not a C# parser. It matches braces with strings, chars and comments skipped, which is enough for the mod's own hand-written files; a
selftest that cannot find what it reads says so and fails, never passes on a miss.
"""
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
GRAFFITI_SOURCE = os.path.join(REPO, "src", "RimMandrake", "Graffiti", "Source")

_MODS = r"(?:(?:public|private|internal|protected|static|override|virtual|abstract|sealed|new|unsafe|extern|async)\s+)*"
_DECL = r"(?m)^[ \t]*" + _MODS + r"(?:[\w.<>\[\],?]+(?:\s*<[^>]*>)?\s+)?{name}\s*\("


def strip_comments(text):
    """The source with // and /* */ comments blanked (same length, newlines kept), strings left alone."""
    out, i, n = [], 0, len(text)
    while i < n:
        c = text[i]
        if text.startswith("//", i):
            j = text.find("\n", i)
            j = n if j < 0 else j
            out.append(" " * (j - i)); i = j
        elif text.startswith("/*", i):
            j = text.find("*/", i + 2)
            j = n if j < 0 else j + 2
            out.append(re.sub(r"[^\n]", " ", text[i:j])); i = j
        elif c in "\"'":
            j = _skip_literal(text, i)
            out.append(text[i:j]); i = j
        else:
            out.append(c); i += 1
    return "".join(out)


def _skip_literal(text, i):
    q = text[i]
    verbatim = i > 0 and text[i - 1] == "@"
    j = i + 1
    while j < len(text):
        if not verbatim and text[j] == "\\":
            j += 2
            continue
        if text[j] == q:
            if verbatim and j + 1 < len(text) and text[j + 1] == q:
                j += 2
                continue
            return j + 1
        j += 1
    return j


def _match(text, i, open_c, close_c):
    depth = 0
    while i < len(text):
        c = text[i]
        if c in "\"'":
            i = _skip_literal(text, i)
            continue
        if c == open_c:
            depth += 1
        elif c == close_c:
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return -1


def methods(text, name):
    """Every declaration of method `name` in comment-stripped `text` -> [(params, body)]. A `=> expr;` body is returned as `return expr;`."""
    found = []
    for m in re.finditer(_DECL.format(name=re.escape(name)), text):
        po = m.end() - 1
        pc = _match(text, po, "(", ")")
        if pc < 0:
            continue
        rest = text[pc + 1:]
        lead = re.match(r"\s*(?:where\s[^{=]*)?", rest).end()
        if rest[lead:lead + 1] == "{":
            bo = pc + 1 + lead
            bc = _match(text, bo, "{", "}")
            if bc > 0:
                found.append((text[po + 1:pc], text[bo + 1:bc]))
        elif rest[lead:lead + 2] == "=>":
            end = text.find(";", pc + 1 + lead)
            found.append((text[po + 1:pc], "return " + text[pc + 1 + lead + 2:end].strip() + ";"))
    return found


def read_source(root=GRAFFITI_SOURCE, skip=("SelfTest", "obj", "bin")):
    """{relative path: comment-stripped text} for every .cs under root."""
    out = {}
    for d, dirs, files in os.walk(root):
        dirs[:] = [x for x in dirs if x not in skip]
        for f in files:
            if f.endswith(".cs"):
                p = os.path.join(d, f)
                with open(p, encoding="utf-8-sig") as fh:
                    out[os.path.relpath(p, root)] = strip_comments(fh.read())
    return out


def find_method(sources, name):
    """[(file, params, body)] for `name` across the {file: text} map."""
    return [(f, p, b) for f, t in sorted(sources.items()) for p, b in methods(t, name)]


def calls_in(body):
    """Names called in a body: `Name(` and `X.Name(`, keywords dropped."""
    kw = {"if", "for", "foreach", "while", "switch", "return", "new", "nameof", "typeof", "catch", "using", "lock", "sizeof", "default"}
    return {m.group(1) for m in re.finditer(r"\b([A-Za-z_]\w*)\s*(?:<[\w, .]*>)?\s*\(", body) if m.group(1) not in kw}


def reachable(sources, start, depth=6):
    """Method names reachable from `start` through calls to methods declared in `sources` (by name, overloads merged)."""
    seen, frontier = {start}, [start]
    for _ in range(depth):
        nxt = []
        for name in frontier:
            for _, _, body in find_method(sources, name):
                for c in calls_in(body):
                    if c not in seen and find_method(sources, c):
                        seen.add(c)
                        nxt.append(c)
        frontier = nxt
    return seen


def class_bodies(text):
    """[(class name, base list, body)] for each class declared in text (nested classes appear inside their parent too)."""
    out = []
    for m in re.finditer(r"\bclass\s+(\w+)\s*(?::\s*([^{]+))?\{", text):
        bo = m.end() - 1
        bc = _match(text, bo, "{", "}")
        if bc > 0:
            out.append((m.group(1), (m.group(2) or "").strip(), text[bo + 1:bc]))
    return out


def top_level_terms(expr, op):
    """Split a C# boolean expression on `op` ('||' or '&&') outside parentheses."""
    terms, depth, cur, i = [], 0, [], 0
    while i < len(expr):
        c = expr[i]
        if c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
        if depth == 0 and expr.startswith(op, i):
            terms.append("".join(cur).strip()); cur = []; i += len(op)
            continue
        cur.append(c); i += 1
    terms.append("".join(cur).strip())
    return terms
