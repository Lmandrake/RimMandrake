# -*- coding: utf-8 -*-
"""Emit the two Insult/Slight Operations from v5.py, already fanned out to the
four speaker conditions. Generated rather than hand-typed: 200 rules is too many
to transcribe safely, and the four copies must agree exactly."""
import io, os, sys

# Resolved from this file, not hardcoded: the repo moved G: -> D: on 2026-08-12
# and is reached by different paths from Windows Python and WSL.
_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lines_insults as v5

CONDS = ["INITIATOR_faction==PlayerColony",
         "INITIATOR_faction==PlayerTribe",
         "INITIATOR_kind==RSW_Jawa",
         "INITIATOR_kind==RSW_JawaTribal"]


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def op(defname, rows, banner):
    x = '/Defs/InteractionDef[defName="%s"]/logRulesInitiator/rulesStrings' % defname
    L = []
    L.append('  <!-- ==================================================================')
    L.append('       %s' % banner)
    L.append('       ================================================================== -->')
    L.append('  <Operation Class="PatchOperationConditional">')
    L.append('    <xpath>%s</xpath>' % x)
    L.append('    <match Class="PatchOperationAdd">')
    L.append('      <xpath>%s</xpath>' % x)
    L.append('      <value>')
    for jaw, gloss in rows:
        body = esc("%s (%s)" % (jaw, gloss))
        for c in CONDS:
            L.append('        <li>r_logentry(%s,priority=250)-&gt;%s</li>' % (c, body))
    L.append('      </value>')
    L.append('    </match>')
    L.append('  </Operation>')
    return "\n".join(L)


if __name__ == "__main__":
    head = io.open(os.path.join(HERE, "header_insults.txt"), encoding="utf-8").read().rstrip("\n")
    out = [head, "<Patch>", ""]
    out.append(op("Insult", v5.INSULT,
                  "INSULT: loud, face to face, and mostly about your resale value"))
    out.append("")
    out.append(op("Slight", v5.SLIGHT,
                  "SLIGHT: sidelong, muttered, walking away"))
    out.append("")
    out.append("</Patch>")
    dest = os.path.join(_REPO_ROOT, "src", "Jawa", "JawaVoice", "Patches",
                        "JawaVoice_Insults.xml")
    io.open(dest, "w", encoding="utf-8", newline="\n").write("\n".join(out) + "\n")
    n = (len(v5.INSULT) + len(v5.SLIGHT))
    print("wrote %s\n  %d authored lines -> %d rules" % (dest, n, n * 4))
