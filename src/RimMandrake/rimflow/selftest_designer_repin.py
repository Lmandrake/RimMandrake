#!/usr/bin/env python3
"""selftest_designer_repin.py - a locked version changed by his card re-pins instead of reopening stage 1
(RIMMANDRAKE_REPIN_LOCKED_CHANGE_STAGES_CARD_REOPENS_STAGE_ONE; refusal record
design/concepts/Pyrelands/version/evidence/exam_and_judge_refusal_2026-11-14.json, clause stale_root_reopens_stage_1).

The fixture is a scratch git repo (ext4, ~/rm/scratch, never /tmp) replaying the real Pyrelands history: the concept
files as stage 3 accepted them (a0d5452ac6), the six maturation test-text corrections (08d917c12a, under his card "All
four now, offline only" on the ADVANCE item) and his paving card "Drop the sentence" (f71693d77a), with the real
stage.json, OWNER lines and a ledger event tying each commit to its card. Checks:
1. before the verb, stale_stage is (1, ['root']), as on the real concept 2026-11-14;
2. `repin` citing each change by its OWNER event and commit (and his two process words on the item) leaves nothing
   stale, stage 4 the open stage, and a locked_change history row; the CLI does the same;
3. it refuses, stage.json byte-identical, a CONDUCTOR source, no source, an unlocked version, a card that is not the
   change's (the exam card for the paving commit), a change left uncited (the corrections), a commit paired with the
   wrong card, an uncommitted edit, and an OWNER event that is not his word (a --per-ruling close);
4. his word after the loop crossed its ceiling lifts the spend park even when no park was written yet (the park would
   have been written after his card and waited for another word); no word, no lift;
6. RIMMANDRAKE_REPIN_WHEN_GRANT_ITEMS_CLOSE: repin_sources (the Maturation tick's own re-pin) finds the cards a hand
   re-pin cites (paving and the advance corrections, never the exam card given after the corrections commit), refuses
   his new words on the item (never cited for him), a commit that carries out no card of his (a CONDUCTOR citation is
   not his word), an uncommitted edit and an unlocked version, each as a refusal record with stage.json
   byte-identical; and the sources it finds pass repin itself;
9. RIMMANDRAKE_REPAIR_FLOWWORKS_REPIN_REFUSAL_AND_ESCAPE_WARNING: a commit of scene test text only (no bar) is cited
   TEXT@<sha> with no card and passes repin; a moved requirement, a dropped scene or a tree.json change still refuses."""
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import concept_tree as CT  # noqa: E402
import designer_stage as DS  # noqa: E402

REPO = DS.REPO
SRC = "design/concepts/Pyrelands"
STATE_AT = "249d86c35e"   # stage.json and VERSION.json as the 2026-11-14 refusal found them (the live ones move on)
FILES = ("record.json", "tree.json", "sheet.md", "scenes.json", "floor.json", "exam.json")
ITEM = "BAROQUE_SCRIPT_MEASURE_PREP_AND_CONTROLS"
ADVANCE = "RIMMANDRAKE_ADVANCE_PYRELANDS_OFFLINE_BESIDE_THE_PILOT"
PAVING = "1794695014598425560"        # his card "Drop the sentence", 2026-11-14 ~2:20 PM PST
PAVING_CLOSE = "1794696026595731326"  # the close that carries f71693d77a: --per-ruling, not his word
ADVANCE_CARD = "1794684238949922350"  # "All four now, offline only"
EXAM_CARD = "1794721014843506307"     # "They still owe it", on the ADVANCE item
HOLD_WORD = "1794611171307640419"     # "Yes, we're going to do what you recommend." on the item
EXAM_CARD_ITEM = "1794721773574845016"  # the exam card recorded on the item
FAILS = []


def check(name, ok, got=""):
    print("%s %s%s" % ("ok  " if ok else "FAIL", name, "" if ok else "  got: %r" % (got,)))
    if not ok:
        FAILS.append(name)


def git(root, *a, env=None):
    r = subprocess.run(["git", "-C", root] + list(a), capture_output=True, text=True, timeout=60,
                       env=dict(os.environ, **env) if env else None)
    if r.returncode:
        raise RuntimeError("git %s: %s" % (" ".join(a), r.stderr.strip()))
    return r.stdout.strip()


def real(commit, path):
    return subprocess.run(["git", "-C", REPO, "show", "%s:%s" % (commit, path)], capture_output=True,
                          timeout=60, check=True).stdout


FROZEN_TSN = 1794748469904049550


def owner_lines():
    keep = {PAVING, PAVING_CLOSE, ADVANCE_CARD, EXAM_CARD}
    out = []
    with open(os.path.join(REPO, CT.OWNER_SHARD), encoding="utf-8") as f:
        for ln in f:
            try:
                ev = json.loads(ln)
            except ValueError:
                continue
            # the shard as it stood when the fixture was cut: a later owner event on ITEM (OWNER:1794748469904049550,
            # 2026-11-15) is not part of the replayed history and turned this selftest red on base
            if (ev.get("id") == ITEM and int(ev.get("tsn") or 0) < FROZEN_TSN) or str(ev.get("tsn")) in keep:
                out.append(ln if ln.endswith("\n") else ln + "\n")
    return out


