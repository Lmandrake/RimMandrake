#!/usr/bin/env python3
"""brief_text.py - the bytes of a judge's brief file that its calibration hash reads (refusal_contract.brief_hash).

A docstring, a comment or a blank line between code lines of a `.py` file is not brief text: no model reads it, so its
edit must not reset the judge to UNTESTED. Page: design/specs/2026-11-24-brief-text-hash/boundary.md."""
import ast
import io
import tokenize

READERS = ("getdoc", "getsource", "getsourcelines")   # a call of one of these can put a docstring before a model
CLI_TEXT = ("description", "epilog")                  # argparse keywords: text a person reads
SKIP = {tokenize.COMMENT, tokenize.NL, tokenize.NEWLINE, tokenize.INDENT, tokenize.DEDENT, tokenize.ENDMARKER,
        tokenize.ENCODING}


def _is_doc_name(n):
    return isinstance(n, ast.Name) and n.id == "__doc__" or isinstance(n, ast.Attribute) and n.attr == "__doc__"


def _reads_docstrings(tree):
    shown = set()   # the __doc__ names that a print or an argparse keyword takes
    for n in ast.walk(tree):
        if not isinstance(n, ast.Call):
            continue
        args = [k.value for k in n.keywords if k.arg in CLI_TEXT]
        if isinstance(n.func, ast.Name) and n.func.id == "print":
            args += n.args
        shown.update(id(m) for a in args for m in ast.walk(a) if _is_doc_name(m))
    for n in ast.walk(tree):
        if _is_doc_name(n) and id(n) not in shown:
            return True
        if isinstance(n, ast.Constant) and n.value == "__doc__":
            return True
        if getattr(n, "attr", None) in READERS or getattr(n, "id", None) in READERS:
            return True
        if isinstance(n, ast.alias) and n.name in READERS:
            return True
    return False


def _docstring_lines(tree):
    out = set()
    for n in ast.walk(tree):
        if isinstance(n, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)) and n.body:
            e = n.body[0]
            if isinstance(e, ast.Expr) and isinstance(e.value, ast.Constant) and isinstance(e.value.value, str):
                out.add((e.lineno, e.end_lineno))
    return out


def rule_bytes(rel, data):
    """-> the bytes of brief file `rel` that count. `data` whole for a file that is not Python, that does not parse or
    that reads its own docstrings; else its code lines, with no docstring, comment or blank line between them."""
    if not rel.endswith(".py"):
        return data
    try:
        text = data.decode("utf-8")
        tree = ast.parse(text)
        toks = list(tokenize.generate_tokens(io.StringIO(text).readline))
    except (SyntaxError, ValueError, tokenize.TokenError):   # UnicodeDecodeError is a ValueError
        return data
    if _reads_docstrings(tree):
        return data
    docs = _docstring_lines(tree)
    keep, cut = set(), {}
    for t in toks:
        if t.type == tokenize.COMMENT:
            cut[t.start[0]] = t.start[1]
        elif t.type not in SKIP and not (t.type == tokenize.STRING and (t.start[0], t.end[0]) in docs):
            keep.update(range(t.start[0], t.end[0] + 1))
    lines = io.StringIO(text).readlines()                   # the same line split as the tokenizer's
    out = []
    for i, line in enumerate(lines, 1):
        if i in keep:
            out.append(line[:cut[i]].rstrip() + "\n" if i in cut else line)
    return "".join(out).encode("utf-8")
