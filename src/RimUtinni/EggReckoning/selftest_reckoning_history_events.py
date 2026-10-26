"""Selftest: RUT_Reckoning's path-3 history events are wired with nodes that really load.

Item RECKONING_HISTORYEVENT_REWIRE_OFF_QUESTEND. successHistoryEvent / failedOrExpiredHistoryEvent
are QuestScriptDef fields (decomp rw16 RimWorld/QuestScriptDef.cs:74,76), not QuestNode_End fields;
placed on a QuestNode_End they log a red XML error at load and the event is never recorded. The
design (webwork_egg_blackmarket_2026-09-24.md section 2d) wants RUT_HistoryEvent_EggAssassination on
both path-3 ends only, so the wiring is a vanilla QuestNode_RecordHistoryEvent on each end's signal,
placed before its QuestNode_End.

Checks:
  1. every QuestNode_End / QuestNode_RecordHistoryEvent child is a real field of that class
     (field sets below are from decomp rw16; re-read from the decomp when it is on this machine);
  2. EggAssassination is recorded on EggHatched and on EggFoundBeforeHatch, each before the End
     on the same signal.
Exit 0 pass, 1 fail.
"""
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
QUEST = os.path.join(HERE, "Defs", "QuestScriptDefs", "RUT_Reckoning.xml")
DECOMP = "/mnt/d/ClaudeWork/rimmandrake/decomp/rw16/all/RimWorld.QuestGen"
FIELDS = {
    "QuestNode_End": {"inSignal", "outcome", "signalListenMode", "sendStandardLetter",
                      "goodwillChangeAmount", "goodwillChangeFactionOf", "goodwillChangeReason"},
    "QuestNode_RecordHistoryEvent": {"inSignal", "historyDef"},
}
EVENT = "RUT_HistoryEvent_EggAssassination"
SIGNALS = ("EggHatched", "EggFoundBeforeHatch")


def decomp_fields(cls):
    path = os.path.join(DECOMP, cls + ".cs")
    if not os.path.isfile(path):
        return None
    text = open(path, encoding="utf-8", errors="replace").read()
    return set(re.findall(r"public SlateRef<[^;]*>\s+(\w+)\s*;", text))


def main():
    fails = []
    for cls, want in FIELDS.items():
        live = decomp_fields(cls)
        if live is not None and live != want:
            fails.append(f"field set for {cls} drifted from decomp: {sorted(live ^ want)}")
    root = ET.parse(QUEST).getroot()
    # The tree is the abstract Name="RUT_Reckoning"; its two leaves (CartelOffer, Rumor) inherit it.
    reckoning = [q for q in root.iter("QuestScriptDef") if q.get("Name") == "RUT_Reckoning"]
    if len(reckoning) != 1:
        fails.append(f"expected 1 abstract RUT_Reckoning QuestScriptDef, found {len(reckoning)}")
    nodes = list(reckoning[0].iter("li")) if reckoning else []
    seen_class_nodes = 0
    for el in nodes:
        cls = el.get("Class")
        if cls in FIELDS:
            seen_class_nodes += 1
            for ch in el:
                if ch.tag not in FIELDS[cls]:
                    fails.append(f"{cls} (inSignal {el.findtext('inSignal')}) has no field <{ch.tag}>")
    if seen_class_nodes < 3:
        fails.append(f"instrument blind: saw only {seen_class_nodes} End/RecordHistoryEvent nodes")
    order = [(el.get("Class"), el.findtext("inSignal"), el.findtext("historyDef")) for el in nodes
             if el.get("Class") in FIELDS]
    for sig in SIGNALS:
        rec = [i for i, (c, s, h) in enumerate(order)
               if c == "QuestNode_RecordHistoryEvent" and s == sig and h == EVENT]
        end = [i for i, (c, s, _) in enumerate(order) if c == "QuestNode_End" and s == sig]
        if len(rec) != 1:
            fails.append(f"{EVENT} recorded {len(rec)} times on {sig} (want 1)")
        elif not end or rec[0] > end[0]:
            fails.append(f"RecordHistoryEvent on {sig} is not before its QuestNode_End")
    extra = [s for c, s, h in order if c == "QuestNode_RecordHistoryEvent" and h == EVENT
             and s not in SIGNALS]
    if extra:
        fails.append(f"{EVENT} also recorded on non-path-3 signals {extra}")
    for f in fails:
        print("FAIL: " + f)
    print(f"selftest_reckoning_history_events: {'FAIL' if fails else 'PASS'} "
          f"({seen_class_nodes} nodes checked)")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