def fixture(dated=False):
    base = os.path.expanduser("~/rm/scratch")
    os.makedirs(base, exist_ok=True)
    root = tempfile.mkdtemp(prefix="selftest-repin-", dir=base)
    d = os.path.join(root, SRC)
    os.makedirs(os.path.join(d, "version"))
    ev = os.path.join(root, os.path.dirname(CT.OWNER_SHARD))
    os.makedirs(ev)
    git(root, "init", "-q", "-b", "main")
    git(root, "config", "user.email", "selftest@example.invalid")
    git(root, "config", "user.name", "selftest")
    with open(os.path.join(d, "stage.json"), "wb") as f:
        f.write(real(STATE_AT, SRC + "/stage.json"))
    with open(os.path.join(d, "version", "VERSION.json"), "wb") as f:
        f.write(real(STATE_AT, SRC + "/version/VERSION.json"))
    with open(os.path.join(root, CT.OWNER_SHARD), "w", encoding="utf-8") as f:
        f.writelines(owner_lines())
    shas = {}
    for name, commit in (("accepted", "a0d5452ac6"), ("corrections", "08d917c12a"), ("paving", "f71693d77a")):
        for fn in FILES:
            with open(os.path.join(d, fn), "wb") as f:
                f.write(real(commit, "%s/%s" % (SRC, fn)))
        git(root, "add", "-A")
        # dated: each commit made when the real one was (a card given after a commit is not what it carried out)
        when = subprocess.run(["git", "-C", REPO, "log", "-1", "--format=%cI", commit], capture_output=True, text=True,
                              timeout=60, check=True).stdout.strip()
        git(root, "commit", "-q", "-m", "fixture: Pyrelands at %s (%s)" % (commit, name),
            env={"GIT_COMMITTER_DATE": when, "GIT_AUTHOR_DATE": when} if dated else None)
        shas[name] = git(root, "rev-parse", "HEAD")
    with open(os.path.join(root, "infrastructure", "state", "ledger", "events", "BENCH.jsonl"), "w") as f:
        f.write(json.dumps({"seat": "CONDUCTOR", "event": "note", "id": ADVANCE, "tsn": 1,
                            "text": "Stage 1 table + 6 corrections %s" % shas["corrections"][:10]}) + "\n")
    with open(os.path.join(root, CT.OWNER_SHARD), "a", encoding="utf-8") as f:
        f.write(json.dumps({"seat": "OWNER", "event": "close", "id": "RIMMANDRAKE_ASK_PYRE_ROOT_STILL_PROMISES_PAVING_HOLDS",
                            "sha": shas["paving"], "perRuling": "CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM",
                            "tsn": 2}) + "\n")
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "fixture: ledger")
    return root, d, shas


def good(shas):
    return ["OWNER:%s@%s" % (PAVING, shas["paving"]), "OWNER:%s@%s" % (ADVANCE_CARD, shas["corrections"]),
            "OWNER:" + HOLD_WORD, "OWNER:" + EXAM_CARD_ITEM]


def stage_bytes(d):
    with open(DS.state_path(d), "rb") as f:
        return f.read()


def refuses(name, d, root, sources, want):
    before = stage_bytes(d)
    try:
        DS.repin(d, sources, "selftest", repo=root)
        got = None
    except DS.Refused as e:
        got = str(e)
    check("refuses %s (%s)" % (name, want), got is not None and want in got, got)
    check("refused %s leaves stage.json byte-identical" % name, stage_bytes(d) == before)


def auto_refuses(name, d, root, want):
    before = stage_bytes(d)
    srcs, rf = DS.repin_sources(d, repo=root)
    rf = rf or {}
    text = json.dumps(rf)
    check("6 auto refuses %s (%s)" % (name, want), want in text and rf.get("clause") == DS.REPIN_CLAUSE
          and all(rf.get(k) for k in ("evidence", "observed", "would_pass")) and isinstance(rf.get("smallest_fix"), dict)
          and all(k in rf["smallest_fix"] for k in ("what", "attainable", "cost")), text[:300])
    check("6 auto refused %s leaves stage.json byte-identical" % name, stage_bytes(d) == before)
    return srcs, rf


