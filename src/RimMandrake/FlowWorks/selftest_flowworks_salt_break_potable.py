#!/usr/bin/env python3
"""selftest_flowworks_salt_break_potable.py — the salt-water break sees every potable source (SALT_BREAK_FIX_MISSES_POTABLE_SOURCES).

WHY: GPT review FA_core_sim_3.4 (2026-10-23): RM_SaltBreakUtility.PotableReachable asked only bottles, tanks and
terrain, while JobGiver_RM_Drink also drinks from buckets/barrels, water items and pipe faucets — so a parched pawn
with a bucket of fresh water in reach could still take the brine-drinking break. PotableReachable is Verse-bound (the
C# SelfTest cannot run it), so this reads the PRODUCTION .cs (comments masked) and asserts that every source finder
JobGiver_RM_Drink calls is also asked by PotableReachable, with the Potable filter.

CAN IT FAIL: the source list is read from JobGiver_RM_Drink itself (not hard-coded), and each run applies an undo
splice that removes one source from PotableReachable in memory; the check must go RED on that copy.

BEHAVIOUR (gen 3, blind checker's gaps): a presence check stays green when a branch returns false, a finder is
tested `== null`, or the filter variable is bound to BreakOnly. So PotableReachable is also parsed into its statements
and EVALUATED as a truth model: each finder is a source that is either in reach (non-null / true) or not, with
drinkFromTerrain on. With exactly one source in reach it must return true, for every source; with none it must return
false; and every finder's last argument must be RM_DrinkUse.Potable (literally or through a local bound to it). Any
statement or term the model does not understand fails. Mutants for each gap are applied in memory and must go RED.

    python3 src/RimMandrake/FlowWorks/selftest_flowworks_salt_break_potable.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

THIRST = Path(__file__).resolve().parent / "Source" / "Thirst"
FINDER = re.compile(r"\b((?:RM_\w+|Building_RM_\w+)\.(?:Best\w+|TryFindDrinkCell))\(")


def mask_comments(text: str) -> str:
    """Blank // and /* */ comments (keeping strings) so a source named only in a comment does not count."""
    out, i, n = [], 0, len(text)
    while i < n:
        c = text[i]
        if c == '"':
            j = i + 1
            while j < n and text[j] != '"':
                j += 2 if text[j] == "\\" else 1
            out.append(text[i:j + 1]); i = j + 1
        elif text.startswith("//", i):
            j = text.find("\n", i)
            j = n if j < 0 else j
            out.append(" " * (j - i)); i = j
        elif text.startswith("/*", i):
            j = text.find("*/", i + 2)
            j = n if j < 0 else j + 2
            out.append(re.sub(r"[^\n]", " ", text[i:j])); i = j
        else:
            out.append(c); i += 1
    return "".join(out)


def block_after(text: str, anchor: str) -> str | None:
    m = re.search(anchor, text)
    if not m:
        return None
    i = text.find("{", m.end())
    depth = 0
    for j in range(i, len(text)):
        depth += {"{": 1, "}": -1}.get(text[j], 0)
        if depth == 0:
            return text[i:j + 1]
    return None


def finders(block: str) -> set[str]:
    return set(FINDER.findall(block))


class ModelError(Exception):
    pass


def _match(text: str, i: int, open_c: str, close_c: str) -> int:
    """Index just past the bracket matching text[i] == open_c."""
    depth = 0
    for j in range(i, len(text)):
        if text[j] == open_c:
            depth += 1
        elif text[j] == close_c:
            depth -= 1
            if depth == 0:
                return j + 1
    raise ModelError(f"unbalanced {open_c} at {i}")


def _split_top(expr: str, sep: str) -> list[str]:
    parts, depth, start, i = [], 0, 0, 0
    while i < len(expr):
        c = expr[i]
        if c in "([{":
            depth += 1
        elif c in ")]}":
            depth -= 1
        elif depth == 0 and expr.startswith(sep, i):
            parts.append(expr[start:i]); i += len(sep); start = i; continue
        i += 1
    parts.append(expr[start:])
    return [p.strip() for p in parts]


def parse_reach(block: str) -> tuple[dict[str, str], list[tuple[str, str]], str]:
    """PotableReachable's body -> (locals, [(condition, 'true'|'false')], final return expression)."""
    body = block.strip()[1:-1]
    local: dict[str, str] = {}
    branches: list[tuple[str, str]] = []
    i, n = 0, len(body)
    while True:
        while i < n and body[i].isspace():
            i += 1
        if i >= n:
            raise ModelError("no final return")
        if re.match(r"if\b", body[i:]):
            p = body.index("(", i)
            e = _match(body, p, "(", ")")
            cond = body[p + 1:e - 1]
            m = re.match(r"\s*\{\s*return\s+(true|false)\s*;\s*\}", body[e:])
            if not m:
                raise ModelError(f"if-branch is not a bare return true/false: {body[e:e + 60]!r}")
            branches.append((" ".join(cond.split()), m.group(1)))
            i = e + m.end()
        elif re.match(r"return\b", body[i:]):
            j = body.index(";", i)
            if body[j + 1:].strip():
                raise ModelError("code after the final return")
            return local, branches, " ".join(body[i + 6:j].split())
        else:
            j = body.index(";", i)
            m = re.fullmatch(r"\s*(\w+)\s+(\w+)\s*=\s*([\w.]+)\s*", body[i:j])
            if not m:
                raise ModelError(f"statement the model does not understand: {body[i:j]!r}")
            local[m.group(2)] = m.group(3)
            i = j + 1


