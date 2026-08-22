#!/usr/bin/env python3
"""Selftest for rimflow/importer.py.

⭐ THE IMPORT IS THE ONE-WAY DOOR. `model.py`'s refusals can be re-run all day; this
runs ONCE against 827 KB of hand-written prose and whatever it decides becomes the
permanent record. A wrong guess here is not a bug that gets fixed later — it is a
closed item that was never closed, or 21 deferred items marked finished.

So the cases below are the ones where a silent wrong answer is expensive:

  * `⛔ v2` reading as *done* instead of *dropped-to-v2*
  * an emoji state being ignored, or overruling a word that disagrees with it
  * an item quietly disappearing because its heading did not parse
  * prose landing in the wrong section, or arriving as a code block
  * a legacy ID being "tidied" into the new naming scheme
  * `--apply` running twice over a ledger that already exists
  * this tool touching queue/*.md at all

Every case runs against synthetic queue files in a throwaway directory. It never reads
the real queues and never writes the real ledger.

    python3 src/RimMandrake/rimflow/selftest_importer.py
"""
import hashlib
import io
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from rimflow import model, importer                                  # noqa: E402

PASS, FAIL = [], []


def case(name, fn):
    try:
        fn()
        PASS.append(name)
        print("ok    %s" % name)
    except AssertionError as e:
        FAIL.append(name)
        print("FAIL  %s\n        %s" % (name, e))
    except Exception as e:
        FAIL.append(name)
        print("FAIL  %s\n        unexpected %s: %s" % (name, type(e).__name__, e))


# ---------------------------------------------------------------------------
# A synthetic queue that carries one example of every shape the real ones do.
# ---------------------------------------------------------------------------
FIXTURE = {
    "BUILD.md": u"""# BUILD inbox.

## \U0001f534 OWNER RULINGS, 2026-08-19 — prose, not an item
This heading has no ID and must not become an item.

## B58 The dead Jawa pawnkind
row:      12
spec:     Rebuild the kind so the raid can field it.
          A second line, indented to line up under the label.
verify:   `python3 tool.py --check`
criteria: the raid fields it.
state:    ready

## SANDSTORM_WEATHER_TUNING_1 Tune the sandstorm
row:      4
spec:     one
verify:   two
criteria: three
from:     a finding
state:    ⛔ v2 — **OWNER RULING 2026-08-15, blanket triage.**

## LIGHTSABER_PENETRATION_CHECK_1 Measure it live
spec:     one
verify:   two
criteria: three
state:    \U0001f535 IN PROGRESS — WIDER THAN FILED.

## CHERRYPICK_SETTINGS_LOAD_1 The settings actually load
spec:     one
verify:   two
criteria: three
state:    ✅ CLOSED 2026-08-19 — landed in `f0a9f6c`.

## BOILING_BIOME_REFERENCE_1 Cut it
spec:     one
verify:   two
criteria: three
state:    superseded by SANDSTORM_WEATHER_TUNING_1 — same ground.

## ROSTER_HARNESS_ODDITY_1 An unrecognised coinage
spec:     one
verify:   two
criteria: three
state:    harness built 2026-08-20, the soak is CHECK's and is not done.

## NO_FIELDS_AT_ALL_1 A briefing with no fields
Just prose. Nothing here parses as a field at all.
""",
    "CHECK.md": u"""# CHECK inbox.

## B58 The dead Jawa pawnkind — a SECOND heading for the same ID
spec:     CHECK's half.
state:    ready

## C43 The lightsabre check
spec:     one
verify:   two
criteria: three
state:    ⛔ CLOSED — MOVED TO v2, owner's ruling.

## BLOCKED_ON_A_HUMAN_1 Waiting
spec:     one
verify:   two
criteria: three
state:    blocked — needs a human answer
""",
}
CANON_SOURCES = [("BUILD.md", "BUILD", "task"), ("CHECK.md", "CHECK", "check")]


