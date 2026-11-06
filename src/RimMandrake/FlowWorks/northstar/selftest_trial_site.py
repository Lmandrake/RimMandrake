#!/usr/bin/env python3
"""selftest_trial_site -- offline proof of TRIAL_SITE_REBUILD_FOR_FOURTEEN_MODS: the FlowWorks dry golden trial site is
built and preflighted on fw_gss_sitting (v2), trial_site.py's gate/ensure/prove decide right, P-E8 no longer gates on the
window size, and P-E4 --fix sets autosave and passes only on the re-read Prefs.xml. No game, no bridge, no game folder."""
import json
import os
import shutil
import stat
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import site_spec as S  # noqa: E402
import preflight_flowworks as PF  # noqa: E402
import trial_site as TS  # noqa: E402
from northstar_driver import PASS, FAIL, UNMEASURED  # noqa: E402
from northstar_driver.preflight import Check  # noqa: E402

FAILS = []


def check(name, ok, detail=""):
    print("%s  %s%s" % ("PASS" if ok else "FAIL", name, "" if ok else "  -- %s" % str(detail)[:300]))
    if not ok:
        FAILS.append(name)


class Stub(object):
    """A bridge session: scripted replies, every call recorded."""

    def __init__(self, replies=None, on=None):
        self.replies = replies or {}
        self.on = on or {}
        self.calls = []
        self.tools = set(self.replies) | set(self.on)

    def call(self, tool, **kw):
        self.calls.append((tool, kw))
        if tool in self.on:
            return self.on[tool](**kw)
        return self.replies.get(tool, {"success": True})


def prefs_xml(path, **kv):
    base = {"screenWidth": "2516", "screenHeight": "1252", "fullscreen": "False", "uiScale": "1",
            "langFolderName": "English", "textureCompression": "True", "autosaveIntervalDays": "14"}
    base.update({k: str(v) for k, v in kv.items()})
    with open(path, "w", encoding="utf-8") as f:
        f.write("<PrefsData>%s</PrefsData>" % "".join("<%s>%s</%s>" % (k, v, k) for k, v in base.items()))


def sec1_site_spec():
    check("site_spec TIER is the 14-mod fw_gss_sitting list", S.TIER == "fw_gss_sitting", S.TIER)
    check("golden name is v2 (building it moves no existing save)", S.GOLDEN_NAME == "NS_FlowWorks_TrialSite_v2",
          S.GOLDEN_NAME)
    check("the stale v1 repo sidecar is deleted, not superseded",
          not os.path.exists(os.path.join(S.REPO_SIDECAR_DIR, "NS_FlowWorks_TrialSite_v1.json")))
    check("prep version bumped past v1's 2", S.PREP_VERSION not in ("1", "2"), S.PREP_VERSION)
    check("P-E8 gates fullscreen/uiScale/lang/texture compression, not the window size",
          set(S.GATE_RENDER_KEYS) == {"fullscreen", "uiScale", "langFolderName", "textureCompression"},
          S.GATE_RENDER_KEYS)
    check("the window size is still recorded in the sidecar", {"screenWidth", "screenHeight"} <= set(S.RENDER_KEYS))


def sec2_gate():
    tier = ["brrainz.harmony", "ludeon.rimworld", "ludeon.rimworld.royalty", "ludeon.rimworld.ideology",
            "ludeon.rimworld.biotech", "ludeon.rimworld.anomaly", "ludeon.rimworld.odyssey", "mandrake.rm.flowworks",
            "mandrake.rm.gimmesomeslack", "mandrake.rm.biomes", "oskarpotocki.vanillafactionsexpanded.core",
            "mandrake.rm.luminouspigment", "ray1203.simplecamerasetting", "rimbridgeserver"]
    want = ["rimbridgeserver", "mandrake.rm.flowworks", "mandrake.rm.gimmesomeslack", "mandrake.rm.biomes",
            "oskarpotocki.vanillafactionsexpanded.core"]
    check("gate: the whole tier fits", TS.gate(tier, tier_list=tier, want=want) == [],
          TS.gate(tier, tier_list=tier, want=want))
    for drop in ("mandrake.rm.luminouspigment", "mandrake.rm.biomes", "ludeon.rimworld.odyssey"):
        g = TS.gate([i for i in tier if i != drop], tier_list=tier, want=want)
        check("gate: a list without %s is the wrong game" % drop, bool(g) and drop in json.dumps(g), g)
    g = TS.gate(tier + ["sarg.alphabiomes"], tier_list=tier, want=want)
    check("gate: a mod beyond the tier is the wrong game", any("beyond" in p for p in g), g)
    g = TS.gate(tier + ["sarg.alphaanimals"], tier_list=tier + ["sarg.alphaanimals"], want=want)
    check("gate: a retired donor is the wrong game even inside the tier list", any("retired" in p for p in g), g)
    import northstar_driver.session as NS
    orig = NS.FastSession

    class Down(object):
        def __init__(self, *a, **k):
            raise ConnectionRefusedError("bridge down")
    NS.FastSession = Down
    try:
        rc = TS.main(["gate"])
    finally:
        NS.FastSession = orig
    check("gate: a bridge that cannot be reached is BLIND (3), never the item's FAIL (1)", rc == TS.BLIND, rc)