def auto_sources_checks():
    root, d, shas = fixture(dated=True)
    try:
        want = sorted(["OWNER:%s@%s" % (PAVING, shas["paving"]), "OWNER:%s@%s" % (ADVANCE_CARD, shas["corrections"])])
        srcs, rf = auto_refuses("his new words on the item", d, root, "OWNER:" + EXAM_CARD_ITEM)
        check("6 auto finds the cards a hand re-pin cites, never the exam card given after the commit",
              sorted(srcs) == want and not any(EXAM_CARD in x for x in srcs), srcs)
        # his words taken in (frozen into the accepted stages, as the Designer citing them would): the sources pass
        st = DS.load_state(d)
        cur = DS.inputs(d, st, root)
        frozen = DS.owner_uncited(root, st.get("item"), d)
        for r in DS.accepted(st):
            if "owner" in DS.DEPS[r["stage"]]:
                r["inputs"]["owner"], r["owner_uncited"] = cur.get("owner"), frozen
        DS.write_json(DS.state_path(d), st)
        srcs, rf = DS.repin_sources(d, repo=root)
        check("6 auto with his words taken in: no refusal, the same two sources", rf is None and sorted(srcs) == want,
              (srcs, rf))
        out = DS.repin(d, srcs, "selftest: the auto sources", repo=root)
        check("6 the auto sources pass repin and leave nothing stale",
              DS.stale_stage(d, DS.load_state(d), root) == (None, []), (out, DS.stale_stage(d, DS.load_state(d), root)))
        # a fix commit citing only a Conductor call: refused, never cited
        with open(os.path.join(d, "sheet.md"), "ab") as f:
            f.write(b"\n- a text leftover fixed\n")
        git(root, "add", "-A")
        git(root, "commit", "-q", "-m", "fix: a text leftover (option A, CONDUCTOR:1794721030959200569)")
        fix = git(root, "rev-parse", "HEAD")
        srcs, rf = auto_refuses("a fix that cites a Conductor call only", d, root, fix)
        check("6 the refusal names the CONDUCTOR citation as not his word", "CONDUCTOR:1794721030959200569" in
              json.dumps(rf.get("evidence")) and not srcs, (srcs, rf.get("evidence")))
        # the smallest fix it names: a ledger event on his card's item naming the sha; then the card is found
        with open(os.path.join(root, "infrastructure", "state", "ledger", "events", "BENCH.jsonl"), "a") as f:
            f.write(json.dumps({"seat": "BENCH", "event": "note", "id": "RIMMANDRAKE_ASK_PYRE_ROOT_STILL_PROMISES_PAVING_"
                                "HOLDS", "tsn": 3, "text": "carried out by %s" % fix[:10]}) + "\n")
        srcs, rf = DS.repin_sources(d, repo=root)
        check("6 after the note on his card's item the fix is cited by that card", rf is None and srcs == [
            "OWNER:%s@%s" % (PAVING, fix)], (srcs, rf))
        keep = open(os.path.join(d, "sheet.md"), "rb").read()
        with open(os.path.join(d, "sheet.md"), "ab") as f:
            f.write(b"\n- an uncommitted line\n")
        auto_refuses("an uncommitted edit", d, root, "uncommitted")
        with open(os.path.join(d, "sheet.md"), "wb") as f:
            f.write(keep)
        vp = os.path.join(d, "version", "VERSION.json")
        v = json.loads(open(vp).read())
        v["state"] = "draft"
        with open(vp, "w") as f:
            json.dump(v, f)
        auto_refuses("an unlocked version", d, root, "not locked")
    finally:
        shutil.rmtree(root, ignore_errors=True)


LATE_ITEM = "RIMMANDRAKE_REPIN_A_LANDED_FIX_HE_APPROVED_AFTER"   # a card item filed by his card, after the fix landed


def late_approval_checks():
    """8 RIMMANDRAKE_CITE_LATE_APPROVAL_CARD_NOTE_FIX_NEVER_PASSED: a fix lands, then his card approves it (Graffiti,
    6c7d175b52 at 10:35 AM, his card 5:24 PM PST 2026-11-17). The refusal's smallest fix is a ledger note on the card's
    item naming the sha; written AFTER the card, that note is the record that this card approves that commit, and the
    auto re-pin cites it as a hand re-pin does. A note written BEFORE the card cannot record it, so it still refuses
    (the exam-card guard of check 6 stays: a later card never borrows an earlier note)."""
    import time
    root, d, shas = fixture(dated=True)
    try:
        st = DS.load_state(d)
        cur = DS.inputs(d, st, root)
        frozen = DS.owner_uncited(root, st.get("item"), d)
        for r in DS.accepted(st):
            if "owner" in DS.DEPS[r["stage"]]:
                r["inputs"]["owner"], r["owner_uncited"] = cur.get("owner"), frozen
        DS.write_json(DS.state_path(d), st)
        srcs, rf = DS.repin_sources(d, repo=root)
        DS.repin(d, srcs, "selftest: level before the late card", repo=root)
        with open(os.path.join(d, "sheet.md"), "ab") as f:
            f.write(b"\n- a fix he approved after it landed\n")
        git(root, "add", "-A")
        git(root, "commit", "-q", "-m", "fix: a scene test he had not yet seen")
        fix = git(root, "rev-parse", "HEAD")
        card = time.time_ns() + 60 * 10 ** 9           # his card, a minute after the fix commit
        with open(os.path.join(root, CT.OWNER_SHARD), "a", encoding="utf-8") as f:
            f.write(json.dumps({"seat": "OWNER", "event": "file", "id": LATE_ITEM, "tsn": str(card),
                                "byCard": "Graffiti -> Approve fix, look after resets (Recommended)"}) + "\n")
        bench = os.path.join(root, "infrastructure", "state", "ledger", "events", "BENCH.jsonl")
        with open(bench, "a") as f:
            f.write(json.dumps({"seat": "BENCH", "event": "note", "id": LATE_ITEM, "tsn": str(card - 1),
                                "text": "early words naming %s" % fix[:12]}) + "\n")
        srcs, rf = auto_refuses("8 a note on the card's item written before the card", d, root, fix)
        check("8 a note older than the card cites nothing", not srcs, srcs)
        with open(bench, "a") as f:
            f.write(json.dumps({"seat": "BENCH", "event": "note", "id": LATE_ITEM, "tsn": str(card + 1),
                                "text": "carried out by %s" % fix[:12]}) + "\n")
        srcs, rf = DS.repin_sources(d, repo=root)
        check("8 after the note on his late card's item, the auto re-pin cites that card", rf is None and srcs == [
            "OWNER:%s@%s" % (card, fix)], (srcs, rf))
        out = DS.repin(d, srcs, "selftest: the late card", repo=root, dry=True) if srcs else None
        check("8 the late card's source passes repin itself", bool(out), out)
    finally:
        shutil.rmtree(root, ignore_errors=True)