def fixture_dir():
    d = tempfile.mkdtemp(prefix="rimflow_imp_fixture_")
    os.makedirs(os.path.join(d, "queue"))
    for name, text in FIXTURE.items():
        with open(os.path.join(d, "queue", name), "w", encoding="utf-8") as fh:
            fh.write(text)
    return d


class Rig(object):
    """Point the importer at the fixture, and put its output in a throwaway dir."""

    def __enter__(self):
        self.dir = fixture_dir()
        self._q, self._s = importer.QUEUE, importer.SOURCES
        self._c, self._i = importer.CLOSED_LEDGER, model.ITEMS
        importer.QUEUE = os.path.join(self.dir, "queue")
        importer.SOURCES = CANON_SOURCES
        importer.CLOSED_LEDGER = os.path.join(self.dir, "closed_ledger.json")
        self.items_dir = os.path.join(self.dir, "items")
        self.events = os.path.join(self.dir, "ledger", "events.jsonl")
        return self

    def __exit__(self, *a):
        importer.QUEUE, importer.SOURCES = self._q, self._s
        importer.CLOSED_LEDGER, model.ITEMS = self._c, self._i
        shutil.rmtree(self.dir, ignore_errors=True)

    def convert(self):
        items, skipped, heads = importer.collect()
        return importer.build(items), skipped, heads

    def by_id(self, iid):
        for c in self.convert()[0]:
            if c.parsed.id == iid and c.body:
                return c
        raise AssertionError("no conversion for %s" % iid)

    def run(self, *argv):
        """Run main() with stdout captured. Returns (rc, output)."""
        buf, old = io.StringIO(), sys.stdout
        sys.stdout = buf
        try:
            rc = importer.main(list(argv) + ["--events", self.events,
                                             "--items", self.items_dir])
        finally:
            sys.stdout = old
        return rc, buf.getvalue()


def verbs(conv):
    return [e["event"] for e in conv.events]


def event(conv, verb):
    for e in conv.events:
        if e["event"] == verb:
            return e
    raise AssertionError("%s has no %s event; it has %s"
                         % (conv.parsed.id, verb, verbs(conv)))


# ---------------------------------------------------------------------------
def t_emoji_state_converts():
    """\U0001f535 IN PROGRESS is `doing`. If this fails the board shows live work as idle."""
    with Rig() as r:
        c = r.by_id("LIGHTSABER_PENETRATION_CHECK_1")
        assert c.state == "doing", c.state
        assert "start" in verbs(c), verbs(c)
        assert c.confidence == "inferred", (c.confidence, c.why)
        assert "emoji" in c.why[0], c.why


def t_v2_is_dropped_to_v2_not_done():
    """⛔ v2 must become dropped AND targeted v2.

    If it reads as `done`, ~21 items the owner deliberately deferred are recorded as
    finished, the board's numerator jumps, and nobody ever looks at them again. If it
    reads as dropped but keeps `target: v1`, the deferral itself is lost.
    """
    with Rig() as r:
        c = r.by_id("SANDSTORM_WEATHER_TUNING_1")
        assert c.state == "dropped", c.state
        assert event(c, "file")["target"] == "v2", event(c, "file")
        assert "drop" in verbs(c) and "close" not in verbs(c), verbs(c)


def t_closed_but_deferred_is_dropped_not_done():
    """🔴 `⛔ CLOSED — MOVED TO v2` is NOT delivered, and it must not import as done.

    The word `closed` is genuinely ambiguous in these queues: it means "done" almost
    everywhere, and "closed the item without doing it" in the two places where the
    owner pushed something to v2. Taking the leading word made both of those `done` —
    writing two undelivered things into the permanent record as delivered, which
    inflates the exact count this migration exists to make trustworthy.

    ⚠️ So a deferral phrase BEATS the word, and both source lines were unambiguous to a
    human on 2026-08-20 and only ambiguous to the classifier. It is `inferred`, not
    `uncertain`: the deferral is explicit, so there is nothing left to guess.
    """
    with Rig() as r:
        c = r.by_id("C43")
        assert c.state == "dropped", (c.state, c.why)
        tgt = [e.get("target") for e in c.events if e["event"] == "file"]
        assert tgt and tgt[0] == "v2", tgt
        assert "close" not in verbs(c), (
            "an undelivered item was imported as a close: %s" % verbs(c))
        assert "NOT delivered" in " ".join(c.why), c.why