def eval_term(term: str, inreach: set[str], local: dict[str, str], seen: list[str]) -> bool:
    term = term.strip()
    if term in ("true", "false"):
        return term == "true"
    if term == "RM_ThirstSettings.drinkFromTerrain":
        return True
    neg = term.startswith("!")
    if neg:
        term = term[1:].strip()
    m = FINDER.match(term)
    if not m:
        raise ModelError(f"term the model does not understand: {term!r}")
    p = term.index("(")
    e = _match(term, p, "(", ")")
    args = _split_top(term[p + 1:e - 1], ",")
    last = args[-1]
    if local.get(last, last) != "RM_DrinkUse.Potable":
        raise ModelError(f"{m.group(1)} is filtered by {last!r} = {local.get(last, last)!r}, not RM_DrinkUse.Potable")
    seen.append(m.group(1))
    found = m.group(1) in inreach
    rest = term[e:].strip()
    if rest == "!= null":
        val = found
    elif rest == "== null":
        val = not found
    elif rest == "":
        val = found
    else:
        raise ModelError(f"comparison the model does not understand: {term!r}")
    return (not val) if neg else val


def eval_expr(expr: str, inreach: set[str], local: dict[str, str], seen: list[str]) -> bool:
    if "||" in expr:
        raise ModelError(f"|| not modelled: {expr!r}")
    return all([eval_term(t, inreach, local, seen) for t in _split_top(expr, "&&")])


def run_model(block: str, inreach: set[str]) -> tuple[bool, list[str]]:
    local, branches, final = parse_reach(block)
    seen: list[str] = []
    for cond, ret in branches:
        if eval_expr(cond, inreach, local, seen):
            return ret == "true", seen
    return eval_expr(final, inreach, local, seen), seen


def behaviour(reach: str, want: set[str]) -> list[str]:
    """Each source alone in reach -> true; nothing in reach -> false."""
    fails: list[str] = []
    try:
        none, _ = run_model(reach, set())
        if none:
            fails.append("model: PotableReachable is true with NO potable source in reach")
        for src in sorted(want):
            got, _ = run_model(reach, {src})
            if not got:
                fails.append(f"model: PotableReachable is false with only {src} in reach")
        _, seen = run_model(reach, set())
        for src in sorted(want - set(seen)):
            fails.append(f"model: {src} is never evaluated when nothing is in reach")
    except (ModelError, ValueError) as ex:
        fails.append(f"model: {ex}")
    return fails


def check(salt_src: str, drink_src: str) -> list[str]:
    """Return failures (empty = pass)."""
    fails: list[str] = []
    giver = block_after(drink_src, r"Job\s+TryGiveJob\(Pawn pawn\)")
    reach = block_after(salt_src, r"static\s+bool\s+PotableReachable\(Pawn pawn, float level\)")
    if giver is None or reach is None:
        return ["could not find JobGiver_RM_Drink.TryGiveJob or PotableReachable"]
    want = finders(giver)
    if len(want) < 6:
        fails.append(f"instrument: JobGiver_RM_Drink shows only {len(want)} source finders {sorted(want)} (expected 6)")
    have = finders(reach)
    for f in sorted(want - have):
        fails.append(f"PotableReachable does not ask {f}")
    for call in re.finditer(FINDER, reach):
        tail = reach[call.end():reach.find(")", call.end()) + 1]
        if not re.search(r"\bpotable\)", tail):
            fails.append(f"{call.group(1)} in PotableReachable is not filtered to Potable")
    fails += behaviour(reach, want)
    return fails


def main() -> int:
    salt = mask_comments((THIRST / "RM_SaltBreak.cs").read_text(encoding="utf-8"))
    drink = mask_comments((THIRST / "RM_ThirstJobs.cs").read_text(encoding="utf-8"))
    bad = check(salt, drink)
    for b in bad:
        print("FAIL", b)
    # can-fail: drop each of the three sources the review found missing; each copy must go red.
    undos = ["RM_ThirstContainerUtility.BestContainer(", "RM_WaterItemUtility.BestItem(", "Building_RM_PipeFaucet.BestFaucet("]
    for u in undos:
        if u not in salt:
            print("FAIL undo anchor missing:", u); bad.append(u); continue
        broken = salt.replace(u, "RM_Gone.Missing(")
        if not check(broken, drink):
            print("FAIL undo stayed green:", u); bad.append(u)
    # can-fail, behaviour: the blind checker's three mutants (gen 2), plus a drop-the-terrain-branch one.
    mutants = [
        ("container branch returns false", r"(BestContainer\([^;]*?\)\s*!=\s*null\s*\)\s*\{\s*return\s+)true", r"\1false"),
        ("faucet tested == null", r"(BestFaucet\([^;]*?\)\s*)!=(\s*null)", r"\1==\2"),
        ("filter bound to BreakOnly", r"(RM_DrinkUse\s+potable\s*=\s*)RM_DrinkUse\.Potable", r"\1RM_DrinkUse.BreakOnly"),
        ("bottle tested == null", r"(BestBottle\([^;]*?\)\s*)!=(\s*null)", r"\1==\2"),
    ]
    for label, pat, rep in mutants:
        broken, k = re.subn(pat, rep, salt, count=1)
        if k != 1:
            print("FAIL mutant anchor missing:", label); bad.append(label); continue
        if not check(broken, drink):
            print("FAIL mutant stayed green:", label); bad.append(label)
    if bad:
        return 1
    n = len(finders(block_after(drink, r"Job\s+TryGiveJob\(Pawn pawn\)")))
    print(f"PASS salt-break PotableReachable asks all {n} drink sources with the Potable filter; {len(undos)} undo splices and {len(mutants)} behaviour mutants go red")
    return 0


if __name__ == "__main__":
    sys.exit(main())