def scene_edit(d, root, edit, msg):
    """Edit the fixture's scenes.json with `edit(scenes)` and commit it with `msg` (no card cited) -> the full sha."""
    p = os.path.join(d, "scenes.json")
    sc = json.loads(open(p, encoding="utf-8").read())
    edit(sc)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(sc, f, indent=1)
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", msg)
    return git(root, "rev-parse", "HEAD")


def text_only_checks():
    """9 RIMMANDRAKE_REPAIR_FLOWWORKS_REPIN_REFUSAL_AND_ESCAPE_WARNING: a commit that changes only the test text of
    scenes.json (a scene's start, action, expect, control or restore; FlowWorks 51e271d211, the moat scene's geometry)
    changes no bar, so it needs no card of his: the auto re-pin cites it as TEXT@<sha>, a note and no refusal, and repin
    itself takes that source. A commit that also moves a bar's link (a scene's requirement), drops a scene, or touches
    tree.json still refuses for lack of his card, and a hand TEXT@ source on such a commit is refused."""
    root, d, shas = fixture(dated=True)
    try:
        st = DS.load_state(d)
        cur, frozen = DS.inputs(d, st, root), DS.owner_uncited(root, st.get("item"), d)
        for r in DS.accepted(st):
            if "owner" in DS.DEPS[r["stage"]]:
                r["inputs"]["owner"], r["owner_uncited"] = cur.get("owner"), frozen
        DS.write_json(DS.state_path(d), st)
        srcs, rf = DS.repin_sources(d, repo=root)
        DS.repin(d, srcs, "selftest: level before the test-text commit", repo=root)

        def text(sc):
            sc["scenes"][0]["action"] += "; game time runs on"
            sc["scenes"][0]["start"] = list(sc["scenes"][0]["start"]) + ["the water a metre below the rim"]
        fix = scene_edit(d, root, text, "moat scene: wider, game time (no bar changed; scenes.json test text)")
        srcs, rf = DS.repin_sources(d, repo=root)
        check("9 a test-text-only commit with no card: no refusal, cited as TEXT@<sha>",
              rf is None and srcs == ["TEXT@%s" % fix], (srcs, rf))
        out = DS.repin(d, srcs, "selftest: test text only", repo=root, dry=True) if srcs else None
        check("9 the TEXT source passes repin itself", bool(out), out)
        if srcs:
            DS.repin(d, srcs, "selftest: test text only", repo=root)
        check("9 after the TEXT re-pin nothing is stale", DS.stale_stage(d, DS.load_state(d), root) == (None, []),
              DS.stale_stage(d, DS.load_state(d), root))
        row = (DS.load_state(d).get("history") or [{}])[-1]
        check("9 the history row names the TEXT source", "TEXT@%s" % fix in row.get("why", ""), row)

        def link(sc):
            sc["scenes"][0]["requirement"] = list(sc["scenes"][0]["requirement"]) + ["a_bar_it_never_proved"]
        bad = scene_edit(d, root, link, "scene: proves one more bar (no card)")
        srcs, rf = auto_refuses("9 a scene's requirement moved with no card", d, root, bad)
        check("9 a moved requirement is never cited as TEXT", not any(x.startswith("TEXT@") for x in srcs), srcs)
        refuses("9 a hand TEXT source on a requirement change", d, root, ["TEXT@" + bad], "test text")
        git(root, "revert", "--no-edit", "HEAD")

        def drop(sc):
            sc["scenes"].pop()
        gone = scene_edit(d, root, drop, "scene dropped (no card)")
        auto_refuses("9 a scene dropped with no card", d, root, gone)
        git(root, "revert", "--no-edit", "HEAD")
        with open(os.path.join(d, "tree.json"), "ab") as f:
            f.write(b"\n")
        with open(os.path.join(d, "scenes.json"), "ab") as f:
            f.write(b"\n ")
        git(root, "add", "-A")
        git(root, "commit", "-q", "-m", "tree and scene text together (no card)")
        both = git(root, "rev-parse", "HEAD")
        refuses("9 a hand TEXT source on a commit that also touched tree.json", d, root, ["TEXT@" + both], "test text")
    finally:
        shutil.rmtree(root, ignore_errors=True)


PAVING_ITEM = "RIMMANDRAKE_ASK_PYRE_ROOT_STILL_PROMISES_PAVING_HOLDS"   # the item of his paving card


def anchored(d, root, r, k):
    """input_changes anchored to the commit that RECORDED the pin (the argument this ticket adds). On base, where
    input_changes takes no anchor, this reports the TypeError as the reading so the case fails instead of crashing."""
    try:
        return DS.input_changes(d, k, root, r["inputs"].get(k), (r.get("pinned_at") or {}).get(k))
    except TypeError as e:
        return None, "input_changes takes no anchor: %s" % e


