#!/usr/bin/env python3
"""Plant a fault in the scene library and see its selftest go red. Page: design/specs/2026-11-23-scene-library/boundary.md.

    python3 scene_library_mutants.py            every plant; exit 0 when the clean copy is green and each plant turns red the
                                                test that is named beside it
The plants run on a copy of scene*.py; nothing in the tree is changed."""
import os
import re
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
# (name, file, old, new, the test that must go red). The first four are the ticket's own.
PLANTS = [
    ("an open that reports a build it read from the repo", "scene.py", '"source_hash": comp.get("srcHash")', '"source_hash": self.W.companion_hash()', "test_open_receipt_build_comes_from_game"),
    ("a run that counts an unreadable value as false", "scene.py", "            if unread:\n", "            if False:\n", "test_run_unreadable_value_stops_as_unknown"),
    ("a second session in a marked process with no stamp", "scene.py", '        self.stamps = d["stamps"]\n        d["session"] = {"id": self.id', '        self.stamps = d["stamps"] = []\n        d["session"] = {"id": self.id', "test_raw_undeclared_tool_marks_the_process_and_a_new_session_carries_it"),
    ("a page that names an argument the function does not take", "scene_contracts/run.md", "| `speed` |", "| `pace` |", "test_help_prints_ten_names_and_each_built_page_matches_its_signature"),
    ("an unreadable condition reads as not hit", "scene_core.py", 'if self.why == "unknown":', "if False:", "test_run_unreadable_value_stops_as_unknown"),
    ("a gone value reads as 0", "scene_core.py", 'if self.state != "ok":\n            raise', 'if self.state != "ok":\n            return 0\n            raise', "test_run_unreadable_value_stops_as_unknown"),
    ("the run is started again after a lost reply", "scene.py", "        row = self._ask(request)\n        if row is None:\n            raise Fault(\"REPLY_LOST\", done=[\"the start", "        row = self.hand.start(request + \"b\", plan, limit, speed)\n        if row is None:\n            raise Fault(\"REPLY_LOST\", done=[\"the start", "test_run_lost_reply_is_recovered_by_request_id"),
    ("the request id is made after the call", "scene_hands.py", 'driver=self.driver, request=request, until=', 'driver=self.driver, request=request + "x", until=', "test_run_lost_reply_is_recovered_by_request_id"),
    ("run_until discards the stop condition", "scene_hands.py", 'request=request, until=json.dumps(plan["until"], sort_keys=True)',
     'request=request, until=json.dumps(C.to_tree(C.game.tick >= 2000000000))', "test_run_true_at_start_plays_no_tick"),
    ("scene_slice discards the stop condition", "scene_hands.py", 'pawn=self.pawn, until=json.dumps(plan["until"], sort_keys=True)',
     'pawn=self.pawn, until=json.dumps(C.to_tree(C.game.tick >= 2000000000))', "test_run_true_at_start_plays_no_tick"),
    ("a raw call is marked after it was made", "scene.py", "        if changing and EXPLORED not in self.stamps:", "        if changing and False:", "test_raw_undeclared_tool_marks_the_process_and_a_new_session_carries_it"),
    ("a raw call goes on with a mark that did not hold", "scene.py", "        if got != json.loads(want):", "        if False:", "test_raw_call_without_a_mark_is_not_made"),
    ("a child process inherits the mark", "scene.py", 'return d if d["pid"] == self.pid else', "return d if True else", "test_raw_undeclared_tool_marks_the_process_and_a_new_session_carries_it"),
    ("jawa/static_call may be declared read-only", "scene.py", 'if descriptor.get("name") == "jawa/static_call":', "if False:", "test_raw_undeclared_tool_is_treated_as_changing"),
    ("an undeclared tool is a read", "scene.py", 'return bool(re.match(r"READ[ -]ONLY\\b"', 'return bool(re.match(r""', "test_raw_undeclared_tool_is_treated_as_changing"),
    ("a lock that could not be read is free", "scene.py", '        if r["code"] != 0:\n', "        if False:\n", "test_lock_that_could_not_be_read_is_a_fault"),
    ("an unreadable mark reads as no mark", "scene.py", '        if r.get("success") is not True:\n            raise Fault("COULD_NOT_LOOK", detail="the process mark could', '        if r.get("success") is not True:\n            return {"pid": self.pid, "stamps": [], "session": None}\n            raise Fault("COULD_NOT_LOOK", detail="the process mark could', "test_lock_that_could_not_be_read_is_a_fault"),
    ("only the first page of the saves is read", "scene.py", "            if not at2 or at2 <= at:", "            if True:", "test_open_refuses_fixture_missing"),
    ("a refusal keeps the lock", "scene.py", "        if self._locked:\n            step(\"lock\", unlock)", "        if False:\n            step(\"lock\", unlock)", "test_open_refuses_mod_not_loaded"),
    ("the calm stays on after a refusal", "scene.py", "        self._calmed = True                     # owed", "        self._calmed = False                    # owed", "test_open_phase_report_names_refusing_phase_and_what_was_put_back"),
    ("a wrong build opens", "scene.py", 'if j["verdict"] in ("WRONG_BUILD", "NOT_LOADED", "FOREIGN_COPY"):', 'if j["verdict"] in ("NOT_LOADED", "FOREIGN_COPY"):', "test_open_refuses_wrong_build"),
    ("a canonical save in other letters loads", "scene.py", "        low = where.lower()\n", "        low = where\n", "test_open_refuses_canonical_save"),
    ("a run starts on a running game", "scene.py", '        if st.get("paused") is not True:\n            raise Refused("GAME_RUNNING"', '        if False:\n            raise Refused("GAME_RUNNING"', "test_run_refuses_game_running"),
    ("a run starts over a live run", "scene.py", '        if live:\n            raise Refused("RUN_ACTIVE"', '        if False:\n            raise Refused("RUN_ACTIVE"', "test_run_refuses_run_active"),
    ("True is a limit", "scene.py", "if isinstance(limit, bool) or not isinstance(limit, int)", "if not isinstance(limit, int)", "test_run_refuses_no_limit"),
    ("optional counts an unreadable value as false", "scene_cond.py", "        if opt:\n", "        if False:\n", "test_run_refuses_unrecorded_value"),
    ("a method is in the path grammar", "scene_cond.py", r'[A-Za-z_]\w*)(?:\[', r'[A-Za-z_]\w*(?:\(\))?)(?:\[', "test_run_refuses_bad_path"),
    ("a gap in the trace passes", "scene_hands.py", "    if None in ns or ns !=", "    if None in ns and ns !=", "test_trace_that_is_not_whole"),
    ("the game's track name is not the script's", "scene_hands.py", 'return self.names.get(track) or (track[6:]', 'return track if track else (track[6:]', "test_run_dead_member_stays_in_group_as_gone"),
    ("a dropped row passes", "scene_hands.py", 'or c.get("dropped") != 0:', "or False:", "test_trace_that_is_not_whole"),
    ("the second reading of the tick is left out", "scene.py", 'if over is None and after.get("tick") != t2:', "if False:", "test_game_that_ran_on"),
    ("the second reading of the pause is left out", "scene.py", 'if over is None and after.get("paused") is not True:', "if False:", "test_game_that_ran_on"),
    ("a dirty tree is accepted", "scene.py", "    if out.strip():\n        rows = out", "    if False:\n        rows = out", "test_accept_refuses_a_dirty_tree_and_an_older_layer"),
    ("an older layer behind a module is accepted", "scene.py", "                    todo.append(os.path.abspath(cand))\n", "                    pass\n", "test_accept_refuses_a_dirty_tree_and_an_older_layer"),
    ("git that could not run is a clean tree", "scene.py", '        rc2, out2 = git("rev-parse", "--is-inside-work-tree")\n        if rc2 != 0:', '        rc2, out2 = git("rev-parse", "--is-inside-work-tree")\n        if False:', "test_lock_that_could_not_be_read_is_a_fault"),
    ("explore leaves no stamp", "scene.py", '({EXPLORED} if LAUNCH["mode"] == "explore" else set())', "set()", "test_explore_run_is_explored"),
    ("an error in the script keeps the session open", "scene.py", "    def __exit__(self, et, ev, tb):\n        try:\n            self.close()", "    def __exit__(self, et, ev, tb):\n        try:\n            et or self.close()", "test_close_puts_back_also_after_an_error"),
    ("what was not put back is not said", "scene.py", "        if bad:\n            raise Fault(\"CLOSE_INCOMPLETE\"", "        if False:\n            raise Fault(\"CLOSE_INCOMPLETE\"", "test_close_puts_back_also_after_an_error"),
    ("an attach that lets the new driver go on", "scene.py", "        if self._taken:\n            raise Refused(\"TAKEN_OVER\"", "        if False:\n            raise Refused(\"TAKEN_OVER\"", "test_attach_then_run_is_refused"),
    ("an attach takes a live driver's session", "scene.py", "        if alive is not False and not (old is None", "        if False and not (old is None", "test_attach_refuses_driver_alive"),
    ("an attach leaves the older hand's run", "scene.py", "            if live:\n                self.hand.cancel(live)\n        if self._status()", "            if False:\n                self.hand.cancel(live)\n        if self._status()", "test_attach_pauses_a_running_game"),
    ("an abort releases the calm", "scene.py", 'if self._calmed and how == "close":', "if self._calmed:", "test_abort_writes_closing_record"),
    ("a live driver's session is ended", "scene.py", "        if alive is not False:\n", "        if False:\n", "test_end_session_ends_a_dead_driver_only"),
    ("another session's process is used", "scene.py", '        if (d["session"] or {}).get("id") != self.id:\n            raise Fault("SESSION_LOST"', '        if False:\n            raise Fault("SESSION_LOST"', "test_session_of_another_is_lost_not_used"),
]


