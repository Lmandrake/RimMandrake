#!/usr/bin/env python3
"""Selftest for rimflow/render.py.

⭐ THE REFUSAL AND THE ORDER ARE THE PRODUCT.

Two properties are worth more than everything else this file checks:

1. **The rendered order IS `priority.rank()`** — not a re-implementation that agrees
   today. A view that sorts items itself will disagree with `rimflow next` the first
   time either changes, and a queue file that disagrees with the command is the exact
   failure the ledger was built to end.
2. **`--overwrite-queues` refuses against a thinner ledger.** Six files, 142 items,
   827 KB of hand-written prose, and one command away from being replaced with
   whatever an unverified importer produced. The refusal has to be tested, because a
   guard that does not actually guard is worse than none: it is believed.

⚠️ EVERY TEMPORARY FILE IS UNDER THE REPO, NEVER `/tmp`. They are different
filesystems here — 9p vs tmpfs — and `selftest_concurrency.py` already reported
3600/3600 green from `/tmp` while the real disk was losing 83% of its writes. A test
on the wrong disk measures nothing.

    python3 src/RimMandrake/rimflow/selftest_render.py
"""
import io
import contextlib
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from rimflow import model, priority, render                        # noqa: E402

PASS, FAIL = [], []
TMP = None


def case(name, fn):
    try:
        fresh()
        fn()
        PASS.append(name)
        print("ok    %s" % name)
    except AssertionError as e:
        FAIL.append(name)
        print("FAIL  %s\n        %s" % (name, e))
    except Exception as e:
        FAIL.append(name)
        print("FAIL  %s\n        unexpected %s: %s" % (name, type(e).__name__, e))


# --------------------------------------------------------------------------
# A throwaway world. Never the real ledger, never the real queue/.
# --------------------------------------------------------------------------
def fresh():
    for d in ("ledger", "items", "queue", "derived"):
        shutil.rmtree(os.path.join(TMP, d), ignore_errors=True)
        os.makedirs(os.path.join(TMP, d), exist_ok=True)
    model.EVENTS = os.path.join(TMP, "ledger", "events.jsonl")
    model.ITEMS = os.path.join(TMP, "items")
    render.QUEUE = os.path.join(TMP, "queue")
    render.DERIVED = os.path.join(TMP, "derived")
    render.PREVIEW = os.path.join(render.DERIVED, "queue_preview")
    render.BOARD = os.path.join(render.DERIVED, "board.json")
    render.item_index(refresh=True)


def emit(**kw):
    kw.setdefault("ts", "2026-08-20T00:00:%02dZ" % (len(model.read()) % 60))
    return model.append(kw)


def prose(iid, spec="build the thing.", extra=""):
    with open(os.path.join(model.ITEMS, "%s.md" % iid), "w", encoding="utf-8") as fh:
        fh.write("## spec\n%s\n%s\n## verify\nrun it\n\n## criteria\nit ran\n"
                 % (spec, extra))
    render.item_index(refresh=True)


def file_item(iid, for_="BUILD", row=None, needs=None, title="t", with_prose=True):
    d = {"seat": "DECIDE", "event": "file", "id": iid, "title": title, "kind": "task"}
    d["for"] = for_
    if row is not None:
        d["row"] = str(row)
    if needs:
        d["needs"] = needs
    if with_prose:
        prose(iid)
    emit(**d)
    emit(seat=for_, event="claim", id=iid)


def view(seat="BUILD"):
    return open(os.path.join(render.PREVIEW, "%s.md" % seat), encoding="utf-8").read()


def headings(text, section=None):
    """-> [ID] under one `# SECTION` header, or in the whole file.

    Sections are h1 and items are h2 precisely so this distinction exists — see the
    note in `render.queue_view`.
    """
    out, live = [], section is None
    for ln in text.splitlines():
        if ln.startswith("## "):
            if live:
                out.append(ln[3:].split()[0])
        elif ln.startswith("# ") and section is not None:
            live = ln[2:].startswith(section)
    return out


def quiet(fn):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
        rc = fn()
    return rc, buf.getvalue()