def first_pin_checks():
    """7 RIMMANDRAKE_TRACE_REPIN_FROM_FIRST_PIN_B_CHANGE_SKIPPED: a frozen input that goes A->B->A->C after the pin
    owes a source for the B change too. input_changes used to anchor to the LAST commit whose hash equalled the pin,
    which for A->B->A->C is the A that reverted B, so it reported only C and a re-pin citing C alone passed with the
    B change unaccounted for. The anchor is the commit that recorded the pin (written at pin time), never a commit
    date (review 2 of the parent found a date-trusting fix wrong), and a recorded anchor that cannot be resolved is
    UNMEASURED, never 'no changes since the pin'."""
    root, d, shas = fixture(dated=True)
    try:
        # the pin, recorded: his words taken in (as the Designer citing them would), then the hand re-pin of case 2,
        # which pins stage 3's sheet at HEAD and records the commit it was pinned at
        st = DS.load_state(d)
        cur, frozen = DS.inputs(d, st, root), DS.owner_uncited(root, st.get("item"), d)
        for r in DS.accepted(st):
            if "owner" in DS.DEPS[r["stage"]]:
                r["inputs"]["owner"], r["owner_uncited"] = cur.get("owner"), frozen
        DS.write_json(DS.state_path(d), st)
        srcs, rf = DS.repin_sources(d, repo=root)
        DS.repin(d, srcs, "selftest: the pin this case anchors to", repo=root)
        pin_at = git(root, "rev-parse", "HEAD")
        check("7 the fixture's pin leaves nothing stale and no refusal", rf is None
              and DS.stale_stage(d, DS.load_state(d), root) == (None, []), (rf, DS.stale_stage(d, DS.load_state(d), root)))
        r3 = {r["stage"]: r for r in DS.accepted(DS.load_state(d))}[3]
        pin = r3["inputs"].get("sheet")
        check("7 a re-pin records the commit it pinned at (stage 3, sheet)",
              (r3.get("pinned_at") or {}).get("sheet") == pin_at, (r3.get("pinned_at"), pin_at))

        # A -> B -> A -> C, all after the pin: the B change, the revert of it, and a later change his card carries out
        sheet = os.path.join(d, "sheet.md")
        a_bytes = open(sheet, "rb").read()
        with open(sheet, "ab") as f:
            f.write(b"\n- the B change: a sentence nobody asked for\n")
        git(root, "add", "-A")
        git(root, "commit", "-q", "-m", "fixture: the B change (cites no card of his)")
        b_sha = git(root, "rev-parse", "HEAD")
        with open(sheet, "wb") as f:
            f.write(a_bytes)
        git(root, "add", "-A")
        git(root, "commit", "-q", "-m", "fixture: the B change reverted, back to the pinned bytes")
        a2_sha = git(root, "rev-parse", "HEAD")
        with open(sheet, "ab") as f:
            f.write(b"\n- the C change, which his paving card asks for\n")
        git(root, "add", "-A")
        git(root, "commit", "-q", "-m", "fixture: the C change")
        c_sha = git(root, "rev-parse", "HEAD")
        with open(os.path.join(root, "infrastructure", "state", "ledger", "events", "BENCH.jsonl"), "a") as f:
            f.write(json.dumps({"seat": "BENCH", "event": "note", "id": PAVING_ITEM, "tsn": 7,
                                "text": "carried out by %s" % c_sha[:10]}) + "\n")
        git(root, "add", "-A")
        git(root, "commit", "-q", "-m", "fixture: the ledger note that ties the C change to his paving card")
        st = DS.load_state(d)
        r3 = {r["stage"]: r for r in DS.accepted(st)}[3]
        at_a2 = git(root, "show", "%s:%s/sheet.md" % (a2_sha, SRC))
        at_b = git(root, "show", "%s:%s/sheet.md" % (b_sha, SRC))
        check("7 the fixture is A->B->A->C: the revert returns the sheet to the pinned bytes, B and C differ from it",
              at_a2 == a_bytes.decode().strip() and at_b != at_a2 and DS.inputs(d, st, root).get("sheet") != pin,
              (len(at_a2), len(at_b), DS.inputs(d, st, root).get("sheet") == pin))

        got, why = anchored(d, root, r3, "sheet")
        check("7 input_changes anchored at the recording commit lists the B change, its revert and C",
              got is not None and [c for c in (got or [])] == [b_sha, a2_sha, c_sha], (got, why))

        # the hole this ticket closes: a re-pin citing only the C change, with B unaccounted for
        refuses("the B change of A->B->A->C, with only C cited", d, root,
                ["OWNER:%s@%s" % (PAVING, c_sha)], b_sha[:10])
        srcs, rf = DS.repin_sources(d, repo=root)
        check("7 the automatic re-pin refuses: the B change carries out no card of his",
              rf is not None and b_sha in json.dumps(rf.get("evidence")), (srcs, (rf or {}).get("evidence")))

        # a recorded anchor that cannot be resolved is UNMEASURED, never "no changes since the pin"
        st = DS.load_state(d)
        for r in st["results"]:
            if r.get("stage") == 3 and isinstance(r.get("pinned_at"), dict):
                r["pinned_at"]["sheet"] = "0" * 40
        DS.write_json(DS.state_path(d), st)
        r3 = {r["stage"]: r for r in DS.accepted(DS.load_state(d))}[3]
        got, why = anchored(d, root, r3, "sheet")
        check("7 an unresolvable recorded anchor is UNMEASURED, not an empty set of changes",
              got is None and "UNMEASURED" in (why or ""), (got, why))
        refuses("an unresolvable recorded anchor", d, root, ["OWNER:%s@%s" % (PAVING, c_sha)], "UNMEASURED")

        # a pin made before the field existed keeps today's behaviour until its next pin
        st = DS.load_state(d)
        for r in st["results"]:
            r.pop("pinned_at", None)
        DS.write_json(DS.state_path(d), st)
        r3 = {r["stage"]: r for r in DS.accepted(DS.load_state(d))}[3]
        got, why = anchored(d, root, r3, "sheet")
        check("7 a pin with no recorded anchor keeps today's behaviour (the last occurrence)",
              got == [c_sha], (got, why))

        # an accepted stage is a pin too: close_run records the anchor, so the first re-pin after an accept is
        # anchored even though no repin has run yet
        st = DS.load_state(d)
        st["stage"], st["status"] = 2, "ready"
        st["results"] = [r for r in st["results"] if r.get("stage", 0) < 2]
        DS.write_json(DS.state_path(d), st)
        real_errors = DS.result_errors
        DS.result_errors = lambda res, d_, st_, repo_=None: []   # the pin's anchor is under test, not validation
        try:
            DS.open_run(d, "pin-run", repo=root)
            DS.write_json(os.path.join(d, "result.json"),
                          {"run": "pin-run", "stage": 2, "outcome": "done", "summary": "selftest"})
            ok, errs = DS.close_run(d, "pin-run", 1000, repo=root)
        finally:
            DS.result_errors = real_errors
        head = git(root, "rev-parse", "HEAD")
        acc2 = [r for r in (DS.load_state(d).get("results") or []) if r.get("stage") == 2
                and r.get("outcome") == "done"][-1]
        check("7 an accepted stage records the commit its inputs were pinned at (close_run)",
              ok and (acc2.get("pinned_at") or {}).get("root") == head
              and sorted(acc2.get("pinned_at") or {}) == sorted(DS.INPUT_FILES), (ok, errs, acc2.get("pinned_at")))
        check("7 the recorded anchor covers only file inputs, never the owner feed",
              "owner" not in (acc2.get("pinned_at") or {}), acc2.get("pinned_at"))

        # 8 (edge 3) a close whose HEAD cannot be read records the pin as UNREAD, never as a pin with no anchor
        # (which input_changes reads as a legacy pin: the last occurrence, the very rule the anchor replaced)
        st = DS.load_state(d)
        st["stage"], st["status"] = 2, "ready"
        st["results"] = [r for r in st["results"] if r.get("stage", 0) < 2]
        DS.write_json(DS.state_path(d), st)
        real_errors, real_git = DS.result_errors, DS._git
        DS.result_errors = lambda res, d_, st_, repo_=None: []
        DS._git = lambda repo, *a: None if a[:1] == ("rev-parse",) and "HEAD^{commit}" in a else real_git(repo, *a)
        try:
            DS.open_run(d, "pin-run-blind", repo=root)
            DS.write_json(os.path.join(d, "result.json"),
                          {"run": "pin-run-blind", "stage": 2, "outcome": "done", "summary": "selftest"})
            ok, errs = DS.close_run(d, "pin-run-blind", 1000, repo=root)
        finally:
            DS.result_errors, DS._git = real_errors, real_git
        acc2 = [r for r in (DS.load_state(d).get("results") or []) if r.get("stage") == 2
                and r.get("outcome") == "done"][-1]
        got, why = anchored(d, root, acc2, "root")
        check("8 a close that could not read HEAD records an anchor that reads UNMEASURED, not a legacy pin",
              ok and sorted(acc2.get("pinned_at") or {}) == sorted(DS.INPUT_FILES) and got is None
              and "UNMEASURED" in (why or ""), (ok, errs, acc2.get("pinned_at"), got, why))
    finally:
        shutil.rmtree(root, ignore_errors=True)