class FakeP(object):
    def __init__(self, d):
        self.saves = d
        self.prefs = os.path.join(d, "Prefs.xml")
        self.player_log = None
        self.sidecar = os.path.join(d, S.GOLDEN_NAME + ".json")


def sec3_contract_tier(d):
    """contract_problems names a golden built on another tier (the v1 class: built on flowworks, run on 14 mods)."""
    P = FakeP(d)
    save = os.path.join(d, S.GOLDEN_NAME + ".rws")
    with open(save, "w") as f:
        f.write("<savegame/>")
    os.chmod(save, stat.S_IREAD)
    orig = (S.sha256_file, S.defs_hash)
    S.sha256_file = lambda p: "x"
    S.defs_hash = lambda *a: "h"
    try:
        sc = {"save": os.path.basename(save), "tier": "flowworks",
              "contract": {"save_sha256": "x", "flowworks_dll_sha256": "x", "defs_hash": "h",
                           "prep_version": S.PREP_VERSION,
                           "settings": {t: dict(fields) for t, fields in S.SETTINGS.items()}}}
        json.dump(sc, open(P.sidecar, "w"))
        got = PF.contract_problems(P)
        check("contract: a golden built on tier flowworks is stale on fw_gss_sitting",
              any("built on tier flowworks" in g for g in got), got)
        sc["tier"] = S.TIER
        json.dump(sc, open(P.sidecar, "w"))
        got = PF.contract_problems(P)
        check("contract: the same sidecar on the right tier is fresh", got == [], got)
    finally:
        S.sha256_file, S.defs_hash = orig
        os.chmod(save, stat.S_IREAD | stat.S_IWRITE)
        os.remove(save)
        os.remove(P.sidecar)


def _with_contract(seq, fn):
    """Run fn with PF.contract_problems answering from `seq` in turn."""
    it = iter(seq)
    orig = PF.contract_problems
    PF.contract_problems = lambda P: next(it)
    try:
        return fn()
    finally:
        PF.contract_problems = orig


def sec4_ensure(d):
    P = FakeP(d)
    dev = {"rimworld/get_game_info": {"devModeEnabled": True, "godMode": True}}
    log = []
    calm = lambda call: log.append("calm") or {"verified": True, "problems": []}   # noqa: E731
    prep = lambda s, P_, seat: log.append("prep") or None                           # noqa: E731
    s = Stub(dev)
    rec = _with_contract([[]], lambda: TS.ensure(s, P, "RELENTLESS", load_calm=calm, prep=prep, log=lambda *a: 0))
    check("ensure: a fresh contract is a no-op (no load, no prep, no bridge call)",
          rec["ok"] and rec["action"] == "fresh" and log == [] and s.calls == [], (rec, log, s.calls))
    log[:] = []
    rec = _with_contract([["golden save missing"], []],
                         lambda: TS.ensure(Stub(dev), P, "RELENTLESS", load_calm=calm, prep=prep))
    check("ensure: a missing golden loads calm then builds, and reads the contract clean after",
          rec["ok"] and rec["action"] == "build" and log == ["calm", "prep"], (rec, log))
    log[:] = []
    rec = _with_contract([["golden built on tier flowworks, the trial runs on fw_gss_sitting"], []],
                         lambda: TS.ensure(Stub(dev), P, "RELENTLESS", load_calm=calm, prep=prep))
    check("ensure: a golden on the wrong tier is rebuilt", rec["ok"] and log == ["calm", "prep"], (rec, log))
    log[:] = []
    bad_calm = lambda call: log.append("calm") or {"verified": False, "problems": ["the load logged X"]}   # noqa: E731
    rec = _with_contract([["missing"]], lambda: TS.ensure(Stub(dev), P, "RELENTLESS", load_calm=bad_calm, prep=prep))
    check("ensure: an unverified calm load stops before prep", not rec["ok"] and log == ["calm"], (rec, log))
    log[:] = []
    refuse = lambda s, P_, seat: "PREP REFUSED at step 8: x"   # noqa: E731
    rec = _with_contract([["missing"], ["golden save missing"]],
                         lambda: TS.ensure(Stub(dev), P, "RELENTLESS", load_calm=calm, prep=refuse))
    check("ensure: a refused prep is NOT CLEAN", not rec["ok"] and any("REFUSED" in p for p in rec["problems"]), rec)
    rec = _with_contract([["missing"], ["FlowWorks DLL changed since prep"]],
                         lambda: TS.ensure(Stub(dev), P, "RELENTLESS", load_calm=calm, prep=prep))
    check("ensure: a contract still dirty after the build is NOT CLEAN", not rec["ok"], rec)


