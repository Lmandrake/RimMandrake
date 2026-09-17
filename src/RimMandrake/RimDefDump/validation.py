"""validation.py -- modcheck suite for RimMandrake RimDefDump
(mandrake.rm.rimdefdump).

Never deployed (deploy_custom_mods.py excludes `.py` wholesale). Run with:

    python.exe src/RimMandrake/Utils/modcheck/cli.py run RimDefDump

Grounded in the mod's actual source, read whole before writing this:
`DefDumper.cs` (the whole file, ~1130 lines -- `Run()`/`RunOnDemand()`/
`RunWithMode()` for the inert-by-default gate and the animals/all scopes,
`Publish()`/`Prune()` for the atomic-rename-then-retain-3 capture lifecycle,
`WriteAllDefs()`'s own collision-disambiguation scheme for `defs/<Type>.json`
filenames); `About.xml` (no ModSettings -- `suite.toggles = []`, per the
runner spec's own floor rule: "zero toggles is not a floor violation");
`JawaBenchDefDumpTools.cs` for the bridge tool this whole suite rides on,
`jawa/rimdefdump_run` (`RimDefDumpDebugActions`'s two `[DebugAction]`s are
UNREACHABLE via `rimworld/execute_debug_action` AND `jawa/debug_actions`,
per that file's own header comment, DEFDUMP_ONDEMAND_BRIDGE_UNREACHABLE_1 --
this bridge tool calls `DefDumper.RunOnDemand` directly instead and reads
back a before/after directory diff rather than trusting the void method's
clean return, since `RunOnDemand` swallows every exception internally).

REAL, CONFIRMED BEHAVIORAL DIVERGENCE between the two ways this mod's dump
can be triggered (not a guess -- read both call sites): the marker-file path
(`DefDumper.Run()` -> `RunWithMode`) treats an unrecognised mode string as a
soft failure -- `Log.Warning` and silently fall through to the animals-only
pass (`DefDumper.cs:188-190`) -- but the BRIDGE tool's own wrapper is
stricter: `RimDefDumpRun`'s own `ToolParameter` doc says exactly why
("Anything else is REFUSED here ... publishing a capture with no defs/ under
a mode the caller never asked for") and returns `Fail(...)` before ever
calling `RunOnDemand` for anything other than exactly `"all"` or `"animals"`.
`mode_bogus_is_refused_by_the_bridge_tool` below asserts the BRIDGE tool's
behavior (the only path this suite can drive), not the marker path's --
walk step 4's "An unrecognised marker mode ... defaults ... rather than
crashing" is about the OTHER path and is NOT exercised here (no bridge tool
writes the marker file at all; see next paragraph).

WHAT THIS SUITE CANNOT PROVE, and why:
  - Walk step 2 ("with no marker file present at game load, Player.log
    contains the inert line and NOT the starting line") is a LOAD-TIME
    contract. Nothing on the bridge can restart the game mid-suite, so
    `inert_by_default_at_load` below only checks that the inert line is
    still SOMEWHERE in the current session's log buffer (`jawa/drain_log`,
    which reads `Log.Messages`, a capped in-memory ring, not the file) from
    THIS run's own boot -- true only as long as that buffer has not rolled
    past it by the time this chain executes, and only as long as no marker
    file was ALREADY sitting at the LocalLow DefDump/dump_request.txt path
    from an unrelated earlier session (this suite never writes or removes
    that file itself -- `jawa/rimdefdump_run` calls `RunOnDemand` directly,
    which takes the mode as a parameter and never touches the marker at
    all). Both are real, uncontrolled preconditions of this component, named
    so a false failure here is not mistaken for a real regression.
  - Retention (walk: "prunes old captures, keeps newest 3") and the capture-
    id-collision refusal (two dumps in the same UTC second) are UNPROVEN --
    no bridge tool lists the full `captures/` directory (only a before/after
    SET DIFF of new entries, from `jawa/rimdefdump_run` itself), and forcing
    two on-demand dumps within the same wall-clock second is not a
    deterministic thing to ask Python to do. Four-plus real captures already
    exist in this repo's own history (DUMP_PRODUCER_DATED_CAPTURES_1), so
    this is a live-observed mechanism, just not one this suite exercises.
  - `defTypeCollisions` (13 real collisions the module's own comment names --
    AbilityDef, CharacterDef, SymbolDef, StructureLayoutDef, FaceTypeDef)
    depends on the exact mod stack loaded; `all_mode_writes_per_deftype_files`
    below only asserts the collisions ARRAY KEY exists and is a list (shape),
    not that any particular collision fired on this run's mod set.
  - Nothing renders in-game (no map object, no pawn, no visible state) --
    per the walk's own step X ("[S] (human pass) none -- this mod produces
    files for another tool to read"), no component below takes a
    screenshot; there is genuinely nothing to photograph.

WHY DIRECT FILE READS, NOT MORE BRIDGE CALLS: this suite's own subject is
"did the right files land on disk with the right content", and no generic
file-read/list-directory bridge tool exists (`jawa/rimdefdump_run` itself
only checks `File.Exists` on `manifest.json`, per its own docstring: "does
not trust a clean return"). Reading `capturePath`'s own files directly with
plain Python is precedented elsewhere in this suite family (KotORBandolierNorthFix
and StarWarsRaces `validation.py` both `os.path.isfile`/`open()` real files on
disk) and is the only way to confirm walk step 3's "manifest.json ... parses
as JSON" and step 4's "defs/<DefType>.json exists" rather than trusting
`manifestPresent` alone. This is safe here specifically because this suite
runs under `python.exe` on the SAME Windows machine as the game
(`GenFilePaths.SaveDataFolderPath` is a native Windows path) -- unlike a
bridge call, this is local disk IO with no session/game-state coupling at
all, so it runs even when `t._guard()` is false only insofar as it is always
skipped by the same guard (see each component below).

Still not proven / likely first-live-run corrections:
  1. `jawa/drain_log`'s ring buffer size was not measured; if a long chain of
     other mods' modcheck runs already pushed the boot-time inert line out
     of `Log.Messages` before this chain runs, `inert_by_default_at_load`
     will fail for a reason unrelated to this mod -- see the note above.
  2. The exact wall-clock gap between the "animals" and "all" on-demand
     calls below is whatever two bridge round-trips take (~tens of ms per
     the runner spec's own measurement); if that ever lands both calls in
     the same UTC second, `Publish()`'s collision-refusal fires for the
     SECOND call and this suite's own `all` component would then see
     `success=False` -- not exercised deliberately, but a real edge this
     suite could hit by accident on a very fast machine.
"""
import json
import os

