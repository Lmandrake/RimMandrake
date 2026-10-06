"""selftest_human_review.py -- FlowWorks/human_review.py (the capability review sheet) does what it says.

    python3 src/RimMandrake/FlowWorks/northstar/selftest_human_review.py

Proves: every row carries a status and a group; status is DERIVED (flip the probes or the result and it moves); a
planted PASS row flips a capability to PROVEN-LIVE; an open owning item lands in the remains list (a closed one does
not); the derivation can return every status; probes can see something known to exist (sanity) and miss something
known absent; no capability maps a harness row; every walk bar is carried by a row; the generated sheet passes
check_sheet.py; and the decisions file is never overwritten.
Designer view (owner, 2026-10-05: "not human readable. Bad medium for review."): every capability sits in exactly one
feature; 30-50 features in <= 9 sections; feature status is derived (every one of the four reachable, and it moves
with the evidence); no main-view string carries a defName, ticket id, test row, class or code chip; the waits-on of an
unbuilt part is read from the ledger; asks are at most five; the status board is written.
"""
import re
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import human_review as H  # noqa: E402

CHECK = os.path.expanduser("~/.claude/skills/review-sheets/assets/check_sheet.py")
FAILS = []


def ok(cond, what):
    print(("PASS " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


def main():
    tmp = tempfile.mkdtemp(prefix="fw_review_selftest_")
    try:
        caps = H.CAPS
        ids = [c["id"] for c in caps]
        ok(len(ids) == len(set(ids)), "capability ids unique (%d)" % len(ids))
        ok(len(ids) >= 80, "at least 80 intended capabilities (%d)" % len(ids))
        ok(all(c["g"] in H.GROUPS for c in caps), "every capability has a known group")
        ok(all(c.get("probes") for c in caps), "every capability declares at least one probe")
        ok(all(c.get("item") for c in caps), "every capability names an owning item")
        bad = [r for c in caps for r in c.get("rows", []) if r.startswith(H.HARNESS_PREFIXES)]
        ok(not bad, "no capability maps a harness row (L*, SITE*, A0, E9, Z): %s" % bad)

        # probe sanity: something known present is seen, something known absent is not
        present = ["cs:class RM_MapComponent_Excavation", "set:pulseIntervalTicks", "xml:defName>RM_Channel_Superdeep<",
                   "tex:RM_Barrel", "file:src/RimMandrake/FlowWorks/About/About.xml"]
        absent = ["cs:class ZZ_NoSuchClass_42", "set:zzNoSuchSetting", "xml:defName>ZZ_NoSuch<", "tex:ZZ_nope",
                  "file:src/RimMandrake/FlowWorks/ZZ_nope.txt"]
        ok(all(H.probe(p) for p in present), "sanity: every known-present probe is seen")
        ok(not any(H.probe(p) for p in absent), "sanity: no known-absent probe is seen")
        ok(H.probe("!cs:class ZZ_NoSuchClass_42") and not H.probe("!cs:class RM_MapComponent_Excavation"), "negated probes invert")
        ok(H.probe("rx:src/RimMandrake/FlowWorks/Source:class RM_MapComponent_Excavation"), "rx probes see a known class")
        ok(not H._rx_dir("src/RimMandrake/FlowWorks", r"never let a probe match its own declaration"),
           "rx probes never match the generator or this selftest")

        # every status reachable, and status follows the evidence (not a typed field)
        c = dict(id="T", g="A", label="t", effect="t", item="X", probes=["a", "b"], rows=["R1"])
        st = lambda pf, rows: H.derive_status(c, rows, pf)["status"]  # noqa: E731
        got = {st(lambda p: False, {}), st(lambda p: p == "a", {}), st(lambda p: True, {}),
               st(lambda p: True, {"R1": ("PASS", "")})}
        ok(got == set(H.STATUSES), "derivation can return each status: %s" % sorted(got))
        ok(st(lambda p: True, {"R1": ("FAIL", "")}) == "BUILT-UNPROVEN", "a FAIL row does not prove anything")
        allno = {H.derive_status(x, {}, lambda p: False)["status"] for x in caps if not x.get("rows")}
        allyes = {H.derive_status(x, {}, lambda p: True)["status"] for x in caps}
        ok(allno == {"NOT BUILT"} and allyes == {"BUILT-UNPROVEN"}, "real table: statuses move with the probes")

        # a planted PASS row flips a real capability to PROVEN-LIVE, end to end through build()
        states = {i: ("done", "") for i in {x["item"] for x in caps}}
        base = H.build(os.path.join(tmp, "a", "s.html"), states=states)
        target = next(x for x in base["caps"] if x["d"]["status"] == "BUILT-UNPROVEN")
        planted = os.path.join(tmp, "validation_v2_result_planted.json")
        json.dump({"rows": [{"id": "FAKE_PLANTED_ROW", "status": "PASS", "detail": "planted"}]}, open(planted, "w"))
        caps2 = [dict(x, rows=x.get("rows", []) + ["FAKE_PLANTED_ROW"]) if x["id"] == target["id"] else x for x in caps]
        before = H.build(os.path.join(tmp, "b", "s.html"), states=states, caps=caps2)
        after = H.build(os.path.join(tmp, "c", "s.html"), result=planted, states=states, caps=caps2)
        sb = next(x for x in before["caps"] if x["id"] == target["id"])["d"]["status"]
        sa = next(x for x in after["caps"] if x["id"] == target["id"])["d"]["status"]
        ok(sb == "BUILT-UNPROVEN" and sa == "PROVEN-LIVE", "planted PASS flips %s: %s -> %s" % (target["id"], sb, sa))

        # remains list: an open owning item lands in it, the same item closed does not
        nb = next(x for x in base["caps"] if x["d"]["status"] == "NOT BUILT")
        open_states = dict(states, **{nb["item"]: ("proposed", "a planted open item")})
        r_open = H.remains(base["caps"], open_states)
        r_done = H.remains(base["caps"], states)
        ok(nb["item"] in r_open and nb["id"] in [x["id"] for x in r_open[nb["item"]]["todo"]],
           "open item %s lands in remains with %s" % (nb["item"], nb["id"]))
        ok(not r_done, "closed items never land in remains")

        # the real sheet: every row has status + group; walk bars covered; check_sheet passes
        real = H.build(os.path.join(tmp, "real", "FlowWorks_review.html"))
        feat_rows = [it for it in real["items"] if it["fw"].get("status")]
        ok(all(it.get("group") for it in real["items"]) and all(it["fw"]["status"] in H.F_LABEL for it in feat_rows)
           and len(feat_rows) == len(H.FEATURES), "every feature row has one status and a group (%d rows)" % len(feat_rows))
        ok(os.path.exists(real["board"]) and "FlowWorks status board" in open(real["board"]).read(), "status board written")
        must, cannot, _ = H.walk_bars()
        ok(must and not real["uncovered"], "every walk bar (%d) is carried by a row; uncovered %s" % (len(must + cannot), real["uncovered"]))
        p = subprocess.run([sys.executable, CHECK, real["out"], "--quiet"], capture_output=True, text=True)
        ok(p.returncode == 0, "check_sheet.py exits 0 on the generated sheet\n" + p.stdout[-600:])
        ok('<script id="RENDER">\nwindow.itemBody' in open(real["out"]).read(), "the RENDER hook is live (outside the comment)")

        # ---- designer view
        from collections import Counter
        use = Counter(c for f in H.FEATURES for c in f["caps"] + f.get("minor", []))
        ok(set(use) == set(ids) and max(use.values()) == 1, "every capability is in exactly one feature")
        ok(30 <= len(H.FEATURES) <= 50 and len(H.SECTIONS) <= 9, "%d features in %d sections" % (len(H.FEATURES), len(H.SECTIONS)))
        ok(set(H.PLAIN) == set(ids), "every capability has a plain phrase")
        jargon = re.compile(r"\b[A-Z][A-Z0-9]+(_[A-Z0-9]+)+\b|\bRM_|\bRUT_|\b[A-N]\d{2}\b|defName|xpath|\bclass\b|"
                            r"PROVEN|UNPROVEN|\bD=\d|\bPh\d|Ruling \d|\.cs\b|\.xml\b|<\w+>")
        texts = [f["title"] for f in H.FEATURES] + [f["say"] for f in H.FEATURES] + list(H.PLAIN.values()) + \
            [a["title"] for a in H.ASKS] + [a["say"] for a in H.ASKS] + [a.get("short", "") for a in H.ASKS] + \
            list(H.SHOT_CAPTIONS.values()) + [n for _, n in H.SECTIONS] + list(H.F_LABEL.values()) + list(H.F_MEANS.values())
        bad = [t for t in texts if jargon.search(t)]
        ok(not bad, "no jargon in the main view: %s" % bad[:3])
        ok(jargon.search("FLOWWORKS_BUILD_PROGRAM_1") and jargon.search("RM_Channel_Empty") and jargon.search("A04"),
           "sanity: the jargon guard catches a ticket id, a defName and a row id")
        f = dict(id="t", s="dig", title="t", say="", caps=["X1", "X2"])
        capd = lambda a, b: {"X1": {"d": {"status": a}}, "X2": {"d": {"status": b}}}  # noqa: E731
        got = {H.feature_status(f, capd(*p))[0] for p in [("NOT BUILT", "NOT BUILT"), ("PROVEN-LIVE", "NOT BUILT"),
                                                             ("PROVEN-LIVE", "BUILT-UNPROVEN"), ("PROVEN-LIVE", "PROVEN-LIVE")]}
        ok(got == set(H.F_ORDER), "feature status can be each of the four: %s" % sorted(got))
        ok(H.feature_status(dict(f, minor=["X2"], caps=["X1"]), capd("PROVEN-LIVE", "BUILT-UNPROVEN"))[0] == H.F_WORKS
           and H.feature_status(dict(f, minor=["X2"], caps=["X1"]), capd("PROVEN-LIVE", "NOT BUILT"))[0] == H.F_PARTLY,
           "a minor part never proves a feature but can hold it back")
        st = {"I1": ("proposed", ""), "I2": ("done", ""), "I3": ("doing", ""), "I4": ("ready", "")}
        nd = {"I1": ("owner", ""), "I3": ("offline", "OTHER_ITEM_1"), "I4": ("offline", "")}
        ok([H.waits_on(i, st, nd) for i in ("I1", "I2", "I3", "I4")] == ["you", "unfiled", "other", "nothing"]
           and H.waits_on("I1", {"I1": ("UNMEASURED", "")}, nd) == "unknown", "waits-on read from the ledger")
        ok(len(real["asks"]) <= 5, "at most five asks (%d)" % len(real["asks"]))
        html_txt = open(real["out"]).read()
        ok('id="glance"' in html_txt and 'id="FWAFTER"' in html_txt and 'id="FWSTYLE"' in html_txt,
           "glance panel, after-hook and style are placed")

        # the decisions file is the owner's once it exists: a rebuild never overwrites it
        dec = os.path.join(os.path.dirname(real["out"]), H.DEC_NAME)
        d = json.load(open(dec))
        ok(d.get("decisions") == {} and d["reviewStatus"]["state"] == "prefill", "fresh decisions file: empty, reviewStatus prefill")
        d["decisions"]["dig_canal"] = {"decision": "wrong", "note": "owner says"}
        json.dump(d, open(dec, "w"))
        H.build(real["out"])
        ok(json.load(open(dec))["decisions"].get("dig_canal", {}).get("decision") == "wrong", "rebuild leaves an existing decisions file alone")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("\n%s: %d failure(s)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
