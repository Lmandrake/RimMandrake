"""Static contract check over every OFFLINE fake of a bridge tool: a fake must not do what the live tool refuses.

jawa/destroy_batch never removes a pawn, whatever `categories` says, and refuses any request naming 'Pawn'
(DESTROY_BATCH_NEVER_KILLS_PAWNS_1). Fakes that removed pawns on Pawn/All let suites' pad resets look clean
offline while the live game kept every pawn. This finds each destroy_batch handler in src/ -- a function named
*destroy_batch, or an `if <x> == "jawa/destroy_batch":` block -- and reports any that mutates pawn state.

    python3 fake_contracts.py [src_root]     prints offenders, exit 1 if any
"""
import ast
import os
import sys

TOOL = "jawa/destroy_batch"
SKIP_DIRS = {".git", "__pycache__", "node_modules", "Textures", "Assemblies", "obj", "bin"}


def _txt(node):
    try:
        return ast.unparse(node)
    except Exception:
        return ""


def _handlers(tree):
    """(lineno, [stmts]) for every destroy_batch handler in a module."""
    out = []
    for n in ast.walk(tree):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name.endswith("destroy_batch"):
            out.append((n.lineno, n.body))
        elif isinstance(n, ast.If) and isinstance(n.test, ast.Compare) and len(n.test.ops) == 1 \
                and isinstance(n.test.ops[0], ast.Eq):
            sides = [n.test.left] + list(n.test.comparators)
            if any(isinstance(s, ast.Constant) and s.value == TOOL for s in sides):
                out.append((n.lineno, n.body))
    return out


def _pawn_mutations(stmts):
    """Source lines inside stmts that remove or rewrite pawn state."""
    hits = []
    for s in stmts:
        for n in ast.walk(s):
            if isinstance(n, ast.Delete):
                hits += [(n.lineno, _txt(n)) for t in n.targets if "pawn" in _txt(t).lower()]
            elif isinstance(n, (ast.Assign, ast.AugAssign, ast.AnnAssign)):
                targets = n.targets if isinstance(n, ast.Assign) else [n.target]
                hits += [(n.lineno, _txt(n)[:120]) for t in targets
                         if not isinstance(t, ast.Name) and "pawn" in _txt(t).lower()]
            elif isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) \
                    and n.func.attr in ("pop", "remove", "clear", "discard", "popitem") \
                    and "pawn" in _txt(n.func.value).lower():
                hits.append((n.lineno, _txt(n)[:120]))
    return hits


def audit_source(text, name="<string>"):
    """[(file, handler_line, mutation_line, code)] for one module's source."""
    try:
        tree = ast.parse(text, name)
    except SyntaxError:
        return []
    return [(name, hl, ml, code) for hl, body in _handlers(tree) for ml, code in _pawn_mutations(body)]


def audit(root):
    """(offenders, handlers_seen) over every .py under root. handlers_seen is the sanity probe: a scan that
    finds no handler at all has proved nothing."""
    offenders, seen = [], 0
    for d, dirs, files in os.walk(root):
        dirs[:] = [x for x in dirs if x not in SKIP_DIRS]
        for f in files:
            if not f.endswith(".py"):
                continue
            p = os.path.join(d, f)
            try:
                text = open(p, encoding="utf-8", errors="replace").read()
            except OSError:
                continue
            if TOOL not in text and "destroy_batch" not in text:
                continue
            try:
                seen += len(_handlers(ast.parse(text, p)))
            except SyntaxError:
                continue
            offenders += audit_source(text, os.path.relpath(p, root))
    return offenders, seen


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    root = sys.argv[1] if len(sys.argv) > 1 else os.path.normpath(os.path.join(here, "..", "..", ".."))
    bad, n = audit(root)
    for f, hl, ml, code in bad:
        print("%s:%d (handler at %d): %s" % (f, ml, hl, code))
    print("%d destroy_batch handler(s) scanned, %d pawn mutation(s)" % (n, len(bad)))
    sys.exit(1 if bad or n == 0 else 0)
