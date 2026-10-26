#!/usr/bin/env python3
"""selftest_sheet_artifact_merge.py — the remote (claude.ai Artifact) review route: sheet_artifact_merge.py writes his
picks the way the sheet's sidecar would, marks them as his input from that route (never an agent guess), refuses what it
cannot place, and is a no-op on a re-run; sheet_to_artifact.py's page carries every lane, facing and full-size link,
and its db document id is the one the merge expects."""
import contextlib
import io
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import decisions_v2 as DV  # noqa: E402
import sheet_artifact_merge as M  # noqa: E402
import sheet_to_artifact as SA  # noqa: E402

FAILS = []
REV = "rev1"
PRIM, SECOND, LOOSE = "Mod/Things/RM_Weir", "Mod/Things/RM_Weir_young", "Mod/Things/RM_Weir_loose"


def check(c, m):
    print(("PASS " if c else "FAIL ") + m)
    if not c:
        FAILS.append(m)


def col(letter, sha, **kw):
    return {"kind": "artpipe", "letter": letter, "short": f"set {letter}", "setId": f"set-{letter}",
            "faces": {"south": sha + "s", "east": sha + "e"}, "scale": {"img": f"img/{sha}_scale.png", "face": "south"}, **kw}


ITEMS = [
    {"id": "RM_Weir", "label": "Weir", "kind": "building", "rev": REV, "prefill": "A",
     "thumbs": {}, "fulls": {}, "graphics": [
         {"key": PRIM, "primary": True, "lane": "slot", "facings": ["south", "east"], "slot": {"id": "s1", "label": "built"},
          "cols": [col("A", "a", winner=True), col("B", "b"), col("C", "c", noSelect=True)]},
         {"key": SECOND, "lane": "slot", "facings": ["south", "east"], "slot": {"id": "s2", "label": "young"},
          "cols": [col("D", "d"), col("E", "e")]},
         {"key": LOOSE, "lane": "unassigned", "facings": ["south", "east"], "cols": [col("F", "f")]}]},
    {"id": "RM_Stake+1", "label": "Stake", "kind": "building", "rev": REV, "prefill": "A", "thumbs": {}, "fulls": {},
     "graphics": [{"key": "Mod/Things/RM_Stake", "primary": True, "lane": "slot", "facings": ["south"],
                   "slot": {"id": "s3"}, "cols": [col("A", "g", winner=True), col("B", "h")]}]},
]
for it in ITEMS:
    for g in it["graphics"]:
        for c in g["cols"]:
            for sha in c["faces"].values():
                it["thumbs"][sha], it["fulls"][sha] = f"img/{sha}.png", f"img/{sha}_full.png"


def sheet_html():
    cfg = {"sheetId": "t_sheet", "title": "Test walk art (rebuilt) — game art", "options": [
        {"key": k, "counts": "in"} for k in "ABCDEF"] + [{"key": "redo", "counts": "out"}, {"key": "hold", "counts": "out"}]}
    return ('<html><body><script id="CONFIG" type="application/json">' + json.dumps(cfg) + '</script>'
            '<script id="ITEMS" type="application/json">' + json.dumps(ITEMS).replace("</", "<\\/") + "</script></body></html>")


def fresh(td: Path, **extra) -> Path:
    dp = td / "t_sheet.decisions.json"
    doc = {"sheetId": "t_sheet", "reviewStatus": {"state": "prefill"}, "decisions": {
        "RM_Weir": {"decision": "A", "note": "", "prefill": "A", "picks": {SECOND: "D"},
                    "reject": {PRIM: ["B", "C"]}},
        "RM_Stake+1": {"decision": "A", "note": "", "prefill": "A",
                       "notes_followed": [{"note": "make it taller", "when": "2026-10-20"}]}}}
    doc.update(extra)
    dp.write_text(json.dumps(doc))
    return dp