from modcheck import Suite, ExpectationFailed

suite = Suite("RimDefDump")
suite.toggles = []   # no ModSettings shipped at all -- About.xml, checked whole.

INERT_TAG = "[RimMandrake.RimDefDump] inert (no dump_request.txt)."
STARTING_TAG = "[RimMandrake.RimDefDump] starting, mode="


def _read_manifest(capture_path):
    """Plain local file IO -- see module docstring on why this, not a bridge
    call, is the right tool here. Returns (manifest_dict_or_None, error_or_None)."""
    path = os.path.join(capture_path, "manifest.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f), None
    except Exception as ex:
        return None, "%s: %s" % (type(ex).__name__, ex)


@suite.chain("inert_by_default_at_load")
def inert_by_default_at_load(t):
    """No test area needed -- this is world/log state only, no map things."""
    with t.component("no_dump_at_load_without_marker", beyond_toggle=True):
        t.expect_log_contains(INERT_TAG)
        if t._guard():
            r = t.bridge_call("jawa/drain_log", limit=500, contains=STARTING_TAG)
            msgs = [m.get("text", "") for m in ((r or {}).get("messages") or [])]
            if msgs:
                raise ExpectationFailed(
                    "Player.log's recent buffer contains %r even though no "
                    "dump was requested yet this session -- either a marker "
                    "file was already present at load (see module docstring's "
                    "uncontrolled-precondition note) or something upstream in "
                    "this run already triggered an on-demand dump: %r"
                    % (STARTING_TAG, msgs))


@suite.chain("on_demand_dump_animals_mode")
def on_demand_dump_animals_mode(t):
    """`mode="animals"` is the fast path -- manifest.json + animals.json,
    no `defs/`. Proves walk step 3."""
    with t.component("animals_capture_published", beyond_toggle=True):
        r = t.bridge_call("jawa/rimdefdump_run", mode="animals")
        if not t._guard():
            return
        if not (r or {}).get("success"):
            raise ExpectationFailed("jawa/rimdefdump_run(mode=animals) failed: %r" % r)
        if r.get("mode") != "animals":
            raise ExpectationFailed("echoed mode was %r, expected 'animals'" % r.get("mode"))
        if not r.get("manifestPresent"):
            raise ExpectationFailed(
                "rimdefdump_run reported success but manifestPresent=False: %r" % r)
        capture_path = r.get("capturePath")
        manifest, err = _read_manifest(capture_path)
        if manifest is None:
            raise ExpectationFailed(
                "manifest.json under %r did not parse as JSON: %s" % (capture_path, err))
        if manifest.get("mode") != "animals":
            raise ExpectationFailed(
                "manifest.json's own 'mode' field was %r, expected 'animals'"
                % manifest.get("mode"))
        animals_json = os.path.join(capture_path, "animals.json")
        if not os.path.isfile(animals_json):
            raise ExpectationFailed("animals.json missing from %r" % capture_path)
        defs_dir = os.path.join(capture_path, "defs")
        if os.path.isdir(defs_dir):
            raise ExpectationFailed(
                "mode=animals published a defs/ directory (%r) -- it should "
                "be animals.json + manifest.json only" % defs_dir)


@suite.chain("on_demand_dump_all_mode")
def on_demand_dump_all_mode(t):
    """`mode="all"` -- proves walk step 4 (a common DefType's own file lands
    in `defs/`) and step 5's positive half (the "wrote N def-type files"
    summary line)."""
    with t.component("all_mode_writes_per_deftype_files", beyond_toggle=True):
        r = t.bridge_call("jawa/rimdefdump_run", mode="all")
        if not t._guard():
            return
        if not (r or {}).get("success"):
            raise ExpectationFailed("jawa/rimdefdump_run(mode=all) failed: %r" % r)
        if r.get("mode") != "all":
            raise ExpectationFailed("echoed mode was %r, expected 'all'" % r.get("mode"))
        capture_path = r.get("capturePath")
        manifest, err = _read_manifest(capture_path)
        if manifest is None:
            raise ExpectationFailed(
                "manifest.json under %r did not parse as JSON: %s" % (capture_path, err))
        def_types = manifest.get("defTypes")
        if not isinstance(def_types, list) or not def_types:
            raise ExpectationFailed(
                "manifest.json's 'defTypes' array is empty/missing for mode=all "
                "-- the generic per-type pass should have walked hundreds of "
                "def-type databases: %r" % def_types)
        if not isinstance(manifest.get("defTypeCollisions"), list):
            raise ExpectationFailed(
                "manifest.json has no 'defTypeCollisions' array at all (shape "
                "check only -- which types collide depends on the live mod "
                "stack, not asserted here): %r" % manifest.get("defTypeCollisions"))
        thing_def_json = os.path.join(capture_path, "defs", "ThingDef.json")
        if not os.path.isfile(thing_def_json):
            raise ExpectationFailed(
                "defs/ThingDef.json missing from %r -- ThingDef is a vanilla "
                "def type that must exist on any mod list" % capture_path)

        t.expect_log_contains("[RimMandrake.RimDefDump] wrote ")
        if t._guard():
            log = t.bridge_call("jawa/drain_log", limit=500, contains="def type name collision")
            hits = [m.get("text", "") for m in ((log or {}).get("messages") or [])]
            # A collision line is only a defect if it names a TYPE that lost
            # data (see module docstring's DUMP_PRODUCER_DATED_CAPTURES_1
            # history) -- but the manifest's own defTypeCollisions array
            # above is the authoritative, structured version of the same
            # fact, so a raw log line here is corroborating evidence only,
            # not re-asserted as a failure condition on its own.
            t._record("collision log lines seen (informational)", hits)


@suite.chain("bridge_tool_mode_validation")
def bridge_tool_mode_validation(t):
    """The bridge wrapper's OWN stricter mode check (see module docstring's
    divergence note) -- distinct from `DefDumper.RunWithMode`'s own
    warn-and-default behavior, which this suite has no path to exercise."""
    with t.component("mode_bogus_is_refused_by_the_bridge_tool", beyond_toggle=True):
        r = t.bridge_call("jawa/rimdefdump_run", mode="ALL_DEFS")
        if not t._guard():
            return
        if (r or {}).get("success"):
            raise ExpectationFailed(
                "jawa/rimdefdump_run(mode='ALL_DEFS') SUCCEEDED -- the tool's own "
                "ToolParameter doc says any mode other than 'all'/'animals' is "
                "refused before DefDumper.RunOnDemand is ever called: %r" % r)
        err = (r or {}).get("error") or ""
        if "must be 'all' or 'animals'" not in err:
            raise ExpectationFailed(
                "rimdefdump_run(mode='ALL_DEFS') failed for an unexpected reason "
                "(expected the mode-validation message): %r" % r)
