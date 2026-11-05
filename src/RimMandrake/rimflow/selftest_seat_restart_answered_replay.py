#!/usr/bin/env python3
"""SEAT_WAKE_FIX_ANSWERED_MESSAGES_REPLAYED: the wake listed messages the old window had answered, from before the goodbye.

The source was undelivered(), which paired queue operations by commandUuid alone. Claude Code writes an enqueue with
commandUuid None and a remove WITH a uuid and the prompt's content (MEASURED 2026-11-05 in a5d80dfe: 27 enqueues uuid
None, 16 dequeues uuid None, 11 removes with uuid and content), so every removed (delivered) prompt stayed "undelivered"
and was replayed at wake as unanswered. These fixtures copy that shape.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import selftest_seat_restart as T  # noqa: E402
import seat_restart as SR  # noqa: E402

check = T.check


def _enq(iso, text):
    return {"type": "queue-operation", "operation": "enqueue", "timestamp": iso, "content": text}


def _rm(iso, text, uid):
    return {"type": "queue-operation", "operation": "remove", "timestamp": iso, "content": text, "commandUuid": uid}


def _deq(iso):
    return {"type": "queue-operation", "operation": "dequeue", "timestamp": iso}


def _instance():
    """01:55-01:59 in the incident: prompts queued mid-turn and removed (delivered), one dequeued, all answered."""
    return [T._hu("1970-01-12T13:30:00Z", "look at these screenshots"),
            T._ha("1970-01-12T13:30:05Z", "tool_use"),
            _enq("1970-01-12T13:30:10Z", "the whole planet turns off"),
            _rm("1970-01-12T13:30:12Z", "the whole planet turns off", "u-1"),
            _enq("1970-01-12T13:30:20Z", "a third screenshot"),
            _rm("1970-01-12T13:30:21Z", "a third screenshot", "u-2"),
            _enq("1970-01-12T13:31:00Z", "is FlowWorks designed now?"),
            T._ha("1970-01-12T13:31:05Z", "end_turn"),
            _deq("1970-01-12T13:31:06Z"),
            T._hu("1970-01-12T13:31:06Z", "is FlowWorks designed now?"),
            _enq("1970-01-12T13:31:30Z", "my bad, it is the layers"),
            _rm("1970-01-12T13:31:31Z", "my bad, it is the layers", "u-3"),
            T._ha("1970-01-12T13:32:00Z", "end_turn"),
            T._hu(T.GB, "goodbye"),
            T._ha("1970-01-12T13:45:10Z", "end_turn")]


def test_instance_delivered_prompts_are_not_undelivered():
    p, _ = T._bt("sid-replay", _instance())
    got = [SR._text(r) for r in SR.undelivered(p, peers=[])]
    check(got == [], "R1 removed and dequeued prompts (enqueue uuid None) are delivered, not undelivered (%s)" % got)
    owed = SR.unanswered(p, 0, peers=[])
    check(owed == [], "R2 the old window owes nothing: every prompt was answered (%s)" % [SR._text(r) for r in owed or []])


def test_still_queued_prompt_is_still_found():
    recs = _instance()[:-1] + [_enq("1970-01-12T13:45:05Z", "wait, one more thing")]
    p, _ = T._bt("sid-replay2", recs)
    got = [SR._text(r) for r in SR.undelivered(p, peers=[])]
    check(got == ["wait, one more thing"], "R3 a prompt still in the queue is still undelivered (%s)" % got)


def test_remove_pairs_by_content_not_oldest():
    recs = [_enq("1970-01-12T13:30:00Z", "first"), _enq("1970-01-12T13:30:01Z", "second"),
            _rm("1970-01-12T13:30:02Z", "second", "u-9")]
    p, _ = T._bt("sid-replay3", recs)
    got = [SR._text(r) for r in SR.undelivered(p, peers=[])]
    check(got == ["first"], "R4 a remove ends the enqueue with its content, not the oldest (%s)" % got)


def main():
    SR.UNFILED = lambda t: None
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
            except Exception as e:  # noqa: BLE001
                import traceback
                traceback.print_exc()
                check(False, "%s raised %s: %s" % (name, type(e).__name__, e))
    print("\n%s: %d failure(s)" % ("FAIL" if T.FAILS else "PASS", len(T.FAILS)))
    return 1 if T.FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
