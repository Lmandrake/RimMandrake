#!/usr/bin/env python3
"""Acceptance for plan.md step 3: the no-home count, and the owner's one view built by one rule.

Contract:
  a new module src/RimMandrake/Utils/no_home.py
    count(sources) -> {"no_home": int or None, "by_source": {name: int}, "unmeasured": [name]}
        sources = {name: callable -> list of needs with no home}; a callable that raises is a source that could not
        be read: it is named in "unmeasured" and adds nothing. When no source could be read, "no_home" is None.
    unanswered_cards(asked, answered) -> the asked ids with no answer, in the order asked
  a new function owner_queue.one_view(his, ours, home) -> str, the block the page shows
        his, ours = lists of {"item", "q"} (ours also "age"); home = the dict count() returns
  maturation_now.py calls owner_queue.one_view.
Expected when built: PASS 12/12.  Today: FAIL 0/12, because no_home.py and owner_queue.one_view do not exist."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _harness as H  # noqa: E402

NH, why = H.load("no_home")
OQ, why_oq = H.load("owner_queue")


def nh():
    if NH is None:
        raise RuntimeError(why)
    return NH


def boom():
    raise OSError("the transcripts are on another machine")


def view(his, ours, home):
    if OQ is None or not hasattr(OQ, "one_view"):
        raise RuntimeError(why_oq or "owner_queue.one_view does not exist")
    return OQ.one_view(his, ours, home)


def src(name):
    with open(os.path.join(H.UTILS, name), encoding="utf-8") as f:
        return f.read()


HOME = {"no_home": 3, "by_source": {"typed words": 2, "ended runs": 1}, "unmeasured": ["words typed on SteveDesktop"]}
HIS = [{"item": "X_ONE", "q": "Pick the bridge art"}]
OURS = [{"item": "X_TWO", "q": "Write the ruling into the page", "age": "2d"}]

H.check("count sums the readable sources",
        lambda: nh().count({"a": lambda: ["m1", "m2"], "b": lambda: ["r1"]})["no_home"] == 3)
H.check("count names each source's own number",
        lambda: nh().count({"a": lambda: ["m1", "m2"], "b": lambda: []})["by_source"] == {"a": 2, "b": 0})
H.check("a source that cannot be read is named unmeasured and the others still count",
        lambda: (lambda r: r["no_home"] == 1 and r["unmeasured"] == ["b"])(nh().count({"a": lambda: ["m1"], "b": boom})))
H.check("readable and empty is a measured zero",
        lambda: (lambda r: r["no_home"] == 0 and r["unmeasured"] == [])(nh().count({"a": lambda: []})))
H.check("no readable source is None, never zero", lambda: nh().count({"a": boom, "b": boom})["no_home"] is None)
H.check("no sources at all is None, never zero", lambda: nh().count({})["no_home"] is None)
H.check("an asked card with no answer is listed; an answered one is not",
        lambda: nh().unanswered_cards(["c1", "c2", "c3"], {"c2"}) == ["c1", "c3"] and nh().unanswered_cards(["c1"], {"c1"}) == [])
H.check("the view shows the count of needs not filed anywhere", lambda: "not filed anywhere: 3" in view(HIS, OURS, HOME))
H.check("the view names the sources it could not read",
        lambda: "words typed on SteveDesktop" in view(HIS, OURS, HOME))
H.check("an unread count reads UNMEASURED, never 0",
        lambda: (lambda t: "UNMEASURED" in t and "not filed anywhere: 0" not in t)(
            view(HIS, OURS, {"no_home": None, "by_source": {}, "unmeasured": ["typed words"]})))
H.check("the view shows what is his and what is ours with its age",
        lambda: (lambda t: "Pick the bridge art" in t and "Write the ruling into the page" in t and "2d" in t)(view(HIS, OURS, HOME)))
H.check("Maturation Now builds the block from owner_queue.one_view", lambda: "one_view(" in src("maturation_now.py"))
H.done(12)