# --------------------------------------------------------------------------
def t_order_is_priority_rank_not_a_copy_of_it():
    """The one property the whole view exists for."""
    file_item("THIRD_BY_ROW_1", row=9)
    file_item("FIRST_BY_ROW_1", row=1)
    file_item("SECOND_BY_ROW_1", row=4)
    file_item("NO_ROW_AT_ALL_1")             # unrowed sorts LAST, not first
    render.render(quiet=True)
    world, _ = render.build()
    want = [i.id for i in priority.rank(world, "BUILD")]
    got = headings(view(), "NEXT")
    assert want == got, (
        "the file and `rimflow next` disagree.\n  rank(): %s\n  file  : %s" % (want, got))
    assert got[0] == "FIRST_BY_ROW_1" and got[-1] == "NO_ROW_AT_ALL_1", got


def t_this_deployment_wins_the_tie():
    file_item("ORDINARY_ROW_ONE_1", row=1)
    prose("URGENT_LIVE_WINDOW_1")
    # ⚠️ `id` is the item the discovery came FROM. model.validate() demands one on
    # every non-ITEMLESS verb, and _apply refuses an id that was never filed — so a
    # spawn off a bare FINDING name, which is what the plan's §4 example does, cannot
    # be emitted at all. Reported to BUILD, not fixed here.
    emit(seat="CHECK", event="spawn", id="ORDINARY_ROW_ONE_1",
         **{"from": "ORDINARY_ROW_ONE_1", "for": "BUILD",
            "name": "URGENT_LIVE_WINDOW_1", "this_deployment": True})
    emit(seat="BUILD", event="claim", id="URGENT_LIVE_WINDOW_1")
    render.render(quiet=True)
    got = headings(view(), "NEXT")
    assert got[0] == "URGENT_LIVE_WINDOW_1", (
        "the live window is closing and the item flagged for it is not first: %s" % got)


def t_blocked_item_appears_with_its_reason():
    file_item("WAITING_ON_PILLOW_1", row=2)
    emit(seat="BUILD", event="block", id="WAITING_ON_PILLOW_1",
         reason="Pillow is not installed", on="INSTALL_PILLOW_FIRST_1")
    file_item("INSTALL_PILLOW_FIRST_1", row=3)
    render.render(quiet=True)
    txt = view()
    assert "WAITING_ON_PILLOW_1" not in headings(txt, "NEXT"), (
        "a blocked item was offered as next")
    assert "WAITING_ON_PILLOW_1" in headings(txt, "BLOCKED"), txt
    assert "Pillow is not installed" in txt and "INSTALL_PILLOW_FIRST_1" in txt, (
        "the reason and the item it is blocked ON must both be visible, or the "
        "reader has to open the ledger to find out what to do")


def t_needs_a_window_is_not_blocked():
    """`needs` and `blocked` are different axes, and the view must not merge them."""
    file_item("NEEDS_THE_GAME_UP_1", row=1, needs="game-up")
    render.render(quiet=True)
    txt = view()
    assert "NEEDS_THE_GAME_UP_1" in headings(txt, "WAITING ON A WINDOW"), txt
    assert "NEEDS_THE_GAME_UP_1" not in headings(txt, "BLOCKED"), (
        "an item waiting for the game read as BLOCKED — that conflation is exactly "
        "what made the old board unable to report either")


def t_view_carries_one_line_not_the_prose():
    long_spec = "line one of the spec, and it is quite long. " * 6
    file_item("HAS_LOTS_OF_PROSE_1", row=1, with_prose=False)
    prose("HAS_LOTS_OF_PROSE_1", spec=long_spec,
          extra="\nA SECOND PARAGRAPH THAT MUST NOT BE COPIED.\n")
    render.render(quiet=True)
    txt = view()
    assert "A SECOND PARAGRAPH THAT MUST NOT BE COPIED." not in txt, (
        "the prose was copied into the generated view — that is the drift the "
        "ledger exists to end")
    line = [l for l in txt.splitlines() if l.startswith("summary:")][0]
    assert len(line) < 140 and line.endswith("…"), line
    assert "items/HAS_LOTS_OF_PROSE_1.md" in txt, "the view must point at the prose"


def t_generated_marker_and_regen_command():
    file_item("ANY_ITEM_AT_ALL_1", row=1)
    render.render(quiet=True)
    txt = view()
    assert txt.startswith(render.MARKER), txt[:120]
    assert "DO NOT EDIT" in txt and render.REGEN in txt, (
        "a generated file that does not say how to regenerate it gets hand-edited")


