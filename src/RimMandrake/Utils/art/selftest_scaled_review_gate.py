#!/usr/bin/env python3
"""selftest_scaled_review_gate.py — one fixture per requirement that must FAIL, plus one that passes, plus the wiring
(stamp, enforce leaves the old sheet, serve_gated refuses, ingest req 9)."""
from __future__ import annotations

import copy
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import scaled_review_gate as G  # noqa: E402
import ingest as I  # noqa: E402

FAILS = []


def check(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


def col(letter, kind, label, **kw):
    return {"letter": letter, "kind": kind, "label": label, "detail": "", "faces": {"south": "a" * 64}, **kw}


def scale(sid, d, **kw):
    (d / "img").mkdir(exist_ok=True)
    for suf in ("", "_full"):
        (d / "img" / f"scale_{sid}{suf}.png").write_bytes(b"x")
    return {"status": "measured", "source": "live def dump 2026-10-04 · drawSize", "kind": "animal", "cells": 1.0,
            "img": f"img/scale_{sid}.png", "full": f"img/scale_{sid}_full.png", "zoomPpc": 140, **kw}


def html_of(items, sheet_id, extra=""):
    cfg = {"sheetId": sheet_id}
    return ('<html><head><title>t</title></head><body><script id="CONFIG" type="application/json">' + json.dumps(cfg) +
            '</script><script id="ITEMS" type="application/json">' + json.dumps(items) + '</script>'
            '<script id="RENDER">bs-scale entry has no images (this entry lists no Must show) lists no Must show purge' + extra + '</script></body></html>')


def fixture(td: Path):
    """A sheet that passes every requirement. Returns ctx (mutable pieces are deep-copied by callers)."""
    sd = td / "sheets"
    sd.mkdir()
    ap = td / "artpipe"
    for d in ("pending", "active", "done", "failed"):
        (ap / d).mkdir(parents=True)
    (ap / "pending" / "RM_Gamma.json").write_text(json.dumps({"id": "RM_Gamma", "target_def": "RM_Gamma"}))
    (ap / "failed" / "alpha_v1_south.manifest.json").write_text(json.dumps({"worker_status": "failed_canon"}))
    os.environ["ARTPIPE_STATE_DIR"] = str(ap)
    sid = "fix_sheet_2026-10-05"
    donor = col("A", "donor", "donor original — AA_Beta")
    mine = col("B", "artpipe", "render beta_v1")
    items = [
        {"id": "RM_Alpha", "kind": "fauna", "tier": "ours", "flags": [], "canon": None, "canonTag": "no canon-library entry",
         "graphics": [{"cols": [col("A", "live", "live"), col("B", "artpipe", "render alpha_v1" + G.FAILED_CANON_BADGE)]}],
         "scale": scale("alpha", sd), "group": "Fauna"},
        {"id": "RSW_Beta", "kind": "fauna", "tier": "sw", "flags": [], "canonTag": "",
         "canon": {"imgs": ["i.png"], "must": "wings", "brief": "b", "dir": "beta"},
         "graphics": [{"cols": [donor, mine]}], "scale": scale("beta", sd), "group": "Fauna"},
        {"id": "RM_Gamma", "kind": "fauna", "tier": "donor", "flags": [], "canon": None, "canonTag": "no canon-library entry",
         "graphics": [{"cols": [col("A", "donor", "donor original — AA_Gamma")]}], "scale": scale("gamma", sd), "group": "Fauna"},
        {"id": "RM_Delta", "kind": "fauna", "tier": "ours", "flags": [], "canon": None, "canonTag": "no canon-library entry",
         "graphics": [{"cols": [col("A", "live", "live")]}], "scale": scale("delta", sd), "group": G.RULED_GROUP,
         "ruledElsewhere": {"sheet": "Other", "sheetId": "other_sheet_2026-10-05", "pick": "B"}},
    ]
    census_rows = [{"key": "RM_Alpha", "donors": [], "defNames": ["RM_Alpha"], "canon": {"entry": None}},
                   {"key": "RSW_Beta", "donors": ["AA_Beta"], "defNames": ["RSW_Beta"], "canon": {"entry": "/x/beta"}},
                   {"key": "RM_Gamma", "donors": [], "defNames": ["RM_Gamma"], "canon": {"entry": None}},
                   {"key": "RM_Delta", "donors": [], "defNames": ["RM_Delta"], "canon": {"entry": None}}]
    snap = {"sheetId": sid, "biome": "RM_Fix", "snapshotId": "s1", "rows": {"RM_Alpha": {"columns": {"A": {"south": "1"}, "B": {"south": "2"}}}}}
    snap_path = td / "snap.json"
    snap_path.write_text(json.dumps(snap))
    dec = {"savedBy": "review-sheet-sidecar", "writeCount": 3, "snapshotId": "s1",
           "decisions": {"RM_Alpha": {"decision": "B", "at": "t", "decidedAt": "t"}}}
    (sd / "other_sheet_2026-10-05.decisions.json").write_text(json.dumps(
        {"biome": "RM_Other", "savedBy": "x", "writeCount": 2, "decisions": {"RM_Delta": {"decision": "B", "at": "2026-10-05T01:00:00Z", "decidedAt": "t"}}}))
    (sd / f"{sid}.decisions.json").write_text(json.dumps(dec))
    ctx = {"html": html_of(items, sid), "sheet_id": sid, "sheet_dir": sd, "html_path": sd / f"{sid}.html", "snap": snap,
           "snap_path": snap_path, "decisions": dec, "decisions_path": sd / f"{sid}.decisions.json", "biome": "RM_Fix",
           "census_rows": census_rows, "ground": {"rgb": [120, 100, 80], "source": "Sand -> Terrain/Sand (mean of 900 px)"},
           "check_sheet_fn": lambda p, d: (0, "ok"), "browser_fn": lambda p: (40, [], ""), "is_purged": lambda sh: False, "problems": []}
    return ctx, items


def with_items(ctx, items):
    return dict(ctx, html=html_of(items, ctx["sheet_id"]))


def failing(ctx, req):
    cs = G.run_gate(ctx)
    return [c for c in cs if c.req == req and not c.ok]


def main():
    with tempfile.TemporaryDirectory() as t:
        td = Path(t)
        ctx, items = fixture(td)
        base = G.run_gate(ctx)
        check(all(c.ok for c in base), "passing fixture: every check passes" + ("" if all(c.ok for c in base) else " — " + "; ".join(c.line() for c in base if not c.ok)))
        check(any("awaiting a render" in c.note for c in base if c.req == "3") and any(c.req == "7" and "1 collapsed" in c.note for c in base),
              "passing fixture: the donor-only row with a pending job and the collapsed ruled row are both counted")

        def mut(fn):
            it = copy.deepcopy(items)
            c2 = dict(ctx)
            fn(it, c2)
            return with_items(c2, it)

        # req 1
        c = mut(lambda it, c2: it.append(dict(copy.deepcopy(it[0]), id="RM_FromElsewhere")))
        f = failing(c, "1")
        check(f and "RM_FromElsewhere" in f[0].problems[0], "req 1 FAILS: a row from another biome merged in is named")
        check(failing(mut(lambda it, c2: c2.update(biome="", snap={})), "1"), "req 1 FAILS UNMEASURED: snapshot names no biome")
        # req 2
        def no_panel(it, c2): it[0]["scale"] = {"why": "set B has no archived picture"}
        f = failing(mut(no_panel), "2")
        check(f and "RM_Alpha" in f[0].problems[0] and "no scale panel" in f[0].problems[0], "req 2 FAILS: a row with art but no scale panel is named")
        def no_src(it, c2): it[0]["scale"]["source"] = ""
        check(failing(mut(no_src), "2"), "req 2 FAILS: scale panel with no size source")
        def fb_unflagged(it, c2): it[0]["scale"].update(status="fallback", source="FALLBACK 1 cell — no ThingDef")
        check(failing(mut(fb_unflagged), "2"), "req 2 FAILS: a FALLBACK size that the row does not flag")
        def fb_flagged(it, c2):
            it[0]["scale"].update(status="fallback", source="FALLBACK 1 cell — no ThingDef")
            it[0]["flags"] = [G.SIZE_FALLBACK_FLAG + " — x"]
        check(not failing(mut(fb_flagged), "2"), "req 2 passes: a FLAGGED fallback size is allowed")
        check(failing(mut(lambda it, c2: c2.update(ground={"rgb": None, "source": "no terrain texture"})), "2"), "req 2 FAILS: ground colour not measured")
        check(failing(mut(lambda it, c2: c2.update(ground=None)), "2"), "req 2 FAILS UNMEASURED: no ground record at all")
        def zero_html(it, c2): c2["html"] = html_of(it, c2["sheet_id"]).replace("bs-scale", "x")
        check(failing(dict(mut(lambda it, c2: None), html=html_of(items, ctx["sheet_id"]).replace("bs-scale", "zz")), "2"), "req 2 FAILS: page has no scale-panel renderer")
        # req 3
        def donor_only(it, c2): it.append(dict(copy.deepcopy(it[2]), id="RM_NoJob"))
        c = mut(donor_only); c["census_rows"] = ctx["census_rows"] + [{"key": "RM_NoJob", "donors": [], "defNames": ["RM_NoJob"], "canon": {"entry": None}}]
        f = failing(c, "3")
        check(f and "RM_NoJob" in f[0].problems[0] and "RM_Gamma" not in " ".join(f[0].problems), "req 3 FAILS: a donor-only row with no pending/active job; the one WITH a job passes")
        def ph_only(it, c2):
            n = copy.deepcopy(it[0]); n["id"] = "RM_PhNoJob"
            for g in n["graphics"]:
                for col in g["cols"]:
                    col["placeholder"] = "FLAT: 2 colours"
            it.append(n)
        c = mut(ph_only); c["census_rows"] = ctx["census_rows"] + [{"key": "RM_PhNoJob", "donors": [], "defNames": ["RM_PhNoJob"], "canon": {"entry": None}}]
        f = failing(c, "3")
        check(f and "RM_PhNoJob" in f[0].problems[0] and "placeholder art only" in f[0].problems[0], "req 3 FAILS: a placeholder-only row with no pending/active job")
        saved = os.environ["ARTPIPE_STATE_DIR"]
        os.environ["ARTPIPE_STATE_DIR"] = str(td / "nowhere")
        f = failing(ctx, "3")
        os.environ["ARTPIPE_STATE_DIR"] = saved
        check(f and "UNMEASURED" in f[0].problems[0], "req 3 FAILS UNMEASURED when the artpipe state dir cannot be read")
        # req 4
        def no_donor_col(it, c2): it[1]["graphics"][0]["cols"] = [it[1]["graphics"][0]["cols"][1]]
        f = failing(mut(no_donor_col), "4")
        check(f and "RSW_Beta" in f[0].problems[0], "req 4 FAILS: donor-sourced row lost its donor column")
        # req 5
        def canon_missing(it, c2): it[1]["canon"] = None; it[1]["canonTag"] = "no canon-library entry"
        f = failing(mut(canon_missing), "5")
        check(f and "RSW_Beta" in f[0].problems[0], "req 5 FAILS: census has a canon entry but the row shows none")
        def silent(it, c2): it[0]["canonTag"] = ""
        f = failing(mut(silent), "5")
        check(f and "does not say so" in f[0].problems[0], "req 5 FAILS: a row without canon that does not say so")
        # req 6
        def unbadged(it, c2): it[0]["graphics"][0]["cols"][1]["label"] = "render alpha_v1"
        f = failing(mut(unbadged), "6")
        check(f and "not badged" in f[0].problems[0], "req 6 FAILS: a failed-canon render without the badge")
        # req 7
        def repeated(it, c2): it[3].pop("ruledElsewhere"); it[3]["group"] = "Fauna"
        f = failing(mut(repeated), "7")
        check(f and "RM_Delta" in f[0].problems[0], "req 7 FAILS: a subject ruled on another sheet shown as a live row")
        # req 8
        dec2 = copy.deepcopy(ctx["decisions"])
        snap2 = copy.deepcopy(ctx["snap"]); snap2["rows"]["RM_Alpha"]["columns"]["B"] = {"south": "CHANGED"}
        old_snap = ctx["snap"]
        (td / "snap.json").write_text(json.dumps(old_snap))   # the ruled snapshot s1 on disk
        c = dict(ctx, snap=snap2, decisions=dec2)
        f = failing(c, "8")
        check(f and "RM_Alpha:B" in f[0].problems[0], "req 8 FAILS: a letter his decision uses now names different pictures")
        c = dict(ctx, decisions=dict(dec2, snapshotId="gone"))
        f = failing(c, "8")
        check(f and "UNMEASURED" in f[0].problems[0], "req 8 FAILS UNMEASURED: the snapshot his decisions name is not on disk or in git")
        c = dict(ctx, snap=snap2, decisions={"decisions": {"RM_Alpha": {"decision": "B", "prefill": "B"}}, "reviewStatus": {"state": "prefill"}})
        check(not failing(c, "8"), "req 8 passes: an untouched generator prefill is never checked against letters")
        # check_sheet
        f = failing(dict(ctx, check_sheet_fn=lambda p, d: (1, "FAIL  filter bar inside the brief")), "9/chk")
        check(f and "check_sheet exit 1" in f[0].problems[0], "check_sheet nonzero FAILS the gate")
        # req 14
        f = failing(dict(ctx, is_purged=lambda sh: sh.startswith("a")), "14")
        check(f and "purged" in f[0].problems[0], "req 14 FAILS: a ledger-purged picture shown as a column")
        f = failing(dict(ctx, is_purged=lambda sh: sh == "a" * 64), "14")
        check(f and "RM_Alpha" in f[0].problems[0], "req 14 names the row and set")
        # req 14 exception: a purged picture that is still the live IN GAME column is allowed, but only non-pickable
        def _pl(it, c2, **kw):
            cc = it[0]["graphics"][0]["cols"][0]       # RM_Alpha A, the live column (faces "a"*64)
            cc.update(winner=True, purgeable=False, faces={"south": "p" * 64}, **kw)
            it[0]["letters"] = ["B"] if kw.get("purgedLive") else ["A", "B"]
        _pu = dict(ctx, is_purged=lambda sh: sh == "p" * 64)
        check(not failing(dict(mut(lambda it, c2: _pl(it, c2, purgedLive=True)), is_purged=_pu["is_purged"]), "14"),
              "req 14 passes: a purged picture that is still live is shown as the non-pickable IN GAME column")
        f = failing(dict(mut(lambda it, c2: _pl(it, c2)), is_purged=_pu["is_purged"]), "14")
        check(f and "purged" in f[0].problems[0], "req 14 FAILS: a purged picture that is NOT flagged purgedLive")
        def _pk(it, c2):
            _pl(it, c2, purgedLive=True); it[0]["letters"] = ["A", "B"]
        f = failing(dict(mut(_pk), is_purged=_pu["is_purged"]), "14")
        check(f and "pickable" in f[0].problems[0], "req 14 FAILS: a purged-but-live picture that is pickable")
        # req 13
        f = failing(dict(ctx, browser_fn=lambda p: (0, [], "")), "13")
        check(f and "renders blank" in f[0].problems[0], "req 13 FAILS: a sheet that renders far fewer images than its rows")
        f = failing(dict(ctx, browser_fn=lambda p: (40, ["Uncaught (in promise) TypeError: Cannot read properties of null (reading '0')"], "")), "13")
        check(f and "Uncaught" in f[0].problems[0], "req 13 FAILS: an uncaught console error")
        f = failing(dict(ctx, browser_fn=lambda p: (None, [], "UNMEASURED: Edge not found")), "13")
        check(f and "UNMEASURED" in f[0].problems[0], "req 13 FAILS UNMEASURED: no browser")
        # req 10
        (ctx["sheet_dir"] / f"{ctx['sheet_id']}.serve.log").write_text("http://localhost:9/?t=abc\n")
        items_ = G._items(ctx)
        check(not G.check_urls(ctx, items_).ok, "req 10 FAILS: the served link does not answer 200")
        (ctx["sheet_dir"] / f"{ctx['sheet_id']}.serve.log").unlink()
        check("UNMEASURED" in G.check_urls(ctx, items_).problems[0], "req 10 FAILS UNMEASURED: no serve log to read the link from")
        # req 11
        check(failing(dict(ctx, html=ctx["html"].replace("purge", "xx")), "11"), "req 11 FAILS: no purge control on the page")
        # a crashing check is a FAIL, never a pass
        bad = dict(ctx, census_rows=[{"nokey": 1}])
        cs = G.run_gate(bad)
        check(any(not c.ok for c in cs), "a malformed census cannot silently pass")

        # stamp
        s = G.stamp(ctx["html"])
        check(G.verify_stamp(s)[0], "stamp verifies on the HTML it was made for")
        check(not G.verify_stamp(ctx["html"])[0], "an HTML never gated has no valid stamp")
        check(not G.verify_stamp(s.replace("purge", "purgX"))[0], "a hand edit after the gate invalidates the stamp")
        # enforce: pass moves stamped; fail leaves the old sheet and no tmp
        out = ctx["sheet_dir"] / "fix_sheet_2026-10-05.html"
        out.write_text("PREVIOUS GOOD SHEET")
        G.enforce(ctx["html"], ctx, out)
        G.commit(out.with_name(out.stem + ".gate.tmp.html"), out)
        check(G.verify_stamp(out.read_text())[0] and not out.with_name(out.stem + ".gate.tmp.html").exists(), "enforce: a passing sheet is moved into place, stamped")
        good = out.read_text()
        try:
            G.enforce(no_panel_html := mut(no_panel)["html"], dict(ctx), out)
            raised = False
        except G.GateFailed as e:
            raised = any(c.req == "2" for c in e.checks if not c.ok)
        check(raised and out.read_text() == good and not out.with_name(out.stem + ".gate.tmp.html").exists(),
              "enforce: a failing sheet raises GateFailed, the previous good sheet is byte-identical, no tmp left")
        # serve_gated
        ctx["html_path"].write_text(ctx["html"])
        r = subprocess.run([sys.executable, str(HERE / "serve_gated.py"), "--no-open", "--sheet", str(ctx["html_path"]), "--decisions", "x.json"],
                           capture_output=True, text=True)
        check(r.returncode == 4 and "no gate stamp" in r.stderr, "serve_gated REFUSES an HTML without a gate stamp (exit 4)")
        ctx["html_path"].write_text(G.stamp(ctx["html"]).replace("purge", "purgX", 1))
        r = subprocess.run([sys.executable, str(HERE / "serve_gated.py"), "--sheet", str(ctx["html_path"])], capture_output=True, text=True)
        check(r.returncode == 4 and "edited after the gate" in r.stderr, "serve_gated REFUSES a stamped HTML that was edited after the gate")

        # ingest req 9
        d = {"decisions": {"RM_Alpha": {"decision": "redo", "note": "make it teardrop-shaped", "at": "t", "decidedAt": "t"},
                           "RM_Beta": {"decision": "B", "note": "more variations", "at": "t", "decidedAt": "t"}}}
        good_jobs = [{"id": "a_v1", "target_def": "RM_Alpha", "owner_note": "make it teardrop-shaped"},
                     {"id": "b_v1", "target_def": "RM_Beta", "owner_note": ["more variations"]}]
        check(I.check_redo_jobs(d, good_jobs) == [], "ingest req 9: jobs carrying the note verbatim pass")
        bad_jobs = [dict(good_jobs[0], owner_note="teardrop"), good_jobs[1]]
        check(any("verbatim" in x for x in I.check_redo_jobs(d, bad_jobs)), "ingest req 9 FAILS: a paraphrased owner_note")
        check(any("redo with no regen job" in x for x in I.check_redo_jobs(d, [good_jobs[1]])), "ingest req 9 FAILS: a redo decision with no job")
        check(any("UNMEASURED" in x for x in I.check_redo_jobs(d, [{"id": "z", "target_def": "RM_Nope", "owner_note": "n"}])), "ingest req 9 FAILS UNMEASURED: a job targeting no decided row")
        (td / "dec.json").write_text(json.dumps(d))
        r = I.ingest(td / "dec.json")
        check(not r["ok"] and "REFUSED (req 9)" in r["error"], "ingest REFUSES redo decisions with no --redo-jobs file")
        (td / "jobs.json").write_text(json.dumps(bad_jobs))
        r = I.ingest(td / "dec.json", redo_jobs=td / "jobs.json")
        check(not r["ok"] and "verbatim" in r["error"], "ingest REFUSES when a queued job's owner_note is not his note")
    print(f"{'ALL PASS' if not FAILS else str(len(FAILS)) + ' FAIL'}")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