def tiny(commits):
    """A scratch repo holding one concept folder whose sheet.md goes through `commits` (bytes, or None = the file is
    absent in that commit), one commit each. -> (root, concept dir, [sha per commit])."""
    base = os.path.expanduser("~/rm/scratch")
    os.makedirs(base, exist_ok=True)
    root = tempfile.mkdtemp(prefix="selftest-repin-edge-", dir=base)
    d = os.path.join(root, "design", "concepts", "Edge")
    os.makedirs(d)
    git(root, "init", "-q", "-b", "main")
    git(root, "config", "user.email", "selftest@example.invalid")
    git(root, "config", "user.name", "selftest")
    shas = []
    for n, body in enumerate(commits):
        p = os.path.join(d, "sheet.md")
        if body is None:
            if os.path.exists(p):
                os.remove(p)
        else:
            with open(p, "wb") as f:
                f.write(body)
        with open(os.path.join(d, "other.txt"), "w") as f:
            f.write("%d\n" % n)
        git(root, "add", "-A")
        git(root, "commit", "-q", "-m", "edge fixture %d" % n)
        shas.append(git(root, "rev-parse", "HEAD"))
    return root, d, shas


def sheet_hash(body):
    import hashlib
    return hashlib.sha256(body.replace(b"\r\n", b"\n")).hexdigest()


