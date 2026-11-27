#!/usr/bin/env python3
"""Selftest: the deploy index (design/specs/2026-11-26-deploy-index/boundary.md).

Every promise of the page has a check of the same name. Three planted faults each must make the
indexed compare report a difference (a new size; the same size and a new time; a deleted file), and a
MUTANT index that trusts the size alone must be caught by the same-size check (the test can see).

    python3 src/RimMandrake/Utils/selftest_deploy_index.py
"""
import builtins
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import deploy_custom_mods as D                                  # noqa: E402
import deploy_def_guard as G                                    # noqa: E402
import deploy_index as DI                                       # noqa: E402

def write(path, text, mtime=None):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)
    if mtime is not None:
        os.utime(path, ns=(mtime, mtime))


class Opens:
    """Records every path opened for reading under `under` while active."""
    def __init__(self, under):
        self.under, self.seen = under, []

    def __enter__(self):
        self.real = builtins.open
        me = self

        def spy(path, *a, **k):
            try:
                p = os.fspath(path)
            except TypeError:
                p = None
            if isinstance(p, str) and p.startswith(me.under):
                me.seen.append(p)
            return me.real(path, *a, **k)
        builtins.open = spy
        return self

    def __exit__(self, *a):
        builtins.open = self.real


class Fixture:
    def __init__(self):
        self.tmp = tempfile.mkdtemp(prefix="deployindex-")
        self.src = os.path.join(self.tmp, "repo", "ModA")
        self.dst = os.path.join(self.tmp, "game", "ModA")
        self.db = os.path.join(self.tmp, "state", "index.sqlite")
        self.t0 = 1_700_000_000_000_000_000
        for rel, body in (("About/About.xml", "<ModMetaData><packageId>t.a</packageId></ModMetaData>\n"),
                          ("Defs/a.xml", "<Defs><ThingDef><defName>AAAA</defName></ThingDef></Defs>\n"),
                          ("Defs/b.xml", "<Defs><ThingDef><defName>BBBB</defName></ThingDef></Defs>\n"),
                          ("Textures/t.bin", "0123456789" * 50)):
            write(os.path.join(self.src, rel), body)
            write(os.path.join(self.dst, rel), body, self.t0)

    def index(self, **kw):
        D.forget_all()
        return DI.Index(self.db, **kw)

    def compare(self, idx):
        D.forget_all()
        return D.compare(self.src, self.dst, index=idx)

    def close(self):
        D.forget_all()
        shutil.rmtree(self.tmp, ignore_errors=True)


def warm(fx):
    """A first (cold) compare that writes the index; returns nothing."""
    idx = fx.index()
    new, changed, gone, same = fx.compare(idx)
    assert (new, changed, gone) == ([], [], []) and len(same) == 4, (new, changed, gone, same)
    idx.save()


def t_a_missing_index_reads_every_file_and_writes_the_index():
    fx = Fixture()
    try:
        with Opens(fx.dst) as o:
            idx = fx.index()
            new, changed, gone, same = fx.compare(idx)
            idx.save()
        assert len(same) == 4 and not (new or changed or gone)
        assert len(set(o.seen)) == 4, o.seen                 # every deployed file read once
        assert os.path.isfile(fx.db)
        return True
    finally:
        fx.close()


def t_an_unchanged_file_is_not_read():
    fx = Fixture()
    try:
        warm(fx)
        with Opens(fx.dst) as o:
            idx = fx.index()
            new, changed, gone, same = fx.compare(idx)
        assert not (new or changed or gone) and len(same) == 4
        assert o.seen == [], o.seen
        return True
    finally:
        fx.close()


def t_a_new_size_is_a_difference():
    fx = Fixture()
    try:
        warm(fx)
        write(os.path.join(fx.dst, "Defs/a.xml"), "<Defs>much longer text than before</Defs>\n", fx.t0)
        with Opens(fx.dst) as o:
            new, changed, gone, same = fx.compare(fx.index())
        return changed == [os.path.join("Defs", "a.xml")] and not new and not gone and o.seen == []   # no read needed
    finally:
        fx.close()


def same_size_new_time(fx, make_index):
    warm(fx)
    p = os.path.join(fx.dst, "Defs/a.xml")
    body = open(p, encoding="utf-8").read()
    write(p, body.replace("AAAA", "ZZZZ"), fx.t0 + 5_000_000_000)     # same size, new bytes, new time
    return fx.compare(make_index(fx))


