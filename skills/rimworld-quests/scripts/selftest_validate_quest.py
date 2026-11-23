#!/usr/bin/env python3
"""Offline selftest of the firing-route checks in validate_quest.py. Needs no game: the corpus is empty."""
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import validate_quest as v  # noqa: E402

BODY = ("<questNameRules><rulesStrings><li>questName->a</li></rulesStrings></questNameRules>"
        "<questDescriptionRules><rulesStrings><li>questDescription->b</li></rulesStrings></questDescriptionRules>"
        '<root Class="QuestNode_Sequence"><nodes><li Class="QuestNode_End" /></nodes></root>')
GIVER = ("<givenBy><li>Traders</li></givenBy><rootSelectionWeight>1</rootSelectionWeight>"
         "<randomlySelectable>false</randomlySelectable><expireDaysRange>1~2</expireDaysRange>")
DECREE = "<decreeSelectionWeight>1</decreeSelectionWeight>"
RATED = "<defaultChallengeRating>1</defaultChallengeRating>"
CASES = [  # name, def fields, codes that must be present, codes that must be absent
    ("giver-only with a star rating is the ConfigError", GIVER + RATED, {"config-challenge"}, {"never-fires"}),
    ("giver with a star rating and isRootSpecial is clean", GIVER + RATED + "<isRootSpecial>true</isRootSpecial>",
     set(), {"config-challenge", "never-fires", "special-only"}),
    ("giver with weight 0 is never picked", "<givenBy><li>Traders</li></givenBy>", {"never-fires"}, set()),
    ("decree with tags fires", RATED + DECREE + "<decreeTags><li>T</li></decreeTags>", set(),
     {"config-challenge", "never-fires"}),
    ("decree without tags is never picked", RATED + DECREE, {"never-fires"}, {"config-challenge"}),
    ("isRootSpecial alone is noted", "<isRootSpecial>true</isRootSpecial>", {"special-only"}, {"never-fires"}),
    ("no route at all", "", {"never-fires"}, set()),
    ("random pool with a star rating is clean", RATED + "<rootSelectionWeight>1</rootSelectionWeight>"
     "<expireDaysRange>1~2</expireDaysRange>", set(), {"config-challenge", "never-fires", "special-only"}),
]


def main():
    bad = 0
    with tempfile.TemporaryDirectory() as d:
        src = Path(d) / "Defs" / "q.xml"
        src.parent.mkdir()
        src.write_text("<Defs/>")
        for name, fields, want, absent in CASES:
            el = ET.fromstring("<QuestScriptDef><defName>T</defName>%s%s</QuestScriptDef>" % (fields, BODY))
            rep = v.Report()
            v.check_def("T", el, {"nodes": []}, rep, src)
            got = {i[2] for i in rep.items}
            if want - got or absent & got:
                bad += 1
                print("FAIL %s: missing %s, unwanted %s" % (name, want - got, absent & got))
    print("%s: %d cases, %d failed" % ("FAIL" if bad else "PASS", len(CASES), bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
