#!/usr/bin/env python3
"""HOSE_PROOFS_FIX_STALE_LAYOK_AFTER_PEEK: since fa833277f8 the hose census reads the cached lay and never lays, so a proof row
that acts and reads layOk at once read a stale or null lay. Proves (offline):

  1. validation_core.lay_settled / settle_hose / settle_census wait until a LAID hose reads layKeyed true and layRunning
     false; an unlaid hose and a census without the fields are settled at once; a timeout comes back marked layUnsettled.
  2. validation_hose.H.hose re-reads a census until the hose settles (behaviour, on a scripted census sequence).
  3. every census-hose reader the item names reads through the settle (source check), and CR2 no longer asks a carried
     hose for a lay (a carried hose is never laid: the tick lays laid reels only).
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for p in (HERE, os.path.join(REPO, "src", "RimMandrake", "Utils")):
    if p not in sys.path:
        sys.path.insert(0, p)

import validation_core as V  # noqa: E402
import validation_hose as VH  # noqa: E402

FAILS = []


def check(name, ok, detail=""):
    print("%s %s%s" % ("PASS" if ok else "FAIL", name, (" -- %s" % detail) if detail and not ok else ""))
    if not ok:
        FAILS.append(name)


class Clock(object):
    def __init__(self):
        self.t = 0.0

    def now(self):
        return self.t

    def sleep(self, s):
        self.t += s


def scripted(seq):
    it = iter(seq)
    last = [None]

    def read():
        try:
            last[0] = next(it)
        except StopIteration:
            pass
        return last[0]
    return read


def hose(laid=True, keyed=True, running=False, ok=True):
    return {"reel": [10, 10], "laid": laid, "layKeyed": keyed, "layRunning": running, "layOk": ok}


# 1. the predicate
check("settled: laid, keyed, not running", V.lay_settled(hose()))
check("unsettled: laid, not keyed (reset, not re-laid)", not V.lay_settled(hose(keyed=False, ok=False)))
check("unsettled: laid, lay on the queue", not V.lay_settled(hose(running=True)))
check("settled: unlaid hose (the tick never lays it)", V.lay_settled(hose(laid=False, keyed=False, running=False)))
check("settled: census without the fields (old DLL / fake)", V.lay_settled({"reel": [1, 1], "laid": True, "layOk": True}))
check("settled: empty row", V.lay_settled({}))

# settle_hose: waits through a reset and a running lay, returns the landed read
ck = Clock()
seq = [(hose(keyed=False, ok=False), "c0"), (hose(running=True), "c1"), (hose(), "c2")]
got = V.settle_hose(scripted(seq), sleep=ck.sleep, clock=ck.now)
check("settle_hose waits for keyed and not running", got[1] == "c2" and got[0]["layOk"] is True, got)
check("settle_hose waited wall-clock only (two polls)", abs(ck.t - 0.5) < 1e-9, ck.t)

ck = Clock()
got = V.settle_hose(scripted([(hose(laid=False, keyed=False), "c0"), (hose(), "c1")]), sleep=ck.sleep, clock=ck.now)
check("settle_hose: unlaid read returned at once", got[1] == "c0" and ck.t == 0.0, (got, ck.t))

ck = Clock()
got = V.settle_hose(scripted([hose(running=True)]), wait_s=2.0, sleep=ck.sleep, clock=ck.now)
check("settle_hose: timeout marks layUnsettled", got.get("layUnsettled") is True and ck.t >= 2.0, got)

# settle_census: only the matched hose gates the wait
ck = Clock()
other = dict(hose(running=True), reel=[50, 50])
seq = [{"hoses": [hose(keyed=False), other]}, {"hoses": [hose(), other]}]
c = V.settle_census(scripted(seq), lambda h: h["reel"] == [10, 10], sleep=ck.sleep, clock=ck.now)
check("settle_census waits on the matched hose only", c["hoses"][0]["layKeyed"] is True and abs(ck.t - 0.25) < 1e-9, (c, ck.t))
ck = Clock()
c = V.settle_census(scripted([{"success": True, "layOk": True}]), lambda h: True, sleep=ck.sleep, clock=ck.now)
check("settle_census: a census with no hoses list is settled", ck.t == 0.0)
ck = Clock()
c = V.settle_census(scripted([{"hoses": [hose(running=True)]}]), lambda h: True, wait_s=1.0, sleep=ck.sleep, clock=ck.now)
check("settle_census: timeout marks the hose", c["hoses"][0].get("layUnsettled") is True)

# 2. H.hose behaviour on a scripted census (no bridge)
cens = iter([{"hoses": [hose(keyed=False, ok=False)]}, {"hoses": [hose(running=True)]}, {"hoses": [hose()]}])
calls = []


def fake_hp(cmd, wait_s=20.0):
    calls.append(cmd)
    return next(cens)


Hb = VH.H.__new__(VH.H)
Hb.hp = fake_hp
h, c = Hb.hose((10, 10))
check("H.hose re-reads until the lay lands (layOk true, 3 census reads)", h.get("layOk") is True and calls == ["census"] * 3, (h, calls))
cens = iter([{"hoses": [hose(keyed=False, ok=False)]}])
calls[:] = []
h, c = Hb.hose((10, 10), settle=False)
check("H.hose(settle=False) reads once", calls == ["census"] and h.get("layOk") is False)

# 3. every named reader goes through the settle
F = os.path.join(REPO, "src", "RimMandrake", "FlowWorks")
N = os.path.join(F, "northstar")


def src(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def body(text, header, stop=r"\n    def |\ndef |\nclass "):
    i = text.find(header)
    if i < 0:
        return ""
    m = re.search(stop, text[i + len(header):])
    return text[i: i + len(header) + (m.start() if m else len(text))]


vh = src(os.path.join(F, "validation_hose.py"))
check("validation_hose H.hose settles", "V.settle_hose(read)" in body(vh, "    def hose(self, reel"))
check("validation_hose save/load census settles", vh.count('V.settle_census(lambda: B.hp("census"), lambda h: True)') >= 2)
cr2 = vh[vh.find('"CR2_trail_follows_walk"') - 600: vh.find('"CR2_trail_follows_walk"') + 400]
check("CR2 asks for the carry draw, not a lay", 'carry_drawn' in cr2 and 'b.get("layOk")' not in cr2)
vsh = src(os.path.join(F, "validation_style_hose.py"))
check("validation_style_hose: no bare census read", 'c = H.hp("census")\n' not in vsh and "V.settle_census" in vsh)
ph = src(os.path.join(N, "proof_hose.py"))
check("proof_hose walls census settles", 'walls_verdict(V.settle_census(' in ph)
sg = src(os.path.join(N, "sitting_gaps_proof.py"))
check("sitting_gaps _census_hose settles", "V.settle_census" in body(sg, "def _census_hose("))
lp = src(os.path.join(N, "lines_proof.py"))
check("lines_proof hose() settles before ProofHoseLine", "V.settle_census" in body(lp, "    def hose(reel):"))
wg = src(os.path.join(N, "walk_gaps_proof.py"))
i = wg.find('kh, th = static(LPROOF, "ProofHoseLine", xz(r))')
check("walk_gaps settles before ProofHoseLine", i > 0 and "V.settle_census" in wg[i - 300: i])
pl = src(os.path.join(N, "pipe_levelling_perf_proof.py"))
i = pl.find('kl, tl = static("ProofLevelLink"')
check("pipe_levelling settles before ProofLevelLink", i > 0 and "V.settle_census" in pl[i - 300: i])
rl = src(os.path.join(REPO, "src", "RimMandrake", "GimmeSomeSlack", "northstar_matrix", "run_live.py"))
i = rl.find('st["kind"] == "hose_census"')
check("GSS run_live hose_census settles", i > 0 and "V.settle_census" in rl[i: i + 400])

print("%s: %d failed" % ("FAIL" if FAILS else "PASS", len(FAILS)))
sys.exit(1 if FAILS else 0)
