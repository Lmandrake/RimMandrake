#!/usr/bin/env python3
"""Objective grading of the eval work-trees. Text assertions stay for human review."""
import json, os, re, sys
W = "/mnt/d/Luke/dev/Rimworld/skills/skills-workspace/iteration-1"
def rd(p):
    try: return open(p, encoding="utf-8", errors="replace").read()
    except OSError: return ""
def files(cfgdir):
    out = {}
    for dp, dn, fn in os.walk(os.path.join(cfgdir, "work")):
        for f in fn:
            full = os.path.join(dp, f)
            out[os.path.relpath(full, os.path.join(cfgdir, "work"))] = rd(full)
    return out
STRIKE = re.compile(r"~~|⛔|\bSTRUCK\b|\bSUPERSEDED\b|\bREVERSED\b|\bCANCELLED\b|\bCLOSED\b", re.I)
def grade(eid, cfg):
    d = os.path.join(W, eid, cfg); F = files(d)
    outs = " ".join(rd(os.path.join(d,"outputs",f)) for f in (os.listdir(os.path.join(d,"outputs")) if os.path.isdir(os.path.join(d,"outputs")) else []))
    A = []
    def a(text, ok, ev=""): A.append({"text":text,"passed":bool(ok),"evidence":ev[:200]})
    if eid == "A1":
        nr = F.get("NEXT_RELOAD.md",""); bd = F.get("queue/BUILD.md","")
        live_off = re.search(r"turn the turrets mod OFF(?!.*~~)", nr) and "~~" not in nr
        a("NEXT_RELOAD no longer carries a live 'turn the turrets mod OFF' order", not re.search(r"^\|?[^~]*turn the turrets mod OFF", nr, re.M) or STRIKE.search(nr))
        a("Old instruction STRUCK/marked rather than silently deleted", bool(STRIKE.search(nr)), nr[:150])
        a("Reversal recorded with a date", "2026-08-15" in nr or "2026-08-15" in bd)
        a("B10 (disable turrets) closed/struck not left ready", bool(re.search(r"B10", bd)) and bool(STRIKE.search(bd)))
        a("V1.md turret-cull row updated", "turret" in F.get("V1.md","").lower() and STRIKE.search(F.get("V1.md","")) is not None)
        a("agents/POLICY.md standing change corrected", "keep" in F.get("agents/POLICY.md","").lower() or STRIKE.search(F.get("agents/POLICY.md","")) is not None)
        a("design/turret_spec.md addressed", STRIKE.search(F.get("design/turret_spec.md","")) is not None or "keep" in F.get("design/turret_spec.md","").lower())
        touched = sum(1 for k in ("NEXT_RELOAD.md","V1.md","queue/BUILD.md","agents/POLICY.md","design/turret_spec.md") if "2026-08-15" in F.get(k,"") or STRIKE.search(F.get(k,"")))
        a("All 5 directive-bearing files touched", touched >= 5, "touched=%d" % touched)
        a("Notes B21 (retexture turret bases) is no longer moot", "B21" in outs and re.search(r"B21.{0,120}(no longer|now|un-?block|relevant|wanted)", outs, re.S|re.I) is not None)
    if eid == "A3":
        v1 = F.get("V1.md",""); bd = F.get("queue/BUILD.md","")
        a("V1 step 1 marked frozen/closed", bool(re.search(r"cherrypick.{0,80}(frozen|closed)", v1, re.I|re.S)))
        a("KEY: identifies steps 2/3 now unblocked", bool(re.search(r"(unblock|no longer blocked|input is (now )?fixed)", v1+bd+outs, re.I)))
        a("KEY: identifies B14's stated blocker dissolved", bool(re.search(r"B14", bd+outs)) and bool(re.search(r"(cannot be invented|blocker).{0,200}(gone|dissolv|no longer|fixed)", bd+outs, re.I|re.S)))
        a("Ruling carries a date", "2026-08-15" in v1+bd)
        a("Does not flip B14 to ready blindly", "state:    blocked" in bd or "blocked" in bd)
    if eid == "B3":
        a("docs/DEPLOY.md no longer documents --plan", "--plan" not in F.get("docs/DEPLOY.md",""))
        a("KEY: fixed the OTHER copy too (docs/STATE.md)", "--plan" not in F.get("docs/STATE.md",""))
        a("Report notes dry-run is the default", bool(re.search(r"(dry.?run is the default|default.{0,30}dry.?run|dry-run-by-default)", outs, re.I)))
        a("Corrected the 8-mod count in STATE.md", "8 active" not in F.get("docs/STATE.md","") )
    if eid == "B2":
        a("Counted ModsConfig directly (found 5)", "5" in outs and "activeMods" in outs or "5 active" in outs)
        a("Reports the documented 8 is wrong", bool(re.search(r"(false|wrong|not 8|drift)", outs, re.I)))
        st = F.get("docs/STATE.md","")
        # correct behaviour is to STRIKE the old claim, not delete it: the doc must
        # state the true count and no longer assert 8 as current.
        asserts_8_now = bool(re.search(r"(is|baseline is)\s*\**8\**\s*active", st, re.I))
        states_5 = bool(re.search(r"\b5\b", st))
        a("KEY: actually CORRECTED docs/STATE.md rather than only recommending", states_5 and not asserts_8_now, st[:160])
    if eid == "B1":
        a("Read the manifest", "capturedUtc" in outs or "manifest" in outs.lower())
        a("KEY: identified capture date as 2026-08-15", "2026-08-15" in outs or "08-15" in outs)
        a("KEY: declined to escalate / no 25-min reload", bool(re.search(r"(do not escalate|don't escalate|not escalate|no.{0,20}reload|premise (does not|doesn't) hold|refus)", outs, re.I)))
        a("Explains the folder-mtime trap", bool(re.search(r"(mtime|overwrit.{0,30}in place|directory.{0,30}(date|timestamp))", outs, re.I)))
        a("KEY: corrected docs/STATE.md", "2026-08-14" not in F.get("docs/STATE.md",""))
    if eid == "A2":
        a("Does NOT adopt option (b) as offered", bool(re.search(r"(reject|not).{0,40}\(?b\)?", outs, re.I)))
        a("Splits the criterion into two claims", bool(re.search(r"(split|two (independent )?(claims|parts)|part one.{0,200}part two)", outs, re.I|re.S)))
        a("Uses VOID rather than 'passed'", "void" in outs.lower())
        a("Names the laundering risk", "launder" in outs.lower())
        a("Rejects leaving it open forever", bool(re.search(r"reject.{0,40}\(?c\)?", outs, re.I)))
    return A
res = {}
for eid in ["A1","A2","A3","B1","B2","B3"]:
    for cfg in ["with_skill","without_skill"]:
        d = os.path.join(W, eid, cfg)
        if not os.path.isdir(d): continue
        A = grade(eid, cfg)
        if not A: continue
        json.dump({"expectations":A}, open(os.path.join(d,"grading.json"),"w"), indent=2)
        p = sum(1 for x in A if x["passed"])
        res.setdefault(eid,{})[cfg] = (p, len(A))
print("%-6s %-14s %-14s" % ("eval","with_skill","baseline"))
for eid, v in res.items():
    w = v.get("with_skill"); b = v.get("without_skill")
    fmt = lambda t: ("%d/%d" % t) if t else "PENDING"
    print("%-6s %-14s %-14s" % (eid, fmt(w), fmt(b)))
