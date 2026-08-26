"""rimplace.contract - what parameters each jawa/ tool ACTUALLY takes.

WHY THIS FILE EXISTS
====================
`rimplace calls` compiled `{"rect": "171,171,4,8", "terrainDef": "Gravel"}` for
jawa/set_terrain_batch for as long as it had existed. **No such parameter.** The
tool takes `ops`, in the grammar 'Def:x,z,w,h' joined by ';'. Four of one
dwelling's thirteen compiled calls could not execute, taking all 112 terrain and
180 roof cells with them - and 23/23 rimplace selftests passed the whole time,
because the selftest compared the compiler against ITSELF.

TEMPLATE_RECT_PARAM_NOT_ACCEPTED_1. The bridge refused loudly, which is the only
reason this was a broken call list rather than a silent half-built house.

THE SOURCE OF TRUTH, AND WHY IT IS THIS ONE
===========================================
The companion C# is the definition of every jawa/ tool's parameter list, and it
is a FILE - so this check runs offline, with no game, no bridge and no dump. The
live `tools/list` is a better answer when a game is up (it knows what actually
registered), but it is not available at 3am with the game down, and a contract
check nobody can run is a contract check nobody runs.

⚠️ WHAT THIS CANNOT SEE. It reads the parameter NAMES a tool declares. It does
not know a name is required, what a value must look like, or that `ops` wants
'Def:x,z,w,h' rather than 'x,z,w,h:Def'. A call whose every key is real can still
be nonsense - so a pass here means "no key is invented", never "the call works".
"""
from __future__ import annotations

import re
from pathlib import Path

_HERE = Path(__file__).resolve().parent
# src/RimMandrake/Utils/rimplace -> src/RimMandrake/bridgetools/...
_SOURCE = (_HERE.parents[1] / "bridgetools" / "JawaBench.BridgeTools")

_TOOL = re.compile(r'\[Tool\(\s*\n?\s*"(jawa/[a-z_0-9]+)"')
_ATTR = re.compile(r'\[[^\]]*\]')
# ⚠️ Deliberately NOT one regex over the whole parameter list. The first version
# was, and it anchored each parameter on the comma before it - so a match that
# CONSUMED its trailing comma hid the next parameter entirely. It found all 7 of
# build_batch's (every line ends '= null,', so the match stopped at the '=') and
# silently dropped `terrainDef` and `roofDef`, whose predecessor is a bare
# 'string ops,'. Attributes come out first, then a plain split on commas.
_PARAM = re.compile(r'^\s*(?:params\s+)?'
                    r'(?:string|bool|int|long|float|double)\s+(\w+)\s*(?:=|$)')


def _blank_strings(text: str) -> str:
    """Replace the CONTENT of every string literal with spaces, preserving
    length so indices taken from the original text still line up.

    Necessary because a [Tool(...)] description is prose full of commas,
    brackets and parentheses - '(1,2)', 'ops: Def:x,z,w,h' - and every one of
    them would confuse a paren-matcher or a parameter regex.
    """
    out, i, n, instr = [], 0, len(text), False
    while i < n:
        c = text[i]
        if not instr:
            out.append(c)
            if c == '"':
                instr = True
        else:
            if c == '\\' and i + 1 < n:
                out.append('  ')
                i += 2
                continue
            if c == '"':
                out.append('"')
                instr = False
            else:
                out.append('\n' if c == '\n' else ' ')
        i += 1
    return ''.join(out)


def _params_after(blank: str, start: int) -> set[str]:
    """The parameter names of the method whose [Tool] attribute starts here."""
    sig = blank.find("Task<object>", start)
    if sig < 0:
        return set()
    open_paren = blank.find("(", sig)
    if open_paren < 0:
        return set()
    depth, i, n = 0, open_paren, len(blank)
    while i < n:
        if blank[i] == '(':
            depth += 1
        elif blank[i] == ')':
            depth -= 1
            if depth == 0:
                break
        i += 1
    body = _ATTR.sub(" ", blank[open_paren + 1:i])
    names = set()
    for piece in body.split(","):
        m = _PARAM.match(piece)
        if m:
            names.add(m.group(1))
    return names


def tool_parameters(source_dir: Path | None = None) -> dict[str, set[str]] | None:
    """{tool name -> declared parameter names}, or None if unreadable.

    🔑 None means UNMEASURED. A caller must report that, never treat it as a
    pass - an absent contract is exactly when a wrong key ships.
    """
    src = Path(source_dir) if source_dir else _SOURCE
    if not src.is_dir():
        return None
    found: dict[str, set[str]] = {}
    for cs in sorted(src.rglob("*.cs")):
        if "obj" in cs.parts or "bin" in cs.parts:
            continue
        try:
            raw = cs.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        blank = _blank_strings(raw)
        for m in _TOOL.finditer(raw):
            found[m.group(1)] = _params_after(blank, m.start())
    if not found:
        return None
    # Validate the parse against a KNOWN answer before anyone trusts it. If the
    # C# is ever restructured past this parser, it must read UNMEASURED rather
    # than quietly returning a short list that passes everything.
    known = {
        "jawa/set_terrain_batch": {"ops", "terrainDef", "layer", "refresh"},
        "jawa/build_batch": {"ops", "stuff", "faction", "quality",
                             "hitPoints", "wipeExisting", "readBack"},
    }
    for tool, expect in known.items():
        if found.get(tool) != expect:
            return None
    return found


def check_calls(calls: list[dict], params: dict[str, set[str]] | None) -> list[str]:
    """Every emitted key must be a parameter the tool declares.

    Keys starting with '_' are rimplace's own markers (cli.py strips them before
    the call is sent) and are deliberately exempt.
    """
    if params is None:
        return ["UNMEASURED: the companion source could not be parsed, so no "
                "call was contract-checked. This is not a pass."]
    bad = []
    for c in calls:
        tool = c.get("tool", "?")
        if tool not in params:
            bad.append(f"{tool}: no such tool in the companion source")
            continue
        for k in sorted(c.get("params", {})):
            if k.startswith("_"):
                continue
            if k not in params[tool]:
                bad.append(f"{tool}: '{k}' is not a parameter of that tool "
                           f"(it takes {', '.join(sorted(params[tool]))})")
    return bad