def t_emoji_word_conflict_with_no_deferral_is_uncertain():
    """A bare emoji/word disagreement is still a guess and must be shown to a human.

    ⚠️ This is the case the deferral rule must NOT swallow. Without an explicit
    "MOVED TO v2" there is nothing to disambiguate on, the word wins by
    derive_matrix's rule, and the item is flagged `uncertain` so someone looks.
    """
    state, conf, why = importer.classify("⛔ DONE — shipped 2026-08-14")
    assert conf == "uncertain", (state, conf, why)
    assert "emoji" in why and "word" in why, why


def t_nothing_is_silently_dropped():
    """Item count in must equal item count out, and an unparseable item still lands."""
    with Rig() as r:
        convs, skipped, heads = r.convert()
        n_in = len(convs)
        filed = sum(1 for c in convs if c.body)
        merged = n_in - filed
        assert heads == n_in + len(skipped), (heads, n_in, len(skipped))
        assert filed + merged == n_in, (filed, merged, n_in)
        c = r.by_id("NO_FIELDS_AT_ALL_1")
        assert c.confidence == "uncertain", c.confidence
        assert "note" in verbs(c), (
            "an item nothing could be parsed from was filed with no `note` saying so; "
            "a silent guess here becomes the permanent record")


def t_prose_lands_in_the_right_section():
    """spec/verify/criteria go to their own sections; everything else to notes."""
    with Rig() as r:
        body = r.by_id("B58").body
        assert body.startswith("## spec\n"), body[:40]
        for want in ("## spec", "## verify", "## criteria", "## notes"):
            assert want in body, want
        assert "Rebuild the kind" in body.split("## verify")[0]
        assert "tool.py --check" in body.split("## verify")[1].split("## criteria")[0]
        assert "the raid fields it." in body.split("## criteria")[1].split("## notes")[0]
        above_notes = body.split("## notes")[0]
        assert "row:" not in above_notes and "state:" not in above_notes, (
            "a scalar was copied into items/<ID>.md as well as the ledger — that is "
            "the drift the whole design exists to end:\n%s" % above_notes)


def t_continuations_are_dedented():
    """A field's continuation lines are aligned past `criteria: `. Carried through, the
    ten-space indent turns every multi-line field into a markdown code block."""
    with Rig() as r:
        spec = r.by_id("B58").body.split("## verify")[0]
        assert "\nA second line" in spec, (
            "the continuation kept its label indent and will render as code:\n%r" % spec)


def t_other_fields_reach_notes():
    with Rig() as r:
        notes = r.by_id("SANDSTORM_WEATHER_TUNING_1").body.split("## notes")[1]
        assert "**from:** a finding" in notes, notes
        assert "OWNER RULING 2026-08-15" in notes, (
            "the raw `state:` prose was discarded; it is the argument nobody can "
            "reconstruct, and it is the only place the ruling is quoted")


def t_legacy_id_survives_unrenamed():
    """B58 stays B58. Renumbering an item away breaks the board's history
    irrecoverably — `Closes: B58` in a commit must still resolve."""
    with Rig() as r:
        c = r.by_id("B58")
        assert c.parsed.id == "B58"
        assert os.path.basename("B58.md") == "B58.md"
        assert event(c, "file")["id"] == "B58"
        model.validate(dict(event(c, "file"), ts=model.now()))