# ---- the refusal ---------------------------------------------------------
def t_overwrite_refuses_against_an_empty_ledger():
    """The guard that stands between one command and 827 KB of hand-written prose."""
    real = os.path.join(render.QUEUE, "BUILD.md")
    with open(real, "w", encoding="utf-8") as fh:
        fh.write("## HAND_WRITTEN_ITEM_1 t\nstate: ready\n\n"
                 "## ANOTHER_HAND_ITEM_1 t\nstate: ready\n\n"
                 "## THIRD_HAND_ITEM_1 t\nstate: ready\n")
    before = open(real, encoding="utf-8").read()
    s = render.render(overwrite_queues=True, quiet=True)
    assert s["refused"], "an EMPTY ledger was allowed to overwrite three filed items"
    assert not s["overwrote"]
    assert open(real, encoding="utf-8").read() == before, "the real queue was written"
    msg = s["refused"]
    assert "0 item" in msg and "3" in msg, (
        "the refusal must print BOTH counts; a refusal without numbers cannot be "
        "acted on. Got: %s" % msg)


def t_overwrite_allowed_once_the_ledger_is_at_least_as_full():
    real = os.path.join(render.QUEUE, "BUILD.md")
    with open(real, "w", encoding="utf-8") as fh:
        fh.write("## ONE_HAND_ITEM_1 t\nstate: ready\n")
    file_item("ONE_HAND_ITEM_1", row=1)
    file_item("AND_ONE_MORE_HERE_1", row=2)
    s = render.render(overwrite_queues=True, quiet=True)
    assert not s["refused"] and s["overwrote"], s["refused"]
    txt = open(real, encoding="utf-8").read()
    assert txt.startswith(render.MARKER) and "ONE_HAND_ITEM_1" in txt, txt[:200]


# ---- reindex -------------------------------------------------------------
def t_reindex_verify_is_identical_after_a_clean_render():
    file_item("STABLE_ITEM_HERE_1", row=1)
    file_item("SECOND_STABLE_ITEM_1", row=2)
    emit(seat="BUILD", event="block", id="SECOND_STABLE_ITEM_1", reason="waiting")
    render.render(quiet=True)
    rc, out = quiet(lambda: render.reindex(verify=True))
    assert rc == 0, out
    assert "0 differ, 0 missing" in out, out
    assert "identical" in out and " 0 identical" not in out, (
        "verify compared nothing at all, which would pass forever: %s" % out)


def t_reindex_verify_sees_a_hand_edit():
    """A generated file somebody edited must be VISIBLE, not silently re-flattened."""
    file_item("STABLE_ITEM_HERE_1", row=1)
    render.render(quiet=True)
    with open(render.BOARD, "a", encoding="utf-8") as fh:
        fh.write("\n<- somebody hand-edited this\n")
    rc, out = quiet(lambda: render.reindex(verify=True))
    assert rc == 1 and "DIFFERS  board.json" in out, out


def t_render_is_deterministic():
    """No wall clock anywhere, or `--verify` is theatre."""
    file_item("DETERMINISTIC_ITEM_1", row=1)
    render.render(quiet=True)
    a = open(render.BOARD, "rb").read(), view().encode()
    render.render(quiet=True)
    b = open(render.BOARD, "rb").read(), view().encode()
    assert a == b, "two renders of one ledger differed — something reads the clock"
    assert '"as_of": "2026-' in a[0].decode(), (
        "as_of must be the ledger's last event, not now()")


# ---- the board -----------------------------------------------------------
def t_board_reports_state_blockers_velocity_and_seats():
    file_item("CLOSED_TODAY_ITEM_1", row=1)
    emit(seat="BUILD", event="start", id="CLOSED_TODAY_ITEM_1")
    emit(seat="BUILD", event="close", id="CLOSED_TODAY_ITEM_1", sha="deadbee",
         ts="2026-08-19T10:00:00Z")
    file_item("BLOCKED_ON_A_HUMAN_1", row=2)
    emit(seat="BUILD", event="block", id="BLOCKED_ON_A_HUMAN_1",
         reason="needs a human answer")
    file_item("BUSY_RIGHT_NOW_ITEM_1", row=3)
    emit(seat="BUILD", event="start", id="BUSY_RIGHT_NOW_ITEM_1")
    emit(seat="BUILD", event="seat", state="busy", item="BUSY_RIGHT_NOW_ITEM_1")
    emit(seat="CHECK", event="bridge", state="taken")
    emit(seat="OWNER", event="game", state="UP")
    render.render(quiet=True)
    b = json.load(open(render.BOARD, encoding="utf-8"))
    assert b["game"] == "UP" and b["bridge_holder"] == "CHECK", b["game"]
    assert b["velocity"]["closed"] == 1 and b["velocity"]["days"][0]["d"] == "2026-08-19"
    assert b["blockers"]["on_human"] == 1, b["blockers"]
    assert b["blocked"][0]["reason"] == "needs a human answer", b["blocked"]
    seat = b["seats"]["BUILD"]
    assert seat["doing"] == ["BUSY_RIGHT_NOW_ITEM_1"], seat
    assert seat["says"]["state"] == "busy", seat
    assert seat["counts"]["done"] == 1, seat


