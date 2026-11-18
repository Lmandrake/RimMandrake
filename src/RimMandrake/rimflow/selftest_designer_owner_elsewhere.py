#!/usr/bin/env python3
"""selftest_designer_owner_elsewhere.py - his words on a mod's OTHER items reach its concept
(RIMMANDRAKE_HARVEST_OWNER_WORDS_OFF_CONCEPT_ITEM_FOURTH_ASK): the Gimme Some Slack slope rule sat on a build item and a
fix item, and designer_stage.owner_uncited read only the concept's own item, so it never became a bar of 0.1.0.
Covers: which items are the mod's (own, prefix, alias, cause chain, a title that starts with the mod's name; a title
merely naming it is not), his words only (a per-ruling note is not), a citation takes a word out, the feed and the
accepted stages do not move (no relaunch), the lock refuses only words newer than the concept, an unreadable shard is
UNMEASURED and refuses the lock, the packet lists them; and finding 1 of RIMMANDRAKE_FIX_DESIGNER_STAGE_CODEX_REVIEW_
FINDINGS (an event on X_EXTRA is not on X). Runs in a temp dir; touches no real concept or ledger."""
import json
import os
import shutil
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.environ.setdefault("RM_JUDGE_SYNC", "0")
import concept_tree as CT  # noqa: E402
import designer_stage as DS  # noqa: E402

FAILS = []
ITEM = "WIDGETWORKS_CONCEPT_ITEM"
OLD = int(time.mktime((2020, 1, 1, 0, 0, 0, 0, 0, 0))) * 10 ** 9     # long before the concept began


def check(name, ok, got=""):
    print("%s %s%s" % ("ok  " if ok else "FAIL", name, "" if ok else "  got: %s" % (got,)))
    if not ok:
        FAILS.append(name)


class Repo:
    def __init__(self, tmp):
        self.root = tmp
        self.owner = os.path.join(tmp, CT.OWNER_SHARD)
        os.makedirs(os.path.dirname(self.owner))
        open(self.owner, "w").close()
        self.tsn = time.time_ns() + 10 ** 9

    def add(self, ev, tsn=None):
        if tsn is None:
            self.tsn += 1
            tsn = self.tsn
        ev = dict({"seat": "OWNER", "tsn": str(tsn)}, **ev)
        with open(self.owner, "a") as f:
            f.write(json.dumps(ev) + "\n")
        return str(tsn)

    def said(self, item, words, tsn=None):
        return self.add({"id": item, "event": "note", "ownerSaid": words}, tsn)

    def filed(self, item, title, caused_by=None, seat="BENCH"):
        ev = {"seat": seat, "event": "file", "id": item, "title": title, "tsn": str(self.tsn)}
        if caused_by:
            ev["caused_by"] = caused_by
        p = os.path.join(self.root, CT.LEDGER_DIR, "events", "%s.jsonl" % seat)
        with open(p, "a") as f:
            f.write(json.dumps(ev) + "\n")


def put(d, name, obj):
    with open(os.path.join(d, name), "w", encoding="utf-8") as f:
        json.dump(obj, f)