def t_duplicate_id_is_merged_not_lost():
    """B58 is filed in BOTH queues. `file` twice is refused by the model, so the second
    becomes a note — and its prose is appended rather than thrown away."""
    with Rig() as r:
        convs = r.convert()[0]
        b58 = [c for c in convs if c.parsed.id == "B58"]
        assert len(b58) == 2, len(b58)
        second = [c for c in b58 if not c.body][0]
        assert verbs(second) == ["note"], verbs(second)
        assert second.confidence == "uncertain", second.confidence
        host = [c for c in b58 if c.body][0]
        assert "CHECK's half." in host.body, (
            "the duplicate heading's prose vanished:\n%s" % host.body[-400:])


def t_supersede_names_its_successor():
    with Rig() as r:
        c = r.by_id("BOILING_BIOME_REFERENCE_1")
        assert event(c, "supersede")["by"] == "SANDSTORM_WEATHER_TUNING_1", c.events


def t_blocked_is_a_flag_not_a_state():
    with Rig() as r:
        c = r.by_id("BLOCKED_ON_A_HUMAN_1")
        assert "block" in verbs(c) and event(c, "block")["reason"], c.events
        world = model.replay([dict(e, ts=model.now()) for e in c.events], strict=False)
        it = world.items["BLOCKED_ON_A_HUMAN_1"]
        assert it.blocked and it.state != "blocked", (
            "blocked collapsed into the state enum, which is what made the old queues "
            "unable to say 'ready, but waiting on an answer'")


def t_unrecognised_coinage_stays_open():
    """A state nobody's vocabulary knows must fall to OPEN work and be flagged, never
    to `done`. Falling closed is how work disappears."""
    with Rig() as r:
        c = r.by_id("ROSTER_HARNESS_ODDITY_1")
        assert c.state == "ready", c.state
        assert c.confidence == "uncertain", (c.confidence, c.why)


def t_every_event_passes_the_model():
    with Rig() as r:
        for c in r.convert()[0]:
            for e in c.events:
                model.validate(dict(e, ts=model.now()))


def t_prose_headings_are_skipped_but_reported():
    with Rig() as r:
        skipped = r.convert()[1]
        assert any("OWNER RULINGS" in h for h, _b in skipped), skipped
        rc, out = r.run()
        assert "OWNER RULINGS" in out, (
            "a skipped heading was not listed; a human has to be able to check that "
            "none of them was actually work")


def t_skipped_prose_keeps_its_body():
    """A heading with no body would be a useless rescue."""
    with Rig() as r:
        skipped = r.convert()[1]
        bodies = [b for h, b in skipped if "OWNER RULINGS" in h]
        assert bodies and any(l.strip() for l in bodies[0]), (
            "the section was captured as a bare heading; its prose is what matters")


def t_apply_preserves_prose_before_writing_anything():
    """🔴 THE GUARD ON THE ONE-WAY DOOR.

    18 sections across the six queues carry no fields at all — session handoffs, owner
    rulings, and in `HUMAN.md` thirteen sections of briefings written TO the owner,
    several still unanswered. 853 lines, measured 2026-08-20. The ledger has nowhere to
    put them: an event carries scalars, an item file carries spec/verify/criteria, and
    a briefing is neither. Once `queue/*.md` is a generated view they are gone — git
    would still have them, which is recovery, not access, because nobody greps a
    deleted file.

    ⚠️ So preservation runs INSIDE `--apply`, first, and this asserts it. A separate
    step is a step someone skips, and this one is unskippable exactly once.
    """
    with Rig() as r:
        dest = os.path.join(r.dir, "preserved")
        importer.preserve(r.convert()[1], dest)
        files = sorted(os.listdir(dest))
        assert files, "nothing was preserved"
        text = open(os.path.join(dest, files[0]), encoding="utf-8").read()
        assert "OWNER RULINGS" in text, text[:200]
        assert "This heading has no ID" in text, (
            "the heading was rescued without its body")
        # 🔴 The banner used to read "HAND-WRITTEN. NOT GENERATED. Nothing regenerates
        # this file" — and this test ASSERTED that wording, which is how a false claim
        # survived: the function printing it was the generator, opening with "w".
        # ⚠️ What the file actually needed was not a claim, it was a GUARD. Corrected
        # 2026-08-22: the banner tells the truth, and the two asserts below pin the
        # protection instead of the assertion of protection.
        assert "GENERATED ONCE" in text and "refuses to overwrite" in text, (
            "the rescue file must say what actually made it, and that it is now safe "
            "to edit:\n%s" % text[:300])
        # ⛔ THE GUARD ITSELF. A second run must not touch a file that exists.
        marked = os.path.join(dest, files[0])
        open(marked, "a", encoding="utf-8").write("\n<!-- a human edited this -->\n")
        importer.preserve(r.convert()[1], dest)
        assert "a human edited this" in open(marked, encoding="utf-8").read(), (
            "a second preserve() run destroyed a hand-edit — the exact loss the old "
            "banner promised could not happen")


