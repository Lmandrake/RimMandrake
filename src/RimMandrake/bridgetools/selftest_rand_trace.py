#!/usr/bin/env python3
"""selftest_rand_trace.py - the verdict over jawa/rand_trace reads (src/RimMandrake/Utils/rand_trace_verdict.py), on made-up traces.

Item RIMMANDRAKE_FIND_RAND_DRAWS_PARTING_RUNS_EVEN_STEP. Each case is one shape the verdict must tell apart: runs that repeat,
runs that part on a named draw, and each way the instrument can be blind (an unseen tick, an unseen gap, a cut read, a window
that never opened, too few runs, a parting with no caller), and the fix experiment (isolated draws at a pushed state, runs
that isolated different methods). Exit 0 when every case gives its expected answer."""
import copy
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Utils"))
import rand_trace_verdict as V  # noqa: E402

ANCHOR_ITER = 1000
ANCHOR = str((ANCHOR_ITER << 32) | 12345)


def run(extra=None, arm="step"):
    """A whole, seeing trace: 2 pre draws, ticks 3..5 with 4 draws each, 1 frame draw after tick 4."""
    rows = [{"t": 2, "ph": "pre", "c": "UI.Draw", "n": 2}]
    ticks, it = [], ANCHOR_ITER + 2
    for t in (3, 4, 5):
        rows.append({"t": t, "ph": "tick", "c": "Pawn.TickInterval", "n": 4})
        ticks.append({"t": t, "i0": it, "i1": it + 4, "hooked": 4, "reseeds": 0, "seen": True})
        it += 4
        if t == 4:
            rows.append({"t": 4, "ph": "frame", "c": "Sound.TryPlay", "n": 1})
            it += 1
    tr = {"success": True, "anchorTick": 2, "anchorState": ANCHOR, "ticks": ticks, "rows": rows, "rowsCut": False, "faults": 0}
    r = {"arm": arm, "trace": tr}
    if extra:
        extra(tr)
    return r


def extra_sound_draw(tr):
    """+3 draws in tick 4 from the sound grain (the run that parts), stream and hook both see them."""
    tr["rows"].append({"t": 4, "ph": "tick", "c": "Verse.Sound.SubSoundDef.RandomizedResolvedGrain", "n": 3})
    for x in tr["ticks"]:
        if x["t"] == 4:
            x["i1"] += 3; x["hooked"] += 3
        elif x["t"] == 5:
            x["i0"] += 3; x["i1"] += 3


def case(name, data, want_ok, want_text):
    ok, lines, _p = V.verdict(data)
    text = " ".join(lines)
    good = ok == want_ok and want_text in text
    print("%s %s: %s" % ("PASS" if good else "FAIL", name, text))
    return good


def main():
    res = []
    res.append(case("repeat", {"runs": [run(), run(), run()]}, True, "same count"))
    res.append(case("parts_named", {"runs": [run(), run(), run(extra_sound_draw)]}, True, "1 of 2 STEP runs part"))
    ok, text = V.report({"runs": [run(), run(), run(extra_sound_draw)]})
    res.append(ok and "RandomizedResolvedGrain" in text and "first parting tick 4" in text)
    print("%s report_names_the_parting_row" % ("PASS" if res[-1] else "FAIL"))
    res.append(case("play_runs_do_not_count", {"runs": [run(), run(), run(arm="play1"), run(arm="play1")]}, False, "2 STEP runs, 3 needed"))

    def unseen(tr):
        tr["ticks"][1]["i1"] += 2; tr["ticks"][1]["seen"] = False
        tr["ticks"][2]["i0"] += 2; tr["ticks"][2]["i1"] += 2
    res.append(case("inlined_draw_unseen_tick", {"runs": [run(), run(), run(unseen)]}, False, "more draws than the hook saw"))

    def gap(tr):
        for x in tr["ticks"][2:]:
            x["i0"] += 1; x["i1"] += 1
    res.append(case("unseen_frame_gap", {"runs": [run(), run(gap), run()]}, False, "the gap after tick 4"))

    def pre_gap(tr):
        for x in tr["ticks"]:
            x["i0"] += 5; x["i1"] += 5
    res.append(case("unseen_pre_gap", {"runs": [run(pre_gap), run(), run()]}, False, "the gap after tick 2"))
    res.append(case("rows_cut", {"runs": [run(), run(lambda tr: tr.update(rowsCut=True, rowCount=99)), run()]}, False, "rows were cut"))
    res.append(case("window_never_opened", {"runs": [run(), run(lambda tr: tr.update(anchorTick=-1)), run()]}, False, "never opened"))
    res.append(case("no_ticks", {"runs": [run(), run(lambda tr: tr.update(ticks=[])), run()]}, False, "no tick was traced"))
    res.append(case("faulted", {"runs": [run(), run(lambda tr: tr.update(faults=2, lastFault="x")), run()]}, False, "faulted"))

    def other_anchor(tr):
        tr["anchorState"] = str(((ANCHOR_ITER) << 32) | 999)
    res.append(case("different_start", {"runs": [run(), run(other_anchor), run()]}, False, "different random states"))

    def unnamed(tr):
        extra_sound_draw(tr)
        for r in tr["rows"]:
            if r["c"].startswith("Verse.Sound"):
                r["c"] = "?"
    res.append(case("parting_with_no_caller", {"runs": [run(), run(unnamed), run()]}, False, "no caller named"))
    res.append(case("empty_file_shape", {}, False, "0 STEP runs"))
    res.append(case("repeat_names_iterations", {"runs": [run(), run(), run()]}, True, "iterations equal on every traced tick"))

    def pushed_fish(n):
        def f(tr):
            tr["rows"].append({"t": 4, "ph": "tick+pushed", "c": "Verse.FishShadowComponent.SpawnFishFleck", "n": n})
        return f
    # isolated draws (at a pushed state) differ between runs and leave the global stream still: the runs repeat
    res.append(case("pushed_rows_do_not_part", {"runs": [run(pushed_fish(4)), run(), run(pushed_fish(6))]}, True, "same count"))

    def iso(names):
        return lambda tr: tr.update(isolate=names)
    res.append(case("mixed_isolate_not_compared", {"runs": [run(iso(["A:B"])), run(), run(iso(["A:B"]))]}, False, "isolated different methods"))
    res.append(case("same_isolate_compared", {"runs": [run(iso(["A:B"])), run(iso(["A:B"])), run(iso(["A:B"]))]}, True, "isolating A:B"))
    n_ok = sum(1 for x in res if x)
    print("RESULT %s (%d/%d)" % ("PASS" if n_ok == len(res) else "FAIL", n_ok, len(res)))
    return 0 if n_ok == len(res) else 1


if __name__ == "__main__":
    sys.exit(main())