def sec5_prove(d):
    P = FakeP(d)
    golden = os.path.join(d, S.GOLDEN_NAME + ".rws")
    hdr = ["ludeon.rimworld", "ludeon.rimworld.royalty", "ludeon.rimworld.ideology", "ludeon.rimworld.biotech",
           "ludeon.rimworld.anomaly", "ludeon.rimworld.odyssey", "mandrake.rm.flowworks"]
    with open(golden, "w") as f:
        f.write("<savegame><meta><modIds>%s</modIds></meta></savegame>" % "".join("<li>%s</li>" % i for i in hdr))
    os.chmod(golden, stat.S_IREAD)
    stale = os.path.join(d, TS.WORK_PREFIX + "old.rws")
    open(stale, "w").close()
    passing = lambda s, P_, seat, fix=False: [Check("P-L1", PASS, "ok"), Check("P-E4", PASS, "ok")]   # noqa: E731
    seen = {}

    def loader(s, name):
        seen["name"] = name
        return []
    rec = _with_contract([["golden save sha changed since prep"]],
                         lambda: TS.prove(Stub(), P, "RELENTLESS", tier_list=hdr + ["rimbridgeserver"], running=hdr, loader=loader, live=passing))
    check("prove: a dirty contract is NOT CLEAN and loads nothing", not rec["ok"] and "name" not in seen, rec)
    rec = _with_contract([[]], lambda: TS.prove(Stub(), P, "RELENTLESS", tier_list=hdr + ["rimbridgeserver"], running=hdr[:-1], loader=loader, live=passing))
    check("prove: a header naming a mod the running list lacks is NOT CLEAN",
          not rec["ok"] and "name" not in seen and any("lacks" in p for p in rec["problems"]), rec)
    rec = _with_contract([[]], lambda: TS.prove(Stub(), P, "RELENTLESS", tier_list=hdr + ["rimbridgeserver"], running=hdr, loader=loader, live=passing))
    work = os.path.join(d, seen.get("name", "?") + ".rws")
    check("prove: clean contract + header + load + every row PASS is CLEAN", rec["ok"], rec)
    check("prove: it loads a Work copy, never the golden", seen.get("name", "").startswith(TS.WORK_PREFIX)
          and os.path.isfile(work) and os.access(work, os.W_OK), seen)
    check("prove: the older Work copy was removed", not os.path.exists(stale))
    check("prove: the golden stays read-only", not os.access(golden, os.W_OK))
    for st in (FAIL, UNMEASURED):
        rows = lambda s, P_, seat, fix=False, st=st: [Check("P-L1", PASS, "ok"), Check("P-E8", st, "x")]   # noqa: E731
        rec = _with_contract([[]], lambda: TS.prove(Stub(), P, "RELENTLESS", tier_list=hdr + ["rimbridgeserver"], running=hdr, loader=loader, live=rows))
        check("prove: one %s row is NOT CLEAN" % st, not rec["ok"], rec)
    rec = _with_contract([[]], lambda: TS.prove(Stub(), P, "RELENTLESS", tier_list=hdr + ["rimbridgeserver"], running=hdr,
                                                loader=lambda s, n: ["the load logged Error in Map.FinalizeLoading"],
                                                live=passing))
    check("prove: a broken load is NOT CLEAN", not rec["ok"], rec)
    rec = _with_contract([[]], lambda: TS.prove(Stub(), P, "RELENTLESS", tier_list=hdr[:-1], running=hdr,
                                                loader=loader, live=passing))
    check("prove: a header naming a mod beyond the fixture tier is NOT CLEAN",
          not rec["ok"] and any("beyond" in p for p in rec["problems"]), rec)
    fixes = []
    spy = lambda s, P_, seat, fix=False: fixes.append(fix) or [Check("P-L1", PASS, "ok")]   # noqa: E731
    _with_contract([[]], lambda: TS.prove(Stub(), P, "RELENTLESS", tier_list=hdr + ["rimbridgeserver"], running=hdr, loader=loader, live=spy))
    check("prove: preflight runs with --fix", fixes == [True], fixes)
    os.chmod(golden, stat.S_IREAD | stat.S_IWRITE)
    os.remove(golden)