# ---- the irreversible half -------------------------------------------------
def t_dry_run_writes_nothing():
    with Rig() as r:
        rc, out = r.run()
        assert rc == 0, out[-800:]
        assert "DRY RUN" in out
        assert not os.path.exists(r.events), "the dry run wrote the ledger"
        assert not os.path.exists(r.items_dir), "the dry run wrote items/"


def t_apply_writes_then_refuses_a_second_run():
    """\U0001f534 The refusal that matters. A second import would file all 145 items again;
    `file` on an existing id is refused, so the run half-lands and leaves a ledger
    nobody can read backwards to a clean state."""
    with Rig() as r:
        rc, out = r.run("--apply")
        assert rc == 0, out[-800:]
        assert os.path.getsize(r.events) > 0
        assert os.path.exists(os.path.join(r.items_dir, "B58.md"))

        err, old = io.StringIO(), sys.stderr
        sys.stderr = err
        try:
            rc2, _ = r.run("--apply")
        finally:
            sys.stderr = old
        assert rc2 == 2, "a second --apply was allowed over a non-empty ledger"
        msg = err.getvalue()
        assert "REFUSED" in msg and "--force" in msg, (
            "the refusal must say why and how to override it: %s" % msg)
        assert "append-only" in msg.lower(), msg


def t_apply_never_touches_the_queues():
    """⛔ The one mistake that cannot be undone. queue/*.md is the only copy until a
    human has compared the import against it."""
    with Rig() as r:
        before = {}
        for name, _, _ in CANON_SOURCES:
            p = os.path.join(importer.QUEUE, name)
            before[name] = (os.path.getmtime(p),
                            hashlib.sha256(open(p, "rb").read()).hexdigest())
        r.run("--apply")
        r.run()
        for name, (mt, h) in before.items():
            p = os.path.join(importer.QUEUE, name)
            assert os.path.getmtime(p) == mt, "%s was touched" % name
            assert hashlib.sha256(open(p, "rb").read()).hexdigest() == h, \
                "%s was REWRITTEN by the importer" % name


def t_applied_ledger_replays_clean():
    with Rig() as r:
        r.run("--apply")
        saved, model.ITEMS = model.ITEMS, r.items_dir   # the gate reads model.ITEMS
        try:
            world = model.replay(model.read(r.events))
        finally:
            model.ITEMS = saved
        assert not world.errors, world.errors
        assert world.items["SANDSTORM_WEATHER_TUNING_1"].state == "dropped"
        assert world.items["SANDSTORM_WEATHER_TUNING_1"].target == "v2"
        assert world.items["CHERRYPICK_SETTINGS_LOAD_1"].state == "done"
        assert world.items["LIGHTSABER_PENETRATION_CHECK_1"].state == "doing"
        assert world.items["B58"].state == "ready"


CASES = [(k[2:], v) for k, v in sorted(globals().items()) if k.startswith("t_")]

if __name__ == "__main__":
    for name, fn in CASES:
        case(name, fn)
    print("\n%d/%d passed" % (len(PASS), len(PASS) + len(FAIL)))
    sys.exit(1 if FAIL else 0)