def anchor_edge_checks():
    """8 RIMMANDRAKE_HARDEN_PIN_ANCHOR_THREE_EDGES_CODEX_FOUND: each edge of the recorded anchor reads UNMEASURED
    (None, why), never a shorter list of changes."""
    O, A, B, C = b"old\n", b"the pinned bytes\n", b"the B change\n", b"the C change\n"

    def changes(d, root, pinned, anchor):
        try:
            return DS.input_changes(d, "sheet", root, sheet_hash(pinned), anchor)
        except Exception as e:      # a crash is not a reading
            return "CRASH", "%s: %s" % (type(e).__name__, e)
    # edge 1: the anchor (HEAD at close) holds the old bytes; B lands before the pinned bytes do
    root, d, sh = tiny([O, B, A, C])
    try:
        got, why = changes(d, root, A, sh[0])
        check("8 edge 1: B landed between the recording commit and the pinned bytes: UNMEASURED, B does not escape",
              got is None and "UNMEASURED" in (why or ""), (got, why))
    finally:
        shutil.rmtree(root, ignore_errors=True)
    root, d, sh = tiny([O, A, C])
    try:
        got, why = changes(d, root, A, sh[0])
        check("8 edge 1 control: the pinned bytes land right after the recording commit (close, then land): traced",
              got == [sh[2]], (got, why))
        got, why = changes(d, root, A, sh[1])
        check("8 edge 1 control: an anchor that carries the pinned bytes itself is traced", got == [sh[2]], (got, why))
        got, why = changes(d, root, C, sh[2])
        check("8 edge 1 control: nothing changed since the pin is an empty list, a reading", got == [], (got, why))
    finally:
        shutil.rmtree(root, ignore_errors=True)
    # edge 2: a shallow clone in which the anchor resolves but the history between it and HEAD is cut
    root, d, sh = tiny([A, B, A + b"\n", C])
    shallow = tempfile.mkdtemp(prefix="selftest-repin-shallow-", dir=os.path.expanduser("~/rm/scratch"))
    try:
        git(root, "config", "uploadpack.allowAnySHA1InWant", "true")
        subprocess.run(["git", "clone", "-q", "--depth=1", "file://" + root, shallow], capture_output=True, check=True,
                       timeout=120)
        git(shallow, "fetch", "-q", "--depth=1", "origin", sh[0])
        d2 = os.path.join(shallow, "design", "concepts", "Edge")
        resolves = git(shallow, "rev-parse", "--verify", sh[0] + "^{commit}") == sh[0]
        got, why = changes(d2, shallow, A, sh[0])
        check("8 edge 2: a shallow clone whose history from the anchor is cut: UNMEASURED, never a partial list",
              resolves and got is None and "UNMEASURED" in (why or ""), (resolves, got, why))
        got, why = changes(d, root, A, sh[0])
        check("8 edge 2 control: the same history, whole, lists every change", got == sh[1:], (got, why))
    finally:
        shutil.rmtree(root, ignore_errors=True)
        shutil.rmtree(shallow, ignore_errors=True)
    # edge 4: a blob that cannot be read is not the file's absence
    root, d, sh = tiny([A, B, C, O])
    real_git = DS._git
    try:
        DS._git = lambda repo, *a: None if a[:1] == ("show",) and a[1].split(":")[0] in (sh[1], sh[2]) \
            else real_git(repo, *a)
        got, why = changes(d, root, A, sh[0])
        check("8 edge 4: a commit whose blob cannot be read is UNMEASURED, not 'the file was absent'",
              got is None and "UNMEASURED" in (why or ""), (got, why))
    finally:
        DS._git = real_git
        shutil.rmtree(root, ignore_errors=True)
    root, d, sh = tiny([A, None, C])
    try:
        got, why = changes(d, root, A, sh[0])
        check("8 edge 4 control: a commit that really deletes the file is a change, read as one",
              got == [sh[1], sh[2]], (got, why))
    finally:
        shutil.rmtree(root, ignore_errors=True)


