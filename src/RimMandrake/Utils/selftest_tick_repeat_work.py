#!/usr/bin/env python3
"""Replay a recorded tick and page using only temporary stores.

--profile scales the same replay to the run and image counts in the slow-actions study.
"""

import cProfile
import contextlib
import datetime as dt
import io
import json
import os
from pathlib import Path
import pstats
import shutil
import sys
import tempfile
import time
import unittest
from unittest.mock import Mock, patch

from PIL import Image

import maturation_now as MN
import maturation_dispatch as MD
import detached_helper as DH
import fleet_mods
import game_lock
import model
import owner_queue

REPO = Path(MN.REPO)
MODS = ("GimmeSomeSlack", "ExplosiveKnockback")
NOW = dt.datetime(2026, 11, 27, 18, tzinfo=dt.timezone.utc)
RUNS = {
    "1794684282": MODS[0], "1794687332": MODS[0], "1794755734": MODS[0], "1794748869": MODS[1],
}


class Replay:
    def __init__(self, directory, full=False):
        self.root = Path(directory)
        self.state = self.root / "state"
        self.records = self.state / "detached"
        self.records.mkdir(parents=True)
        self.logs = self.root / "logs"
        self.logs.mkdir()
        self.ledger = self.root / "events.jsonl"
        notes = []
        # Project four actual ending notes into detached records. Capture only these rows in the replay.
        shard = REPO / "infrastructure/state/ledger/events/BENCH.jsonl"
        with shard.open(encoding="utf-8") as f:
            for line in f:
                if "DETACHED run " in line and " ended" in line and "Result:" in line:
                    note = json.loads(line)
                    if (note.get("role_unit") or "").rsplit("-", 1)[-1] in RUNS:
                        notes.append(note)
        assert len(notes) == len(RUNS)
        concepts = self.root / "design/concepts"
        names = list(MODS) + (["Replay%03d" % i for i in range(282)] if full else [])
        for i, name in enumerate(names):
            source = REPO / "design/concepts" / MODS[i % len(MODS)]
            dest = concepts / name
            (dest / "version").mkdir(parents=True)
            for file in ("version/VERSION.json", "version/stage_record.json"):
                shutil.copyfile(source / file, dest / file)
            with (source / "journal.md").open(encoding="utf-8") as f:
                (dest / "journal.md").write_text("".join(f.readline() for _ in range(18)), encoding="utf-8")
        events = []
        for i in range(716 if full else len(notes)):
            note = dict(notes[i % len(notes)])
            unit = note["role_unit"]
            at = int(unit.rsplit("-", 1)[-1])
            mod = RUNS[str(at)]
            if i >= len(notes):
                note["role_unit"] += "-replay-%d" % i
                note["text"] = note["text"].replace(unit, note["role_unit"], 1)
                mod = names[i % len(names)]
            unit = note["role_unit"]
            events.append(note)
            # Include a newer own note to test that an ending note still takes precedence.
            events.append(dict(note, text="A newer note from the same run.", ts="2026-11-27T17:00:00Z"))
            out = self.logs / unit
            out.write_text('{"total_cost_usd": 1.25, "result": "spent about $1.25"}\n', encoding="utf-8")
            rec = {"unit": unit, "item": note["id"], "status": "finished", "result": "success",
                   "at": at, "ended": at + 60, "out": str(out), "tokens": 100, "token_unit": "weighted_v2",
                   "env": {"RM_CONTROL_MOD": mod, "RM_CONTROL_STAGE": "offline_build"}}
            (self.records / (unit + ".json")).write_text(json.dumps(rec), encoding="utf-8")
        self.ledger.write_text("".join(json.dumps(e) + "\n" for e in events), encoding="utf-8")
        self.cfg = {"advancing": list(MODS), "max_live": 2}

    @contextlib.contextmanager
    def isolated(self):
        env = {key: str(self.root / name) for key, name in {
            "RIMFLOW_LEDGER": "events.jsonl", "RM_DISPATCHER_STATE": "state",
            "RM_MATURATION_DISPATCH_DIR": "dispatch", "RM_LIST_DISPATCH_DIR": "list",
            "RM_OWNER_HOLD_FILE": "holds.json", "RM_CONTROL_DB": "control.db",
            "RM_CONDUCTOR_LOG": "conductor.md", "RM_OWNER_VIEW_DIR": "owner",
            "RM_OPS_WATCH_DIR": "ops", "RM_RED_DISPATCH_DIR": "red", "TESTQ_QUEUE": "testq",
        }.items()}
        (self.root / "legacy/items").mkdir(parents=True, exist_ok=True)
        with patch.dict(os.environ, env), patch.object(model, "EVENTS", str(self.ledger)), \
                patch.object(fleet_mods, "STORE", str(self.root / "legacy")), \
                patch.object(owner_queue, "designer_turns", return_value={}), \
                patch.object(game_lock, "query_all", return_value=[]), \
                patch.object(MN.MNM, "STEVE_READING", str(self.root / "steve.json")), \
                patch.object(MN.MNM, "SHOWINGS", str(self.root / "showings")), \
                patch.object(MN, "bundle_page", return_value={}), patch.object(MN, "monitor_page", return_value={}), \
                patch.object(MN, "time_now", return_value=NOW.timestamp()), patch.dict(MN._READERS, clear=True):
            import control
            control.init(env["RM_CONTROL_DB"])
            yield self

    def tick(self):
        fx = {"autonomy": False, "code": lambda: {}, "convergence": lambda *a: None,
              "account": lambda: (True, ""), "releases": lambda: {}}
        return MD.tick(str(self.root), self.cfg, False, fx=fx, now=NOW.timestamp())

    def page(self):
        return MN.gather(str(self.root))