def t_a_new_time_is_a_difference():
    fx = Fixture()
    try:
        new, changed, gone, same = same_size_new_time(fx, lambda f: f.index())
        return changed == [os.path.join("Defs", "a.xml")] and not new and not gone
    finally:
        fx.close()


def t_a_deleted_file_is_a_difference():
    fx = Fixture()
    try:
        warm(fx)
        os.remove(os.path.join(fx.dst, "Defs/b.xml"))                  # deployed copy deleted
        new, changed, gone, same = fx.compare(fx.index())
        ok1 = new == [os.path.join("Defs", "b.xml")] and not changed and not gone
        os.remove(os.path.join(fx.src, "Textures/t.bin"))              # repo file deleted
        new, changed, gone, same = fx.compare(fx.index())
        ok2 = gone == [os.path.join("Textures", "t.bin")]
        return ok1 and ok2
    finally:
        fx.close()


def t_the_test_can_see_a_mutant_that_trusts_the_size_alone():
    """The same-size check must go RED on an index that ignores the time (mutate-your-checker)."""
    fx = Fixture()
    real = DI.Index.valid
    try:
        DI.Index.valid = lambda self, entry, size, mtime_ns: entry is not None and entry[0] == size
        new, changed, gone, same = same_size_new_time(fx, lambda f: f.index())
        missed = not changed                                            # the mutant misses the fault
        return missed
    finally:
        DI.Index.valid = real
        fx.close()


def t_a_same_size_different_bytes_is_changed():
    fx = Fixture()
    try:
        write(os.path.join(fx.dst, "Defs/a.xml"),
              open(os.path.join(fx.src, "Defs/a.xml"), encoding="utf-8").read().replace("AAAA", "QQQQ"), fx.t0)
        new, changed, gone, same = fx.compare(fx.index())               # no index yet: read
        return changed == [os.path.join("Defs", "a.xml")]
    finally:
        fx.close()


def t_a_same_size_same_time_edit_is_found_only_by_the_full_read():
    """The page's DOES NOT SURVIVE line, pinned: the index cannot see it; --full-read can."""
    fx = Fixture()
    try:
        warm(fx)
        p = os.path.join(fx.dst, "Defs/a.xml")
        write(p, open(p, encoding="utf-8").read().replace("AAAA", "YYYY"), fx.t0)   # time restored
        blind = fx.compare(fx.index())[1] == []
        full = fx.compare(fx.index(full_read=True))[1] == [os.path.join("Defs", "a.xml")]
        return blind and full
    finally:
        fx.close()


def t_a_full_read_rewrites_the_index():
    fx = Fixture()
    try:
        warm(fx)
        with Opens(fx.dst) as o:
            idx = fx.index(full_read=True)
            fx.compare(idx)
            idx.save()
        ok_read = len(set(o.seen)) == 4
        with Opens(fx.dst) as o2:
            fx.compare(fx.index())
        return ok_read and o2.seen == []
    finally:
        fx.close()


def t_the_index_holds_only_bytes_that_were_read():
    """A deploy drops the entry of each file it writes; the verify compare reads it and records it."""
    fx = Fixture()
    try:
        warm(fx)
        idx = fx.index()
        # the repo file has the SAME size as the deployed one and the SAME time as the entry: a copy (copy2 keeps the
        # source's time) then leaves size and time as the old entry has them, so only the drop makes the verify read it
        a_src = os.path.join(fx.src, "Defs/a.xml")
        write(a_src, open(a_src, encoding="utf-8").read().replace("AAAA", "NNNN"), fx.t0)
        D.forget_all()
        new, changed, gone, same = D.compare(fx.src, fx.dst, index=idx)
        assert changed == [os.path.join("Defs", "a.xml")]
        D.copy(fx.src, fx.dst, changed)
        idx.drop_under(fx.dst, changed)
        D.forget(fx.dst)
        with Opens(fx.dst) as o:
            n2, c2, g2, s2 = D.compare(fx.src, fx.dst, index=idx)
        assert not (n2 or c2 or g2), (n2, c2, g2)
        assert [os.path.basename(x) for x in o.seen] == ["a.xml"], o.seen   # only the written file is read
        idx.save()
        with Opens(fx.dst) as o3:
            fx.compare(fx.index())
        return o3.seen == []
    finally:
        fx.close()


