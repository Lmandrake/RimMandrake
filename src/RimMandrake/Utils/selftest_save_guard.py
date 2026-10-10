"""selftest_save_guard.py - save_guard never lets a save-capable run change a keeper unnoticed
(KEEPER_SAVES_HARDEN_WRONG_SLOT_WRITES). Written failing-first. Temp Saves dir + temp store; no game.
"""
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import save_guard as G  # noqa: E402

HEAD = '<?xml version="1.0" encoding="utf-8"?>\n<savegame>\n<meta>'


def w(d, n, body):
    with open(os.path.join(d, n), "w") as fh:
        fh.write(HEAD + body + "</meta></savegame>\n")


def case(name, cond, detail=""):
    print("%-4s %s %s" % ("ok" if cond else "FAIL", name, detail))
    return bool(cond)


def setup():
    saves, store = tempfile.mkdtemp(), tempfile.mkdtemp()
    w(saves, "KEEPER_A.rws", "a" * 3000)
    w(saves, "KEEPER_B.rws", "b" * 3000)
    w(saves, "Autosave-1.rws", "z" * 3000)
    return saves, store


def main():
    good = []
    saves, store = setup()
    snap = G.snapshot(saves, store)
    good.append(case("snapshot covers keepers, not autosaves", sorted(snap["keepers"]) == ["KEEPER_A.rws", "KEEPER_B.rws"],
                     sorted(snap["keepers"])))
    good.append(case("every keeper is backed up in the store by hash",
                     all(os.path.exists(G.store_path(store, k["sha256"])) for k in snap["keepers"].values())))

    good.append(case("admit refuses an existing target", G.admit(snap, "KEEPER_A", current_slot="none")))
    good.append(case("admit refuses when the current slot is a keeper (save_game may write it)",
                     G.admit(snap, "NEW_ONE", current_slot="KEEPER_B")))
    good.append(case("admit refuses when the current slot is unknown", G.admit(snap, "NEW_ONE", current_slot=None)))
    good.append(case("admit passes a new name from a fileless game", G.admit(snap, "NEW_ONE", current_slot="none") == []))
    good.append(case("admit refuses a path escape", G.admit(snap, "../evil", current_slot="none")))

    # the trap: save_game wrote the CURRENT slot instead of the requested name
    w(saves, "KEEPER_B.rws", "B" * 3500)
    v = G.verify(snap, saves, "NEW_ONE")
    good.append(case("wrong-slot write: no new file AND keeper changed -> refused",
                     not v["verified"] and any("KEEPER_B" in p for p in v["problems"]) and
                     any("no NEW_ONE.rws" in p for p in v["problems"]), v["problems"]))
    good.append(case("changed keeper is restorable from the store", G.restore(snap, saves, store, "KEEPER_B.rws") and
                     open(os.path.join(saves, "KEEPER_B.rws")).read().count("b") == 3000))

    saves, store = setup()
    snap = G.snapshot(saves, store)
    w(saves, "NEW_ONE.rws", "n" * 3000)
    w(saves, "Autosave-2.rws", "y" * 3000)
    v = G.verify(snap, saves, "NEW_ONE")
    good.append(case("honest save verifies, lists every changed file", v["verified"] and
                     sorted(v["changed"]) == ["Autosave-2.rws", "NEW_ONE.rws"], v))

    saves, store = setup()
    snap = G.snapshot(saves, store)
    with open(os.path.join(saves, "NEW_ONE.rws"), "w") as fh:
        fh.write("truncated")
    v = G.verify(snap, saves, "NEW_ONE")
    good.append(case("a malformed / tiny target is refused", not v["verified"], v["problems"]))

    saves, store = setup()
    snap = G.snapshot(saves, store)
    os.remove(os.path.join(saves, "KEEPER_A.rws"))
    v = G.verify(snap, saves, None)
    good.append(case("run mode (no target): a vanished keeper is refused", not v["verified"] and
                     any("KEEPER_A" in p for p in v["problems"]), v["problems"]))

    # same-size rewrite is caught by hash, not size
    saves, store = setup()
    snap = G.snapshot(saves, store)
    w(saves, "KEEPER_A.rws", "c" * 3000)
    v = G.verify(snap, saves, None)
    good.append(case("same-size keeper rewrite caught by hash", not v["verified"], v["problems"]))

    # saved_base.save_base (the northstar runner's save) now goes through the guard
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "modcheck"))
    import saved_base
    G.STORE = tempfile.mkdtemp()

    class Wrong:                                   # save_game writes the current slot, reports success
        def __init__(self, d):
            self.d = d

        def call(self, tool, **kw):
            w(self.d, "KEEPER_B.rws", "X" * 3200)
            return {"success": True}
    saves, store = setup()
    r = saved_base.save_base(Wrong(saves), saves_dir=saves, name="NS_BASE", wait=0, current_slot="none")
    good.append(case("save_base catches a wrong-slot write by keeper hash", not r["verified"] and
                     any("KEEPER_B" in p for p in r["problems"]), r["problems"]))
    saves, store = setup()
    r = saved_base.save_base(Wrong(saves), saves_dir=saves, name="NS_BASE", wait=0, current_slot="KEEPER_B")
    good.append(case("save_base refuses before the call when the current slot is a keeper",
                     not r["verified"] and open(os.path.join(saves, "KEEPER_B.rws")).read().count("b") == 3000,
                     r["problems"]))

    print("%d/%d" % (sum(good), len(good)))
    return 0 if all(good) else 1


if __name__ == "__main__":
    sys.exit(main())