def main():
    anchor_edge_checks()
    root, d, shas = fixture()
    try:
        st = DS.load_state(d)
        s = DS.stale_stage(d, st, root)
        check("1 before the verb: stale_stage is (1, ['root'])", s == (1, ["root"]), s)

        refuses("a CONDUCTOR source", d, root, ["CONDUCTOR:1794721030959200569@" + shas["paving"]] + good(shas)[1:],
                "OWNER")
        refuses("no source", d, root, [], "no source")
        refuses("the exam card for the paving commit", d, root,
                ["OWNER:%s@%s" % (EXAM_CARD, shas["paving"])] + good(shas)[1:], "not tied")
        refuses("the corrections left uncited", d, root, [good(shas)[0]] + good(shas)[2:], shas["corrections"][:10])
        refuses("commits paired with the wrong cards", d, root,
                ["OWNER:%s@%s" % (PAVING, shas["corrections"]), "OWNER:%s@%s" % (ADVANCE_CARD, shas["paving"])]
                + good(shas)[2:], "not tied")
        refuses("a --per-ruling close as the source", d, root,
                ["OWNER:%s@%s" % (PAVING_CLOSE, shas["paving"])] + good(shas)[1:], "his word")
        refuses("his process word left uncited", d, root, good(shas)[:3], EXAM_CARD_ITEM)
        sheet = os.path.join(d, "sheet.md")
        keep = open(sheet, "rb").read()
        with open(sheet, "ab") as f:
            f.write(b"\n- an uncommitted line\n")
        refuses("an uncommitted edit", d, root, good(shas), "uncommitted")
        with open(sheet, "wb") as f:
            f.write(keep)
        vp = os.path.join(d, "version", "VERSION.json")
        vkeep = open(vp, "rb").read()
        v = json.loads(vkeep)
        v["state"] = "draft"
        with open(vp, "w") as f:
            json.dump(v, f)
        refuses("an unlocked version", d, root, good(shas), "not locked")
        with open(vp, "wb") as f:
            f.write(vkeep)

        out = DS.repin(d, good(shas), "selftest: his paving card and the advance corrections", repo=root)
        st = DS.load_state(d)
        s = DS.stale_stage(d, st, root)
        check("2 after repin: nothing stale", s == (None, []), s)
        check("2 after repin: stage 4 is the open stage", st.get("stage") == 4, st.get("stage"))
        row = (st.get("history") or [{}])[-1]
        check("2 a locked_change history row cites every source", row.get("what") == "locked_change"
              and all(("OWNER:" + t) in row.get("why", "") for t in (PAVING, ADVANCE_CARD, HOLD_WORD)), row)
        check("2 repin reports the re-pinned stages", sorted(out) == [1, 2, 3], out)
        refuses("a second repin with nothing stale", d, root, good(shas), "nothing to re-pin")

        # the CLI, on a fresh fixture
        shutil.rmtree(root)
        root, d, shas = fixture()
        argv = ["repin", d, "--why", "selftest cli"]
        for sv in good(shas):
            argv += ["--source", sv]
        old = DS.REPO
        DS.REPO = root
        try:
            rc = DS.main(argv)
            rc_bad = DS.main(["repin", d, "--why", "selftest cli"])
        finally:
            DS.REPO = old
        st = DS.load_state(d)
        check("2 cli repin exits 0 and leaves nothing stale", rc == 0 and DS.stale_stage(d, st, root) == (None, []),
              (rc, DS.stale_stage(d, st, root)))
        check("3 cli repin with no source exits 1", rc_bad == 1, rc_bad)

        # 5: RIMMANDRAKE_REPIN_STAGE_FOUR_LEAVES_EXAM_VOID: an accepted exam over a changed tree is not re-pinned
        root5, d5, shas5 = fixture()
        try:
            st5 = DS.load_state(d5)
            res = {r["stage"]: r for r in st5.get("results") or [] if r.get("outcome") == "done"}
            with open(os.path.join(d5, "exam.json"), "w") as f:      # the exam, frozen against stage 3's tree and sheet
                json.dump({"inputs": {k: res[3]["inputs"].get(k) for k in ("tree", "sheet")}}, f)
            git(root5, "add", "-A")
            git(root5, "commit", "-q", "-m", "fixture: an exam taken before the change")
            cur5 = DS.inputs(d5, st5, root5)
            r4 = {"stage": 4, "outcome": "done", "inputs": dict(
                {k: res[3]["inputs"].get(k) for k in ("sheet", "tree", "scenes", "floor")},
                exam=cur5.get("exam"), owner=res[2]["inputs"].get("owner")),
                "owner_uncited": res[2].get("owner_uncited")}
            st5["results"].append(r4)
            st5["stage"] = 5
            st5["status"] = "locked"     # as Pyrelands and Graffiti stood 2026-11-17: stage 5 signed, then his card
            DS.write_json(DS.state_path(d5), st5)
            changed4 = sorted(k for k in ("tree", "sheet") if r4["inputs"].get(k) != cur5.get(k))
            out5 = DS.repin(d5, good(shas5), "selftest: a tree change under an accepted exam", repo=root5)
            st5 = DS.load_state(d5)
            s5 = DS.stale_stage(d5, st5, root5)
            ee = DS.exam_errors(DS.read_json(os.path.join(d5, "exam.json")), d5, st5, root5)
            check("5 the fixture's change moves the exam's tree or sheet", bool(changed4), changed4)
            check("5 repin leaves stage 4 out when its exam's tree or sheet changed", 4 not in out5, out5)
            check("5 stale_stage reports stage 4, agreeing with exam_errors", s5[0] == 4
                  and any("another" in e for e in ee), (s5, ee[:2]))
            row5 = (st5.get("history") or [{}])[-1]
            check("5 the history says stage 4 was left stale", "stage 4 left stale" in row5.get("why", ""), row5)
            # RIMMANDRAKE_UNLOCK_REPIN_VOIDED_EXAM_NEXT_OPEN_REFUSED: a locked concept whose exam the repin voids must
            # be openable for the retake, and the maturation chain must be owed; a lock would refuse both forever
            check("5 a voided exam unlocks the concept for its retake", st5.get("status") != "locked", st5.get("status"))
            try:
                DS.open_run(d5, "selftest-preview", repo=root5, commit=False)
                why5 = None
            except DS.Refused as e:
                why5 = str(e)
            check("5 the next open is not refused as LOCKED", not (why5 or "").startswith("LOCKED"), why5)
            import maturation_autonomy as MA
            check("5 the maturation chain is owed for the locked change", (MA.chain_owed(st5) or {}).get(
                "what") == "locked_change", MA.chain_owed(st5))
        finally:
            shutil.rmtree(root5, ignore_errors=True)

        auto_sources_checks()
        late_approval_checks()
        text_only_checks()
        first_pin_checks()

        # 4: the spend ceiling and his word that predates the park
        st = DS.load_state(d)
        check("4 the replayed loop is past its ceiling", bool(DS.loop_ceiling(st)), DS.loop_ceiling(st))
        check("4 no park written yet", not isinstance(st.get("park"), dict), st.get("park"))
        lifted = DS.lift_park(st, d, root)
        check("4 his word after the crossing lifts the ceiling with no park written", lifted is True
              and DS.loop_ceiling(st) is None and (st.get("parks") or [{}])[-1].get("kind") == "ceiling",
              (lifted, DS.loop_ceiling(st), st.get("parks")))
        st = DS.load_state(d)
        st["item"] = "NO_SUCH_ITEM_HAS_HIS_WORD"
        check("4 no word on the item, no lift", DS.lift_park(st, d, root) is False and bool(DS.loop_ceiling(st)))
    finally:
        shutil.rmtree(root, ignore_errors=True)
    print("%d check(s) failed" % len(FAILS) if FAILS else "all checks passed")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
