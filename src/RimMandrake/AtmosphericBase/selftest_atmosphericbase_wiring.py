#!/usr/bin/env python3
"""selftest_atmosphericbase_wiring.py -- source-level check of the compositor wiring the C# kernel selftest cannot reach.

    python3 src/RimMandrake/AtmosphericBase/selftest_atmosphericbase_wiring.py   (exit 0 = clean, 1 = a wire is cut)

The kernel selftest (selftest_atmosphericbase_kernel.py) compiles RM_PatternModifiers.cs / RM_Quotas.cs and proves the
travelling ember and the hitch rule as pure functions. RM_AtmosphericCompositor.cs needs a live Map and is NOT compiled
there, so these two wires (spec §2.6a) were unproven:

  W1 ember: Evaluate passes ITS clock and the lamps' positions to RM_Hush.PickKeepers. Without the clock
     (PickKeepers' default time=0) the keeper never moves in game and the "observable travelling change" is lost.
     The position lists must be filled with t.Position.x / t.Position.z in the same loop that fills the id list,
     and the result must reach RM_Hush.Apply.
  W2 hitch: Evaluate counts a gap over RM_Hitch.MaxDelaySeconds (hitches++, maxGapSeconds) under
     RM_Hitch.IsHitch(lastTime, time), and only then stamps lastTime = time.

Comments are stripped before matching, so a commented-out call does not pass. Every run also applies MUTANTS (each
cut one wire, in memory) to the real compositor and requires the check to go red on every one: a check that cannot see
a cut wire fails the run.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
COMPOSITOR = os.path.join(HERE, "Source", "RM_AtmosphericCompositor.cs")


def strip_comments(src):
    out, i, n = [], 0, len(src)
    while i < n:
        if src.startswith("//", i):
            j = src.find("\n", i)
            i = n if j < 0 else j
        elif src.startswith("/*", i):
            j = src.find("*/", i + 2)
            i = n if j < 0 else j + 2
        elif src[i] == '"':
            j = i + 1
            while j < n and src[j] != '"':
                j += 2 if src[j] == "\\" else 1
            out.append(src[i:j + 1]); i = j + 1
        else:
            out.append(src[i]); i += 1
    return "".join(out)


def block_after(src, start):
    """The text of the {...} block whose opening brace is the first one at or after `start`."""
    i = src.index("{", start)
    depth = 0
    for j in range(i, len(src)):
        if src[j] == "{":
            depth += 1
        elif src[j] == "}":
            depth -= 1
            if depth == 0:
                return src[i + 1:j]
    raise ValueError("unbalanced braces")


def split_args(s):
    args, depth, cur = [], 0, ""
    for ch in s:
        if ch in "([{<":
            depth += 1
        elif ch in ")]}>":
            depth -= 1
        if ch == "," and depth == 0:
            args.append(cur.strip()); cur = ""
        else:
            cur += ch
    if cur.strip():
        args.append(cur.strip())
    return args


def call_args(src, name, start=0):
    """Argument list of the first call `name(` at or after start, or None."""
    m = re.compile(re.escape(name) + r"\s*\(").search(src, start)
    if not m:
        return None, -1
    depth, i = 1, m.end()
    while depth:
        depth += {"(": 1, ")": -1}.get(src[i], 0)
        i += 1
    return split_args(src[m.end():i - 1]), m.start()


def evaluate_body(src):
    m = re.search(r"public\s+int\s+Evaluate\s*\(\s*RM_MapComponent_AtmosphericBase\s+\w+\s*,\s*double\s+(\w+)", src)
    if not m:
        return None, None
    return m.group(1), block_after(src, m.end())


def check_ember(body, clock):
    fails = []
    args, at = call_args(body, "RM_Hush.PickKeepers")
    if args is None:
        return ["W1: Evaluate never calls RM_Hush.PickKeepers"]
    if len(args) != 8:
        return ["W1: PickKeepers gets %d args (%s); the ember needs (ids, rooms, owned, tremor, hushed, time, xs, zs)"
                % (len(args), ", ".join(args))]
    ids, time_arg, xs, zs = args[0], args[5], args[6], args[7]
    if time_arg != clock:
        fails.append("W1: PickKeepers' clock is %r, not Evaluate's %r -- the ember would not travel" % (time_arg, clock))
    # the id/x/z lists are filled together, from the same Thing, in one loop
    loop = None
    for fm in re.finditer(r"foreach\s*\(\s*Thing\s+(\w+)\s+in\s+\w+\s*\)", body[:at]):
        blk = block_after(body, fm.end())
        if re.search(re.escape(ids) + r"\.Add\(", blk):
            loop = (fm.group(1), blk)
    if loop is None:
        fails.append("W1: no foreach(Thing ...) before PickKeepers fills %s" % ids)
    else:
        t, blk = loop
        for lst, axis in ((xs, "x"), (zs, "z")):
            if not re.search(re.escape(lst) + r"\.Add\(\s*" + re.escape(t) + r"\.Position\." + axis + r"\s*\)", blk):
                fails.append("W1: %s is not filled with %s.Position.%s beside %s" % (lst, t, axis, ids))
    # the keepers reach Apply
    am = re.search(r"(\w+)\s*=\s*RM_Hush\.PickKeepers", body)
    kv = am.group(1) if am else None
    aargs, _ = call_args(body, "RM_Hush.Apply", at)
    if kv is None or aargs is None or len(aargs) != 5 or not re.search(r"\b" + re.escape(kv) + r"\b", aargs[4]):
        fails.append("W1: the keepers from PickKeepers do not reach RM_Hush.Apply's keeper argument")
    return fails


def check_hitch(body, clock):
    fails = []
    m = re.search(r"if\s*\(([^{]*RM_Hitch\.IsHitch\(\s*lastTime\s*,\s*" + re.escape(clock) + r"\s*\)[^{]*)\)\s*\{", body)
    if not m:
        return ["W2: Evaluate has no `if (... RM_Hitch.IsHitch(lastTime, %s))` block" % clock]
    blk = block_after(body, m.end() - 1)
    if not re.search(r"\bhitches\s*(\+\+|\+=\s*1\b)", blk):
        fails.append("W2: the hitch block does not count hitches")
    if not re.search(r"maxGapSeconds\s*=\s*" + re.escape(clock) + r"\s*-\s*lastTime", blk):
        fails.append("W2: the hitch block does not record maxGapSeconds = %s - lastTime" % clock)
    after = body[m.end() - 1 + len(blk) + 2:]
    stamp = re.search(r"\blastTime\s*=\s*" + re.escape(clock) + r"\s*;", body)
    if not stamp or stamp.start() < m.start():
        fails.append("W2: lastTime = %s is not stamped after the hitch test" % clock)
    if not re.search(r"\blastTime\s*=\s*" + re.escape(clock) + r"\s*;", after):
        fails.append("W2: lastTime = %s is missing after the hitch block" % clock)
    return fails


# (name, exact text in the compositor, replacement): each must turn the check red.
MUTANTS = [
    ("gen2 call: no clock, no positions", "hushOf.Keys, time, kXs, kZs);", "hushOf.Keys);"),
    ("clock pinned to 0", "hushOf.Keys, time, kXs, kZs);", "hushOf.Keys, 0, kXs, kZs);"),
    ("x list not filled from Position.x", "kXs.Add(t.Position.x);", "kXs.Add(0);"),
    ("z list filled from Position.x", "kZs.Add(t.Position.z);", "kZs.Add(t.Position.x);"),
    ("keepers dropped at Apply", "dark, keepers != null && keepers.TryGetValue(room, out int kp) && kp == id);", "dark, false);"),
    ("call commented out", "keepers = RM_Hush.PickKeepers(", "// keepers = RM_Hush.PickKeepers("),
    ("hitch not counted", "hitches++;", ";"),
    ("max gap not recorded", "maxGapSeconds = time - lastTime;", "maxGapSeconds = 0;"),
    ("lastTime never stamped", "lastTime = time;\n            List<RM_MoodClaim>", "List<RM_MoodClaim>"),
]


def run(path=COMPOSITOR, text=None):
    src = strip_comments(text if text is not None else open(path, encoding="utf-8").read())
    clock, body = evaluate_body(src)
    if body is None:
        return ["W0: no `public int Evaluate(RM_MapComponent_AtmosphericBase, double ...)` in %s" % path]
    return check_ember(body, clock) + check_hitch(body, clock)


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else COMPOSITOR
    fails = run(path)
    for f in fails:
        print("FAIL " + f)
    if fails:
        return 1
    raw = open(path, encoding="utf-8").read()
    blind = []
    for name, old, new in MUTANTS:
        if raw.count(old) != 1:
            blind.append("mutant %r: its anchor occurs %d times (want 1); update MUTANTS with the code" % (name, raw.count(old)))
        elif not run(path, raw.replace(old, new)):
            blind.append("mutant %r stays green: the check cannot see this wire" % name)
    for b in blind:
        print("FAIL " + b)
    if blind:
        return 1
    print("ok   M  %d mutants, each cutting one wire, all go red" % len(MUTANTS))
    print("ok   W1 ember: Evaluate's clock and t.Position.x/.z reach RM_Hush.PickKeepers; keepers reach RM_Hush.Apply")
    print("ok   W2 hitch: IsHitch(lastTime, clock) counts hitches and maxGapSeconds, then lastTime = clock")
    print("PASS selftest_atmosphericbase_wiring")
    return 0


if __name__ == "__main__":
    sys.exit(main())
