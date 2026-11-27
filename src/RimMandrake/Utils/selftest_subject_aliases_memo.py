#!/usr/bin/env python3
"""Exercise subject alias resolution through streams.collect with fixture sheets and rulings."""
import json
import os
import sys
import tempfile
from collections import Counter
from contextlib import ExitStack, contextmanager
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent / "ops_core"))
import streams as S  # noqa: E402
import artledger as L  # noqa: E402

NOW = 1_792_000_000.0
SHEET = "fauna_sheet_2026-07-01"
ALIASES = {"Newt": "Middle", "Middle": "Otter"}


def write_json(path, value):
    path.write_text(json.dumps(value), encoding="utf-8")


@contextmanager
def fixture():
    # Keep the actual collector, queue reader and art ledger index. Stub the external instruments.
    with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent) as td, ExitStack() as stack:
        root = Path(td)
        art = root / "art"
        (art / "events").mkdir(parents=True)
        aliases = art / L.ALIASES_FILE
        write_json(aliases, {"aliases": ALIASES})
        subjects = ("Newt", "Finch", "Crane")
        items = [{"id": subject, "graphics": [{"lane": "slot", "key": subject,
                  "cols": [{"faces": {"south": subject}}]}]} for subject in subjects]
        (root / f"{SHEET}.html").write_text(
            '<script id="ITEMS" type="application/json">' + json.dumps(items) + "</script>", encoding="utf-8")
        write_json(root / f"{SHEET}.decisions.json", {"biome": "SUBJECTS_fauna", "decisions": {}})
        write_json(root / "fauna.subjects.json", {"biomes": {"SUBJECTS_fauna": {"rows": []}}})
        drawn, ruled = "2026-07-02T00:00:00Z", "2026-07-03T00:00:00Z"
        events = [{"type": "variant", "id": subject, "sha": subject, "ts": drawn} for subject in subjects]
        events += [{"type": "ruling", "id": f"ruling-{i}", "subject_key": subject, "ts": ruled,
                    "by": "owner", "trust": "ruled", "verdict": "redo"}
                   for i, subject in enumerate(("Otter", "Unrelated", "UNRELATED", "Otter"))]
        (art / "events" / "BENCH.jsonl").write_text("".join(json.dumps(e) + "\n" for e in events), encoding="utf-8")
        stack.enter_context(patch.dict(os.environ, {"ART_LEDGER_DIR": str(art), "RM_DATA_ROOT": str(root)}))
        stack.enter_context(patch.multiple(
            S, ART_OUT=root, DIR=root, NIGHTLY=root / "nightly", time=SimpleNamespace(time=lambda: NOW),
            code_review_dirty=lambda: S.U("fixture"), modcheck_today=lambda now: {"O4": S.U("fixture"), "fold": None},
            _art_events=lambda: [(NOW - 60, "variant", "agent")], budget=lambda now: S.U("fixture"),
            probe_game=lambda: {"evidence": "fixture", "at": NOW}, pacing=lambda now: {"mode": "fixture"},
        ))
        stack.enter_context(patch.multiple(
            S.TM, load_testq=lambda: {"root": root, "why": "fixture"}, load_bridge=lambda: {"why": "fixture"},
        ))
        yield aliases


def collect():
    return S.collect(now=NOW, events=[])


def t_aliases_computed_once_per_subject_per_run():
    class CountedAliases(dict):
        def __contains__(self, key):
            checks[key] += 1
            return super().__contains__(key)

    with fixture() as aliases:
        checks = Counter()
        real_stat = Path.stat
        alias_stats = []

        def count_stat(path, *args, **kwargs):
            if path == aliases:
                alias_stats.append(path)
            return real_stat(path, *args, **kwargs)

        read_aliases = L.subject_aliases
        with patch.object(Path, "stat", count_stat), patch.object(
            L, "subject_aliases", side_effect=lambda: CountedAliases(read_aliases())
        ) as load:
            for run in (1, 2):
                checks.clear()
                assert collect()["measures"]["A1"]["v"] == 2
                assert load.call_count == len(alias_stats) == run, (
                    f"after run {run}: {load.call_count} alias loads and {len(alias_stats)} stats"
                )
                assert checks["unrelated"] == checks["newt"] == 1, checks


def t_a_changed_source_file_recomputes():
    with fixture() as aliases:
        assert collect()["measures"]["A1"]["v"] == 2
        # An atomic replacement can carry forward the original timestamp and size.
        stamp = aliases.stat()
        replacement = aliases.with_suffix(".tmp")
        write_json(replacement, {"aliases": {**ALIASES, "Middle": "Bison"}})
        os.utime(replacement, ns=(stamp.st_atime_ns, stamp.st_mtime_ns))
        replacement.replace(aliases)
        assert collect()["measures"]["A1"]["v"] == 3, "a second collect used the old alias map"
        write_json(aliases, {"aliases": ALIASES})
        assert collect()["measures"]["A1"]["v"] == 2
        aliases.unlink()
        assert collect()["measures"]["A1"]["v"] == 3


def t_collect_output_unchanged():
    def uncached_subject(key):
        aliases = L.subject_aliases()
        seen = set()
        key = (key or "").lower()
        while key in aliases and key not in seen:
            seen.add(key)
            key = aliases[key]
        return key

    with fixture():
        with patch.object(L, "canonical_subject", uncached_subject):
            expected = collect()
        actual = collect()
        assert actual["measures"]["A1"]["v"] == 2, actual["measures"]["A1"]
        assert actual == expected


if __name__ == "__main__":
    tests = (t_aliases_computed_once_per_subject_per_run, t_a_changed_source_file_recomputes, t_collect_output_unchanged)
    failures = 0
    for test in tests:
        try:
            test()
        except AssertionError as exc:
            failures += 1
            print(f"FAIL {test.__name__}: {exc}")
        else:
            print(f"PASS {test.__name__}")
    print(f"selftest_subject_aliases_memo: {'FAIL' if failures else 'PASS'} ({len(tests) - failures}/{len(tests)})")
    sys.exit(bool(failures))