def t_board_keeps_status_matrix_shape():
    """`status_server.py` reads rows[].cells[COL].{done,total,state,mix}. Keep it."""
    file_item("SHAPE_CHECK_ITEM_1", row=1)
    render.render(quiet=True)
    b = json.load(open(render.BOARD, encoding="utf-8"))
    row = [r for r in b["rows"] if r["name"].startswith("1")]
    assert row, [r["name"] for r in b["rows"]]
    cell = row[0]["cells"]["BUILD"]
    assert set(cell) == {"done", "total", "state", "mix"}, cell
    assert set(cell["mix"]) == {"closed", "done", "doing", "blocked", "ready"}, cell
    assert set(b["velocity"]) >= {"days", "per_day", "closed", "eta_days"}
    assert set(b["blockers"]) == {"on_human", "classes"}


def t_replay_refusals_are_surfaced_not_swallowed():
    file_item("GOOD_ITEM_HERE_1", row=1)
    # A refusal that is ALREADY in an append-only file: CHECK may not set game state.
    with open(model.EVENTS, "a", encoding="utf-8") as fh:
        fh.write(json.dumps({"ts": "2026-08-20T00:00:00Z", "seat": "CHECK",
                             "event": "game", "state": "UP"}) + "\n")
    render.render(quiet=True)
    b = json.load(open(render.BOARD, encoding="utf-8"))
    assert len(b["errors"]) == 1 and "OWNER" in b["errors"][0]["message"], b["errors"]


def t_diff_summary_names_what_only_the_queue_has():
    with open(os.path.join(render.QUEUE, "BUILD.md"), "w", encoding="utf-8") as fh:
        fh.write("## ONLY_IN_THE_QUEUE_1 t\nstate: ready\n")
    file_item("ONLY_IN_THE_LEDGER_1", row=1)
    s = render.render(quiet=True)
    d = [x for x in s["diffs"] if x["seat"] == "BUILD"][0]
    assert d["in_queue_only"] == ["ONLY_IN_THE_QUEUE_1"], d
    assert d["in_ledger_only"] == ["ONLY_IN_THE_LEDGER_1"], d


def t_prose_headings_are_not_counted_as_items():
    """`## 🔴 OWNER RULINGS…` is a section, not an item, and must not gate the guard."""
    with open(os.path.join(render.QUEUE, "BUILD.md"), "w", encoding="utf-8") as fh:
        fh.write("## 🔴 OWNER RULINGS, 2026-08-19 — the queue triage\nprose\n\n"
                 "## REAL_ITEM_HERE_1 t\nstate: ready\n")
    total, per = render.queue_census(render.QUEUE)
    assert total == 1 and per["BUILD.md"] == 1, (total, per)


CASES = [(k[2:], v) for k, v in sorted(globals().items()) if k.startswith("t_")]

if __name__ == "__main__":
    # ⚠️ UNDER THE REPO. `tempfile.mkdtemp()` is /tmp, which is a different
    # filesystem with different atomicity and different speed.
    TMP = os.path.join(model.STATE, "derived", ".selftest")
    shutil.rmtree(TMP, ignore_errors=True)
    os.makedirs(TMP, exist_ok=True)
    real = (model.EVENTS, model.ITEMS, render.QUEUE, render.DERIVED,
            render.PREVIEW, render.BOARD)
    try:
        for name, fn in CASES:
            case(name, fn)
    finally:
        (model.EVENTS, model.ITEMS, render.QUEUE, render.DERIVED,
         render.PREVIEW, render.BOARD) = real
        shutil.rmtree(TMP, ignore_errors=True)
    print("\n%d/%d passed" % (len(PASS), len(PASS) + len(FAIL)))
    sys.exit(1 if FAIL else 0)