def copy_tree(to, plant=None):
    top = os.path.join(to, "src", "RimMandrake")
    utils = os.path.join(top, "Utils")
    os.makedirs(utils)
    for n in os.listdir(os.path.join(REPO, "src", "RimMandrake")):
        if n != "Utils":
            os.symlink(os.path.join(REPO, "src", "RimMandrake", n), os.path.join(top, n))
    for n in os.listdir(HERE):
        src = os.path.join(HERE, n)
        if n == "scene_contracts":
            shutil.copytree(src, os.path.join(utils, n))
        elif n == "selftest_scene_library.py" or (n.startswith("scene") and os.path.isfile(src)):
            shutil.copy(src, os.path.join(utils, n))
        elif n != "__pycache__":
            os.symlink(src, os.path.join(utils, n))
    if plant:
        _name, f, old, new, _test = plant
        p = os.path.join(utils, f)
        with open(p, encoding="utf-8") as fh:
            t = fh.read()
        if t.count(old) != 1:
            return None
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(t.replace(old, new))
    return os.path.join(utils, "selftest_scene_library.py")


def one(plant):
    """-> (name, RED | GREEN | WRONG TEST | NOT PLANTED, detail)."""
    with tempfile.TemporaryDirectory() as d:
        t = copy_tree(d, plant)
        if t is None:
            return plant[0], "NOT PLANTED", "the text to replace is not there exactly once"
        # 300 s: a hang guard on a test that ends in seconds
        p = subprocess.run([sys.executable, "-B", t], capture_output=True, text=True, timeout=300)
        red = re.findall(r"^FAIL  (\w+)", p.stdout, re.M)
        if p.returncode == 0:
            return plant[0], "GREEN", "no test saw it"
        return plant[0], "RED" if plant[4] in red else "WRONG TEST", "%s (want %s) %s" % (red, plant[4], p.stderr[-200:])  # cut-ok: test diagnostic display


def main():
    _n, clean, why = _clean()
    print("clean copy: %s" % clean)
    if clean != "GREEN":
        print(why)
        return 1
    with ThreadPoolExecutor(max_workers=8) as ex:
        got = list(ex.map(one, PLANTS))
    for n, state, d in got:
        print("%-12s %s%s" % (state, n, "" if state == "RED" else "  -> " + d))
    red = sum(1 for _n, s, _d in got if s == "RED")
    print("scene library mutants: %d of %d plants seen red" % (red, len(got)))
    return 0 if red == len(got) else 1


def _clean():
    with tempfile.TemporaryDirectory() as d:
        p = subprocess.run([sys.executable, "-B", copy_tree(d)], capture_output=True, text=True, timeout=300)
        return "clean", "GREEN" if p.returncode == 0 else "RED", (p.stdout + p.stderr)[-600:]  # cut-ok: test diagnostic display


if __name__ == "__main__":
    sys.exit(main())