def t_a_bad_index_never_fails_the_plan():
    fx = Fixture()
    try:
        os.makedirs(os.path.dirname(fx.db), exist_ok=True)
        with open(fx.db, "wb") as f:
            f.write(b"this is not a database at all" * 100)
        idx = fx.index()
        new, changed, gone, same = fx.compare(idx)
        idx.save()
        ok_corrupt = len(same) == 4 and not (new or changed or gone)
        bad = DI.Index(os.path.join(fx.tmp, "no_such_dir_is_a_file", "x", "i.sqlite"))   # parent is made
        os.makedirs(os.path.join(fx.tmp, "blocker"), exist_ok=True)
        blocked = DI.Index(os.path.join(fx.tmp, "state", "index.sqlite", "inside", "i.sqlite"))  # parent is a file
        D.forget_all()
        r = D.compare(fx.src, fx.dst, index=blocked)
        blocked.save()
        return ok_corrupt and len(r[3]) == 4 and bad is not None
    finally:
        fx.close()


def t_the_parse_is_kept_with_its_stat():
    fx = Fixture()
    try:
        game = os.path.join(fx.tmp, "game")
        p = os.path.join(fx.dst, "Defs/a.xml")
        idx = DI.Index(fx.db)
        G.STORE = idx
        G._CACHE.clear()
        d1, _ = G.parse_defs(p)
        idx.save()
        assert d1 == [("ThingDef", "AAAA")], d1
        G._CACHE.clear()
        idx2 = DI.Index(fx.db)
        G.STORE = idx2
        with Opens(game) as o:
            d2, _ = G.parse_defs(p)
        assert d2 == d1 and o.seen == [], (d2, o.seen)
        write(p, open(p, encoding="utf-8").read().replace("AAAA", "ZZZZ"), fx.t0 + 9_000_000_000)   # same size
        G._CACHE.clear()
        d3, _ = G.parse_defs(p)
        return d3 == [("ThingDef", "ZZZZ")]
    finally:
        G.STORE = None
        G._CACHE.clear()
        fx.close()


def t_a_folder_that_holds_no_defs_is_not_walked_for_another_mod():
    """The def guard reads Defs/ of each load root; Textures, Sounds, Assemblies and Languages hold no def file,
    and on the Windows drive they are 75% of the folders (measured 2026-11-26: 4,019 of 5,330)."""
    fx = Fixture()
    try:
        mod = os.path.join(fx.tmp, "game", "ModB")
        for rel in ("Defs/a.xml", "1.6/Defs/b.xml", "Compat/Foo/Defs/c.xml", "Textures/Deep/Er/x.xml",
                    "Languages/English/DefInjected/y.xml", "Sounds/z.xml", "LoadFolders.xml", "About/About.xml"):
            write(os.path.join(mod, rel), "<Defs/>\n")
        os.makedirs(os.path.join(mod, "Assemblies", "Sub"))
        walked = []
        real = os.scandir

        def spy(p=".", *a, **k):
            walked.append(os.fspath(p))
            return real(p, *a, **k)
        os.scandir = spy
        try:
            full = G.xml_files(mod)
            walked.clear()
            cut = G.xml_files(mod, prune=G.NON_DEF_DIRS)
        finally:
            os.scandir = real
        want = {"Defs/a.xml", "1.6/Defs/b.xml", "Compat/Foo/Defs/c.xml", "LoadFolders.xml", "About/About.xml"}
        bad_walk = [w for w in walked if any(x in w for x in ("Textures", "Languages", "Sounds", "Assemblies"))]
        return set(cut) == want and "Textures/Deep/Er/x.xml" in full and not bad_walk
    finally:
        fx.close()




def main():
    tests = (
        t_a_missing_index_reads_every_file_and_writes_the_index,
        t_an_unchanged_file_is_not_read,
        t_a_new_size_is_a_difference,
        t_a_new_time_is_a_difference,
        t_a_deleted_file_is_a_difference,
        t_the_test_can_see_a_mutant_that_trusts_the_size_alone,
        t_a_same_size_different_bytes_is_changed,
        t_a_same_size_same_time_edit_is_found_only_by_the_full_read,
        t_a_full_read_rewrites_the_index,
        t_the_index_holds_only_bytes_that_were_read,
        t_a_bad_index_never_fails_the_plan,
        t_the_parse_is_kept_with_its_stat,
        t_a_folder_that_holds_no_defs_is_not_walked_for_another_mod,
    )
    bad = 0
    for fn in tests:
        try:
            ok = fn()
        except Exception as e:                                          # noqa: BLE001
            import traceback
            traceback.print_exc()
            ok = False
            print("   (%s)" % e)
        print("%s %s" % ("PASS" if ok else "FAIL", fn.__name__))
        bad += 0 if ok else 1
    print("%d check(s), %d failed" % (len(tests), bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