def sec6_pe8(d):
    P = FakeP(d)
    sc = {"render_profile": {"screenWidth": "2516", "screenHeight": "1252", "fullscreen": "False", "uiScale": "1",
                             "langFolderName": "English", "textureCompression": "True"}}
    prefs_xml(P.prefs, screenWidth=3467, screenHeight=1826)
    r = PF.p_e8(Stub(), P, sc)
    check("P-E8: a different window size (3467x1826 vs 2516x1252) PASSes and is recorded",
          r.status == PASS and "3467x1826" in r.evidence, (r.status, r.evidence))
    prefs_xml(P.prefs, fullscreen="True")
    r = PF.p_e8(Stub(), P, sc)
    check("P-E8: fullscreen still FAILs", r.status == FAIL and "fullscreen" in r.evidence, (r.status, r.evidence))
    prefs_xml(P.prefs, uiScale="1.25")
    check("P-E8: a different UI scale still FAILs", PF.p_e8(Stub(), P, sc).status == FAIL)


def sec7_pe4(d):
    P = FakeP(d)
    prefs_xml(P.prefs, autosaveIntervalDays="0.25")
    r = PF.p_e4(Stub({"jawa/list_pawns": {"pawns": []}}), P, {})
    check("P-E4: autosave 0.25 days FAILs without --fix", r.status == FAIL, (r.status, r.evidence))

    def setter(**kw):
        prefs_xml(P.prefs, autosaveIntervalDays=kw["autosaveIntervalDays"])
        return {"success": True, "saved": True}
    s = Stub({"jawa/list_pawns": {"pawns": []}}, on={"jawa/prefs": setter})
    r = PF.p_e4(s, P, {}, fix=True)
    check("P-E4 --fix: sets autosave through jawa/prefs and PASSes on the re-read file",
          r.status == PASS and ("jawa/prefs", {"autosaveIntervalDays": PF.AUTOSAVE_OFF_DAYS}) in s.calls,
          (r.status, r.evidence, s.calls))
    prefs_xml(P.prefs, autosaveIntervalDays="0.25")
    liar = Stub({"jawa/list_pawns": {"pawns": []}, "jawa/prefs": {"success": True, "saved": True}})
    r = PF.p_e4(liar, P, {}, fix=True)
    check("P-E4 --fix: a setter that says success but leaves Prefs.xml at 0.25 still FAILs", r.status == FAIL,
          (r.status, r.evidence))
    prefs_xml(P.prefs, autosaveIntervalDays="14")
    quiet = Stub({"jawa/list_pawns": {"pawns": []}})
    r = PF.p_e4(quiet, P, {}, fix=True)
    check("P-E4 --fix: autosave already off makes no setter call", r.status == PASS and not any(
        c[0] == "jawa/prefs" for c in quiet.calls), quiet.calls)
    prefs_xml(P.prefs, autosaveIntervalDays="0.25")
    r = PF.p_e4(Stub({"jawa/list_pawns": {"pawns": [{"id": "Human1"}]}}, on={"jawa/prefs": setter}), P, {}, fix=True)
    check("P-E4 --fix: a pawn on the map still FAILs (the roster is not fixed)", r.status == FAIL, r.evidence)


def sec8_live_tier():
    """GAMEENV_FIX_PROOFSITE_1CD219EC_ITEMS_WAIT: gate passes only on the exact S.TIER list, so every live clause of the
    item's proof file must name that tier (an exact tier runs on SteveDesktop through testq). Without the line,
    Archmagi's round ran A1/A2 on a 23-mod list and read WRONG GAME, which no lane step could fix."""
    root = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
    sys.path.insert(0, os.path.join(root, "src", "RimMandrake", "rimflow"))
    import relentless_live_round as R
    with open(os.path.join(root, "infrastructure", "state", "live_proofs",
                           "TRIAL_SITE_REBUILD_FOR_FOURTEEN_MODS.txt"), encoding="utf-8") as fh:
        text = fh.read()
    cids = [ln.split(":", 1)[0].split()[-1] for ln in text.splitlines() if ln.startswith("live-proof ")]
    got = {k: R.clause_tier(text, k) for k in cids}
    check("live proofs: every clause runs on tier %s (%s)" % (S.TIER, ",".join(cids)),
          bool(cids) and all(v == S.TIER for v in got.values()), got)
    sys.path.insert(0, os.path.join(root, "src", "RimMandrake", "Utils"))
    import modset_builder as MB
    check("live proofs: modset_builder knows tier %s (testq can load it)" % S.TIER, S.TIER in MB.TIERS)


def main():
    d = tempfile.mkdtemp(prefix="selftest_trial_site_")
    try:
        sec1_site_spec()
        sec2_gate()
        sec3_contract_tier(d)
        sec4_ensure(d)
        sec5_prove(d)
        sec6_pe8(d)
        sec7_pe4(d)
        sec8_live_tier()
    finally:
        for root, dirs, files in os.walk(d):
            for f in files:
                os.chmod(os.path.join(root, f), stat.S_IREAD | stat.S_IWRITE)
        shutil.rmtree(d, ignore_errors=True)
    print("%d FAIL" % len(FAILS) if FAILS else "ALL PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
