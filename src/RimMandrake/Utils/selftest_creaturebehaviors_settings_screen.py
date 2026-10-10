#!/usr/bin/env python3
"""CREATURE_BEHAVIORS_SETTINGS_SCREEN_1 offline check: every setting Scribed by RM_CreatureBehaviorsSettings that the screen
draws a control for sits inside exactly one named Group(...) block whose names array lists it (so it collapses, searches and
resets with its group), Group blocks are brace-balanced, and the SettingsKit files are in the csproj. Then plants one defect
at a time and requires the check to fail on each.

    python3 src/RimMandrake/Utils/selftest_creaturebehaviors_settings_screen.py
"""
import os
import re
import sys

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "CreatureBehaviors", "Source")


def check(cs, csproj):
    errs = []
    scribed = set(re.findall(r'Scribe_Values\.Look\(ref (\w+), "(\w+)"', cs))
    for field, key in scribed:
        if field != key:
            errs.append(f"scribe key {key!r} != field {field!r}")
    scribed = {f for f, _ in scribed}
    a = cs.index("public void DoWindowContents")
    body = cs[a:cs.index("list.End();", a)]
    groups = []   # (title, names, text)
    for m in re.finditer(r'if \(Group\(list, "([^"]+)", new\[\] \{ ([^}]*) \}, new', body):
        names = re.findall(r'"(\w+)"', m.group(2))
        i = body.index("))\n", m.end())
        i = body.index("{", i)              # the block's opening brace (the line after the if(...))
        depth, j = 0, i
        while j < len(body):
            depth += body[j] == "{"
            depth -= body[j] == "}"
            j += 1
            if depth == 0:
                break
        else:
            errs.append(f"group {m.group(1)!r}: unbalanced braces")
        if "if (Group(" in body[i:j]:
            errs.append(f"group {m.group(1)!r}: swallows the next group (a closing brace is missing)")
        groups.append((m.group(1), names, body[i:j]))
    if len(groups) < 30:
        errs.append(f"only {len(groups)} groups found, expected >= 30")
    seen = {}
    for title, names, text in groups:
        for n in names:
            if n in seen:
                errs.append(f"{n} listed in two groups: {seen[n]!r} and {title!r}")
            seen[n] = title
            if n not in scribed:
                errs.append(f"group {title!r} names {n}, which is not a Scribed setting")
        drawn = set(re.findall(r'ref (\w+)\b', text)) | set(re.findall(r'(\w+) = (?:Mathf\.\w+\()?list\.Slider', text))
        for d in drawn - set(names):
            errs.append(f"group {title!r} draws {d} but does not list it (it would not reset)")
    for f in scribed:
        if f not in seen:
            errs.append(f"setting {f} is in no group (no reset, not searchable)")
    for kit in ("SettingsKitCore.cs", "SettingsKitDrawer.cs"):
        if kit not in csproj:
            errs.append(f"csproj lacks the {kit} Compile Include")
    if "private static readonly Dictionary<string, object> shippedDefaults" not in cs:
        errs.append("no shippedDefaults snapshot for per-group reset")
    return errs


def main():
    cs = open(os.path.join(SRC, "RM_CreatureBehaviorsMod.cs"), encoding="utf-8").read()
    pj = open(os.path.join(SRC, "RM_CreatureBehaviors.csproj"), encoding="utf-8").read()
    bad = 0
    e = check(cs, pj)
    print(("ok   " if not e else "FAIL ") + "real screen: every setting grouped, resettable" + ("" if not e else " | " + "; ".join(e[:4])))
    bad += bool(e)
    plants = [
        ("a name dropped from its group array", lambda c, p: (c.replace('"breedRateMultiplier" }', ' }', 1), p), "no group"),
        ("a setting in two groups", lambda c, p: (c.replace('new[] { "verminBreedingEnabled", "breedRateMultiplier" }', 'new[] { "verminBreedingEnabled", "breedRateMultiplier", "gnawBehaviorEnabled" }', 1), p), "two groups"),
        ("group names a non-setting", lambda c, p: (c.replace('"breedRateMultiplier" }', '"breedRateMultiplir" }', 1), p), "not a Scribed setting"),
        ("a Group's closing brace lost", lambda c, p: (c.replace("                list.GapLine();\n            }\n            if (Group(list, \"Gnawing", "                list.GapLine();\n            if (Group(list, \"Gnawing", 1) if False else c.replace('                list.GapLine();\n            }\n', '                list.GapLine();\n', 1), p), "swallows"),
        ("kit dropped from the csproj", lambda c, p: (c, p.replace("SettingsKitDrawer.cs", "SettingsKitDrawr.cs")), "SettingsKitDrawer.cs"),
        ("snapshot removed", lambda c, p: (c.replace("shippedDefaults = SnapshotDefaults()", "shippedDefaultz = SnapshotDefaults()"), p), "shippedDefaults"),
    ]
    for label, f, want in plants:
        c2, p2 = f(cs, pj)
        if (c2, p2) == (cs, pj):
            print(f"FAIL {label}: pattern not found")
            bad += 1
            continue
        try:
            e = check(c2, p2)
        except Exception as ex:   # a broken file must still be a failure, not a crash
            e = [f"exception {ex}"]
        hit = any(want in x for x in e)
        print(("ok   " if hit else "FAIL ") + label + ("" if hit else f" | wanted {want!r}, got {e[:2]}"))
        bad += not hit
    print(f"creaturebehaviors settings screen selftest: {7 - bad}/7 ok")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
