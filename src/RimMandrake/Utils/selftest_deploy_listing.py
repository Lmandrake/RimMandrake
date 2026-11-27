#!/usr/bin/env python3
"""Offline checks for the deploy walks and folder-relative game metadata."""

import errno
import hashlib
import io
import os
import tempfile
import traceback
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import deploy_custom_mods as D
import deploy_def_guard as G
import deploy_index as DI


def file_in(root, rel="Defs/example.xml", body="<Defs/>"):
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    return path


def folder_matcher(folder):
    st = folder.stat()

    def matches(arg):
        if isinstance(arg, int):
            return os.path.samestat(st, os.fstat(arg))
        return Path(arg) == folder

    return matches


def walks(root):
    return (lambda: D.inventory(str(root)), lambda: G.xml_files(str(root)))


def t_enomem_listing_is_retried():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        xml = file_in(root)
        other = file_in(root, "Defs/other.xml")
        matches = folder_matcher(xml.parent)
        real_scandir = os.scandir

        class InterruptedScan:
            def __init__(self, folder):
                self.folder = folder

            def __iter__(self):
                with real_scandir(self.folder) as entries:
                    yield next(entries)
                    raise OSError(errno.ENOMEM, os.strerror(errno.ENOMEM))

            def __enter__(self):
                return self

            def __exit__(self, *exc):
                pass

        for walk in walks(root):
            attempts = []

            def scandir(folder):
                if matches(folder):
                    attempts.append(folder)
                    if len(attempts) == 1:
                        return InterruptedScan(folder)
                return real_scandir(folder)

            with patch.object(os, "scandir", scandir), patch("time.sleep"):
                listing = walk()
            assert len(attempts) == 2, attempts
            assert set(listing) == {str(xml.relative_to(root)), str(other.relative_to(root))}, listing


def t_a_listing_that_still_fails_is_named_not_skipped():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        folder = file_in(root).parent
        matches = folder_matcher(folder)
        real_scandir = os.scandir

        for code in (errno.ENOMEM, errno.EACCES):
            for walk in walks(root):
                attempts = []

                def scandir(arg):
                    if matches(arg):
                        attempts.append(arg)
                        raise OSError(code, os.strerror(code))  # the fd error carries no pathname
                    return real_scandir(arg)

                with patch.object(os, "scandir", scandir), patch("time.sleep"):
                    try:
                        walk()
                    except OSError as exc:
                        assert str(folder) in str(exc) and exc.errno == code, exc
                    else:
                        raise AssertionError(f"the unreadable folder {folder} disappeared from the walk")
                if code == errno.ENOMEM:
                    assert len(attempts) > 1, attempts
                else:
                    assert len(attempts) == 1, attempts
                assert str(root) not in D._INV, "an incomplete inventory was cached"


def t_relative_stat_gives_the_same_index_as_absolute():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        dst, src = root / "Mods" / "Example", root / D.SRC_TIERS[0] / "Example"
        about = "<ModMetaData><packageId>mandrake.example</packageId></ModMetaData>"
        body = "<Defs><ThingDef><defName>Example</defName></ThingDef></Defs>"
        rels = ("About/About.xml", "Defs/example.xml", "Defs/link.xml")
        for mod in (src, dst):
            file_in(mod, rels[0], about)
            xml = file_in(mod, rels[1], body)
            (xml.parent / "link.xml").symlink_to(xml.name)
            (xml.parent / "dangling.xml").symlink_to("missing.xml")
            (xml.parent / "loop.xml").symlink_to("loop.xml")
            (mod / "linked_dir").symlink_to("Defs", target_is_directory=True)
            file_in(mod, "Source/excluded.xml")
        (dst.parent / "loop").symlink_to("loop", target_is_directory=True)

        real_stat, real_scandir = os.stat, os.scandir
        absolute = {rel: real_stat(dst / rel) for rel in rels}
        matches = folder_matcher(dst / "Defs")
        relative_stats, absolute_stats, scans = set(), set(), set()

        def stat(path, *args, **kwargs):
            fd = kwargs.get("dir_fd")
            if fd is not None and matches(fd):
                relative_stats.add(os.fspath(path))
            if fd is None and not isinstance(path, int) and os.path.dirname(path) == str(dst / "Defs"):
                absolute_stats.add(os.fspath(path))
            return real_stat(path, *args, **kwargs)

        def scandir(arg):
            if matches(arg):
                scans.add(isinstance(arg, int))
            return real_scandir(arg)

        db = root / "index.sqlite"
        idx = DI.Index(str(db), scope=str(dst.parent))
        with patch.object(os, "stat", stat), patch.object(os, "scandir", scandir):
            assert D.compare(str(src), str(dst), index=idx) == ([], [], [], sorted(rels))
            assert scans == {True}, scans
            assert {"example.xml", "link.xml"} <= relative_stats, relative_stats
            assert not absolute_stats, absolute_stats
            scans.clear()
            relative_stats.clear()
            with (patch.object(D, "SRC_ROOT", str(root)), patch.object(G, "STORE", idx),
                  redirect_stdout(io.StringIO())):
                findings = D._def_guard(SimpleNamespace(prune=False), [("Example", str(src))],
                                        [], str(dst.parent))
            assert len(findings) == 1 and "defined 2 times in ONE mod Example" in findings[0], findings
            assert scans == {True}, scans
            assert {"example.xml", "link.xml"} <= relative_stats, relative_stats
            assert not absolute_stats, absolute_stats
        idx.save()
        saved = DI.Index(str(db), scope=str(dst.parent))
        rows = saved.rows
        assert set(rows) == {str(dst / rel) for rel in rels}, rows
        for rel, st in absolute.items():
            entry = rows[str(dst / rel)]
            assert entry[:3] == (st.st_size, st.st_mtime_ns, hashlib.sha256((dst / rel).read_bytes()).hexdigest())
        for rel in rels[1:]:
            st = absolute[rel]
            assert saved.parsed_get(str(dst / rel), st.st_size, st.st_mtime_ns) == [[["ThingDef", "Example"]], []]


def main():
    tests = (
        t_enomem_listing_is_retried,
        t_a_listing_that_still_fails_is_named_not_skipped,
        t_relative_stat_gives_the_same_index_as_absolute,
    )
    failed = 0
    for test in tests:
        try:
            test()
        except Exception:
            traceback.print_exc()
            print(f"FAIL {test.__name__}")
            failed += 1
        else:
            print(f"PASS {test.__name__}")
        finally:
            D.forget_all()
            G._CACHE.clear()
    print(f"{len(tests)} check(s), {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