@contextlib.contextmanager
def replay(full=False):
    with tempfile.TemporaryDirectory(prefix="tick_repeat_work_") as directory:
        with Replay(directory, full).isolated() as state:
            yield state


class RepeatWork(unittest.TestCase):
    def test_t_last_words_once_per_mod_per_tick(self):
        with replay() as state, patch.object(MN, "last_words", wraps=MN.last_words) as words:
            tick = state.tick()
            self.assertEqual(set(tick["mods"]), set(MODS))
            self.assertEqual(words.call_count, len(MODS), "one last-words pass per mod, even with several runs")
            page = state.page()
            runs = [r for m in page["mods"] for r in m["runs"]]
            self.assertEqual(len(runs), len(RUNS))
            self.assertTrue(all(r["last"] not in (MN.UNM, r["notes"][-1]) for r in runs))

    def test_t_an_unchanged_image_is_not_encoded_again(self):
        Image.init()
        with replay() as state, patch.dict(Image.SAVE):
            encode = Mock(wraps=Image.SAVE["PNG"])
            Image.SAVE["PNG"] = encode
            data = state.page()
            out = state.root / "phone"
            MN.write_phone(data, out, NOW)
            self.assertEqual(encode.call_count, 3)
            self.assertTrue(all(f.endswith(".png") for f in os.listdir(out)), "the phone folder holds images only")
            image = out / (MODS[0] + ".png")
            original = image.read_bytes()
            encode.reset_mock()
            MN.write_phone(data, out, NOW + dt.timedelta(minutes=1))
            self.assertEqual(encode.call_count, 1, "only the overview's measurement time changed")
            self.assertEqual(image.read_bytes(), original)

            data["mods"][0]["jquestions"] = [{"n": 1, "text": "What changed?", "answered": False, "who": "conductor"}]
            encode.reset_mock()
            MN.write_phone(data, out, NOW + dt.timedelta(minutes=1))
            self.assertEqual(encode.call_count, 1, "only the mod with a new question changed")
            image.unlink()
            encode.reset_mock()
            MN.write_phone(data, out, NOW + dt.timedelta(minutes=1))
            self.assertEqual(encode.call_count, 1, "a missing image must be rebuilt")

    def test_t_tick_and_page_output_unchanged_by_the_cache(self):
        with replay() as state:
            initial_tick = state.tick()
            real_open = open
            reads = []

            def count_open(path, *args, **kwargs):
                if isinstance(path, (str, os.PathLike)) and Path(path).parent in (state.records, state.logs):
                    reads.append(Path(path))
                return real_open(path, *args, **kwargs)

            with patch("builtins.open", side_effect=count_open):
                warm_page = state.page()
                warm_tick = state.tick()
            self.assertEqual(initial_tick, warm_tick)
            self.assertEqual(reads, [], "the page and next tick should reuse the first tick's unchanged inputs")

            # Drop only the cache. Every source path and the clock stay the same.
            cache = state.state / "maturation-file-reads-v1.json"
            cache.unlink()
            self.assertEqual(state.tick(), warm_tick)
            cache.unlink()
            cold_page = state.page()
            self.assertEqual(MN.build(cold_page, NOW), MN.build(warm_page, NOW))
            self.assertEqual(MN.build_detail(cold_page, NOW), MN.build_detail(warm_page, NOW))
            first = MN.write_phone(warm_page, state.root / "phone", NOW)
            other = MN.write_phone(cold_page, state.root / "cold-phone", NOW)
            for (a, sa), (b, sb) in zip(first, other, strict=True):
                self.assertEqual(sa, sb)
                with Image.open(a) as left, Image.open(b) as right:
                    self.assertEqual(left.tobytes(), right.tobytes())

            changed = next(state.records.glob("*.json"))
            rec = json.loads(changed.read_text(encoding="utf-8"))
            rec["tokens"] = 101
            changed.write_text(json.dumps(rec), encoding="utf-8")
            Path(rec["out"]).write_text('{"total_cost_usd": 2.5}\n', encoding="utf-8")
            data = state.page()
            run = next(r for m in data["mods"] for r in m["runs"] if r["unit"] == rec["unit"])
            self.assertEqual((run["tokens"], run["usd"]), (101, 2.5))
            changed.unlink()
            self.assertFalse(any(r["unit"] == rec["unit"] for m in state.page()["mods"] for r in m["runs"]))


def profile(fn):
    profiler = cProfile.Profile()
    start = time.perf_counter()
    profiler.runcall(fn)
    print("wall %.3f s" % (time.perf_counter() - start))
    stats = pstats.Stats(profiler).strip_dirs().sort_stats("cumulative")
    stats.print_stats(r"last_words|\{built-in method io.open\}|\{built-in method _io.open\}|"
                      r"\{built-in method builtins.open\}|PngImagePlugin.*\(_save\)")


def profile_replay():
    with replay(full=True) as state:
        def page(now):
            data = state.page()
            MN.build(data, now)
            MN.build_detail(data, now)
            MN.write_phone(data, state.root / "phone", now)

        state.tick()
        page(NOW)
        print("Tick")
        profile(state.tick)
        print("Page one minute later")
        profile(lambda: page(NOW + dt.timedelta(minutes=1)))


if __name__ == "__main__":
    if sys.argv[1:] == ["--profile"]:
        profile_replay()
    else:
        unittest.main(verbosity=2)
