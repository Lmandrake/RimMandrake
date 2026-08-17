#!/usr/bin/env python3
"""Turn the owner's A/S/R matrix into xenotypeChances on every faction.

Reads design/Jawa/worldbuilding/review/race_faction_assignment.prefill.json and
rewrites each faction's <xenotypeSet>. Weights: A=30, S=10, R=3, normalised per
faction so each set sums to 1.00.

  python3 src/RimMandrake/Utils/apply_race_factions.py            # plan only
  python3 src/RimMandrake/Utils/apply_race_factions.py --apply

Our 8 authored factions are edited in place. The 4 vanilla reskins (Empire,
OutlanderCivil, TribeCivil, Pirate) have no def of ours, so they get a patch file
in Jawa_Patches instead.

🔴 Inherit="False" is forced on every set. Without it the vanilla parent's xenotypes
are APPENDED and the faction fields Hussars and Dirtmoles alongside ours - which is
exactly how Jawa_FreeDroidEnclaves ended up with none of its own.
⚠️ Refuses to run if the decisions file is still byte-identical to the generated
pre-fill, because that means the sheet never wrote and these are the agent's guesses,
not the owner's.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
DEC = os.path.join(REPO, "design/Jawa/worldbuilding/review/race_faction_assignment.prefill.json")
FACDIR = os.path.join(REPO, "src/Jawa/Jawa_Patches/Defs/FactionDefs")
PATCH = os.path.join(REPO, "src/Jawa/Jawa_Patches/Patches/VanillaFaction_Xenotypes.xml")

WEIGHT = {"A": 30, "S": 10, "R": 3}
VANILLA = {"Empire", "OutlanderCivil", "TribeCivil", "Pirate"}
MAYREQ = ' MayRequire="mandrake.starwarsraces"'


def main():
    apply = "--apply" in sys.argv
    d = json.load(open(DEC))
    grid = d.get("grid") or {}
    if "placedCount" not in d and "--i-know-these-are-not-the-owners" not in sys.argv:
        sys.exit("REFUSING: %s has no 'placedCount' key, which the sheet writes on every "
                 "save. These are the generated guesses, not the owner's decisions. "
                 "Link the sheet to the file first." % os.path.basename(DEC))

    per = {}
    for race, cells in grid.items():
        for fac, grade in (cells or {}).items():
            if grade in WEIGHT:
                per.setdefault(fac, {})[race] = WEIGHT[grade]

    print("factions to write: %d" % len(per))
    for fac in sorted(per, key=lambda f: -len(per[f])):
        tot = sum(per[fac].values())
        print("  %-30s %2d races" % (fac, len(per[fac])))
        for r, w in sorted(per[fac].items(), key=lambda kv: -kv[1]):
            print("       %-34s %.3f" % (r, w / tot))

    if not apply:
        print("\nplan only - pass --apply to write")
        return

    def block(fac, indent="    "):
        tot = sum(per[fac].values())
        li = "".join('%s    <%s%s>%.3f</%s>\n'
                     % (indent, r, "" if r == "Baseliner" else MAYREQ, w / tot, r)
                     for r, w in sorted(per[fac].items(), key=lambda kv: -kv[1]))
        return ('%s<xenotypeSet Inherit="False">\n%s  <xenotypeChances>\n%s%s  </xenotypeChances>\n%s</xenotypeSet>'
                % (indent, indent, li, indent, indent))

    wrote = 0
    for fn in sorted(os.listdir(FACDIR)):
        p = os.path.join(FACDIR, fn)
        s = open(p, encoding="utf-8").read()
        for m in re.finditer(r"<defName>([\w.]+)</defName>", s):
            fac = m.group(1)
            if fac not in per:
                continue
            new = block(fac)
            # ⚠️ handle BOTH forms. A self-closing <xenotypeSet Inherit="False" /> has no
            # closing tag, so a paired-tag regex matches nothing while `"<xenotypeSet" in s`
            # is still true - the write then silently does nothing. Cost four hours today.
            if re.search(r"<xenotypeSet[^>]*/>", s):
                s = re.sub(r"[ \t]*<xenotypeSet[^>]*/>", new, s, count=1)
            elif re.search(r"<xenotypeSet[^>]*>.*?</xenotypeSet>", s, re.S):
                s = re.sub(r"[ \t]*<xenotypeSet[^>]*>.*?</xenotypeSet>", new, s, count=1, flags=re.S)
            else:
                s = s.replace("</FactionDef>", new + "\n  </FactionDef>", 1)
            wrote += 1
        open(p, "w", encoding="utf-8").write(s)

    ops = []
    for fac in sorted(VANILLA & set(per)):
        ops.append('  <Operation Class="PatchOperationAddOrReplace_Safe_Placeholder" />')
    # vanilla defs: Replace the set if present, Add it if not - Conditional does both
    ops = []
    for fac in sorted(VANILLA & set(per)):
        b = block(fac, "        ")
        ops.append(
'''  <Operation Class="PatchOperationConditional">
    <xpath>/Defs/FactionDef[defName="%s"]/xenotypeSet</xpath>
    <match Class="PatchOperationReplace">
      <xpath>/Defs/FactionDef[defName="%s"]/xenotypeSet</xpath>
      <value>
%s
      </value>
    </match>
    <nomatch Class="PatchOperationAdd">
      <xpath>/Defs/FactionDef[defName="%s"]</xpath>
      <value>
%s
      </value>
    </nomatch>
  </Operation>''' % (fac, fac, b, fac, b))
    open(PATCH, "w", encoding="utf-8").write(
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<!-- Generated by src/RimMandrake/Utils/apply_race_factions.py from the owner\'s\n'
        '     race/faction matrix. Do not hand-edit. Inherit="False" is deliberate: without\n'
        '     it the vanilla parent\'s xenotypes are appended. -->\n'
        '<Patch>\n' + "\n".join(ops) + '\n</Patch>\n')
    print("\nrewrote %d authored FactionDefs; patched %d vanilla reskins -> %s"
          % (wrote, len(VANILLA & set(per)), PATCH))
    print("Defs parse at startup: this needs a RESTART, but it does not gate worldgen.")


if __name__ == "__main__":
    main()
