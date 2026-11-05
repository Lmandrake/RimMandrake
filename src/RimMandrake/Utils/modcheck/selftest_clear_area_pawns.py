#!/usr/bin/env python3
"""selftest_clear_area_pawns.py - suite.TestContext.clear_area removes the pawns in the cleared area, by id.

MODCHECK_CLEARAREA_FIX_PAWNS_STILL_LOITER: clear_area cleared with jawa/destroy_batch categories=All, which never removes
pawns (DESTROY_BATCH_NEVER_KILLS_PAWNS_1), so wildlife, raiders and leftovers loitered in the 'cleared' test area.
Offline, on a fake bridge:
C1  every living, spawned pawn in the rect that is not a site colonist or a bystander is vanished by id;
C2  rows outside the rect or with no readable cell are kept (a list_pawns that ignored `rect`);
    the site's own colonists (humanlike player pawns this chain did not spawn) and t._bystanders are kept;
    a chain's own colonist fixture is removed; corpses and unspawned pawns are skipped;
C3  list_pawns is asked for exactly the destroy_batch rect, and destroy_batch is never asked for Pawn;
C4  the bullet fallback fires only when the vanish does not read back;
C5  a guarded (upstream-failed) context makes no call at all;
C6  an unreadable list_pawns reply removes nothing and never raises.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import suite  # noqa: E402

fails, ran = [], [0]


def check(name, ok, detail=""):
    ran[0] += 1
    print(("PASS " if ok else "FAIL ") + name + ("" if ok else "  " + str(detail)[:400]))
    if not ok:
        fails.append(name)


PAWNS = [
    {"id": "Wolf1", "isPlayer": False, "intelligence": "Animal", "spawned": True, "dead": False, "x": 95, "z": 95},
    {"id": "Raider2", "isPlayer": False, "intelligence": "Humanlike", "spawned": True, "dead": False, "hostile": True, "x": 90, "z": 109},
    {"id": "Colonist3", "isPlayer": True, "intelligence": "Humanlike", "spawned": True, "dead": False, "x": 95, "z": 95},
    {"id": "Fixture4", "isPlayer": True, "intelligence": "Humanlike", "spawned": True, "dead": False, "x": 95, "z": 95},
    {"id": "Corpse5", "isPlayer": False, "intelligence": "Animal", "spawned": False, "dead": True, "x": 95, "z": 95},
    {"id": "Carried6", "isPlayer": False, "intelligence": "Animal", "spawned": False, "dead": False, "x": 95, "z": 95},
    {"id": "Bystander7", "isPlayer": False, "intelligence": "Humanlike", "spawned": True, "dead": False, "x": 95, "z": 95},
    {"id": "Far9", "isPlayer": False, "intelligence": "Animal", "spawned": True, "dead": False, "x": 110, "z": 95},
    {"id": "NoCell10", "isPlayer": False, "intelligence": "Animal", "spawned": True, "dead": False},
    {"id": "Husky8", "isPlayer": True, "intelligence": "Animal", "spawned": True, "dead": False, "x": 95, "z": 95},
]


class FakeSession(object):
    def __init__(self, vanish_ok=True):
        self.calls = []
        self.vanish_ok = vanish_ok

    def call(self, tool, **kw):
        self.calls.append((tool, kw))
        if tool == "jawa/list_pawns":
            return {"success": True, "pawns": [dict(p) for p in PAWNS]}
        if tool == "jawa/pawn_force_incapacitate":
            return {"success": True, "destroyedAfter": self.vanish_ok}
        return {"success": True}

    def tool(self, name):
        return [kw for t, kw in self.calls if t == name]


def ctx(vanish_ok=True):
    s = FakeSession(vanish_ok)
    t = suite.TestContext(s, anchor=(100, 100))
    t.fixture_ids.add("Fixture4")
    t._bystanders = ["Bystander7"]
    return s, t


s, t = ctx()
t.clear_area(size=20)
gone = sorted(k.get("pawn") for k in s.tool("jawa/pawn_force_incapacitate"))
check("C1 vanishes exactly the wolf, the raider, the chain's own fixture and the player animal",
      gone == ["Fixture4", "Husky8", "Raider2", "Wolf1"], gone)
check("C1 every removal is action=vanish",
      all(k.get("action") == "vanish" for k in s.tool("jawa/pawn_force_incapacitate")))
check("C2 site colonist, bystander, corpse, unspawned, out-of-rect and cell-less pawns untouched",
      not ({"Colonist3", "Bystander7", "Corpse5", "Carried6", "Far9", "NoCell10"} & set(gone)), gone)
db = s.tool("jawa/destroy_batch")
lp = s.tool("jawa/list_pawns")
check("C3 one destroy_batch, categories=All (never Pawn)", len(db) == 1 and db[0].get("categories") == "All", db)
check("C3 list_pawns asked for the same rect as destroy_batch",
      len(lp) == 1 and db and lp[0].get("rect") == db[0].get("rects") == "90,90,20,20", (db, lp))
check("C4 no bullet when every vanish reads back", not s.tool("jawa/damage"), s.tool("jawa/damage"))

s, t = ctx(vanish_ok=False)
t.clear_area(size=20)
shot = sorted(k.get("thingId") for k in s.tool("jawa/damage"))
check("C4 bullet fallback for each pawn whose vanish did not read back",
      shot == ["Fixture4", "Husky8", "Raider2", "Wolf1"], shot)

for bad in (None, ["x"], {"success": False}, {"pawns": "nope"}):
    s, t = ctx()
    s.call = (lambda b: (lambda tool, **kw: (s.calls.append((tool, kw)), b if tool == "jawa/list_pawns" else {})[1]))(bad)
    try:
        t.clear_area(size=20)
        ok = not s.tool("jawa/pawn_force_incapacitate") and not s.tool("jawa/damage")
        check("C6 an unreadable listing %r removes nothing and does not raise" % (bad,), ok, s.calls)
    except Exception as ex:
        check("C6 an unreadable listing %r removes nothing and does not raise" % (bad,), False, ex)

s, t = ctx()
t.upstream_failed = True
check("C5 guarded context returns None and calls nothing", t.clear_area(size=20) is None and not s.calls, s.calls)

print("%d/%d passed" % (ran[0] - len(fails), ran[0]))
sys.exit(1 if fails else 0)
