#!/usr/bin/env python3
"""selftest_choose_look_rows.py -- objects_sheet.choose_look picks the whole-run row of a pipe's style menu, whatever its tail.

Visit 11 (2026-11-24, ArchBig, flowworks_list): the pipe's menu read "Modern: the whole line" (live probe), choose_look looked only for
"whole connected run", picked nothing, and the walk save's four sprinkler pipes all kept Scrapper ("game reads None"). The menus
are given here as the game printed them; a fake bridge records the option index chosen.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import objects_sheet as O  # noqa: E402

FAILS = []


def check(name, ok, got=None):
    print(("ok    " if ok else "FAIL  ") + name + ("" if ok else "  got %r" % (got,)))
    if not ok:
        FAILS.append(name)


class FakeB(object):
    def __init__(self, labels):
        self.labels, self.chosen = labels, None

    def call(self, tool, **kw):
        if tool == "rimworld/list_selected_gizmos":
            return {"gizmos": [{"label": "Choose style", "gizmoId": "g1"}]}
        if tool == "rimworld/get_context_menu_options":
            cur = self.chosen
            return {"menuId": "m1", "options": [
                {"index": i, "label": (l.replace(":", " (current):", 1) if i == cur else l)} for i, l in enumerate(self.labels)]}
        if tool == "rimworld/execute_context_menu_option":
            self.chosen = kw.get("optionIndex")
        return {"success": True}


class FakeW(object):
    def __init__(self, labels):
        self.B = FakeB(labels)


LIVE = ["Scrapper: the whole line", "Industrial: the whole line", "Modern: the whole line", "Futuristic: the whole line"]
OLD = ["Scrapper: this pipe", "Scrapper: whole connected run", "Modern: this pipe", "Modern: whole connected run"]
REEL = ["Scrapper", "Industrial", "Modern", "Futuristic"]

w = FakeW(LIVE)
O.choose_look(w, (0, 0), "Modern", run=True)
check("the live pipe menu ('<Look>: the whole line'): the Modern row is chosen", w.B.chosen == 2, w.B.chosen)
w = FakeW(OLD)
O.choose_look(w, (0, 0), "Modern", run=True)
check("the old pipe menu: the whole-connected-run row, not 'this pipe'", w.B.chosen == 3, w.B.chosen)
w = FakeW(OLD)
O.choose_look(w, (0, 0), "Modern", run=False)
check("the old pipe menu, one thing: 'this pipe'", w.B.chosen == 2, w.B.chosen)
w = FakeW(REEL)
O.choose_look(w, (0, 0), "Industrial", run=False)
check("a reel's bare menu: the bare row", w.B.chosen == 1, w.B.chosen)
w = FakeW(LIVE)
O.choose_look(w, (0, 0), "Neon", run=True)
check("can-fail: a look the menu lacks picks nothing", w.B.chosen is None, w.B.chosen)


class FakeReachB(object):
    """RIMMANDRAKE_OFFER_FLOWWORKS_STYLE_REACHES_AS_SLACK_DOES (2026-11-25): the first menu is the reach, the second the look.
    As the live game does (ArchSmall, 2026-11-26, BIGNET_PROOF_FIX_SIZE_NOT_RESTORED bundle): a FloatMenu that an option's
    action opens through rimworld/execute_context_menu_option is gone before the next call ("No context menu or pop-up option
    menu is open"); jawa/debug_action_menu picks on the newest open menu in one main-thread call and pins the menu the pick
    opens, so get_context_menu_options then reads it."""
    REACH = ["This item: this pipe only", "All connected: the whole connected line", "All on map: 12 FlowWorks parts you own"]
    LOOKS = ["Scrapper (current)", "Industrial", "Modern", "Futuristic"]

    def __init__(self):
        self.menu, self.picks = None, []

    def _labels(self):
        return None if self.menu is None else (self.REACH if self.menu == 0 else self.LOOKS)

    def call(self, tool, **kw):
        if tool == "rimworld/list_selected_gizmos":
            return {"gizmos": [{"label": "Choose style", "gizmoId": "g1"}]}
        if tool == "rimworld/execute_gizmo":
            self.menu = 0
        if tool == "rimworld/get_context_menu_options":
            labels = self._labels()
            if labels is None:
                return {"success": False, "message": "No context menu or pop-up option menu is open."}
            return {"menuId": "m%d" % self.menu, "options": [{"index": i, "label": l} for i, l in enumerate(labels)]}
        if tool == "rimworld/execute_context_menu_option":
            if self.menu is not None:
                self.picks.append((self.menu, kw.get("optionIndex")))
            self.menu = None            # a reach pick's new menu vanishes; a look pick closes the menu
        if tool == "jawa/debug_action_menu":
            labels = self._labels() or []
            hit = [i for i, l in enumerate(labels) if l.lower() == str(kw.get("pick")).lower()]
            if not hit:
                return {"success": False, "message": "no option %r" % kw.get("pick")}
            self.picks.append((self.menu, hit[0]))
            self.menu = 1 if self.menu == 0 else None   # the reach opens the looks menu, pinned
            return {"success": True, "picked": {"index": hit[0], "label": labels[hit[0]]}, "menuOpenAfter": int(self.menu == 1)}
        if tool in ("rimworld/close_context_menu", "rimworld/clear_selection"):
            if tool == "rimworld/close_context_menu":
                self.menu = None
        return {"success": True}


for run, want in ((True, [(0, 1), (1, 2)]), (False, [(0, 0), (1, 2)])):
    w = FakeW([])
    w.B = FakeReachB()
    O.choose_look(w, (0, 0), "Modern", run=run)
    check("the reach menu (run=%s): reach %s, then the Modern look; the read-back opens This item" % (run, want[0][1]),
          w.B.picks == want + [(0, 0)], w.B.picks)
w = FakeW([])
w.B = FakeReachB()
O.choose_look(w, (0, 0), "Neon", run=True)
check("can-fail: the reach menu with a look it lacks picks no look", all(m == 0 for m, _ in w.B.picks), w.B.picks)
print("selftest_choose_look_rows: %d failure(s)" % len(FAILS))
sys.exit(1 if FAILS else 0)