def main():
    tmp = tempfile.mkdtemp(prefix="owner_elsewhere_")
    try:
        repo = Repo(tmp)
        d = os.path.join(tmp, "design/concepts/WidgetWorks")
        DS.init(d, "RimMandrake/WidgetWorks", ITEM, aliases=["WW"])
        st = DS.load_state(d)
        check("no word of his anywhere: {} (looked, found none), not None", DS.owner_elsewhere(tmp, d, st) == {},
              DS.owner_elsewhere(tmp, d, st))
        on_own = repo.said(ITEM, "the widget turns")
        feed0, uncited0 = DS.owner_feed(tmp, ITEM, d), DS.owner_uncited(tmp, ITEM, d)
        check("base: his word on the concept's own item is in owner_uncited", uncited0 == [on_own], uncited0)
        check("his own-item word alone is the whole list", DS.owner_elsewhere(tmp, d, st) == {on_own: ITEM},
              DS.owner_elsewhere(tmp, d, st))

        prefix = repo.said("WIDGETWORKS_BUILD_GEARS", "gears mesh by position AND slope")
        alias = repo.said("WW_FIX_TEETH", "the teeth line up")
        repo.filed("RIMMANDRAKE_FIX_WIDGET_ENDS_OWNER_CAUGHT", "Widget Works, two drawing defects he saw")
        by_title = repo.said("RIMMANDRAKE_FIX_WIDGET_ENDS_OWNER_CAUGHT", "hard wire the slope rule")
        repo.filed("RIMMANDRAKE_HOLD_SIX_MODS", "Hold six mods: Cauldron, WidgetWorks and four more")
        mention = repo.said("RIMMANDRAKE_HOLD_SIX_MODS", "stop the new mods work")
        repo.filed("RIMMANDRAKE_REPAIR_CHILD", "repair the scorer", caused_by=ITEM)
        repo.filed("RIMMANDRAKE_REPAIR_GRANDCHILD", "repair the scorer again", caused_by="RIMMANDRAKE_REPAIR_CHILD")
        by_cause = repo.said("RIMMANDRAKE_REPAIR_GRANDCHILD", "the gear must not slip")
        card = repo.add({"id": "WIDGETWORKS_SITTING", "event": "note", "byCard": "Which gear? -> the brass one"})
        ruling = repo.add({"id": "WIDGETWORKS_BUILD_GEARS", "event": "note", "text": "per ruling",
                           "perRuling": "SOME_RULING", "why": "delegated: x"})
        other = repo.said("SOMETHING_ELSE_ENTIRELY", "unrelated words")
        extra = repo.said(ITEM + "_EXTRA", "words on a longer id")
        old = repo.said("WIDGETWORKS_BUILD_GEARS", "an old word, before the concept", tsn=OLD)

        u = DS.owner_elsewhere(tmp, d, st)
        got = set(u or {})
        check("an item under the mod's prefix is the mod's", prefix in got, u)
        check("an item under an alias prefix is the mod's", alias in got, u)
        check("an item whose filed title starts with the mod's name is the mod's", by_title in got, u)
        check("a title merely naming the mod is not enough", mention not in got, u)
        check("an item whose cause chain reaches the concept's item is the mod's", by_cause in got, u)
        check("a card answer (byCard) is his word", card in got, u)
        check("a per-ruling note is not his word", ruling not in got, u)
        check("an unrelated item is not the mod's", other not in got, u)
        check("his words on the concept's own item are listed too (any item of the mod; Codex review 2)", on_own in got, u)
        check("the list maps each word to its item", (u or {}).get(prefix) == "WIDGETWORKS_BUILD_GEARS", u)

        # finding 1: X is not named by an event on X_EXTRA
        check("finding 1: an event on X_EXTRA is not in X's owner_uncited",
              extra not in (DS.owner_uncited(tmp, ITEM, d) or []), DS.owner_uncited(tmp, ITEM, d))
        named = repo.add({"id": "SOMETHING_ELSE_TWO", "event": "note", "ownerSaid": "about %s, the widget" % ITEM})
        check("finding 1: words naming X exactly still count for X", named in (DS.owner_uncited(tmp, ITEM, d) or []),
              DS.owner_uncited(tmp, ITEM, d))

        # no relaunch: siblings' words are not part of the feed a stage freezes
        repo2 = Repo(tempfile.mkdtemp(prefix="owner_elsewhere_feed_"))
        try:
            d2 = os.path.join(repo2.root, "design/concepts/WidgetWorks")
            DS.init(d2, "RimMandrake/WidgetWorks", ITEM)
            repo2.said(ITEM, "the widget turns")
            st2 = DS.load_state(d2)
            st2["stage"] = 3
            st2["results"] = [{"stage": s, "outcome": "done", "inputs": DS.inputs(d2, st2, repo2.root),
                               "owner_uncited": DS.owner_uncited(repo2.root, ITEM, d2)} for s in (0, 1, 2)]
            DS.write_json(DS.state_path(d2), st2)
            before = DS.owner_feed(repo2.root, ITEM, d2)
            repo2.said("WIDGETWORKS_BUILD_GEARS", "a sibling's new word")
            check("a sibling's word does not move the owner feed", DS.owner_feed(repo2.root, ITEM, d2) == before)
            check("a sibling's word reopens no accepted stage",
                  DS.stale_stage(d2, DS.load_state(d2), repo2.root) == (None, []),
                  DS.stale_stage(d2, DS.load_state(d2), repo2.root))
            check("a sibling's word sends no reopen", DS.reopen_if_stale(d2, DS.load_state(d2), repo2.root) is None)
        finally:
            shutil.rmtree(repo2.root, ignore_errors=True)
        check("the base feed did not move either (finding 1 only drops X_EXTRA)",
              DS.owner_feed(tmp, ITEM, d) == DS._feed_of(sorted([on_own, named])), (feed0, DS.owner_uncited(tmp, ITEM, d)))

        # binding: only words newer than the concept's start bind the lock
        u, bind = DS.elsewhere_binding(tmp, d, st)
        check("an old word is listed", old in u, u)
        check("an old word does not bind the lock", old not in bind, bind)
        check("a word given after the concept began binds the lock", prefix in bind and by_title in bind, bind)

        # the packet lists them
        text = "\n".join(DS.elsewhere_section(tmp, d, st))
        check("packet: a binding word is listed with its words", ("OWNER:%s on WIDGETWORKS_BUILD_GEARS" % prefix) in text
              and "position AND slope" in text, text[:600])
        check("packet: an old word is listed by reference", ("OWNER:%s on WIDGETWORKS_BUILD_GEARS" % old) in text, text)
        st["running"] = {"run": "pk"}
        full = DS.packet(d, st, {}, 1000, repo=tmp)
        check("packet: open_run's packet carries the section at every stage",
              "His words on the mod's items" in full and prefix in full, full[-400:])
        for s_ in range(6):
            pk = DS.packet(d, dict(st, stage=s_), {}, 1000, repo=tmp)
            check("packet: stage %d carries the section" % s_, "His words on the mod's items" in pk)

        # the lock refuses while a binding word is uncited
        st5 = dict(st, stage=5, running={"run": "r5"})
        res = {"run": "r5", "stage": 5, "outcome": "done"}

        def lock_errs():
            return [e for e in DS.result_errors(res, d, st5, tmp) if e.startswith("lock:")]
        le = lock_errs()
        check("lock: refuses with the uncited binding words named", len(le) == 1 and ("OWNER:" + prefix) in le[0]
              and ("OWNER:" + old) not in le[0], le)
        put(d, "record.json", {"owner_elsewhere_reviewed": [{"source": "OWNER:" + t, "not_design_input": "x"}
                                                            for t in bind if t != prefix],
                               "decisions": [{"id": "slope", "source": "OWNER:" + prefix}]})
        check("a citation in record.json takes a word out", prefix not in (DS.owner_elsewhere(tmp, d, st) or {}),
              DS.owner_elsewhere(tmp, d, st))
        check("lock: passes this check once every binding word is cited", lock_errs() == [], lock_errs())
        put(d, "record.json", {"decisions": [{"id": "slope", "source": "OWNER:%s0" % prefix}]})
        check("a longer tsn does not cite a prefix of itself", prefix in (DS.owner_elsewhere(tmp, d, st) or {}))

        # Codex review 2026-11-18 (its probes, each failing on 114a720def)
        put(d, "record.json", {"decisions": [{"id": "slope", "source": "NOTOWNER:" + prefix}]})
        check("review: NOTOWNER:<tsn> is not a citation", prefix in (DS.owner_elsewhere(tmp, d, st) or {}))
        put(d, "record.json", {})
        with open(os.path.join(tmp, CT.LEDGER_DIR, "events", "BENCH.jsonl"), "a") as f:
            f.write(json.dumps({"seat": "BENCH", "event": "file", "id": ["NOT", "A", "STRING"], "title": "x"}) + "\n")
        try:
            u2 = DS.owner_elsewhere(tmp, d, st)
        except Exception as e:  # noqa: BLE001 - a crash is the defect
            u2 = repr(e)
        check("review: a file event whose id is a list spoils itself only", isinstance(u2, dict) and by_title in u2, u2)
        long_words = "the slope rule " + "x" * 600 + " END_OF_HIS_WORDS"
        long_t = repo.said("WIDGETWORKS_BUILD_GEARS", long_words)
        text = "\n".join(DS.elsewhere_section(tmp, d, st))
        check("review: a binding word is shown in full, not clipped", "END_OF_HIS_WORDS" in text and long_t in text)
        t0 = DS.concept_start(st)
        same_sec = repo.said("WIDGETWORKS_BUILD_GEARS", "said in the second the concept began",
                             tsn=int(t0) * 10 ** 9 + 1)
        check("review: a word given within the concept's first second binds the lock",
              same_sec in (DS.elsewhere_binding(tmp, d, st)[1] or []), DS.elsewhere_binding(tmp, d, st)[1])

        # second Codex review 2026-11-18
        named_sib = repo.said("RIMMANDRAKE_SOME_REPAIR", "about %s: keep the gears oiled" % ITEM)
        repo.filed("RIMMANDRAKE_SOME_REPAIR", "WidgetWorks: repair the oiler")
        check("review 1: a sibling's word naming the concept item is listed (it is in owner_uncited too)",
              named_sib in (DS.owner_elsewhere(tmp, d, st) or {}) and named_sib in (DS.owner_uncited(tmp, ITEM, d) or []))
        prev = ITEM
        for i in range(40):
            repo.filed("RIMMANDRAKE_LINK_%02d_CHAIN" % i, "a link", caused_by=prev)
            prev = "RIMMANDRAKE_LINK_%02d_CHAIN" % i
        deep = repo.said(prev, "forty links down")
        check("review 6: a cause chain of forty links still reaches the concept", deep in (DS.owner_elsewhere(tmp, d, st) or {}))
        put(d, "record.json", {"decisions": [{"id": "x", "source": "NOTOWNER:" + on_own}]})
        check("review 7: NOTOWNER:<tsn> does not take his own-item word out of owner_uncited",
              on_own in (DS.owner_uncited(tmp, ITEM, d) or []), DS.owner_uncited(tmp, ITEM, d))
        put(d, "record.json", {})
        other = os.path.join(tempfile.mkdtemp(prefix="owner_elsewhere_judge_"))
        try:
            os.makedirs(os.path.join(other, os.path.dirname(CT.OWNER_SHARD)))
            shutil.copy(repo.owner, os.path.join(other, CT.OWNER_SHARD))
            check("review 3: a title filed only in the concept's clone counts when another clone judges",
                  by_title in (DS.owner_elsewhere(other, d, st) or {}), DS.owner_elsewhere(other, d, st))
        finally:
            shutil.rmtree(other, ignore_errors=True)
        shard = os.path.join(tmp, CT.LEDGER_DIR, "events", "BENCH.jsonl")
        os.chmod(shard, 0)
        try:
            check("review 4: an unreadable ledger shard makes the list UNMEASURED (None), never 'not ours'",
                  os.access(shard, os.R_OK) or DS.owner_elsewhere(tmp, d, st) is None, DS.owner_elsewhere(tmp, d, st))
        finally:
            os.chmod(shard, 0o644)

        # an unreadable shard is UNMEASURED, never an empty list, and the lock does not pass blind
        os.replace(repo.owner, repo.owner + ".away")
        try:
            check("unreadable OWNER.jsonl: owner_elsewhere is None, not {}", DS.owner_elsewhere(tmp, d, st) is None,
                  DS.owner_elsewhere(tmp, d, st))
            le = lock_errs()
            check("unreadable OWNER.jsonl: the lock refuses as could-not-read", len(le) == 1 and "could not be read" in le[0],
                  le)
            check("unreadable OWNER.jsonl: the packet says UNMEASURED",
                  "UNMEASURED" in "\n".join(DS.elsewhere_section(tmp, d, st)))
        finally:
            os.replace(repo.owner + ".away", repo.owner)

        # sanity probe: the real instrument sees the real case (valid while GSS does not cite the ruling)
        gss = os.path.join(DS.REPO, "design/concepts/GimmeSomeSlack")
        if os.path.isfile(os.path.join(gss, "stage.json")):
            real = DS.owner_elsewhere(DS.REPO, gss)
            check("sanity probe: the real GSS list is readable (a dict, possibly empty once all is cited)",
                  isinstance(real, dict), real)
            cited = any("OWNER:1794839121624014370" in open(os.path.join(gss, n), encoding="utf-8").read()
                        for n in ("record.json", "tree.json") if os.path.isfile(os.path.join(gss, n)))
            if not cited:
                check("ticket's case: the 2026-11-16 hard-wired slope ruling is listed for GSS",
                      "1794839121624014370" in (real or {}), sorted(real or {})[:5])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("FAILED %d: %s" % (len(FAILS), FAILS) if FAILS else "ALL PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