def body(row="RM_Weir", **kw):
    b = {"rowId": row, "sheetId": "t_sheet", "rev": REV, "pick": "", "slots": {}, "note": "", "done": False,
         "ts": "2026-10-26T10:00:00Z", "pickedAt": None, "route": M.ROUTE}
    b.update(kw)
    return b


def run(td: Path, docs, *flags, dp=None, raw=None):
    pp = td / "picks.json"
    pp.write_text(raw if raw is not None else json.dumps(docs))
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = M.main([str(pp), str(dp or td / "t_sheet.decisions.json"), *flags])
    return rc, out.getvalue() + err.getvalue()


def dec(td: Path) -> dict:
    return json.loads((td / "t_sheet.decisions.json").read_text())


def main() -> int:
    with tempfile.TemporaryDirectory() as t:
        td = Path(t)
        (td / "t_sheet.html").write_text(sheet_html())

        # 1. a primary pick: his decision, stamped as his, with the sheet's slot ids, through the sidecar's writer
        fresh(td)
        picked = body(pick="B", slots={PRIM: {"state": "pick", "pick": "B"}}, pickedAt="2026-10-26T10:00:00Z", note="good")
        rc, out = run(td, {"picks": {"RM_Weir": picked}})
        check(rc == 0 and "dry run" in out and "writeCount" not in dec(td), "dry run by default writes nothing")
        rc, out = run(td, [picked], "--apply")
        d = dec(td)
        r = d["decisions"]["RM_Weir"]
        check(rc == 0 and r["decision"] == "B" and r["decidedAt"] == "2026-10-26T10:00:00Z", f"primary pick -> decision B, decidedAt (rc {rc}) {out[-200:]}")
        check(r["slots"][PRIM] == {"state": "pick", "pick": "B", "set_id": "set-B", "slot_id": "s1", "at": "2026-10-26T10:00:00Z"},
              f"slot record mirrors SLX.setSlot {r['slots'].get(PRIM)}")
        check(r["reject"].get(PRIM) == ["C"], "picking B clears B's reject mark, keeps C's")
        check(r["via"]["route"] == M.ROUTE and r["via"]["by"] == "owner" and r["schema"] == 2 and r["rev"] == REV,
              "row marked as his input from the remote route, schema 2, sheet rev")
        check(d["savedBy"] == "artifact-db-merge" and d["writeCount"] == 1 and d["reviewStatus"]["state"] == "prefill",
              "file stamped savedBy artifact-db-merge, writeCount 1, reviewStatus untouched")
        check(DV.decision_is_his(r), "decisions_v2 reads the pick as his")
        check(r["note"] == "good" and r["picks"] == {SECOND: "D"}, "note written; second-slot legacy map untouched")

        # 2. a re-run of the same picks is a no-op
        rc, out = run(td, [picked], "--apply")
        check(rc == 0 and dec(td)["writeCount"] == 1 and "0 row(s) change" in out, "re-run changes nothing")

        # 3. a note-only touch never turns the prefill into his decision; a followed note is not re-opened
        fresh(td)
        rc, out = run(td, [body(note="tidy the base"), body("RM_Stake+1", note="make it taller", done=True)], "--apply")
        d = dec(td)["decisions"]
        check(rc == 0 and d["RM_Weir"]["decision"] == "A" and "decidedAt" not in d["RM_Weir"]
              and not DV.decision_is_his(d["RM_Weir"]) and d["RM_Weir"]["note"] == "tidy the base",
              "note-only row keeps the prefill as a prefill")
        rc, out = run(td, [body(note="tidy the base"), body("RM_Stake+1", note="make it taller", done=True)], "--apply")
        check("0 row(s) change" in out and dec(td)["writeCount"] == 1, "re-sending a followed note is a no-op on re-run")
        check(d["RM_Stake+1"]["note"] == "" and d["RM_Stake+1"]["remoteDone"] is True
              and d["RM_Stake+1"]["notes_followed"][0]["note"] == "make it taller",
              "a note enact already followed is blanked (guard_ops); done tick kept")

        # 4. hold, redraw, a second-slot pick
        fresh(td)
        rc, _ = run(td, [body(pick="hold", pickedAt="2026-10-26T11:00:00Z", slots={PRIM: {"state": ""}}),
                         body("RM_Stake+1", pick="redo", slots={"Mod/Things/RM_Stake": {"state": "redraw"}},
                              pickedAt="2026-10-26T11:00:00Z")], "--apply")
        d = dec(td)["decisions"]
        check(rc == 0 and d["RM_Weir"]["decision"] == "hold" and PRIM not in d["RM_Weir"]["slots"], "hold -> decision hold, no primary slot")
        check(d["RM_Stake+1"]["decision"] == "redo" and d["RM_Stake+1"]["slots"]["Mod/Things/RM_Stake"]["state"] == "redraw",
              "redraw -> decision redo + redraw slot")
        rc, _ = run(td, [body(pick="", pickedAt="2026-10-26T12:00:00Z")], "--apply")
        check(dec(td)["decisions"]["RM_Weir"]["decision"] == "", "taking the hold back clears it")
        fresh(td)
        rc, _ = run(td, [body(pick="", slots={SECOND: {"state": "pick", "pick": "E"}}, pickedAt="2026-10-26T12:00:00Z")], "--apply")
        r = dec(td)["decisions"]["RM_Weir"]
        check(rc == 0 and r["picks"][SECOND] == "E" and r["slots"][SECOND]["pick"] == "E" and r["decision"] == "A"
              and "decidedAt" not in r, "second-slot pick updates its lane and the legacy map, never the primary decision")

        # 5. ArtifactData-style nesting is found
        fresh(td)
        rc, out = run(td, None, raw=json.dumps({"collection": "picks", "docs": [{"id": "RM_Weir", "data": picked}]}))
        check(rc == 0 and "1 row(s) change" in out, "documents nested under docs[].data are found")

        # 6. refusals: nothing written
        fresh(td)
        cases = {
            "empty input": (None, "[]"),
            "two documents for one row": ([picked, dict(picked, note="other")], None),
            "unknown row": ([body("RM_Nope")], None),
            "another sheet": ([body(sheetId="other")], None),
            "stale rev": ([body(rev="old", note="x")], None),
            "letter not in the slot": ([body(slots={PRIM: {"state": "pick", "pick": "D"}}, pickedAt="t")], None),
            "placeholder set": ([body(slots={PRIM: {"state": "pick", "pick": "C"}}, pickedAt="t")], None),
            "unassigned lane": ([body(slots={LOOSE: {"state": "pick", "pick": "F"}}, pickedAt="t")], None),
            "bad primary pick": ([body(pick="AB", pickedAt="t")], None),
        }
        for name, (docs, raw) in cases.items():
            rc, out = run(td, docs, "--apply", raw=raw)
            check(rc == 2 and "REFUSED" in out and "writeCount" not in dec(td), f"refuses {name} (rc {rc})")
        rc, _ = run(td, [body(rev="old", note="x")], "--apply", "--allow-stale")
        check(rc == 0 and dec(td)["decisions"]["RM_Weir"]["note"] == "x", "--allow-stale accepts an older rev")
        fresh(td, frozen=True, frozenOn="2026-10-25")
        rc, out = run(td, [picked], "--apply")
        check(rc == 5 and "frozen" in out and "writeCount" not in dec(td), "a frozen file is refused (exit 5)")

        # 7. the page: doc ids match, every lane/facing/full link present, page rules
        ids = ["RM_Weir", "RM_Stake+1", "a.b/c d", "RM_Ä", "x\U0001F600", "x\u1F60" + "0"]
        check(len({SA.doc_id(i) for i in ids}) == len(ids) and all(re.fullmatch(r"[A-Za-z0-9_~]+", SA.doc_id(i)) for i in ids),
              "doc ids are injective and use only db-safe characters")
        js = re.search(r"const docId = .*", SA.PAGE).group(0)
        node = shutil.which("node")
        if node:
            src = js + "\nconsole.log(JSON.stringify(%s.map(docId)));" % json.dumps(ids)
            r = subprocess.run([node, "-e", src], capture_output=True, text=True, timeout=30)
            check(json.loads(r.stdout) == [SA.doc_id(i) for i in ids], "page JS docId == python doc_id")
        else:
            check("/^[A-Za-z0-9_]$/" in js and "padStart(4, '0')" in js, "page JS docId uses the same rule (no node to run it)")
        from PIL import Image
        (td / "img").mkdir()
        for it in ITEMS:
            for ref in list(it["thumbs"].values()) + list(it["fulls"].values()) + \
                    [c["scale"]["img"] for g in it["graphics"] for c in g["cols"]]:
                Image.new("RGBA", (8, 8), (90, 70, 50, 255)).save(td / ref)
        out_dir = td / "out"
        imgs = SA.Images(td, out_dir)
        rows = SA.build_rows(ITEMS, json.loads(re.search(r'id="CONFIG"[^>]*>(.*?)</script>', sheet_html()).group(1)),
                             {}, imgs)
        page = SA.render("Test walk review", {"rows": rows, "fullMode": {}, "sheetId": "t", "route": SA.ROUTE})
        lanes = rows[0]["lanes"]
        check([ln["pickable"] for ln in lanes] == [True, True, False], "unassigned lane shown but not pickable")
        check(all(len(c["faces"]) == 2 and all(f["full"].endswith("_full.webp") for f in c["faces"]) for ln in lanes for c in ln["cols"]),
              "every facing carries a full-resolution sprite")
        check(len(imgs.published()) == len(set(imgs.published())) and all((out_dir / n).is_file() for n in imgs.published()),
              "every published picture exists")
        title = re.search(r"<title>(.*?)</title>", page).group(1)
        check(2 <= len(title.split()) <= 4, f"title is 2-4 words ({title!r})")
        check(":root{--bg:" in page and '@media (prefers-color-scheme: dark){:root:not([data-theme="light"])' in page
              and ':root[data-theme="dark"]' in page and "body{background:var(--bg)" in page, "theme variables + both dark rules + body background")
        check(not re.search(r"<script[^>]+src=", page) and "padding:0 16px" in page, "no external scripts; 16px gutter")
        check(SA.CAPABILITIES == {"db": {"rules": [{"path": "", "read": "admin", "write": "owner"}]}}, "capabilities declared")
        check("mark done" not in page and 'data-act="done"' not in page and "answered" in page,
              "no 'mark done' (owner 2026-10-26: 'I had no idea what marked done means'); a pick reads 'answered'")

        # 8. questions (owner 2026-10-26): one object per question, coupled states picked as whole sets, explicit no-change
        st_items = []
        for stt in ("Wrecked", "Kludged", "Repaired"):
            it = {"id": f"RM_Pump_{stt}", "label": f"Pump ({stt})", "kind": "building", "rev": REV, "stateSet": "RM_Pump",
                  "thumbs": {}, "fulls": {}, "graphics": [{"key": f"T/RM_Pump_{stt}", "primary": True, "lane": "slot",
                  "facings": ["south"], "slot": {"id": "p"}, "cols": [col("A", f"pa{stt}", winner=True), col("B", f"pb{stt}")]}]}
            for c in it["graphics"][0]["cols"]:
                for sha in c["faces"].values():
                    it["thumbs"][sha], it["fulls"][sha] = f"img/{sha}.png", f"img/{sha}_full.png"
                for ref in list(c["faces"].values()):
                    for r_ in (f"img/{ref}.png", f"img/{ref}_full.png"):
                        Image.new("RGBA", (8, 8), (90, 70, 50, 255)).save(td / r_)
                Image.new("RGBA", (8, 8), (90, 70, 50, 255)).save(td / c["scale"]["img"])
            st_items.append(it)
        qitems = ITEMS + st_items
        qrows = SA.build_rows(qitems, {}, {}, SA.Images(td, td / "out2"))
        rid = [i["id"] for i in st_items]

        def q(**kw):
            base = {"id": "pump", "title": "Pump: which look?", "deciding": "How the pump looks in all three states.",
                    "rows": rid, "options": [
                        {"label": "Keep today's grey pump", "noChange": True, "members": {r: "A" for r in rid}},
                        {"label": "Rusty red pump", "members": {r: "B" for r in rid}}]}
            base.update(kw)
            return {"questions": [base]}

        def refused(spec, what, items=qitems):
            try:
                SA.load_questions(spec, items, qrows)
            except SA.Refused as e:
                return what in str(e)
            return False
        good = SA.load_questions(q(), qitems, qrows)
        check(len(good) == 1 and [len(o["members"]) for o in good[0]["options"]] == [3, 3]
              and all(m["panel"] for o in good[0]["options"] for m in o["members"]),
              "a state set is one question; each option shows every state with its true-scale panel")
        check(refused(q(options=[{"label": "render RM_Pump_v1", "noChange": True, "members": {r: "A" for r in rid}},
                                  {"label": "Rusty", "members": {r: "B" for r in rid}}]), "what it looks like"),
              "an option labelled by render id is refused")
        check(refused(q(options=[{"label": "Grey", "noChange": True, "members": {r: "A" for r in rid}},
                                  {"label": "Rusty", "members": {rid[0]: "B"}}]), "picked whole"),
              "an option that does not cover every state is refused (no mixing machines)")
        check(refused(q(options=[{"label": "Grey", "members": {r: "A" for r in rid}},
                                  {"label": "Rusty", "members": {r: "B" for r in rid}}]), "no change"),
              "a question without an explicit no-change option is refused")
        check(refused(q(options=[{"label": "Grey", "members": {r: "A" for r in rid}},
                                  {"label": "Rusty", "noChange": True, "members": {r: "B" for r in rid}}]), "not what the game shows"),
              "a no-change option that is not the in-game art is refused")
        check(refused(q(rows=rid[:2], options=[{"label": "Grey", "noChange": True, "members": {r: "A" for r in rid[:2]}},
                                                {"label": "Rusty", "members": {r: "B" for r in rid[:2]}}]), "COUPLED"),
              "a state set split across questions is refused")
        mixed = q(options=[{"label": "Grey", "noChange": True, "members": {r: "A" for r in rid}},
                           {"label": "Grey, wrecked and kludged redrawn to match", "members": {rid[0]: "redo", rid[1]: "redo", rid[2]: "A"}}])
        ok_mixed = SA.load_questions(mixed, qitems, qrows)
        check([m["state"] for m in ok_mixed[0]["options"][1]["members"]] == ["redraw", "redraw", "pick"],
              "an option may ask for some states to be redrawn to match the kept one")
        qp = SA.render("Pump states review", {"rows": [r for r in qrows if r["id"] in rid], "fullMode": {}, "sheetId": "t",
                                               "route": SA.ROUTE, "questions": good, "intro": ""})
        check('data-act="qpick"' in qp and "about ${mins} minute" in qp and "Question ${i + 1} of ${Q.length}" in qp,
              "the page offers one choose button per option and states the question count and time")
        if node:
            js = re.search(r"<script>\n(.*?)</script>", qp, re.S).group(1)
            r = subprocess.run([node, "--check", "-"], input=js, capture_output=True, text=True, timeout=30)
            check(r.returncode == 0, "page script parses " + r.stderr[-200:])
    print(f"{'FAILED' if FAILS else 'ALL PASS'} ({len(FAILS)} failing)")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
